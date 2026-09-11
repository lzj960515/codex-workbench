#!/usr/bin/env python3
"""Snapshot a discovered Skill catalog, then run one local fixture in fresh Codex.

Discovery, execution and grading are separate claims. A completed run is ungraded.
Use --help and references/codex-evaluation.md for the two-phase CLI contract.
"""

import argparse
import hashlib
import json
import os
import queue
import re
import shutil
import stat
import subprocess
import tempfile
import time
import tomllib
from pathlib import Path

from codex_eval_runtime import CodexSession, EvaluationBlocked, run_turn, write_json


IGNORED = {'.git', '__pycache__', '.DS_Store', '.pytest_cache'}


def check_catalog(actual, expected):
    if actual['errors']:
        raise EvaluationBlocked('Skill discovery errors: ' + json.dumps(actual['errors']))
    enabled = [s for s in actual['skills'] if s['enabled']]
    names = [s['name'] for s in enabled]
    if len(names) != len(set(names)):
        raise EvaluationBlocked('Duplicate enabled Skill names require resolving discovery precedence first')
    found = {str(Path(s['path']).resolve()) for s in enabled}
    wanted = {str(Path(p).resolve()) for p in expected}
    if found != wanted:
        raise EvaluationBlocked(json.dumps({'unexpected': sorted(found-wanted), 'missing': sorted(wanted-found)}))
    return sorted(found)


def workspace_state(root):
    state = {}
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts):
            continue
        if path.is_symlink():
            state[str(relative)] = {'kind': 'symlink', 'target': os.readlink(path)}
        elif path.is_file():
            state[str(relative)] = {'kind': 'file', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                    'mode': stat.S_IMODE(path.stat().st_mode)}
    return state


def package_hash(skill_file):
    state = workspace_state(Path(skill_file).parent)
    return hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()


def copy_skill(source, destination):
    # 用例和评分答案留给评估端；执行端只接收可用的 Skill 工程内容。
    shutil.copytree(source, destination,
                    ignore=shutil.ignore_patterns(*IGNORED, 'evals'))


def discover(session, cwd):
    session.initialize()
    return session.request('skills/list', {'cwds': [str(cwd)], 'forceReload': True})['data'][0]


def snapshot(args):
    output = Path(args.out).resolve()
    output.mkdir(parents=True, exist_ok=False)
    cwd = Path(args.cwd).resolve()
    session = CodexSession(cwd, output, {})
    try:
        discovered = discover(session, cwd)
    finally:
        session.close()
    expected = [s['path'] for s in discovered['skills'] if s['enabled']]
    check_catalog(discovered, expected)
    write_json(output/'source-discovery.json', discovered)
    sources = []
    for skill in discovered['skills']:
        if not skill['enabled']:
            continue
        source = Path(skill['path']).parent.resolve()
        if source == output or source in output.parents:
            raise ValueError('Snapshot output must be outside source Skill packages')
        if Path(skill['name']).name != skill['name'] or skill['name'] in {'.', '..'}:
            raise ValueError('Invalid discovered Skill name: ' + skill['name'])
        for variant in ['baseline', 'candidate']:
            copy_skill(source, output/variant/skill['name'])
        sources.append({'name': skill['name'], 'path': str(source), 'scope': skill['scope'],
                        'sha256': package_hash(source/'SKILL.md')})
    variants = {}
    for variant in ['baseline', 'candidate']:
        paths = sorted((output/variant).glob('*/SKILL.md'))
        variants[variant] = {'roots': [variant], 'expected_paths': [str(p.relative_to(output)) for p in paths]}
    paths = {s['path'] for s in discovered['skills']}
    paths |= {str(Path(p).resolve()) for p in paths}
    cases = []
    if args.suite:
        suite_path = Path(args.suite).resolve()
        for original in json.loads(suite_path.read_text())['evals']:
            case = dict(original)
            validate_case(case)
            if case.get('fixture'):
                case['fixture'] = str((suite_path.parent/case['fixture']).resolve())
            cases.append(case)
    matrix = {'version': 1, 'variants': variants, 'disabled_paths': sorted(paths),
              'common_config': {}, 'cases': cases}
    write_json(output/'snapshot-manifest.json', {'source_cwd': str(cwd), 'sources': sources})
    write_json(output/'evaluation-matrix.json', matrix)
    print(json.dumps({'output': str(output), 'skills': len(sources), 'model_calls': 0}))
    return 0


def prepare_workspace(base, case, workspace):
    fixture = case.get('fixture')
    if fixture:
        source = (base/fixture).resolve()
        if any(p.is_symlink() for p in source.rglob('*')):
            raise ValueError('Use self-contained fixture files instead of symlinks')
        shutil.copytree(source, workspace, ignore=shutil.ignore_patterns(*IGNORED))
    else:
        workspace.mkdir()
    for stored, restored in case.get('fixture_renames', {}).items():
        source, destination = workspace/stored, workspace/restored
        if any(workspace.resolve() not in p.resolve().parents for p in [source, destination]):
            raise ValueError('Fixture renames must stay inside the trial workspace')
        if destination.exists():
            raise ValueError('Fixture rename would overwrite: ' + restored)
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)
    subprocess.run(['git', 'init', '--quiet'], cwd=workspace, check=True, capture_output=True)


def validate_case(case):
    if not isinstance(case.get('prompt'), str) or not case['prompt'].strip():
        raise ValueError('A case needs a nonempty natural-language prompt')
    if case.get('sandbox', 'read-only') not in {'read-only', 'workspace-write'}:
        raise ValueError('Local evaluations support read-only or workspace-write only')


def capture_outcome(workspace, output, before):
    after = workspace_state(workspace)
    changes = {name: {'before': before.get(name), 'after': after.get(name)}
               for name in sorted(before.keys() | after.keys()) if before.get(name) != after.get(name)}
    write_json(output/'workspace-before.json', before)
    write_json(output/'workspace-after.json', after)
    write_json(output/'changes.json', changes)
    for name, record in after.items():
        if record['kind'] == 'file':
            destination = output/'outputs'/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(workspace/name, destination)


def cleanup_trial_trust(config_path, trial_root, prior_keys):
    if not config_path.exists():
        return 0
    text = config_path.read_text()
    before = tomllib.loads(text)
    root = trial_root.resolve()
    remove = {key for key in before.get('projects', {}) if key not in prior_keys
              and (Path(key).resolve() == root or root in Path(key).resolve().parents)}
    if not remove:
        return 0
    kept = []
    for part in re.split(r'(?=^\[)', text, flags=re.M):
        header = part.split('\n', 1)[0]
        name = None
        if header.startswith('[projects.') and header.endswith(']'):
            name = tomllib.loads('key = ' + header[len('[projects.'):-1])['key']
        if name not in remove:
            kept.append(part)
    updated = ''.join(kept)
    expected = {**before, 'projects': {key: value for key, value in before.get('projects', {}).items() if key not in remove}}
    if tomllib.loads(updated) != expected or config_path.read_text() != text:
        raise EvaluationBlocked('Configuration changed during cleanup; preserve it and review temporary trust entries')
    config_path.write_text(updated)
    return len(remove)


def run_configuration(matrix, variant, base):
    config = dict(matrix.get('common_config', {}))
    disabled = matrix.get('disabled_paths', []) + variant.get('disabled_paths', [])
    config['skills.config'] = [{'path': str((base/path).resolve()), 'enabled': False} for path in sorted(set(disabled))]
    return config


def environment_fingerprint(config_path, workspace):
    config = tomllib.loads(config_path.read_text()) if config_path.exists() else {}
    # 项目信任记录会由CLI创建；它们单独清理，不参与两次运行的内容比较。
    config.pop('projects', None)
    paths = {config_path.parent/'AGENTS.md', config_path.parent/'AGENTS.override.md'}
    for parent in workspace.parents:
        paths.update([parent/'AGENTS.md', parent/'AGENTS.override.md'])
    instructions = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
    # 仅保存摘要，不把用户配置中的敏感值复制到测试报告。
    digest = hashlib.sha256(json.dumps({'config': config, 'instructions': instructions}, sort_keys=True).encode()).hexdigest()
    return {'sha256': digest, 'instruction_files': instructions}


def evaluate(args):
    matrix_path = Path(args.matrix).resolve()
    base = matrix_path.parent
    matrix = json.loads(matrix_path.read_text())
    if matrix.get('version') != 1:
        raise ValueError('Unsupported evaluation matrix version')
    variant = matrix['variants'][args.variant]
    cases = [c for c in matrix['cases'] if str(c['id']) == str(args.case)]
    if len(cases) != 1:
        raise ValueError('Select exactly one case by id')
    case = cases[0]
    validate_case(case)
    output = Path(args.out).resolve()
    output.mkdir(parents=True, exist_ok=False)
    expected = [str((base/p).resolve()) for p in variant['expected_paths']]
    roots = [str((base/p).resolve()) for p in variant['roots']]
    result = {'variant': args.variant, 'case': case['id'], 'status': 'preflight',
              'quality_grade': 'not_graded', 'model_calls_started': 0,
              'prompt': case['prompt'], 'check_only': args.check_only,
              'sandbox': case.get('sandbox', 'read-only'),
              'matrix_sha256': hashlib.sha256(matrix_path.read_bytes()).hexdigest(),
              'limits': ['CLI execution is not proven equivalent to the desktop app.',
                         'Enabled catalog is not proof of invocation or filesystem isolation.',
                         'Skill snapshots omit evals and flatten discovery scope; external tools and global instructions remain environment inputs.']}
    write_json(output/'eval_metadata.json', {'eval_id': case['id'], 'eval_name': case.get('name', str(case['id'])), 'prompt': case['prompt']})
    config_path = Path(os.environ.get('CODEX_HOME', str(Path.home()/'.codex')))/'config.toml'
    prior_keys = set(tomllib.loads(config_path.read_text()).get('projects', {})) if config_path.exists() else set()
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='codex-skill-eval-') as trial:
        trial_root = Path(trial)
        workspace = trial_root/'workspace'
        session = None
        before = None
        try:
            prepare_workspace(base, case, workspace)
            before = workspace_state(workspace)
            result['fixture_sha256'] = hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest()
            result['environment'] = environment_fingerprint(config_path, workspace)
            session = CodexSession(workspace, output, run_configuration(matrix, variant, base))
            session.initialize()
            session.request('skills/extraRoots/set', {'extraRoots': roots})
            discovery = session.request('skills/list', {'cwds': [str(workspace)], 'forceReload': True})['data'][0]
            write_json(output/'discovery.json', discovery)
            result['enabled_paths'] = check_catalog(discovery, expected)
            result['enabled_package_sha256'] = {p: package_hash(p) for p in expected}
            result['catalog_verified'] = True
            if args.check_only:
                result['status'] = 'discovery_verified'
            else:
                result['model_calls_started'] = 1
                run_turn(session, case, workspace, result, output, args.timeout)
            if result['enabled_package_sha256'] != {p: package_hash(p) for p in expected}:
                raise EvaluationBlocked('Skill packages changed during the trial; rerun against a stable snapshot')
            if result['environment'] != environment_fingerprint(config_path, workspace):
                raise EvaluationBlocked('Local configuration or global instructions changed during the trial')
        except (EvaluationBlocked, TimeoutError, queue.Empty, OSError, ValueError, subprocess.CalledProcessError) as error:
            result['status'] = 'incomplete'
            result['execution_error'] = str(error) or 'Runtime response timed out'
        finally:
            if session is not None:
                session.close()
            if before is not None:
                capture_outcome(workspace, output, before)
            try:
                result['temporary_trust_entries_removed'] = cleanup_trial_trust(config_path, trial_root, prior_keys)
            except (EvaluationBlocked, OSError, ValueError) as error:
                result['status'] = 'incomplete'
                result['cleanup_error'] = str(error)
                result['temporary_project_path'] = str(trial_root)
            result['duration_seconds'] = round(time.monotonic()-started, 2)
            write_json(output/'result.json', result)
            write_json(output/'timing.json', {'total_tokens': result.get('token_usage', {}).get('total', {}).get('totalTokens'),
                                              'duration_ms': round(result['duration_seconds']*1000),
                                              'total_duration_seconds': result['duration_seconds']})
    print(json.dumps({k: result.get(k) for k in ['case', 'variant', 'status', 'quality_grade', 'catalog_verified', 'duration_seconds', 'execution_error', 'cleanup_error']}, ensure_ascii=False))
    return 0 if result['status'] in {'discovery_verified', 'completed'} else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', action='store_true', help='Copy enabled packages into baseline and candidate; no model call')
    parser.add_argument('--cwd', default='.', help='Source project used for discovery when snapshotting')
    parser.add_argument('--suite', help='Optional evals.json to import when snapshotting')
    parser.add_argument('--matrix', help='Evaluation matrix; paths are relative to this JSON file')
    parser.add_argument('--variant', help='Variant name in matrix')
    parser.add_argument('--case', help='Run exactly one selected case')
    parser.add_argument('--out', required=True, help='New output directory, never overwritten')
    parser.add_argument('--check-only', action='store_true', help='Check enabled catalog without starting a model turn')
    parser.add_argument('--timeout', type=int, default=240, help='Seconds per model turn; default 240')
    args = parser.parse_args()
    if args.snapshot:
        return snapshot(args)
    if not all([args.matrix, args.variant, args.case]):
        parser.error('A run needs --matrix, --variant, and --case')
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    return evaluate(args)


if __name__ == '__main__':
    raise SystemExit(main())

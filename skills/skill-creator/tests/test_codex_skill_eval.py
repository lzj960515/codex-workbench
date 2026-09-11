import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch
import sys

SCRIPTS = Path(__file__).parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('codex_skill_eval', SCRIPTS / 'codex_skill_eval.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class EvaluationIsolationTest(unittest.TestCase):
    def test_catalog_rejects_unexpected_enabled_skill_and_duplicate_names(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = (Path(directory) / name for name in ['a/SKILL.md', 'b/SKILL.md'])
            entries = [{'name': 'same', 'path': str(p), 'enabled': True} for p in [a, b]]
            actual = {'skills': entries, 'errors': []}
            with self.assertRaises(runner.EvaluationBlocked):
                runner.check_catalog(actual, [str(a)])
            with self.assertRaises(runner.EvaluationBlocked):
                runner.check_catalog(actual, [str(a), str(b)])

    def test_fixture_is_independent_and_grader_material_stays_outside(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            fixture = base / 'fixture'; fixture.mkdir()
            (fixture / 'input.txt').write_text('original')
            (base / 'answer-key.json').write_text('secret grader answer')
            first, second = base / 'first', base / 'second'
            runner.prepare_workspace(base, {'fixture': 'fixture'}, first)
            runner.prepare_workspace(base, {'fixture': 'fixture'}, second)
            (first / 'input.txt').write_text('mutated')
            self.assertEqual((second / 'input.txt').read_text(), 'original')
            self.assertEqual((fixture / 'input.txt').read_text(), 'original')
            self.assertFalse((first / 'answer-key.json').exists())

    def test_end_state_captures_deletion_change_addition_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); workspace = base / 'workspace'; workspace.mkdir()
            (workspace / 'gone.txt').write_text('old')
            (workspace / 'changed.txt').write_text('before')
            before = runner.workspace_state(workspace)
            (workspace / 'gone.txt').unlink()
            (workspace / 'changed.txt').write_text('after')
            (workspace / 'new.txt').write_text('new')
            outside = base / 'private.txt'; outside.write_text('do not copy')
            (workspace / 'pointer').symlink_to(outside)
            output = base / 'run'; output.mkdir()
            runner.capture_outcome(workspace, output, before)
            changes = json.loads((output / 'changes.json').read_text())
            self.assertIsNone(changes['gone.txt']['after'])
            self.assertNotEqual(changes['changed.txt']['before'], changes['changed.txt']['after'])
            self.assertIsNone(changes['new.txt']['before'])
            self.assertEqual(changes['pointer']['after']['kind'], 'symlink')
            self.assertFalse((output / 'outputs/pointer').exists())
            self.assertEqual((output / 'outputs/new.txt').read_text(), 'new')

    def test_skill_snapshot_excludes_evaluation_answers_and_keeps_neighbor_layout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / 'source/sample'
            (source / 'evals').mkdir(parents=True)
            (source / 'SKILL.md').write_text('---\nname: sample\ndescription: Sample task.\n---\n')
            (source / 'evals/answers.json').write_text('expected answers')
            destination = root / 'snapshot/sample'
            runner.copy_skill(source, destination)
            self.assertTrue((destination / 'SKILL.md').is_file())
            self.assertFalse((destination / 'evals').exists())

    def test_stored_skill_fixture_is_restored_only_inside_trial(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); fixture = base / 'fixture'; fixture.mkdir()
            (fixture / 'SKILL.md.fixture').write_text('skill body')
            workspace = base / 'workspace'
            runner.prepare_workspace(base, {'fixture': 'fixture', 'fixture_renames': {'SKILL.md.fixture': 'SKILL.md'}}, workspace)
            self.assertEqual((workspace / 'SKILL.md').read_text(), 'skill body')
            self.assertFalse((fixture / 'SKILL.md').exists())
            with self.assertRaises(ValueError):
                runner.prepare_workspace(base, {'fixture': 'fixture', 'fixture_renames': {'SKILL.md.fixture': '../escape'}}, base / 'unsafe')

    def test_case_validation_keeps_evaluations_local_and_single_turn(self):
        for case in [{'id': 1, 'prompt': 'x', 'sandbox': 'danger-full-access'},
                     {'id': 1, 'prompt': ''}]:
            with self.assertRaises(ValueError):
                runner.validate_case(case)


class RuntimeEvidenceTest(unittest.TestCase):
    def test_child_completion_cannot_complete_the_parent_trial(self):
        class FakeSession:
            def __init__(self):
                self.events = iter([
                    {'method': 'turn/completed', 'params': {'threadId': 'child', 'turn': {'id': 'child-turn', 'status': 'completed'}}},
                    {'method': 'item/completed', 'params': {'threadId': 'parent', 'turnId': 'turn', 'item': {'id': 'answer', 'type': 'agentMessage', 'text': 'actual answer'}}},
                    {'method': 'turn/completed', 'params': {'threadId': 'parent', 'turn': {'id': 'turn', 'status': 'failed', 'error': {'message': 'runtime failed'}}}},
                ])
            def request(self, method, params):
                if method == 'thread/start':return {'thread': {'id': 'parent', 'model': 'configured-model'}}
                return {'turn': {'id': 'turn'}}
            def receive(self, timeout):return next(self.events)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory); result = {}
            runner.run_turn(FakeSession(), {'prompt': 'task'}, output, result, output, 10)
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(result['turn_error']['message'], 'runtime failed')
            self.assertEqual((output / 'response.md').read_text(), 'actual answer')

    def test_trust_cleanup_preserves_previous_and_unrelated_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); config = root / 'config.toml'; trial = root / 'trial'
            prior = str(trial / 'already-there'); added = str(trial / 'created'); other = str(root / 'unrelated')
            config.write_text('model = "keep"\n' + ''.join('[projects.' + json.dumps(p) + ']\ntrust_level = "trusted"\n' for p in [prior, added, other]))
            count = runner.cleanup_trial_trust(config, trial, {prior})
            parsed = runner.tomllib.loads(config.read_text())
            self.assertEqual(count, 1)
            self.assertEqual(parsed['model'], 'keep')
            self.assertEqual(set(parsed['projects']), {prior, other})


if __name__ == '__main__':
    unittest.main()

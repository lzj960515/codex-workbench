#!/usr/bin/env python3

import argparse
import json
import os
import shlex
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPOSITORY_ROOT / "skills"
IGNORED_NAMES = {".DS_Store", "__pycache__"}
IGNORED_SUFFIXES = {".dtmp", ".pyc"}


class SkillTargetState(Enum):
    MISSING = "missing"
    CURRENT_LINK = "current-link"
    BROKEN_LINK = "broken-link"
    IDENTICAL_DIRECTORY = "identical-directory"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class SkillInstallationPlan:
    source: Path
    target: Path
    state: SkillTargetState


def copy_tree(source: Path, target: Path) -> None:
    shutil.copytree(
        source,
        target,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc", "*.dtmp"),
    )


def repository_skill_directories() -> list[Path]:
    return sorted(path.parent for path in SKILLS_ROOT.glob("*/SKILL.md"))


def is_ignored(relative_path: Path) -> bool:
    return (
        any(part in IGNORED_NAMES for part in relative_path.parts)
        or relative_path.suffix in IGNORED_SUFFIXES
    )


def tree_snapshot(directory: Path) -> dict[Path, tuple[str, object]]:
    snapshot = {}
    for path in sorted(directory.rglob("*")):
        relative_path = path.relative_to(directory)
        if is_ignored(relative_path):
            continue

        if path.is_symlink():
            snapshot[relative_path] = ("symlink", os.readlink(path))
        elif path.is_dir():
            snapshot[relative_path] = ("directory", None)
        elif path.is_file():
            snapshot[relative_path] = ("file", path.read_bytes())
        else:
            snapshot[relative_path] = ("other", None)
    return snapshot


def inspect_skill_target(source: Path, target: Path) -> SkillTargetState:
    if target.is_symlink():
        try:
            resolved_target = target.resolve(strict=True)
        except FileNotFoundError:
            return SkillTargetState.BROKEN_LINK
        return (
            SkillTargetState.CURRENT_LINK
            if resolved_target == source.resolve()
            else SkillTargetState.CONFLICT
        )

    if not target.exists():
        return SkillTargetState.MISSING

    if target.is_dir() and tree_snapshot(target) == tree_snapshot(source):
        return SkillTargetState.IDENTICAL_DIRECTORY

    return SkillTargetState.CONFLICT


def plan_skill_installation(skills_directory: Path) -> list[SkillInstallationPlan]:
    return [
        SkillInstallationPlan(
            source=source,
            target=skills_directory / source.name,
            state=inspect_skill_target(source, skills_directory / source.name),
        )
        for source in repository_skill_directories()
    ]


def reject_skill_conflicts(plans: list[SkillInstallationPlan]) -> None:
    conflicts = [plan for plan in plans if plan.state is SkillTargetState.CONFLICT]
    if not conflicts:
        return

    details = "\n".join(
        f"- {plan.source.name}: {plan.target}" for plan in conflicts
    )
    raise SystemExit(
        "Skill installation stopped because local content differs from the "
        f"repository:\n{details}"
    )


def link_skill(plan: SkillInstallationPlan) -> None:
    if plan.state is SkillTargetState.CURRENT_LINK:
        print(f"Using linked Skill {plan.source.name} -> {plan.source}")
        return

    if plan.state is SkillTargetState.IDENTICAL_DIRECTORY:
        shutil.rmtree(plan.target)
    elif plan.state is SkillTargetState.BROKEN_LINK:
        plan.target.unlink()

    plan.target.symlink_to(plan.source.resolve(), target_is_directory=True)
    print(f"Linked Skill {plan.source.name} -> {plan.source}")


def copy_skill(plan: SkillInstallationPlan) -> None:
    if plan.state is SkillTargetState.IDENTICAL_DIRECTORY:
        print(f"Using copied Skill {plan.source.name} -> {plan.target}")
        return

    if plan.state in (
        SkillTargetState.CURRENT_LINK,
        SkillTargetState.BROKEN_LINK,
    ):
        plan.target.unlink()

    copy_tree(plan.source, plan.target)
    print(f"Copied Skill {plan.source.name} -> {plan.target}")


def install_skills(skills_directory: Path, mode: str) -> None:
    if mode == "skip":
        return

    plans = plan_skill_installation(skills_directory)
    reject_skill_conflicts(plans)
    skills_directory.mkdir(parents=True, exist_ok=True)

    install_skill = link_skill if mode == "link" else copy_skill
    for plan in plans:
        install_skill(plan)


def install_agents_file(codex_home: Path) -> None:
    source = REPOSITORY_ROOT / "AGENTS.md"
    target = codex_home / "AGENTS.md"
    if not target.exists() or target.read_bytes() == source.read_bytes():
        shutil.copy2(source, target)
        print(f"Installed AGENTS.md -> {target}")
        return

    merge_source = codex_home / "AGENTS.codex-workbench.md"
    shutil.copy2(source, merge_source)
    print(f"Existing AGENTS.md preserved; ask your AI to merge {merge_source} into {target}")


def load_task_handoff_template(command: str) -> dict:
    template_path = (
        REPOSITORY_ROOT / "hooks" / "task-handoff" / "hooks.template.json"
    )
    template = json.loads(template_path.read_text(encoding="utf-8"))
    for definitions in template["hooks"].values():
        for definition in definitions:
            for hook in definition["hooks"]:
                if hook["command"] == "__TASK_HANDOFF_COMMAND__":
                    hook["command"] = command
    return template


def belongs_to_task_handoff(definition: dict) -> bool:
    return any(
        "task_handoff.py" in hook.get("command", "")
        for hook in definition.get("hooks", [])
        if isinstance(hook, dict)
    )


def install_hooks(codex_home: Path) -> None:
    hooks_directory = codex_home / "hooks"
    hooks_directory.mkdir(parents=True, exist_ok=True)
    copy_tree(REPOSITORY_ROOT / "hooks" / "task-handoff", hooks_directory)

    hooks_path = codex_home / "hooks.json"
    command = f"/usr/bin/env python3 {shlex.quote(str(hooks_directory / 'task_handoff.py'))}"
    template = load_task_handoff_template(command)
    config = (
        json.loads(hooks_path.read_text(encoding="utf-8"))
        if hooks_path.exists()
        else {"description": template["description"], "hooks": {}}
    )
    hooks = config.setdefault("hooks", {})

    for event_name, task_handoff_definitions in template["hooks"].items():
        existing = hooks.setdefault(event_name, [])
        hooks[event_name] = [
            definition
            for definition in existing
            if not belongs_to_task_handoff(definition)
        ]
        hooks[event_name].extend(task_handoff_definitions)

    hooks_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Installed task handoff hooks -> {hooks_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install Codex Workbench Skills, user rules, and hooks."
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path.home() / ".codex",
        help="Codex user configuration directory.",
    )
    parser.add_argument(
        "--skills-directory",
        type=Path,
        default=Path.home() / ".agents" / "skills",
        help="Shared user Skills directory.",
    )
    parser.add_argument(
        "--skills-mode",
        choices=("link", "copy", "skip"),
        default="link",
        help="Install Skills as repository links, independent copies, or skip them.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    install_skills(args.skills_directory, args.skills_mode)
    args.codex_home.mkdir(parents=True, exist_ok=True)
    install_agents_file(args.codex_home)
    install_hooks(args.codex_home)


if __name__ == "__main__":
    main()

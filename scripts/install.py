#!/usr/bin/env python3

import argparse
import json
import os
import shlex
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Optional


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPOSITORY_ROOT / "skills"
IGNORED_NAMES = {".DS_Store", "__pycache__"}
IGNORED_SUFFIXES = {".dtmp", ".pyc"}


class ManagedTargetState(Enum):
    MISSING = "missing"
    CURRENT_LINK = "current-link"
    BROKEN_LINK = "broken-link"
    IDENTICAL_CONTENT = "identical-content"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class ManagedInstallationPlan:
    source: Path
    target: Path
    state: ManagedTargetState


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


def files_match(source: Path, target: Path) -> bool:
    return target.is_file() and target.read_bytes() == source.read_bytes()


def directories_match(source: Path, target: Path) -> bool:
    return target.is_dir() and tree_snapshot(target) == tree_snapshot(source)


def inspect_managed_target(
    source: Path,
    target: Path,
    content_matches: Callable[[Path, Path], bool],
) -> ManagedTargetState:
    if target.is_symlink():
        try:
            resolved_target = target.resolve(strict=True)
        except FileNotFoundError:
            return ManagedTargetState.BROKEN_LINK
        return (
            ManagedTargetState.CURRENT_LINK
            if resolved_target == source.resolve()
            else ManagedTargetState.CONFLICT
        )

    if not target.exists():
        return ManagedTargetState.MISSING

    if content_matches(source, target):
        return ManagedTargetState.IDENTICAL_CONTENT

    return ManagedTargetState.CONFLICT


def plan_skill_installation(skills_directory: Path) -> list[ManagedInstallationPlan]:
    return [
        ManagedInstallationPlan(
            source=source,
            target=skills_directory / source.name,
            state=inspect_managed_target(
                source,
                skills_directory / source.name,
                directories_match,
            ),
        )
        for source in repository_skill_directories()
    ]


def plan_agents_installation(codex_home: Path) -> ManagedInstallationPlan:
    source = REPOSITORY_ROOT / "AGENTS.md"
    target = codex_home / "AGENTS.md"
    return ManagedInstallationPlan(
        source=source,
        target=target,
        state=inspect_managed_target(source, target, files_match),
    )


def reject_conflicts(plans: list[ManagedInstallationPlan]) -> None:
    conflicts = [plan for plan in plans if plan.state is ManagedTargetState.CONFLICT]
    if not conflicts:
        return

    details = "\n".join(
        f"- {plan.source.name}: {plan.target}" for plan in conflicts
    )
    raise SystemExit(
        "Installation stopped because local content differs from the "
        f"repository:\n{details}"
    )


def remove_existing_target(plan: ManagedInstallationPlan) -> None:
    if plan.target.is_dir() and not plan.target.is_symlink():
        shutil.rmtree(plan.target)
    else:
        plan.target.unlink()


def link_managed_path(plan: ManagedInstallationPlan, label: str) -> None:
    if plan.state is ManagedTargetState.CURRENT_LINK:
        print(f"Using linked {label} {plan.source.name} -> {plan.source}")
        return

    if plan.state in (
        ManagedTargetState.IDENTICAL_CONTENT,
        ManagedTargetState.BROKEN_LINK,
    ):
        remove_existing_target(plan)

    plan.target.symlink_to(
        plan.source.resolve(),
        target_is_directory=plan.source.is_dir(),
    )
    print(f"Linked {label} {plan.source.name} -> {plan.source}")


def copy_managed_path(plan: ManagedInstallationPlan, label: str) -> None:
    if plan.state is ManagedTargetState.IDENTICAL_CONTENT:
        print(f"Using copied {label} {plan.source.name} -> {plan.target}")
        return

    if plan.state in (
        ManagedTargetState.CURRENT_LINK,
        ManagedTargetState.BROKEN_LINK,
    ):
        remove_existing_target(plan)

    if plan.source.is_dir():
        copy_tree(plan.source, plan.target)
    else:
        shutil.copy2(plan.source, plan.target)
    print(f"Copied {label} {plan.source.name} -> {plan.target}")


def install_skills(plans: list[ManagedInstallationPlan], mode: str) -> None:
    if not plans:
        return

    plans[0].target.parent.mkdir(parents=True, exist_ok=True)

    for plan in plans:
        if mode == "link":
            link_managed_path(plan, "Skill")
        else:
            copy_managed_path(plan, "Skill")


def install_agents_file(
    plan: Optional[ManagedInstallationPlan],
    mode: str,
) -> None:
    if plan is None:
        return

    plan.target.parent.mkdir(parents=True, exist_ok=True)
    if mode == "link":
        link_managed_path(plan, "user rules")
    else:
        copy_managed_path(plan, "user rules")


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
    parser.add_argument(
        "--agents-mode",
        choices=("link", "copy", "skip"),
        default="link",
        help="Install AGENTS.md as a repository link, independent copy, or skip it.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    skill_plans = (
        []
        if args.skills_mode == "skip"
        else plan_skill_installation(args.skills_directory)
    )
    agents_plan = (
        None
        if args.agents_mode == "skip"
        else plan_agents_installation(args.codex_home)
    )
    managed_plans = skill_plans + ([agents_plan] if agents_plan else [])

    reject_conflicts(managed_plans)
    install_skills(skill_plans, args.skills_mode)
    install_agents_file(agents_plan, args.agents_mode)
    install_hooks(args.codex_home)


if __name__ == "__main__":
    main()

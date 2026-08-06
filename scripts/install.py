#!/usr/bin/env python3

import argparse
import json
import shlex
import shutil
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def copy_tree(source: Path, target: Path) -> None:
    shutil.copytree(
        source,
        target,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc", "*.dtmp"),
    )


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
        description="Install Codex Workbench user rules and hooks."
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path.home() / ".codex",
        help="Codex user configuration directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.codex_home.mkdir(parents=True, exist_ok=True)
    install_agents_file(args.codex_home)
    install_hooks(args.codex_home)


if __name__ == "__main__":
    main()

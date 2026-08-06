import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPOSITORY_ROOT / "scripts" / "install.py"


class InstallerTest(unittest.TestCase):
    def run_installer(self, codex_home: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(INSTALLER),
                "--codex-home",
                str(codex_home),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_fresh_install_installs_rules_and_portable_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home = root / "codex"

            self.run_installer(codex_home)

            self.assertEqual(
                (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8"),
                (codex_home / "AGENTS.md").read_text(encoding="utf-8"),
            )
            self.assertTrue((codex_home / "hooks" / "task_handoff.py").is_file())

            hooks = json.loads((codex_home / "hooks.json").read_text(encoding="utf-8"))
            self.assertEqual({"SessionStart", "PostToolUse", "UserPromptSubmit"}, set(hooks["hooks"]))
            serialized_hooks = json.dumps(hooks)
            self.assertIn(str(codex_home / "hooks" / "task_handoff.py"), serialized_hooks)
            self.assertNotIn(str(Path.home()), serialized_hooks)
            self.assertNotIn("__TASK_HANDOFF_COMMAND__", serialized_hooks)

            session_start = hooks["hooks"]["SessionStart"][0]
            self.assertEqual("^compact$", session_start["matcher"])
            self.assertEqual(3, session_start["hooks"][0]["timeout"])

    def test_existing_agents_file_is_preserved_for_ai_assisted_merge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home = root / "codex"
            codex_home.mkdir(parents=True)
            existing_content = "# Existing user rules\n"
            (codex_home / "AGENTS.md").write_text(existing_content, encoding="utf-8")

            result = self.run_installer(codex_home)

            self.assertEqual(existing_content, (codex_home / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertTrue((codex_home / "AGENTS.codex-workbench.md").is_file())
            self.assertIn("merge", result.stdout.lower())

    def test_existing_unrelated_hooks_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home = root / "codex"
            codex_home.mkdir(parents=True)
            existing_hooks = {
                "description": "Existing hooks",
                "hooks": {
                    "UserPromptSubmit": [
                        {
                            "hooks": [
                                {"type": "command", "command": "/usr/bin/example-hook"}
                            ]
                        }
                    ]
                },
            }
            (codex_home / "hooks.json").write_text(
                json.dumps(existing_hooks), encoding="utf-8"
            )

            self.run_installer(codex_home)

            hooks = json.loads((codex_home / "hooks.json").read_text(encoding="utf-8"))
            commands = [
                hook["command"]
                for definition in hooks["hooks"]["UserPromptSubmit"]
                for hook in definition["hooks"]
            ]
            self.assertIn("/usr/bin/example-hook", commands)
            self.assertTrue(any("task_handoff.py" in command for command in commands))


if __name__ == "__main__":
    unittest.main()

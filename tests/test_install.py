import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPOSITORY_ROOT / "scripts" / "install.py"


class InstallerTest(unittest.TestCase):
    def run_installer(
        self,
        codex_home: Path,
        skills_directory: Path,
        *,
        skills_mode: str = "link",
        agents_mode: str = "link",
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(INSTALLER),
                "--codex-home",
                str(codex_home),
                "--skills-directory",
                str(skills_directory),
                "--skills-mode",
                skills_mode,
                "--agents-mode",
                agents_mode,
            ],
            check=check,
            capture_output=True,
            text=True,
        )

    def make_installation_paths(self, root: Path) -> tuple[Path, Path]:
        return root / "codex", root / "agents" / "skills"

    def test_fresh_install_installs_rules_and_portable_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)

            self.run_installer(codex_home, skills_directory)

            self.assertEqual(
                (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8"),
                (codex_home / "AGENTS.md").read_text(encoding="utf-8"),
            )
            self.assertTrue((codex_home / "AGENTS.md").is_symlink())
            self.assertEqual(
                (REPOSITORY_ROOT / "AGENTS.md").resolve(),
                (codex_home / "AGENTS.md").resolve(),
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

            source = REPOSITORY_ROOT / "skills" / "deep-discussion"
            installed = skills_directory / "deep-discussion"
            self.assertTrue(installed.is_symlink())
            self.assertEqual(source.resolve(), installed.resolve())

    def test_agents_conflict_stops_the_entire_installation_before_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)
            codex_home.mkdir(parents=True)
            existing_content = "# Existing user rules\n"
            (codex_home / "AGENTS.md").write_text(existing_content, encoding="utf-8")

            result = self.run_installer(
                codex_home,
                skills_directory,
                check=False,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("AGENTS.md", result.stderr)
            self.assertEqual(existing_content, (codex_home / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertFalse((codex_home / "AGENTS.codex-workbench.md").exists())
            self.assertFalse(skills_directory.exists())
            self.assertFalse((codex_home / "hooks.json").exists())

    def test_identical_agents_file_is_converted_to_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)
            codex_home.mkdir(parents=True)
            source = REPOSITORY_ROOT / "AGENTS.md"
            installed = codex_home / "AGENTS.md"
            shutil.copy2(source, installed)

            self.run_installer(codex_home, skills_directory)

            self.assertTrue(installed.is_symlink())
            self.assertEqual(source.resolve(), installed.resolve())

    def test_existing_unrelated_hooks_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)
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

            self.run_installer(codex_home, skills_directory)

            hooks = json.loads((codex_home / "hooks.json").read_text(encoding="utf-8"))
            commands = [
                hook["command"]
                for definition in hooks["hooks"]["UserPromptSubmit"]
                for hook in definition["hooks"]
            ]
            self.assertIn("/usr/bin/example-hook", commands)
            self.assertTrue(any("task_handoff.py" in command for command in commands))

    def test_link_install_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)

            self.run_installer(codex_home, skills_directory)
            self.run_installer(codex_home, skills_directory)

            installed_agents = codex_home / "AGENTS.md"
            self.assertTrue(installed_agents.is_symlink())
            self.assertEqual(
                (REPOSITORY_ROOT / "AGENTS.md").resolve(),
                installed_agents.resolve(),
            )

            for source in sorted((REPOSITORY_ROOT / "skills").glob("*/SKILL.md")):
                installed = skills_directory / source.parent.name
                with self.subTest(skill=source.parent.name):
                    self.assertTrue(installed.is_symlink())
                    self.assertEqual(source.parent.resolve(), installed.resolve())

    def test_identical_skill_directory_is_converted_to_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)
            source = REPOSITORY_ROOT / "skills" / "deep-discussion"
            installed = skills_directory / "deep-discussion"
            shutil.copytree(source, installed)
            (installed / ".DS_Store").touch()
            cache_directory = installed / "__pycache__"
            cache_directory.mkdir()
            (cache_directory / "generated.pyc").touch()
            (installed / "transient.dtmp").touch()

            self.run_installer(codex_home, skills_directory)

            self.assertTrue(installed.is_symlink())
            self.assertEqual(source.resolve(), installed.resolve())

    def test_conflict_stops_all_skill_migration_before_changes(self) -> None:
        for skills_mode in ("link", "copy"):
            with self.subTest(skills_mode=skills_mode):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    codex_home, skills_directory = self.make_installation_paths(root)
                    conflicting = skills_directory / "wiki-maintainer"
                    conflicting.mkdir(parents=True)
                    (conflicting / "SKILL.md").write_text(
                        "# Local work that must be preserved\n",
                        encoding="utf-8",
                    )

                    result = self.run_installer(
                        codex_home,
                        skills_directory,
                        skills_mode=skills_mode,
                        check=False,
                    )

                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("wiki-maintainer", result.stderr)
                    self.assertEqual(
                        "# Local work that must be preserved\n",
                        (conflicting / "SKILL.md").read_text(encoding="utf-8"),
                    )
                    self.assertFalse(
                        (skills_directory / "architecture-design-review").exists()
                    )

    def test_link_to_another_source_is_preserved_as_a_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)
            alternate_source = root / "alternate" / "deep-discussion"
            shutil.copytree(
                REPOSITORY_ROOT / "skills" / "deep-discussion",
                alternate_source,
            )
            skills_directory.mkdir(parents=True)
            installed = skills_directory / "deep-discussion"
            installed.symlink_to(alternate_source, target_is_directory=True)

            result = self.run_installer(
                codex_home,
                skills_directory,
                check=False,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("deep-discussion", result.stderr)
            self.assertTrue(installed.is_symlink())
            self.assertEqual(alternate_source.resolve(), installed.resolve())

    def test_broken_link_is_repaired_after_the_repository_moves(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)
            skills_directory.mkdir(parents=True)
            installed = skills_directory / "deep-discussion"
            installed.symlink_to(
                root / "old-location" / "skills" / "deep-discussion",
                target_is_directory=True,
            )

            self.run_installer(codex_home, skills_directory)

            source = REPOSITORY_ROOT / "skills" / "deep-discussion"
            self.assertTrue(installed.is_symlink())
            self.assertEqual(source.resolve(), installed.resolve())

    def test_copy_mode_installs_regular_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)

            self.run_installer(
                codex_home,
                skills_directory,
                skills_mode="copy",
            )

            source = REPOSITORY_ROOT / "skills" / "deep-discussion" / "SKILL.md"
            installed_directory = skills_directory / "deep-discussion"
            self.assertTrue(installed_directory.is_dir())
            self.assertFalse(installed_directory.is_symlink())
            self.assertEqual(
                source.read_text(encoding="utf-8"),
                (installed_directory / "SKILL.md").read_text(encoding="utf-8"),
            )

    def test_agents_copy_mode_installs_a_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)

            self.run_installer(
                codex_home,
                skills_directory,
                skills_mode="skip",
                agents_mode="copy",
            )

            installed = codex_home / "AGENTS.md"
            self.assertTrue(installed.is_file())
            self.assertFalse(installed.is_symlink())
            self.assertEqual(
                (REPOSITORY_ROOT / "AGENTS.md").read_bytes(),
                installed.read_bytes(),
            )

    def test_skip_mode_only_installs_rules_and_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)

            self.run_installer(
                codex_home,
                skills_directory,
                skills_mode="skip",
            )

            self.assertTrue((codex_home / "AGENTS.md").is_file())
            self.assertTrue((codex_home / "AGENTS.md").is_symlink())
            self.assertTrue((codex_home / "hooks" / "task_handoff.py").is_file())
            self.assertFalse(skills_directory.exists())

    def test_agents_skip_mode_installs_skills_and_hooks_without_rules(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)

            self.run_installer(
                codex_home,
                skills_directory,
                agents_mode="skip",
            )

            self.assertFalse((codex_home / "AGENTS.md").exists())
            self.assertTrue((codex_home / "hooks" / "task_handoff.py").is_file())
            self.assertTrue((skills_directory / "deep-discussion").is_symlink())

    def test_broken_agents_link_is_repaired_after_the_repository_moves(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            codex_home, skills_directory = self.make_installation_paths(root)
            codex_home.mkdir(parents=True)
            installed = codex_home / "AGENTS.md"
            installed.symlink_to(root / "old-location" / "AGENTS.md")

            self.run_installer(codex_home, skills_directory)

            self.assertTrue(installed.is_symlink())
            self.assertEqual(
                (REPOSITORY_ROOT / "AGENTS.md").resolve(),
                installed.resolve(),
            )

    def test_readme_uses_the_installer_as_the_single_installation_entrypoint(self) -> None:
        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("python3 scripts/install.py", readme)
        self.assertIn("符号链接", readme)
        self.assertIn("--skills-mode copy", readme)
        self.assertIn("--agents-mode copy", readme)
        self.assertNotIn("npx skills add", readme)


if __name__ == "__main__":
    unittest.main()

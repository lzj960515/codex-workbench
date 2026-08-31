import tempfile
import unittest
from pathlib import Path

from scripts.audit_public import audit_repository


class PublicAuditTest(unittest.TestCase):
    def test_clean_public_files_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Public project\n", encoding="utf-8")

            self.assertEqual([], audit_repository(root))

    def test_personal_data_and_generated_files_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            personal_path = "/" + "Users" + "/private-user/config"
            personal_email = "person" + "@" + "private.invalid"
            github_token = "ghp" + "_" + "A" * 36
            private_key_header = "-----BEGIN RSA " + "PRIVATE KEY-----"
            (root / "notes.md").write_text(
                (
                    f"Path: {personal_path}\n"
                    f"Contact: {personal_email}\n"
                    f"Token: {github_token}\n"
                    f"Key: {private_key_header}\n"
                ),
                encoding="utf-8",
            )
            (root / ".DS_Store").touch()

            findings = audit_repository(root)

            self.assertTrue(any("absolute user path" in item for item in findings))
            self.assertTrue(any("email address" in item for item in findings))
            self.assertTrue(any("access token" in item for item in findings))
            self.assertTrue(any("private key" in item for item in findings))
            self.assertTrue(any("generated file" in item for item in findings))

    def test_broken_markdown_links_are_reported_but_code_examples_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "[Missing](missing.md)\n\n```md\n[Example](example.md)\n```\n",
                encoding="utf-8",
            )

            findings = audit_repository(root)

            self.assertEqual(["broken local link: README.md -> missing.md"], findings)

    def test_local_worktrees_and_tmp_files_are_outside_the_public_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private_path = "/" + "Users" + "/private-user/workspace"
            local_files = (
                root / "tmp" / "task-state.md",
                root / ".worktrees" / "feature" / "notes.md",
            )
            for path in local_files:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(private_path, encoding="utf-8")

            self.assertEqual([], audit_repository(root))

    def test_nested_tmp_directory_remains_part_of_the_public_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private_path = "/" + "Users" + "/private-user/workspace"
            tracked_file = root / "skills" / "example" / "tmp" / "notes.md"
            tracked_file.parent.mkdir(parents=True)
            tracked_file.write_text(private_path, encoding="utf-8")

            findings = audit_repository(root)

            self.assertTrue(any("absolute user path" in item for item in findings))


if __name__ == "__main__":
    unittest.main()

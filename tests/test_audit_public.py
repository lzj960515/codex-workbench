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
            (root / "notes.md").write_text(
                f"Path: {personal_path}\nContact: {personal_email}\n",
                encoding="utf-8",
            )
            (root / ".DS_Store").touch()

            findings = audit_repository(root)

            self.assertTrue(any("absolute user path" in item for item in findings))
            self.assertTrue(any("email address" in item for item in findings))
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


if __name__ == "__main__":
    unittest.main()

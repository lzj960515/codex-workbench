import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPOSITORY_ROOT / "skills"


def read_skill_package(skill_name: str) -> str:
    skill_directory = SKILLS_ROOT / skill_name
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(skill_directory.rglob("*.md"))
    )


class SkillContractTest(unittest.TestCase):
    def test_legacy_frontmatter_fields_are_absent(self) -> None:
        for skill_path in sorted(SKILLS_ROOT.glob("*/SKILL.md")):
            frontmatter = skill_path.read_text(encoding="utf-8").split("---", 2)[1]
            with self.subTest(skill=skill_path.parent.name):
                self.assertNotIn("allowed-tools:", frontmatter)
                self.assertNotIn("when_to_use:", frontmatter)

    def test_source_repo_study_preserves_analysis_and_teaching_contracts(self) -> None:
        package = read_skill_package("source-repo-study")
        required_contracts = (
            "Maintenance layer",
            "Map Mode",
            "Study Mode",
            "Evolution Mode",
            "architecture overview",
            "feature inventory",
            "runtime artifacts",
            "confirmed behavior",
            "index.md",
            "log.md",
            "simple workable model",
            "breaking constraint",
            "technical terms after their meaning",
            "rhetorical questions",
            "<br/>",
            "code as supporting evidence",
            "Match the user's language",
        )

        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, package)

    def test_wiki_maintainer_preserves_persistent_knowledge_contracts(self) -> None:
        package = read_skill_package("wiki-maintainer")
        required_contracts = (
            "原始材料",
            "Wiki 页面",
            "维护规则",
            "摄取来源",
            "回答并沉淀问题",
            "修订结论",
            "健康检查",
            "index.md",
            "log.md",
            "权威页面",
            "可追溯来源",
            "综合判断",
            "争议结论",
            "孤立页面",
            "规模演进",
        )

        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, package)


if __name__ == "__main__":
    unittest.main()

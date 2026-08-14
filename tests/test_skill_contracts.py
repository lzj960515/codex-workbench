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

    def test_tdd_skill_preserves_risk_based_verification_contracts(self) -> None:
        package = read_skill_package("test-driven-development")
        required_contracts = (
            "用户明确要求 TDD 或先写测试时始终使用",
            "业务分支与计算规则",
            "公共 API 或事件契约",
            "并发与乱序",
            "优先使用直接验证",
            "能由 build、typecheck、lint、配置渲染或调用检查完整证明",
            "选择与风险相称的验证方式",
            "决定不新增测试后",
            "测试数量服从风险覆盖",
        )

        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, package)

    def test_code_review_unifies_candidate_feedback_and_rereview_contracts(self) -> None:
        package = read_skill_package("code-review")
        required_contracts = (
            "资深 Maintainer",
            "候选审查",
            "接收审查意见",
            "复审",
            "真实交付阻塞",
            "业务约束",
            "支持的输入路径",
            "代码层面可以构造",
            "批准",
            "修改",
            "回复",
            "请求产品决定",
            "重新判断",
            "反证",
            "architecture-design-review",
            "systematic-debugging",
            "verification-before-completion",
        )

        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, package)

    def test_code_review_replaces_the_receiving_only_skill(self) -> None:
        self.assertTrue((SKILLS_ROOT / "code-review" / "SKILL.md").is_file())
        self.assertFalse((SKILLS_ROOT / "receiving-code-review").exists())

        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("[`code-review`](skills/code-review/)", readme)
        self.assertNotIn("receiving-code-review", readme)

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

import json
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

    def test_software_development_preserves_risk_based_verification_contracts(self) -> None:
        package = read_skill_package("software-development")
        required_contracts = (
            "用户明确要求 TDD 或先写测试时",
            "测试保护已确认的业务结果",
            "已有测试能够保护受影响行为时",
            "选择充分且成本合适的方式",
            "机械接线",
            "禁止为这些内容编写框架层面的测试",
            "生产依赖、接口与行为由真实业务和运行生命周期决定",
        )

        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, package)

    def test_software_development_unifies_candidate_feedback_and_rereview_contracts(self) -> None:
        package = read_skill_package("software-development")
        required_contracts = (
            "只审查代码、分支或合并请求",
            "处理审查意见",
            "复审",
            "主动启动一位独立审查子 Agent",
            "准确批准与准确退回具有同等价值",
            "代码层面可构造的状态只是调查线索",
            "受支持入口",
            "模型、职责与范围问题",
            "授权问题",
            "修改",
            "回复",
            "请求产品决定",
            "反证",
            "systematic-debugging",
        )

        for contract in required_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, package)

    def test_quality_skills_preserve_decision_and_stopping_contracts(self) -> None:
        contracts = {
            "writing-for-ai": (
                "编写让 AI 能够准确理解和使用的内容",
                "让设计意图落实到内容和使用方式中",
                "正确停止方式",
            ),
            "software-development": (
                "总体成本",
                "普通方法已经能完整承载时直接实现",
                "已有证据足够时复用",
            ),
            "systematic-debugging": (
                "根因已确认",
                "主要假设",
                "证据不足",
                "只诊断",
            ),
        }

        for skill_name, required_contracts in contracts.items():
            package = read_skill_package(skill_name)
            for contract in required_contracts:
                with self.subTest(skill=skill_name, contract=contract):
                    self.assertIn(contract, package)

        user_rules = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for contract in ("直接证据", "复用仍有效", "未验证"):
            with self.subTest(document="AGENTS.md", contract=contract):
                self.assertIn(contract, user_rules)

        delivery = (
            SKILLS_ROOT / "software-development" / "references" / "delivery.md"
        ).read_text(encoding="utf-8")
        for contract in ("已提交、已推送", "制品", "部署", "线上"):
            with self.subTest(document="delivery.md", contract=contract):
                self.assertIn(contract, delivery)

    def test_removed_quality_skills_are_not_recommended(self) -> None:
        manifest_path = REPOSITORY_ROOT / "manifests" / "third-party-skills.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        names = {skill["name"] for skill in manifest["skills"]}

        self.assertNotIn("nestjs-best-practices", names)
        self.assertNotIn("typeorm", names)
        self.assertNotIn("skill-creator", names)
        self.assertTrue((SKILLS_ROOT / "writing-for-ai" / "SKILL.md").is_file())
        for retired_skill in (
            "skill-builder",
            "skill-creator",
            "writing-for-agents",
            "architecture-design-review",
            "maintainable-implementation",
            "test-driven-development",
            "code-review",
            "verification-before-completion",
        ):
            with self.subTest(retired_skill=retired_skill):
                self.assertFalse((SKILLS_ROOT / retired_skill).exists())

    def test_software_development_is_the_documented_engineering_entrypoint(self) -> None:
        self.assertTrue((SKILLS_ROOT / "software-development" / "SKILL.md").is_file())
        self.assertFalse((SKILLS_ROOT / "receiving-code-review").exists())

        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("[`software-development`](skills/software-development/)", readme)
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
            "README.md",
            "changes/",
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

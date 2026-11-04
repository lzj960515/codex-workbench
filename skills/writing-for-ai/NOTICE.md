# 来源与修改说明

`writing-for-ai` 的主流程、规则文档、组织示例与 Skill 封装说明由本仓库重新编写，整合现有 `skill-builder`、`skill-creator` 和 `writing-for-agents` 的有效方法。新编写部分使用本仓库 MIT 许可证，见 [LICENSE](LICENSE)。

- 信息层级、读取入口、就近组织和单一来源等方法参考 Matt Pocock 的 `writing-for-agents`。本包采用重新组织的中文表达，保留 [上游 MIT 许可证](LICENSE.mattpocock)。
- `scripts/`、`tests/`、`eval-viewer/`、`assets/` 与三个评估角色沿用本仓库现有 `skill-creator` 资源。该能力基于 Anthropic 的 Apache-2.0 版本持续演化，保留 [Apache-2.0 许可证](LICENSE.anthropic.txt)。
- `evaluation-design.md`、`codex-evaluation.md`、`advanced-evaluation.md`、`schemas.md` 与 `openai_yaml.md` 沿用现有工程资料，调整包名称及必要引用，并补充规则、提示词与知识文档的评估范围。现有工具实现保持原样。

2026-11-04，经用户审阅确认后，本包替换上述三个独立 Skill。共同主稿与个人规则采用已批准的候选，旧三个入口退出，原工程资源和回归用例继续由本包维护。替换依据与验证边界见仓库的采用记录。

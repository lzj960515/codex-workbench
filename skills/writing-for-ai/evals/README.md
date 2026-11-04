# 写作行为用例

按 [评估设计](../references/evaluation-design.md) 选择与本次变化相关的场景，实际执行方法见 [Codex 本地评估](../references/codex-evaluation.md)。执行端只取得请求和初态，评阅标准保留在执行端之外；运行日志、快照和评分放任务 `tmp/`。

- 1–3：新建判断型 Skill、整理个人规则与按需入口、面向客户的普通文案边界。
- 4–6：从原 `skill-creator` 迁入的语义不变校对、资源所有权和描述职责回归用例，保留原请求、初态和标准。

样例 Skill 使用 `SKILL.md.fixture` 保存，在临时项目中按 `fixture_renames` 还原，避免进入实际发现目录。单次通过只说明对应场景；规则、模型或环境改变后，按实际影响重新核实证据范围。

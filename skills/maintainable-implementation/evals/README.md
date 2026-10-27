# 初始评估案例

使用 `skill-creator` 的评估流程，按本次行为变化选择相关案例。evals.json 保存自然请求与预先标准，fixture 路径相对本目录。执行端只取得请求和初态，预期答案留在评估端；运行与评分放任务 tmp。

检查真实文件、工具轨迹和回复，逐项给出通过、失败或证据不足。区分任务成功和目标 Skill 是否自然触发；纯机械对照允许不加载 Skill 或加载后直接结束。

单次结果作为回归集起点，不能证明稳定性或单个 Skill 的贡献。语义不变的校对继续做差异检查；真实使用出现新失误时补脱敏案例。修改评分标准时记录发生变化的用户目标或契约。

`replace-sync` 覆盖已确认业务替换和旧迁移层退出；`replacement-review` 联合架构与代码审查，检查同类兼容在迁移结束、滚动部署与长期公开契约时的不同结论。用例在此统一维护，不复制到相邻 Skill。

`manual-credit-existing-order`、`api-key-model-unapproved` 与 `api-key-model-approved` 覆盖数据模型批准边界：已有人工订单能承载目标时复用；缺少持久化模型时提出具体方案等待批准；具体模型已经批准时直接实施。三例共同观察全局规则与 maintainable-implementation、architecture-design-review、to-spec、code-review 的组合，不归因于单个 Skill。前两例使用旧版与候选对照，已批准例用于检查候选是否误停。

`check_outputs.py` 对已完成的人工加分与 API key 产物执行公开函数和真实 SQLite 检查；模型未批准例通过文件差异、方案内容与工具轨迹评分。脚本只验证可执行行为，模型范围、批准时点及越界访问继续由评估者核对。

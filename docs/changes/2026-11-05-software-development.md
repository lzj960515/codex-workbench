# 采用统一的软件开发 Skill

2026-11-05，用户审阅并确认候选后，正式启用 [software-development](../../skills/software-development/SKILL.md)，移除原架构设计、代码实现、TDD 和代码审查四个独立入口。

## 当前职责

开发流程从真实业务结果出发，按职责与生命周期选择代码位置，使用适合当前业务的模型与技术，选择必要的业务验证，并在形成可交付代码改动后主动安排独立子 Agent 审查。

主稿及四份参考与审查者说明采用已确认版本。设计、只审查和反馈回复保留各自结束方式；生产设计由业务需要决定，测试不扩写需求、不要求为方便测试增加生产抽象。

## 替换与保留

- 原 `architecture-design-review`、`maintainable-implementation`、`test-driven-development` 和 `code-review` 目录与本机入口退出，个人规则和相关调用指向新能力。
- 原设计参考的方法由新包的[设计与实现](../../skills/software-development/references/design-and-implementation.md)承接，架构探索与来源记录同步当前归属。
- 原 11 个评估场景、初态和已有产物检查器保留在新包，适配选用名称并记录来源。
- `systematic-debugging` 继续负责未知根因调查。后续整理将原 `verification-before-completion` 的有效方法归回通用证据原则与对应任务流程，独立入口退出，见[调试与交付方法整理](2026-11-05-debugging-and-delivery.md)。
- 安装器沿用既有的托管链接清理和冲突预检，增加本次四个已退出名字。

本次采用按结构、引用、必要的安装回归和独立审查核对迁移结果；未运行新上下文行为评测，不据此宣称实际表现优于原版。用户已确认将本轮整合与后续调试优化一起提交推送。

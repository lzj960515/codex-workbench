# Codex Workbench

我的 Codex 用户规则、上下文交接 Hooks 和常用 Skills 的公开存档。主要用于跨设备同步，也方便把同一套协作习惯安装到其他环境。

## 内容

- `AGENTS.md`：用户级协作、代码质量、架构、异常处理和长任务交接规则。
- `hooks/task-handoff/`：上下文接近压缩时提醒更新任务状态，压缩后提醒恢复工作上下文。
- `skills/`：自己维护的通用 Skills。
- `manifests/third-party-skills.json`：第三方 Skills、参考材料及相关项目的来源、版本与修改范围。

仓库不包含项目业务资料、邮箱联系人、费用统计工具、访问令牌或本机绝对路径。

## 安装

安装需要 Python 3.9 或更高版本。

```bash
git clone https://github.com/lzj960515/codex-workbench.git
cd codex-workbench

python3 scripts/install.py
```

仓库中的 `AGENTS.md` 和 `skills/` 是对应用户规则与 Skill 的 Git 权威来源。安装器默认把 `AGENTS.md` 链接到 `~/.codex/AGENTS.md`，并把每个仓库 Skill 单独链接到 `~/.agents/skills`；其他本机 Skill 不受影响。之后直接修改仓库文件即可，不需要再同步本机副本。仓库位置移动后，重新运行安装器即可修复断链。

安装器会在写入前一起检查用户规则和全部仓库 Skill。已有相同内容的文件或目录会安全转换为链接，仓库移动后留下的断链会自动修复；已有不同内容、指向其他现存来源的链接或同名目标时，安装会整体停止并保留本机内容。不支持符号链接的环境可以安装独立副本：

```bash
python3 scripts/install.py --skills-mode copy --agents-mode copy
```

`--skills-mode` 和 `--agents-mode` 分别支持 `link`、`copy` 和 `skip`。只安装用户规则与 Hooks 时使用 `--skills-mode skip`；需要保留含私人内容的本机 `AGENTS.md` 时使用 `--agents-mode skip`，该文件不会进入仓库单一来源。Skill 聚合目录和 Codex 用户目录可以分别通过 `--skills-directory` 与 `--codex-home` 指定。

公开仓库只保存适合公开、跨设备复用的内容。私人资料、机器专属绝对路径、密钥和内部项目知识保留在本机或对应项目中，不通过本仓库连接。

也可以直接把仓库地址交给 AI，让它阅读本文件并完成安装和合并。

## Skills 清单

| Skill | 用途 |
| --- | --- |
| [`architecture-design-review`](skills/architecture-design-review/) | 设计或审查框架、公共 API、核心基础设施和跨模块重构。 |
| [`code-review`](skills/code-review/) | 审查候选、评估审查意见并在返工后复审，以真实交付风险推动结论收敛。 |
| [`deep-discussion`](skills/deep-discussion/) | 依据真实证据和决策依赖推进讨论，澄清领域概念，为外部信息缺口整理问卷，并选择直接答复或持续文档。 |
| [`prototype`](skills/prototype/) | 手动使用 `$prototype`，制作可操作的逻辑模型或比较界面方案；默认不自动触发。 |
| [`to-spec`](skills/to-spec/) | 将已有讨论和决策地图中的确认内容整理为正式规格，明确行为、验收与未决事项。 |
| [`wayfinder`](skills/wayfinder/) | 创建和恢复跨会话决策地图，跟踪依赖、未决事项与当前可推进的问题。 |
| [`improve-codebase-architecture`](skills/improve-codebase-architecture/) | 从变更热点和设计摩擦中寻找重构机会，给出证据、优先建议及改前改后对比。 |
| [`maintainable-implementation`](skills/maintainable-implementation/) | 为普通代码改动选择合适的实现尺度、复用方式和职责边界。 |
| [`systematic-debugging`](skills/systematic-debugging/) | 调查 Bug、偶发失败、状态不一致、性能退化和生产异常。 |
| [`test-driven-development`](skills/test-driven-development/) | 按回归风险选择 TDD 或直接验证，并用失败测试保护高风险行为。 |
| [`verification-before-completion`](skills/verification-before-completion/) | 在完成、提交、推送或发布前建立与声明相匹配的验证证据。 |
| [`skill-builder`](skills/skill-builder/) | 从真实需求设计 Skill 的职责、边界和验收标准。 |
| [`skill-creator`](skills/skill-creator/) | 实现、组织、校验和评测已经明确职责的 Skill 工程包。 |
| [`writing-for-agents`](skills/writing-for-agents/) | 保留 Matt Pocock 原文的 Agent 文档写作指导；供独立使用及 Skill Creator 写作环节引用。 |
| [`source-repo-study`](skills/source-repo-study/) | 系统研究源码仓库，并整理成架构、功能和数据流 Wiki。 |
| [`wiki-maintainer`](skills/wiki-maintainer/) | 持续摄取和修订 Markdown Wiki，维护索引、链接和知识一致性。 |
| [`drawio`](skills/drawio/) | 创建、修改、检查 draw.io 架构图和流程图，并导出 PNG。 |
| [`mindmap`](skills/mindmap/) | 将想法、文档和讨论整理成可编辑的 draw.io 思维导图。 |

`drawio` 和 `mindmap` 需要安装 draw.io Desktop，并让 `drawio` 命令可以从终端调用。

`skill-creator` 基于 Anthropic 发布的 Apache-2.0 版本持续修改，目录内保留原许可证和修改说明。

## Hooks 清单

当前仓库收录一套 [`task-handoff`](hooks/task-handoff/) Hook，用于在长任务中保存和恢复工作上下文。

| Hook 事件 | 触发时机 | 用途 |
| --- | --- | --- |
| `UserPromptSubmit` | 用户提交新消息后 | 上下文使用率达到 70% 时，提醒为当前用户任务创建或更新状态文件。 |
| `PostToolUse` | AI 每次调用工具后 | AI 连续工作期间达到 70% 时及时提醒，不依赖用户再次发送消息。 |
| `SessionStart`（`compact`） | 上下文压缩完成后 | 提醒先读取任务状态文件，再结合 Git 状态和差异恢复工作。 |

同一个用户任务只提醒一次；并行工具回调会合并为一次提醒，下一条用户消息开始新的提醒周期。

## 第三方内容

仍由上游维护的第三方 Skills、Codrive 和文档处理 Skills 来源记录在 [`manifests/third-party-skills.json`](manifests/third-party-skills.json)，使用时遵循对应项目的许可证。

`writing-for-agents` 的 `SKILL.md` 保留上游原文；`SKILL-MECHANICS.md` 适配本体系的自动发现偏好和平台调用设置。来源版本与修改范围记录在来源清单中，MIT 许可证随包保留。

Matt Pocock 的追问、领域建模与对外确认问卷方法由 `deep-discussion/references/` 承载；代码设计方法由 `architecture-design-review/references/` 维护并供实现技能共享。`wayfinder` 和 `improve-codebase-architecture` 保留独立入口并适配本体系。来源与逐文件映射见来源清单，相关包保留 `LICENSE.mattpocock`。

`to-spec` 保留上游的规格模板与原型决策表达，适配自动发现、已有文档归属、确认范围与后续动作授权；`deep-discussion` 和 `wayfinder` 在需要正式规格时按名称使用它。

## 许可证

[MIT](./LICENSE)

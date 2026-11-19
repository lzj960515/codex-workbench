# Codex Workbench

我的 Codex 用户规则、上下文交接 Hooks 和常用 Skills 的公开存档。主要用于跨设备同步，也方便把同一套协作习惯安装到其他环境。

## 内容

- `AGENTS.md`：用户级偏好、目标与授权边界、修改原则、工程约束及长任务协作规则。
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

更新后，安装器会清理已退出的本仓库托管链接：`writing-for-ai` 替代 `skill-builder`、`skill-creator`、`writing-for-agents`；`software-development` 替代 `architecture-design-review`、`maintainable-implementation`、`test-driven-development`、`code-review`；原 `verification-before-completion` 的有效方法归入通用证据原则与对应任务流程。旧名字若是独立目录、副本或指向其他来源的链接，安装会在写入前停止并保留内容；先核对并自行迁走这些旧内容，再重新安装。`--skills-mode skip` 保留全部现有 Skill。

`knowledge-maintenance` 承接原 `wiki-maintainer` 与 `source-repo-study`，安装器在更新时清理这两个旧托管链接；其他来源的同名内容沿用上述核对与保留方式。

`writing-for-humans` 是原 `plain-writing` 的新名称，安装器在更新时同步切换仓库托管链接。

公开仓库只保存适合公开、跨设备复用的内容。私人资料、机器专属绝对路径、密钥和内部项目知识保留在本机或对应项目中，不通过本仓库连接。

也可以直接把仓库地址交给 AI，让它阅读本文件并完成安装和合并。

## Skills 清单

| Skill | 用途 |
| --- | --- |
| [`software-development`](skills/software-development/) | 围绕业务完成设计、实现、重构、业务测试与代码审查，代码完成后主动独立审查并交付。 |
| [`align`](skills/align/) | 手动使用 `$align` 对齐意思和期望的处理程度，理解了就简短确认，有疑问就提问；默认不自动触发。 |
| [`explain`](skills/explain/) | 手动使用 `$explain`，先用生活例子解释，再讲专业机制，最后给出三个理解检查问题；默认不自动触发。 |
| [`breakdown`](skills/breakdown/) | 手动使用 `$breakdown`，拆解业务背景、要解决的问题和具体做法，理解关键选择与可迁移规律；默认不自动触发。 |
| [`tech-choice`](skills/tech-choice/) | 手动使用 `$tech-choice`，根据业务目标筛选技术方案、比较关键取舍并给出推荐；默认不自动触发。 |
| [`ask`](skills/ask/) | 手动使用 `$ask`，通过逐轮提问澄清困惑、事实和假设，找到真正值得回答的问题。 |
| [`fact-check`](skills/fact-check/) | 手动使用 `$fact-check`，核查说法中的事实、推理和价值判断，指出证据缺口并说明可以相信到什么程度。 |
| [`panel`](skills/panel/) | 手动使用 `$panel`，用三种互补专业视角分析问题，检验分歧和假设，综合形成可行动的建议。 |
| [`rethink`](skills/rethink/) | 手动使用 `$rethink`，从基本事实、目标和现实约束重新推导路径，检查惯性假设与表面修补。 |
| [`borrow`](skills/borrow/) | 手动使用 `$borrow`，从其他领域寻找结构相似的问题，提炼可迁移机制并设计低成本尝试。 |
| [`decide`](skills/decide/) | 手动使用 `$decide`，分别建立两个选择的最强论证，找出关键分歧，再根据补充信息作出判断。 |
| [`experiment`](skills/experiment/) | 手动使用 `$experiment`，找出决定背后的关键假设，设计低成本可逆实验，明确指标和继续或停止的条件。 |
| [`talent`](skills/talent/) | 手动使用 `$talent`，通过具体经历探索被忽略的能力、兴趣和能量模式，形成个人天赋使用说明书。 |
| [`life`](skills/life/) | 手动使用 `$life`，梳理当前状态与价值取向，探索三个五年人生版本，并制定可以尝试的原型行动。 |
| [`deep-discussion`](skills/deep-discussion/) | 围绕具体问题共同推敲方案，明确用户需要回应的取舍与 Agent 自主查证的事项，并按需要维护讨论记录或对外问卷。 |
| [`prototype`](skills/prototype/) | 制作可操作的逻辑模型或比较界面方案，验证尚未确定的设计问题。 |
| [`to-spec`](skills/to-spec/) | 将已有讨论和决策地图中的确认内容整理为正式规格，明确行为、验收与未决事项。 |
| [`wayfinder`](skills/wayfinder/) | 创建和恢复跨会话决策地图，跟踪依赖、未决事项与当前可推进的问题。 |
| [`improve-codebase-architecture`](skills/improve-codebase-architecture/) | 从变更热点和设计摩擦中寻找重构机会，给出证据、优先建议及改前改后对比。 |
| [`systematic-debugging`](skills/systematic-debugging/) | 调查 Bug、偶发失败、状态不一致、性能退化和生产异常。 |
| [`writing-for-ai`](skills/writing-for-ai/) | 编写和组织面向 AI 的 Skill、规则、提示词与知识文档，统一内容设计、写作、封装与验证。 |
| [`writing-for-humans`](skills/writing-for-humans/) | 撰写和修改面向人的内容，按读者与用途组织信息，讲清事实、原因、结果和下一步。 |
| [`knowledge-maintenance`](skills/knowledge-maintenance/) | 研究和持续维护有来源依据的知识，统一资料摄取、Wiki 修订、源码研究与独立变更记录。 |
| [`diagramming`](skills/diagramming/) | 创建和维护业务流程图、架构图与思维导图，讲清条件、路径、边界和业务理由，按阅读用途交付可编辑源图或图片。 |

`diagramming` 统一原 `drawio` 与 `mindmap`；共用的图型选择、来源、制作与交付方法集中维护，业务图与脑图设计按需读取。读取、生成和结构检查使用包内脚本；PNG 导出需要 draw.io Desktop，原生显示检查使用当前环境的界面工具。安装器更新时将两个旧托管链接切换到新入口。采用依据见[图解能力整合记录](docs/changes/2026-11-19-diagramming-215b3d9e.md)。

`writing-for-ai` 整合原三个写作 Skill，保留已有的工程与评测工具；替换依据和验证边界见[采用记录](docs/changes/2026-11-04-writing-for-ai.md)。

软件开发与异常调查分别由 `software-development` 和 `systematic-debugging` 承担。个人规则不重复维护 Skill 选用目录；收尾在对应任务中复用有效证据。相关调整见[调试与交付方法整理](docs/changes/2026-11-05-debugging-and-delivery.md)。

知识维护统一由 `knowledge-maintenance` 承担，源码概览、机制讲解和演进研究按问题读取。目录采用逐层 `README.md` 与独立 `changes/`；采用范围见[知识维护整合记录](docs/changes/2026-11-05-knowledge-maintenance-ea0ad5b7.md)。

## Hooks 清单

当前仓库收录一套 [`task-handoff`](hooks/task-handoff/) Hook，用于在长任务中保存和恢复工作上下文。

| Hook 事件 | 触发时机 | 用途 |
| --- | --- | --- |
| `UserPromptSubmit` | 用户提交新消息后 | 上下文使用率达到 70% 时，提醒为当前用户任务创建或更新状态文件。 |
| `PostToolUse` | AI 每次调用工具后 | AI 连续工作期间达到 70% 时及时提醒，不依赖用户再次发送消息。 |
| `SessionStart`（`compact`） | 上下文压缩完成后 | 提醒先读取任务状态文件，再结合 Git 状态和差异恢复工作。 |

同一个用户任务只提醒一次；并行工具回调会合并为一次提醒，下一条用户消息开始新的提醒周期。

## 第三方内容

仍由上游维护的第三方 Skills、Codrive 和文档处理 Skills 来源记录在 [`manifests/third-party-skills.json`](manifests/third-party-skills.json)。

`writing-for-ai` 重新编写共同的写作方法，参考 Matt Pocock 的信息组织方法，并沿用本仓库原 `skill-creator` 中基于 Anthropic 版本演化的工程与评测资源。来源与修改范围见[来源清单](manifests/third-party-skills.json)。

Matt Pocock 的追问、领域建模与对外确认问卷方法由 `deep-discussion/references/` 承载；代码设计方法重组到 `software-development/references/design-and-implementation.md`，按真实职责和业务需要使用。`wayfinder` 和 `improve-codebase-architecture` 保留独立入口并适配本体系。来源与逐文件映射见来源清单。

`to-spec` 保留上游的规格模板与原型决策表达，适配自动发现、已有文档归属、确认范围与后续动作授权；`deep-discussion` 和 `wayfinder` 在需要正式规格时按名称使用它。


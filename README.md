# Codex Workbench

我的 Codex 用户规则、上下文交接 Hooks 和常用 Skills 的公开存档。主要用于跨设备同步，也方便把同一套协作习惯安装到其他环境。

## 内容

- `AGENTS.md`：用户级协作、代码质量、架构、异常处理和长任务交接规则。
- `hooks/task-handoff/`：上下文接近压缩时提醒更新任务状态，压缩后提醒恢复工作上下文。
- `skills/`：自己维护的通用 Skills。
- `manifests/third-party-skills.json`：常用第三方 Skills 和相关项目的来源，不复制第三方实现。

仓库不包含项目业务资料、邮箱联系人、费用统计工具、访问令牌或本机绝对路径。

## 安装

需要 Node.js 22.20 或更高版本，以及 Python 3.9 或更高版本。

```bash
git clone https://github.com/lzj960515/codex-workbench.git
cd codex-workbench

npx skills add . --global --agent codex --skill '*' --yes --copy
python3 scripts/install.py
```

`npx skills add` 使用通用 Skills CLI 安装仓库中的 Skills。`scripts/install.py` 只安装用户级 `AGENTS.md` 和 Hooks；已有不同的 `AGENTS.md` 会被保留，并生成 `AGENTS.codex-workbench.md` 供 AI 合并。

也可以直接把仓库地址交给 AI，让它阅读本文件并完成安装和合并。

## Skills 清单

| Skill | 用途 |
| --- | --- |
| [`architecture-design-review`](skills/architecture-design-review/) | 设计或审查框架、公共 API、核心基础设施和跨模块重构。 |
| [`receiving-code-review`](skills/receiving-code-review/) | 评估代码审查意见，并依据代码和业务证据决定如何处理。 |
| [`systematic-debugging`](skills/systematic-debugging/) | 调查 Bug、偶发失败、状态不一致、性能退化和生产异常。 |
| [`test-driven-development`](skills/test-driven-development/) | 用失败测试保护功能实现、Bug 修复和行为重构。 |
| [`verification-before-completion`](skills/verification-before-completion/) | 在完成、提交、推送或发布前建立与声明相匹配的验证证据。 |
| [`skill-builder`](skills/skill-builder/) | 从真实需求设计 Skill 的职责、边界和验收标准。 |
| [`source-repo-study`](skills/source-repo-study/) | 系统研究源码仓库，并整理成架构、功能和数据流 Wiki。 |
| [`wiki-maintainer`](skills/wiki-maintainer/) | 持续摄取和修订 Markdown Wiki，维护索引、链接和知识一致性。 |
| [`drawio`](skills/drawio/) | 创建、修改、检查 draw.io 架构图和流程图，并导出 PNG。 |
| [`mindmap`](skills/mindmap/) | 将想法、文档和讨论整理成可编辑的 draw.io 思维导图。 |
| [`design-extractor`](skills/design-extractor/) | 从网站提取品牌视觉语言并生成标准 `DESIGN.md`。 |

`drawio` 和 `mindmap` 需要安装 draw.io Desktop，并让 `drawio` 命令可以从终端调用。

## Hooks 清单

当前仓库收录一套 [`task-handoff`](hooks/task-handoff/) Hook，用于在长任务中保存和恢复工作上下文。

| Hook 事件 | 触发时机 | 用途 |
| --- | --- | --- |
| `UserPromptSubmit` | 用户提交新消息后 | 上下文使用率达到 70% 时，提醒为当前用户任务创建或更新状态文件。 |
| `PostToolUse` | AI 每次调用工具后 | AI 连续工作期间达到 70% 时及时提醒，不依赖用户再次发送消息。 |
| `SessionStart`（`compact`） | 上下文压缩完成后 | 提醒先读取任务状态文件，再结合 Git 状态和差异恢复工作。 |

同一个用户任务只提醒一次；并行工具回调会合并为一次提醒，下一条用户消息开始新的提醒周期。

## 第三方内容

第三方 Skills、Codrive 和文档处理 Skills 的官方来源记录在 [`manifests/third-party-skills.json`](manifests/third-party-skills.json)，使用时遵循对应项目的许可证。

## 许可证

[MIT](./LICENSE)

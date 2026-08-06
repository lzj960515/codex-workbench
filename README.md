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

## 收录的 Skills

- 工程协作：`architecture-design-review`、`receiving-code-review`、`systematic-debugging`、`test-driven-development`、`verification-before-completion`。
- 知识与提示词：`skill-builder`、`source-repo-study`、`wiki-maintainer`。
- 图形与设计：`drawio`、`mindmap`、`design-extractor`。

`drawio` 和 `mindmap` 需要安装 draw.io Desktop，并让 `drawio` 命令可以从终端调用。

## 第三方内容

第三方 Skills、Codrive 和文档处理 Skills 的官方来源记录在 [`manifests/third-party-skills.json`](manifests/third-party-skills.json)，使用时遵循对应项目的许可证。

## 许可证

[MIT](./LICENSE)

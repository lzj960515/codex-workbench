---
name: skill-creator
description: 创建、修改、组织、校验和评测 Skill 工程包。适用于需求已经明确，需要处理 SKILL.md、frontmatter、触发描述、scripts/references/assets/agents 资源、Skill 重名、静态验证、Fresh Agent 测试或高级基线评测的场景；需求仍模糊时先使用 skill-builder 形成 Skill Brief。
license: Apache-2.0
---

# Skill Creator

本 Skill 基于 Anthropic 发布的 `skill-creator` 持续演化，当前仓库维护产品职责、渐进披露、OpenAI metadata 和评测流程等修改。许可证见 [LICENSE.txt](LICENSE.txt)，修改范围见 [NOTICE.md](NOTICE.md)。

## 职责

把明确的用户需求实现成合法、精简、可发现、可复用并经过验证的 Skill 包。Skill 是给另一个 Agent 使用的工程产品，正文只保存执行任务所需的非显然知识。

产品职责不清楚时，先读取 `skill-builder` 并形成 Skill Brief；已有清晰需求、现有 Skill 或小范围修改时，直接进入工程流程。

## 核心原则

### 控制上下文成本

Skill metadata 会进入初始上下文，正文会在触发后加载。保留真正影响执行质量的知识：

- description 简洁说明能力、触发场景和边界。
- `SKILL.md` 保存核心工作流、判断原则和资源导航。
- 详细文档放入 `references/`，只在对应场景读取。
- 重复、确定且容易写错的操作放入 `scripts/`。
- 输出模板和二进制资源放入 `assets/`。

解释关键原因，让 Agent 可以根据上下文判断；把低概率特例和实现历史留在 Skill 之外。

### 把设计意图变成行为

实现 Skill Brief 时保留它的存在理由和优化目标，不把设计意图只复制成一段开场说明。

- 判断型 Skill 把需要纠正的默认偏差、关键取舍和停止条件融入目标、决策顺序、Reference 路由、输出契约和验收场景。
- 让 Agent 知道为什么在当前证据下选择某个动作，也知道何时批准、不修改、不新增测试、不继续抽象或暂不下结论是完整结果。
- 操作型 Skill 围绕权限、输入输出、副作用和失败边界保持直接；没有真实判断分支时不增加理念段落。

标题和章节服从任务结构。验收关注 Agent 的选择与结果是否改变，不检查是否出现“哲学”“原则”或其他固定措辞。

### 按任务风险设置自由度

- 多种方案都合理时，提供原则和决策依据。
- 有稳定模式但允许变化时，提供模板、伪代码或参数化脚本。
- 操作脆弱、重复且一致性重要时，提供经过测试的确定性脚本。

### 保持行为可信

Skill 的名称、description、实际能力和副作用保持一致。敏感值存入 Keychain、环境变量或专用 Secret Manager；Skill 只记录安全的检索方式和非敏感标识。

## Skill 结构

```text
skill-name/
├── SKILL.md                 # 必需：frontmatter 与核心工作流
├── agents/                  # 可选：产品 UI metadata 或辅助 Agent 指南
│   └── openai.yaml
├── scripts/                 # 可选：可执行、可重复、确定性工具
├── references/              # 可选：按需读取的详细知识
└── assets/                  # 可选：输出使用的模板、图像和样例资产
```

只创建实际需要的目录。详细信息在一个位置维护，`SKILL.md` 负责指向它，而不是复制一遍。

## 工程流程

### 1. 确认输入与现状

1. 阅读 Skill Brief、当前对话或现有 Skill。
2. 搜索目标范围内的同名和近似 Skill，确认是新建、扩展、合并还是排重。
3. 确定安装范围：项目专用放仓库 `.agents/skills`，个人跨项目能力放 `~/.agents/skills`，产品内置或插件 Skill 按对应平台管理。
4. 识别需要保留的现有行为、脚本、参考资料和跨平台兼容性。
5. 判断该 Skill 主要提供判断还是确定性操作。判断型 Skill 核对默认偏差、优化结果、关键取舍和停止条件；操作型 Skill 核对权限、输入输出、副作用和失败边界。
6. 从用户请求、实际差异和已有用例明确本次要保护的行为，再按“校验与测试”选择最低充分验证。语义不变的校对用差异复核；行为变化选择能暴露目标问题的场景，并在涉及判断或触发边界时覆盖正确停止或不触发的情况。

同名 Skill 不会自动合并。需要一个权威版本时，保留可维护的来源，并使用平台支持的配置禁用其他版本。

### 2. 规划可复用资源

对每个验收场景从零执行一次思考：

- 会反复重写的代码形成脚本。
- 只有特定问题才需要的长文形成 Reference。
- 输出中复用的文件形成 Asset。
- 只影响 UI、调用策略或工具依赖的信息放入 `agents/`。

工具输出以事实和结构化数据为主；业务判断和结论由使用该 Skill 的 Agent 完成，除非 Skill 本身的稳定职责就是执行确定性判断。

### 3. 初始化或更新

新 Skill 优先使用初始化脚本创建合法骨架：

```bash
python3 <skill-creator>/scripts/init_skill.py <skill-name> \
  --path <target-directory> \
  [--resources scripts,references,assets]
```

更新现有 Skill 时保留原始名称和公开职责，先阅读完整上下文，再把改动融入现有结构。涉及大幅改写或行为回归风险时，在临时目录保留修改前快照。

### 4. 编写 frontmatter

```yaml
---
name: skill-name
description: Skill 做什么，以及用户在什么任务、领域、文件或症状下应使用它。
compatibility: 运行 Skill 所需的跨平台环境、工具或依赖约束（可选）。
---
```

- `name` 使用小写字母、数字和连字符，目录名与之相同，长度不超过 64。
- description 是主要触发面：先写核心用例，再写必要边界；避免与相邻 Skill 使用相同的宽泛触发语句。
- 所有触发条件放在 description。正文只在 Skill 已触发后加载。
- `compatibility` 只声明影响 Skill 能否运行的跨平台约束；OpenAI 产品的 MCP 或 UI 依赖放在 `agents/openai.yaml`。
- 用户明确提及 Skill 时支持显式调用；描述同时服务于隐式选择。

### 5. 编写正文与资源

编写或修改正文前，使用 `writing-for-agents` Skill，应用其中的信息组织与写作方法。以已有设计意图、行为契约和验收要求约束修改；保留原有有效表达，只调整当前目标需要改变的部分。

正文使用任务所需的自然结构，例如工作流、任务分类、能力分类或参考规范。使用命令式、正向且可判断的指令：

- 先写最重要的决策和执行顺序。
- 解释会改变选择的关键原因，让 Agent 能把原则应用到未见过的变体；用明确条件表达何时已经获得充分结果。
- 让使用者知道何时读取哪个 Reference、何时运行哪个 Script。
- 提供格式模板来约束稳定输出，只在模板不足以表达时增加示例。
- 为脚本定义输入、输出、副作用和失败方式，并实际运行代表性样例。
- 将较长的平台差异和高级流程放到按需 Reference。

正文通常保持在 500 行以内；接近该规模时优先拆分，而不是继续堆叠章节。

### 6. 产品 metadata

Codex 可使用 `agents/openai.yaml` 展示 Skill 和声明调用策略。先阅读 `references/openai_yaml.md`，再运行：

```bash
python3 <skill-creator>/scripts/generate_openai_yaml.py \
  <skill-directory> \
  --interface 'display_name=...' \
  --interface 'short_description=...' \
  --interface 'default_prompt=Use $skill-name to ...'
```

`SKILL.md` 始终是跨平台行为来源；产品 metadata 只承载对应平台的 UI 和策略信息。

### 7. 校验与测试

按行为差异和错误后果选择验证力度，而不是按修改字数、文件数或 Skill 名称打分。一个“可以”改成“必须”可能改变执行策略；整段措辞调整也可能保持原有语义。

| 当前变化与要回答的问题 | 最低充分验证 |
| --- | --- |
| 错字、标点、排版，含义与触发条件保持原样 | 校对完整差异；涉及 frontmatter、路径或资源结构时加解析与引用检查，完成后交付 |
| 可由程序直接证明的脚本或资源变化 | 运行相关单测或代表性调用；Agent 的选择也发生变化时，再覆盖该分支 |
| 新增能力，或改变触发、授权、停止条件、工作顺序、输出契约和 Skill 协作 | 选择受影响的自然任务，在新上下文中检查实际动作和产物；通常从 1–3 个相关场景起步，数量服从真实分支 |
| 判断新版是否更好，较大重构、共享职责变化，或高风险行为边界发生变化 | 在相同环境和初态下比较旧版与候选；结果波动且会改变采用决定时，再增加重复试验或未参与调优的案例 |

新包或结构变化运行：

```bash
python3 <skill-creator>/scripts/quick_validate.py <skill-directory>
```

需要新上下文测试时，读取 [评估设计与用例维护](references/evaluation-design.md)；在 Codex 执行时再读取 [Codex 评估工具](references/codex-evaluation.md)，复用其中的运行脚本。开始前简短说明本轮场景和预计会话数，完成后集中汇报；测试完成通知可能仍由用户现有环境触发。

比较旧版、重复试验或主观质量评审时，按需读取 [高级评测](references/advanced-evaluation.md)，复用已有 grader、benchmark 和 Viewer。保留每次实际结果，区分执行失败、行为退步和无法判断；一次通过只证明该次场景，不能据此宣称新版整体更好。

为常用、影响大或已有真实失误的 Skill 在 `evals/` 保存可复用的请求、脱敏初态和行为标准。运行日志、候选副本及评分输出放任务 `tmp/`。优先复用已有案例，只为新故障或真实职责缺口补例；判定标准来自用户目标与既有契约，修改 Skill 时保持标准独立。

当目标问题已有直接证据、受影响的关键边界通过检查且剩余不确定性不改变当前决定时，结束验证。新增差异、真实失败或未解决的重要疑点才触发下一轮。

### 8. 审查与交付

完成后从两个角度复查：

- **产品审查**：是否回答 Skill Brief 中的真实问题，边界是否清楚，是否减少用户返工。
- **工程审查**：触发是否准确，正文是否精简，资源职责是否清楚，脚本是否可靠，验证声明是否有证据。

对判断型 Skill 再检查设计意图是否真实进入决策和验收：Agent 是否在原始失败场景中改变行为，是否在无需更多动作时干净停止。对操作型 Skill 检查是否保持契约直接，没有为了形式完整增加无关理念。

报告保留、增强和改变的能力，并准确说明已运行与未运行的验证。不要用“更短”代替“更好”。

### 9. 打包与分发

用户需要可安装产物时，使用现有打包脚本：

```bash
python3 <skill-creator>/scripts/package_skill.py <skill-directory>
```

保留原目录名和 frontmatter `name`。已安装目录只读时，先复制到临时工作目录完成修改和验证，再从该副本打包。用户只需要本机或仓库直接发现 Skill 时，不额外生成压缩包。

## 内置工具

- `scripts/init_skill.py`：创建 Skill 骨架和可选资源目录。
- `scripts/generate_openai_yaml.py`：生成 Codex UI metadata。
- `scripts/quick_validate.py`：校验 frontmatter 和命名。
- `scripts/package_skill.py`：生成可安装的 Skill 包。
- `references/openai_yaml.md`：Codex metadata 字段和约束。
- `scripts/codex_skill_eval.py`：快照实际 Skill 目录，在新 Codex 上下文运行单个用例并保存发现、执行和产物证据。
- `references/evaluation-design.md`：行为评估的范围、用例、评分和长期维护。
- `references/codex-evaluation.md`：Codex 本地用例、候选/基线快照与运行工具用法。
- `references/advanced-evaluation.md`：可选的基线、benchmark、Viewer、盲测和触发优化流程。
- `references/schemas.md`：高级评测 JSON 结构。
- `agents/grader.md`、`agents/comparator.md`、`agents/analyzer.md`：高级评测角色标准。

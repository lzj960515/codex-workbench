# Codex 本地 Skill 评估

在 SKILL.md 已判定需要新上下文测试后，使用 `scripts/codex_skill_eval.py`。需要 Python 3.11+、可用的 `codex` CLI 及其现有认证；脚本复用已有 Codex app-server 调用方式，不另建 Agent 产品。

工具执行两个动作：快照实际发现的 Skill 组合；在独立临时项目中运行一个指定案例，保存发现、工具记录和最终文件。结果保持 `not_graded`，由评估者检查实际产物后评分。

## 1. 保留修改前版本

在修改活跃 Skill 前，从代表实际使用范围的目录发现并复制完整组合：

```bash
python3 <skill-creator>/scripts/codex_skill_eval.py \
  --snapshot --cwd <source-project> \
  --suite <target-skill>/evals/evals.json \
  --out <task-tmp>/comparison
```

`--suite` 可省略。快照不启动模型。输出包含 `baseline/`、`candidate/`、来源清单及 `evaluation-matrix.json`。两个目录最初内容相同；只在 `candidate/` 修改或替换已确认范围内的包。新增 Skill 时加入候选目录，并把它的 `SKILL.md` 相对路径加入该变体的 `expected_paths`。

快照保持相邻包目录关系，排除 `evals/` 和缓存，使执行端不自动取得评分答案。原生发现存在重复启用名称时停止，由当前项目的真实优先级决定选哪个版本后再建立可比较目录。

快照前后已发生修改时，使用真实旧版 Git 或先前完整备份补齐基线，并核对内容；缺少旧版时只做当前行为检查。

## 2. 核对矩阵和初态

矩阵路径相对于矩阵文件。下面的结构只展示一个包；实际快照列出整个启用组合：

```json
{
  "version": 1,
  "variants": {
    "baseline": {"roots": ["baseline"], "expected_paths": ["baseline/example/SKILL.md"]},
    "candidate": {"roots": ["candidate"], "expected_paths": ["candidate/example/SKILL.md"]}
  },
  "disabled_paths": ["<original-discovered-SKILL.md>"],
  "common_config": {},
  "cases": [
    {"id": 1, "prompt": "自然语言任务", "fixture": "fixtures/example", "sandbox": "workspace-write"}
  ]
}
```

`--suite` 从 `evals.json` 的 `evals` 读取案例，并解析其 `fixture`。工具只把 `prompt` 作为请求、把 `fixture` 内文件作为初态交给执行 Agent，其他评分字段留在评估端。初态目录只放任务实际可见的材料。样例 Skill 存为 `SKILL.md.fixture`，避免进入真实 Skill 发现；用案例的 `fixture_renames`（如 `{"SKILL.md.fixture": "SKILL.md"}`）在临时项目内还原。重命名只允许在该项目内进行。

测试发现会同时检查精确启用路径与重名。原始发现路径通过进程级配置禁用，副本通过临时额外发现目录启用；实际结果与矩阵不符时停止，不把“计划禁用”当作已经隔离。

两端使用同一模型、推理强度、工具和配置。沿用当前配置时检查两次记录中的实际模型、CLI 版本和环境摘要；需要固定时在 `common_config` 设置已有环境支持的相同值。其余包的摘要也应一致。

用例默认 `read-only`；需要产生文件时选择 `workspace-write`。本工具用于本地可复现材料，外部 API、数据库和生产任务先准备受控替身；CLI 文件沙盒不限制所有外部 MCP 副作用。

## 3. 先检查发现，再按需运行

```bash
python3 <skill-creator>/scripts/codex_skill_eval.py \
  --matrix <comparison>/evaluation-matrix.json --variant candidate --case 1 \
  --check-only --out <task-tmp>/discovery-check

python3 <skill-creator>/scripts/codex_skill_eval.py \
  --matrix <comparison>/evaluation-matrix.json --variant candidate --case 1 \
  --out <task-tmp>/iteration-1/eval-example/new_skill/run-1
```

一个运行命令只启动一个案例、一个新会话，不自动遍历全部案例或重复次数。`--timeout` 默认 240 秒。选择少量必要场景，运行前告知预计会话数；沿用用户现有通知设置，工具不承诺静默通知。

需要旧版对照时，在新输出目录运行同一案例的 `baseline`。新增能力也可保留不含该包的基线。重复时使用新的 `run-N`，每次工具重新复制初态。顺序或并行运行都必须保持两端配置一致、初态独立。

## 4. 读取证据与评分

- `result.json`：实际运行版本、发现目录和包摘要、初态与环境摘要、运行状态、耗时及 token。`completed` 表示 Agent 结束，质量仍是 `not_graded`。
- `discovery.json`：实际启用目录；它不能证明正文确实被读取。
- `items.json`、`protocol.jsonl`、`response.md`：实际工具与消息记录。工具读 Skill 的记录用于核实调用。
- `workspace-before.json`、`workspace-after.json`、`changes.json`：文件与链接状态，覆盖新增、删除及修改。
- `outputs/`：最终普通文件；符号链接只记录目标，不追随复制外部文件。
- `timing.json`、`eval_metadata.json`：供已有评分和报告使用的运行信息。

独立检查任务结果，按 [评估设计](evaluation-design.md) 记录通过、失败或证据不足。评分完成后需要现有 benchmark/Viewer 时，按 [高级评测](advanced-evaluation.md) 写 `grading.json`，将一份相同的 `eval_metadata.json` 放到案例根目录。执行失败与未评分记录单独报告，补足前不纳入通过率。

## 隔离与验证边界

每次执行位于新建临时项目；评分材料与结果目录在项目外。执行后保存初态和结果，清理该临时项目，以及 CLI 本次新增的对应信任记录。清理发生冲突时保留配置并报告，其他用户配置保持原样。

记录本地配置和全局规则的摘要，试验期间变化会使结果标为不完整。项目信任条目单独处理；黑箱系统提示、服务端变化和外部工具状态不能据此视为已固定。

这是发现配置隔离，不是读取权限隔离。具有文件读取能力的 Agent 仍可能访问其他目录；检查轨迹，越过快照取得原版或评分材料的试验不能用于归因。所有副本按用户 Skill 发现，插件命名空间和项目/插件优先级不完全重现；依赖该优先级的故障要另做原生发现测试。

协议来源：[Codex App Server](https://developers.openai.com/codex/app-server) 的 `skills/list`、`skills/extraRoots/set`、`thread/start` 和 `turn/start`；调用设置见 [Agent Skills](https://developers.openai.com/codex/skills)。实际接口以当前 CLI 返回和发现检查为准。

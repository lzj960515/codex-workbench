# Advanced Skill Evaluation

本流程用于证明高风险、团队级或复杂 Skill 的新版本没有退步。普通文案、路径或小范围调整使用静态校验和少量 Fresh Agent 场景即可。

## 适用条件

满足任一条件时考虑高级评测：

- Skill 会执行生产运维、数据库、安全、发布或其他高风险操作。
- 多个团队或 Agent 依赖稳定的输出契约。
- 修改前后差异难以通过单个样例判断。
- description 的误触发或漏触发会造成明显成本。
- 用户明确要求 benchmark、A/B、盲测或证明新版不退步。

## 1. 建立基线

更新现有 Skill 时，修改前将完整 Skill 包复制到临时 workspace：

```text
<skill-name>-workspace/
├── skill-snapshot/
└── iteration-1/
```

新 Skill 的 baseline 是不加载该 Skill 的 Agent；更新 Skill 的 baseline 是加载 `skill-snapshot` 的 Agent。不要把预期答案、已知缺陷或修复方案泄漏给执行 Agent。

## 2. 设计真实测试

选择 3-8 个具有区分度的用户问题，覆盖：

- 最常见的成功路径。
- 容易混淆的相邻职责和 should-not-trigger 场景。
- 缺失数据、权限不足或工具失败。
- 本次修改针对的原始问题。
- 至少一个未参与设计的新变体。
- 判断型 Skill 要纠正的默认偏差，例如为了有结果而过度修改、过度拆分或硬找问题。
- 判断型 Skill 的正确停止场景，例如批准无问题候选、确认无需代码修改或选择轻量验证。

把用例保存在 `evals/evals.json`。完整字段见 `schemas.md`：

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "真实用户问题",
      "expected_output": "可观察的成功结果",
      "files": [],
      "expectations": []
    }
  ]
}
```

客观行为使用断言；语气、设计质量和复杂判断留给人工 Review。断言应说明行为，不绑定偶然措辞或内部实现。正确停止场景检查最终选择和实际动作，不能只检查输出提到“无需修改”之类的关键词。

## 3. 同轮运行新版与基线

在能够启动独立 Agent 时，同一轮并行运行。新 Skill 使用：

- `with_skill`：加载当前 Skill。
- `without_skill`：不加载该 Skill。

更新已有 Skill 时使用：

- `new_skill`：加载当前 Skill。
- `old_skill`：加载修改前快照。

每个 Agent 只得到真实任务、必要输入文件和输出位置。保留原始输出、工具轨迹、耗时和 token，避免前一轮产物污染后一轮。

目录示例：

```text
iteration-1/
└── eval-<name>/
    ├── eval_metadata.json
    ├── with_skill/
    │   └── run-1/
    │       ├── outputs/
    │       ├── grading.json
    │       └── timing.json
    └── without_skill/
        └── run-1/
            ├── outputs/
            ├── grading.json
            └── timing.json
```

每次重复执行使用独立的 `run-2`、`run-3`。更新已有 Skill 时把目录名替换为 `new_skill` 和 `old_skill`。`timing.json` 保存可用的 `total_tokens`、`duration_ms` 和换算后的秒数。时间和 token 用于发现成本变化，不单独决定质量高低。

每个 `eval-<name>/eval_metadata.json` 使用 `schemas.md` 中的统一契约，保存稳定的 `eval_id`、用于 Viewer 的 `eval_name` 和原始 `prompt`。聚合器与 Viewer 都从该 eval 根目录读取同一份 metadata。

## 4. 评分与汇总

优先用程序检查可确定行为；复杂结果使用 `agents/grader.md`。`grading.json` 的断言结果使用以下字段：

```json
{
  "expectations": [
    {
      "text": "明确描述被检查的行为",
      "passed": true,
      "evidence": "来自输出的证据"
    }
  ]
}
```

汇总 benchmark：

```bash
cd <skill-creator>
python3 -m scripts.aggregate_benchmark \
  <workspace>/iteration-N \
  --skill-name <name> \
  --primary-config <with_skill-or-new_skill> \
  --baseline-config <without_skill-or-old_skill>
```

Delta 始终按 `primary - baseline` 计算。标准目录名可以自动识别，命令仍显式传入两端角色，使评测意图可审查并避免依赖目录排序。

然后按照 `agents/analyzer.md` 检查：

- 新版在哪些用例改善或退步。
- 哪些断言没有区分度，两边始终通过。
- 哪些结果方差过大，可能属于偶然成功。
- 质量、耗时和 token 之间的实际取舍。
- Agent 是否重复编写同类工具，提示 Skill 应增加脚本或 Reference。

## 5. 人工 Viewer

需要用户比较复杂输出时，使用现有 Viewer，而不是新写页面：

```bash
python3 <skill-creator>/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "<name>" \
  --benchmark <workspace>/iteration-N/benchmark.json
```

无 GUI 环境使用：

```bash
python3 <skill-creator>/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "<name>" \
  --benchmark <workspace>/iteration-N/benchmark.json \
  --static <output.html>
```

第二轮以后传入 `--previous-workspace`。用户提交的 `feedback.json` 放回对应 workspace，再围绕具体反馈迭代。空反馈表示该用例没有需要调整的地方。

## 6. 盲测

当主观质量重要且标签可能影响判断时，按照 `agents/comparator.md` 做盲测：随机化 A/B 顺序，让比较 Agent 不知道哪个是新版。盲测是可选增强，不替代客观断言和真实用户反馈。

## 7. Description 触发优化

只有真实使用或 Fresh Agent 场景证明存在漏触发、误触发时，才优化 description。

1. 准备 should-trigger 与 should-not-trigger 查询，包含边界相邻 Skill。
2. 先人工审查测试集，避免用错误样例优化错误目标。需要可视化审查时，用 `assets/eval_review.html` 生成临时页面，不把测试数据写回模板。
3. 使用 `scripts/run_loop.py`、`scripts/run_eval.py` 和 `scripts/improve_description.py` 运行可用的触发评测。
4. 保留 held-out 用例，按测试集结果选择 description，避免只拟合训练问题。
5. 更新后重新验证正文能力和相邻 Skill 边界。

这些脚本源自 Claude Skill Creator，运行前检查其 CLI、认证和模型依赖是否适合当前环境。不可用时保留相同评测语义，使用当前平台的 Fresh Agent 能力执行。

## 8. 平台适配

- 有独立 Agent 时并行运行新版与基线，保证比较互不污染。
- 没有独立 Agent 时顺序执行代表性任务并加强人工 Review；明确说明结果不是独立基线，不宣称统计非劣。
- 没有 GUI 时使用 Viewer 的 `--static` 模式，或在对话中逐项呈现 Prompt、输出和评价结果。
- `run_loop.py` 等依赖 `claude -p` 的脚本只在 Claude CLI 可用时执行；Codex 使用当前平台的 Fresh Agent 和输出采集能力完成等价评测。
- 已安装目录只读时，保留原始名称并复制到临时 workspace 修改、验证和打包。

## 9. 迭代停止条件

当以下条件满足时停止：

- 原始问题和关键边界都有代表性用例。
- 新版没有确定退步，或取舍已得到用户接受。
- Skill 修改来自可泛化原因，不是单个样例补丁。
- 验证成本与 Skill 风险匹配。
- 结果、限制和未验证范围已经清楚报告。

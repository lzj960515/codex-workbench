---
name: improve-codebase-architecture
description: Find and compare worthwhile architectural refactoring opportunities in a codebase or subsystem, guided by change hotspots and concrete design friction. Use when the user asks where to refactor, wants an architecture health scan, or needs before-and-after proposals before choosing a candidate.
---

# Improve Codebase Architecture

发现有代码依据的架构摩擦，比较能够让业务职责更完整、调用方更容易使用、后续修改更集中的重构机会。

This command is _informed_ by the project's domain model and built on a shared design vocabulary:

- 读取[设计与实现判断](../software-development/references/design-and-implementation.md)，按业务动作、职责与生命周期理解接口和复杂性归属；采用项目现有领域与框架名称。
- The project's existing glossary, business map, and decision records give names to good seams and explain deliberate constraints. For business-relevant scope, use `semantic-atlas` to find and confirm the current business model; use current source to verify its leads.

## Process

### 1. Explore

**Scope before you scan: YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If the user named a direction (a module, a subsystem, a pain point), take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots, the files and areas that keep coming up, and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.

Read the owning domain documents and existing decisions in the selected area first. Use `CONTEXT.md` and `docs/adr/` when they are the project's established locations.

Then walk the selected code paths. For a broad scan with substantial independent areas, delegate those areas to sub-agents with a shared scope, the design criteria, and a requirement to cite concrete code. Continue the main investigation and verify returned candidates against callers and existing decisions before combining them. Inspect a small area or a tightly coupled path directly. Explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- 哪些接口仍让调用方掌握大量内部细节、反复协调同一组业务动作？
- 哪些纯函数或接口只是为测试提取，实际业务问题仍分散在调用方？
- Where do tightly-coupled modules leak across their seams?
- 哪些真实业务契约难以通过现有接口观察，问题来自职责划分，还是验证方式不合适？

按设计与实现方法核对封装的作用：去掉它后，复杂性会消失，还是重新分散到多个调用方？保留承担真实规则与协调责任的封装，以具体源码说明候选的业务收益与维护成本。没有得到证据支持的改进机会时，报告结论并结束。

### 2. Present candidates visually

For several candidates or complex comparisons, write an HTML report in the project's temporary-artifact location and show it with the available file or browser viewer. Follow the project's storage convention; otherwise use `tmp/YYYY-MM-DD-architecture-review.html`. For a small comparison, present the same evidence and a before/after diagram directly in the response. Use the user's language.

The HTML report uses **Tailwind via CDN** for layout and styling, and **Mermaid via CDN** for diagrams where a graph/flow/sequence reliably communicates the structure. Mix Mermaid with hand-crafted CSS/SVG visuals: use Mermaid when relationships are graph-shaped (call graphs, dependencies, sequences), and hand-built divs/SVG when you want something more editorial (mass diagrams, cross-sections, collapse animations). Each candidate gets a **before/after visualisation**. Be visual.

For each candidate, render a card with:

- **Files**: which files/modules are involved
- **Problem**: why the current architecture is causing friction
- **Solution**: plain-language description of what would change
- **收益**：具体说明哪些业务变化会更集中、调用方少掌握哪些细节，以及现有行为如何验证。
- **前后对比图**：并排展示职责、接口和复杂性如何调整。
- **Recommendation strength**: one of `Strong`, `Worth exploring`, `Speculative`, rendered as a badge

End the report with a **Top recommendation** section: which candidate you'd tackle first and why.

**采用现有领域词汇与设计判断。** 说明被改进的业务概念，链接实际实现它的代码符号；框架原生名称表达真实契约时予以保留。接口或模块数量减少本身不构成收益，测试便利也不单独证明新增边界的必要性。

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly in the card (e.g. a warning callout: _"contradicts ADR-0007, but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

See [HTML-REPORT.md](HTML-REPORT.md) for the full HTML scaffold, diagram patterns, and styling guidance.

Keep this stage at the problem and proposed responsibility level. Recommend the strongest candidate with reasons, then let the user choose what to explore. When the user has already selected the candidate, continue into its design within that authorization.

### 3. Grilling loop

用户选定候选后，使用 `deep-discussion` 讨论真实约束、依赖、目标职责、接口隐藏的复杂性和需要保留的行为验证。

As decisions crystallize, use [domain clarification](../deep-discussion/references/domain-modeling.md) to capture their meaning in the owning discussion or decision record:

- **以新的领域概念命名调整后的模块时**，在所属记录保存已确认含义，区分设计提案与已经实现的业务事实。
- **Sharpening a fuzzy term during the conversation?** Record the clarification at the existing owner while its evidence is fresh.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing; skip ephemeral reasons ("not worth it right now") and self-evident ones.
- **不同接口存在实质取舍时**，按[公共接口与方案比较](../software-development/references/design-and-implementation.md#公共接口与核心基础设施)，在相同事实与已确认用例下比较调用方式、隐藏的复杂性、依赖及总维护成本。已有方案成立时直接采用。

分析使用了 Semantic Atlas 工作流时，完成相应的观察与维护判断；只有稳定业务含义变化时才提出权威地图更新，局部实现重组保持业务地图不变。选定的架构设计与获授权的实现分别进入 `software-development` 的设计和开发分支；设计选择不自动授予代码与数据变更权限。

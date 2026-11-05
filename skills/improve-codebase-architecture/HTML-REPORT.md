# HTML Report Format

Use this reference when the comparison warrants an HTML report. Store it under the artifact convention selected by the `improve-codebase-architecture` skill; the file loads its styling and diagrams from the CDNs below. Tailwind and Mermaid both come from CDNs. Mermaid handles graph-shaped diagrams reliably; hand-built divs and inline SVG handle the more editorial visuals (mass diagrams, cross-sections). Mix the two: don't lean on Mermaid for everything, it'll start to look generic.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Architecture review for {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* small custom layer for things Tailwind doesn't cover cleanly:
         dashed seam lines, hand-drawn-feeling arrow heads, etc. */
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Header

Repo name, date, and a compact legend: solid box = module, dashed line = seam, red arrow = leakage, thick dark box = the module owning the consolidated responsibility. No introduction paragraph. Straight into the candidates.

## Candidate card

图形承担主要解释，文字简短直接。沿用项目的业务与框架词汇，依据[设计与实现判断](../software-development/references/design-and-implementation.md) 表达职责、调用方契约和复杂性归属。

Each candidate is one `<article>`:

- **标题**：简短说明职责调整，例如“将订单接收规则集中到订单入口”。
- **徽标行**：推荐强度（`Strong` = emerald、`Worth exploring` = amber、`Speculative` = slate），需要时标注实际受影响的职责或依赖。
- **Files**: monospaced list, `font-mono text-sm`.
- **Before / After diagram**: the centrepiece. Two columns, side by side. See patterns below.
- **Problem**: one sentence. What hurts.
- **Solution**: one sentence. What changes.
- **收益**：用短句说明具体变化，例如“计价规则集中维护”“调用方直接提交订单”“退出冗余转发层”。
- **ADR callout** (if applicable): one line in an amber-tinted box.

No paragraphs of explanation. If the diagram needs a paragraph to be understood, redraw the diagram.

## Diagram patterns

Pick the pattern that fits the candidate. Mix them. Don't make every diagram look the same. Variety is part of the point.

### Mermaid graph (the workhorse for dependencies / call flow)

Use a Mermaid `flowchart` or `graph` when the point is "X calls Y calls Z, and look at the mess." Wrap it in a Tailwind-styled card so it doesn't feel parachuted in. Style with classDef to colour leakage edges red and the responsibility-owning module dark. Sequence diagrams work well for "before: 6 round-trips; after: 1."

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### Hand-built boxes-and-arrows (when Mermaid's layout fights you)

Modules as `<div>`s with borders and labels. Arrows as inline SVG `<line>` or `<path>` elements positioned absolutely over a relative container. Reach for this when you want the "after" diagram to show one thick-bordered responsibility-owning module with greyed-out internals, since Mermaid won't render that with the right weight.

### Cross-section (good for redundant layers)

Stack horizontal bands (`h-12 border-l-4`) to show layers a call passes through. Before: 6 thin layers each doing nothing. After: 1 thick band labelled with the consolidated responsibility.

### Mass diagram (showing caller obligations and implementation)

每个模块用两个矩形分别示意调用方需要掌握的接口与内部实现。对比前后时标出哪些细节被职责所有者承接；矩形大小只是示意，接口或方法减少本身不证明设计更好。

### Call-graph collapse

Before: a tree of function calls rendered as nested boxes. After: the same tree collapsed into one box, with the now-internal calls shown faded inside it.

## Style guidance

- Lean editorial, not corporate-dashboard. Generous whitespace. Serif optional for headings (`font-serif` works well with stone/slate).
- Colour sparingly: one accent (emerald or indigo) plus red for leakage and amber for warnings.
- Keep diagrams ~320px tall so before/after sits comfortably side by side without scrolling.
- Use `text-xs uppercase tracking-wider` for module labels inside diagrams, so they read as schematic, not as UI.
- The only scripts are the Tailwind CDN and the Mermaid ESM import. The report is otherwise static: no app code, no interactivity beyond Mermaid's own rendering.

## Top recommendation section

One larger card. Candidate name, one sentence on why, anchor link to its card. That's it.

## Tone

使用用户的语言、简洁说明与[设计与实现判断](../software-development/references/design-and-implementation.md)，保留项目具体的领域与框架名称。

**保持概念含义一致：** 业务动作、模块职责、接口、实现、生命周期、依赖与调用方需要掌握的条件。按真实职责解释封装，按业务变化说明复杂性集中在哪里。

Distinguish a concrete code symbol (such as a Service or API) from the design role being evaluated; clarify overloaded terms when the distinction matters.

**Phrasings that fit the style:**

- “订单调用方仍需安排三次内部校验。”
- “计价规则散落在两个调用方。”
- “订单入口统一承担校验与计价。”
- “不同提供方的实际协议差异由现有适配器隔离。”

**收益短句**说明实际业务变化与维护收益：哪些规则集中修改、调用方减少了哪些协调、哪些旧分支可以退出，以及约定行为如何验证。“更容易维护”需要具体原因。生产职责与运行契约决定边界，测试利用已有边界，不以测试替身或测试数量证明新增接口的必要性。

No hedging, no throat-clearing, no "it's worth noting that…". If a sentence could be a bullet, make it a bullet. If a bullet could be cut, cut it. Choose established domain and design terms before inventing a new one.

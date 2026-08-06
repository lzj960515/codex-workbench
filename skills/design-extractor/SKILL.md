---
name: design-extractor
description: >
  Extract a brand's visual design language from its website and generate a standard DESIGN.md file.
  Use when the user provides a company URL, brand name, or website and asks to extract its design system,
  generate a design reference, create a DESIGN.md, or build a design token document.
  Triggers on requests like: "extract the design from stripe.com", "generate a design.md for apple",
  "analyze this website's design language", "create a brand design reference for [company]",
  "帮我提取这个网站的设计系统", "生成 design.md", "分析品牌设计语言".
  Also triggers when the user pastes a URL and says anything related to design, style, or UI.
---

# Design Extractor

A skill for reading a brand's visual DNA from its website and distilling it into a structured DESIGN.md reference file — the kind that AI agents like Claude, Cursor, or Stitch can use to generate on-brand UI.

## The Philosophy of Reading Design

Good design extraction is not inspection — it is interpretation. When you visit a brand's website, you are encountering a system of deliberate choices made by designers who understood the brand's values, audience, and emotional goals. Your job is to reverse-engineer those choices: to answer not just *what* the values are, but *why* the designers made them.

This distinction matters because DESIGN.md is not a style dictionary. It is a design philosophy document. Anyone (or any AI) reading it should come away understanding the *spirit* of the brand, not just its hex codes.

Ask yourself as you observe:
- What feeling is this interface trying to evoke? (Trust? Delight? Speed? Luxury? Warmth?)
- What is the hierarchy of attention here? What do the designers want you to see first?
- Where is the restraint? What is *not* here that you would expect?
- What is the one decision that, if you changed it, would destroy the brand's character?

## The Extraction Process

### Phase 1 — Sense the Brand

Before you touch any inspector or read any code, spend a moment experiencing the website as a user would. Navigate the homepage. Scroll through a product page. Click a button. Notice:

- What is the dominant emotional impression in the first 3 seconds?
- What colors appear? What is the ratio of neutrals to accent colors?
- Does the type feel warm or cold, tight or open, formal or casual?
- Is whitespace used for luxury, for efficiency, or for clarity?
- What does the brand seem to be saying about itself through its visual choices?

Write a sentence or two capturing this raw impression. This becomes the opening of Section 1.

### Phase 2 — Gather Evidence

Use the available web tools (web reader, browser access) to gather concrete visual evidence from the site. Focus on:

**For colors**: Inspect the homepage, a key product page, and a pricing or sign-up page. Look for: the primary background color, the primary text color, the CTA button color, the hover state, any accent colors, and what colors change across light/dark modes. Capture hex and rgba values.

**For typography**: Note the font family names (check CSS, inspect `font-family` rules), the weights in use (headlines, body, captions, buttons), and the letter-spacing and line-height at different sizes. Pay special attention to how headings are tracked — this is often the most brand-defining typographic choice.

**For components**: Study at least: the primary CTA button (all states), a card or content container, the navigation bar, and any distinctive/signature component unique to this brand.

**For layout**: Estimate the max-width of the content container, the base spacing unit, and how sections are separated from each other.

**For depth**: Examine shadow values carefully — they are often deeply on-brand. Apple's shadows mimic studio photography. Stripe's shadows have a blue-indigo tint. These details matter.

When you cannot inspect CSS directly (the site blocks devtools, uses SSR, etc.), infer from visual evidence. A button with very slightly rounded corners probably uses 4-8px radius. If the type feels warm, it probably uses a warm-tinted near-black instead of pure `#000000`. State your inferences explicitly — that is also useful information.

### Phase 3 — Find the Signature Elements

Every great design system has 2-3 choices that are entirely distinctive — the things that make you instantly recognize the brand even in a screenshot with no logo. Find these:

- **Apple**: SF Pro Display at weight 600 with 1.07 line-height; binary black/white section alternation; 980px-radius pill CTAs
- **Stripe**: sohne-var at weight 300 for headlines; blue-tinted multi-layer shadows; `"ss01"` OpenType on every text element
- **Linear**: Inter weight 510 (between regular and medium); darkness as native medium; ultra-thin `rgba(255,255,255,0.05)` borders

Identify these signature choices for the current brand and make sure they are prominently described in Section 1 and referred back to throughout the document.

### Phase 4 — Write the Document

Follow the 9-section template in [references/template.md](references/template.md). The template is a structural contract — every section must be present. But the writing itself should be analytical and explanatory, not just a dump of CSS values.

For each token or value you document, answer: *why does this value exist?* Not always — sometimes a `#f5f5f7` is just a background — but where the value is distinctive or surprising, explain the intent behind it.

**Save a draft early.** Write a first pass of all 9 sections with what you have, then go back and deepen. A complete-but-thin document saved early is better than a perfect document that never gets written.

## When the Site Resists

Some sites use heavy JavaScript, server-side rendering, or aggressive bot protection that makes web fetch return empty or minimal content. When this happens, shift your strategy:

- Try fetching specific sub-pages (pricing, about, careers, design system docs) which are often lighter than the homepage
- Look for the CDN-hosted CSS files referenced in the page source — these often contain all the design tokens even when the rendered HTML is sparse
- Use what you know about the brand combined with what visual evidence you can gather. An inference stated clearly ("the navigation appears to use approximately 60px height based on visual proportions") is still useful
- Never give up and produce nothing — a document built partly from inference, clearly labeled as such, is far more valuable than silence

## Output

Save the completed document as `DESIGN.md` in the current directory, or wherever the user specifies.

The file should be titled:
```
# Design System Inspiration of [Brand Name]
```

Aim for the depth you would find in a professional design critique: each section should be substantive enough that a developer could implement the design without ever visiting the original site. Write exactly as much as each brand demands — every line should carry a real value, a nuance, or a constraint that shapes how the design feels.

## What Makes a Great DESIGN.md

- **Section 1** opens with a vivid, analytical paragraph that would make a designer nod — it should *feel* like reading a design critique, not a spec sheet. Name the 2-3 signature decisions that define the brand and refer back to them throughout.

- **Section 2** groups colors by semantic role (Primary, Interactive, Text, Surface, Shadow), not just by lightness. Each color entry names the token, the hex/rgba value, and its purpose.

- **Section 3** includes a complete hierarchy table with columns: Role / Font / Size / Weight / Line Height / Letter Spacing / Notes. Follow it with 3-5 written principles that explain *why* the typography works the way it does.

- **Section 4** covers every button variant you can find, not just the primary one — hover, active, disabled, ghost, pill, icon-only. Document what changes on hover, not just the default state.

- **Section 6** (Depth & Elevation) is always a dedicated section, never buried inside component descriptions. It contains: a table of elevation levels (Level 0 through N, with shadow values and use cases), then a "Shadow Philosophy" paragraph explaining the *intent* behind the shadow design — is it warm or cool, sharp or diffuse, on-brand or neutral? Shadows are often the most brand-specific detail in the whole system.

- **Section 8** (Responsive Behavior) is always its own section, separate from Layout. It documents breakpoints as a table, describes how the key components collapse (navigation, grids, hero text sizes), and notes minimum touch target sizes.

- **Section 9** (Agent Prompt Guide) has exactly three parts:
  1. **Quick Color Reference** — a flat list of the 8-10 most-needed values (primary CTA color, background, heading text, body text, link, focus ring, card shadow). Copy-paste ready.
  2. **Example Component Prompts** — 3-5 ready-to-use prompts written as descriptive sentences (not CSS code), specific enough that an AI could build recognizable UI from them alone.
  3. **Iteration Guide** — 6-10 numbered rules that represent the brand's non-negotiable constants. These are the things that, if violated, would make the output instantly feel off-brand.

- **Do's and Don'ts** (Section 7) contains only rules that are specific to *this* brand — if the rule would apply equally to any design system, cut it.

## Reference

See [references/template.md](references/template.md) for the full 9-section output template.

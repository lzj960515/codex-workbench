# DESIGN.md Output Template

Use this template verbatim as the structure for every DESIGN.md you produce. Every section must appear; none may be omitted. Within each section, fill in the actual values discovered from the target website.

---

```markdown
# Design System Inspiration of [Brand Name]

## 1. Visual Theme & Atmosphere

[Opening paragraph: 3–5 sentences describing the overall emotional impression of the site. Name the dominant background color(s), the accent color(s), and the typeface(s). Explain what feeling the design is trying to evoke and what design philosophy drives it. Write this as design criticism, not a spec sheet.]

[Second paragraph (optional but recommended): Go deeper on the most distinctive element — the typeface's optical behavior, the shadow system's brand-alignment, the whitespace philosophy. This is where you explain the *why*.]

**Key Characteristics:**
- [Most distinctive typographic choice — font, weight, tracking, or optical feature]
- [Color system summary — dominant palette + accent color(s)]
- [Most distinctive layout choice — grid, section rhythm, whitespace approach]
- [Most distinctive component pattern — button shape, card style, navigation treatment]
- [Shadow/depth philosophy]
- [Any other 2–3 signature design choices unique to this brand]

## 2. Color Palette & Roles

### Primary
- **[Color Name]** (`#xxxxxx`): [Role description — what it's used for and why this value exists]
- **[Color Name]** (`#xxxxxx`): [Role description]
[Add as many as needed. Group logically: brand colors, background colors, etc.]

### Interactive
- **[Color Name]** (`#xxxxxx`): [Link color, button color, focus ring, hover state — explain each]
[Include hover variants, active states, focus colors]

### Text
- **[Color Name]** (`#xxxxxx` or `rgba(...)`): [Primary text — explain if it's warm/cool, why it's not pure black, etc.]
- **[Color Name]** (`#xxxxxx` or `rgba(...)`): [Secondary text]
- **[Color Name]** (`#xxxxxx` or `rgba(...)`): [Tertiary text, captions, disabled]

### Surface & Background
- **[Color Name]** (`#xxxxxx`): [Page background(s), card surfaces, section backgrounds]
[Include light and dark mode variants if present]

### Status (if present)
- **[Success Color]** (`#xxxxxx`): [When/how used]
- **[Error Color]** (`#xxxxxx`): [When/how used]
- **[Warning Color]** (`#xxxxxx`): [When/how used]

### Borders & Dividers
- **[Color Name]** (`#xxxxxx` or `rgba(...)`): [Border usage]

### Shadows
- **[Shadow Name]** (`rgba(...) [x] [y] [blur] [spread]`): [What it's used for, why this shadow color/tint exists]
[Include all distinct shadow values. Describe multi-layer shadows completely.]

## 3. Typography Rules

### Font Family
- **Primary**: `[Font Name]`, with fallbacks: `[fallback-1, fallback-2, ...]`
- **Secondary/Display** (if distinct): `[Font Name]`, with fallbacks: `[...]`
- **Monospace** (if present): `[Font Name]`, with fallbacks: `[...]`
- **OpenType Features** (if present): `"[feature-code]"` — [what it does and why it matters]

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|------|--------|-------------|----------------|-------|
| [Display Hero] | [Font] | [px (rem)] | [weight] | [ratio (label)] | [px or normal] | [context/use] |
| [Section Heading] | [Font] | [px (rem)] | [weight] | [ratio (label)] | [px or normal] | [context/use] |
| [Sub-heading] | [Font] | [px (rem)] | [weight] | [ratio (label)] | [px or normal] | [context/use] |
| [Body Large] | [Font] | [px (rem)] | [weight] | [ratio (label)] | [px or normal] | [context/use] |
| [Body] | [Font] | [px (rem)] | [weight] | [ratio (label)] | [px or normal] | [context/use] |
| [Caption] | [Font] | [px (rem)] | [weight] | [ratio (label)] | [px or normal] | [context/use] |
| [Button] | [Font] | [px (rem)] | [weight] | [ratio (label)] | [px or normal] | [context/use] |
| [Link] | [Font] | [px (rem)] | [weight] | [ratio (label)] | [px or normal] | [context/use] |
| [Micro] | [Font] | [px (rem)] | [weight] | [ratio (label)] | [px or normal] | [context/use] |
[Add rows for every distinct typographic role you observe. Aim for 8–16 rows.]

### Principles
- **[Principle name]**: [Explain the typographic philosophy — why this weight, why this tracking, why this line-height. This is analysis, not just values.]
- **[Principle name]**: [Another rule the designers clearly followed — e.g., "all headings use negative letter-spacing", "only two weights are used", "font size never goes below 12px in the UI"]
[3–5 principles that explain the *why* behind the numbers]

## 4. Component Stylings

### Buttons

**[Primary Button Name]**
- Background: `[color]`
- Text: `[color]`
- Padding: `[top/bottom] [left/right]`
- Border radius: `[value]`
- Border: `[value]` (or "none")
- Font: `[size]`, weight `[n]`
- Hover: `[what changes]`
- Active/Pressed: `[what changes]`
- Focus: `[outline/ring style]`
- Use: `[when/where this button appears]`

**[Secondary Button / Ghost / Outlined]**
[Same structure as above]

**[Any other button variants — pill, icon-only, destructive, disabled, etc.]**
[Same structure for each]

### Cards & Containers
- Background: `[color]`
- Border: `[value or none]`
- Border radius: `[value]`
- Shadow: `[full shadow value]`
- Padding: `[typical value]`
- Hover state: `[if any]`
- [Any distinctive behavior or treatment]

### Navigation
- Background: `[color — often translucent with backdrop-filter]`
- Height: `[px]`
- Text: `[color, size, weight]`
- Active/hover state: `[description]`
- Mobile treatment: `[how it collapses]`
- [Any distinctive navigation behavior]

### Forms & Inputs (if present)
- Background: `[color]`
- Border: `[value]`
- Border radius: `[value]`
- Text: `[color, size]`
- Placeholder: `[color]`
- Focus ring: `[value]`
- Error state: `[color/treatment]`

### [Distinctive / Signature Components]
[Every brand has 1–3 components that are uniquely theirs. Document them with the same detail level as above. Examples: Apple's Product Hero Module, Airbnb's listing card with the three-layer shadow, Stripe's gradient globe, Linear's dark-mode activity graph.]

**[Component Name]**
- [Structural description: what it contains, how it's laid out]
- [Key style values]
- [How it behaves — hover, animation, responsive]

## 5. Layout Principles

### Spacing System
- Base unit: `[px]`
- Scale: `[list of spacing values — e.g., 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px]`
- [Any notable characteristics — e.g., "granular 1px steps at small sizes", "powers of 2 only"]

### Grid & Container
- Max content width: `[px or description]`
- Column system: `[2-col, 3-col, 12-col grid, or none visible]`
- Hero/hero sections: `[full-bleed vs. contained? How is the hero structured?]`
- [Any notable layout patterns — single-column for hero moments, etc.]

### Whitespace Philosophy
- **[Philosophy name]**: [Describe the *intent* behind how whitespace is used — cinematic breathing room? efficient density? generous luxury?]
- **[Another principle]**: [How sections are separated — by color blocks, by large whitespace gaps, by dividers, etc.]
- **[Another principle]**: [How the density of text relates to the surrounding space]

### Border Radius Scale
- `[value]px`: [Name + context]
- `[value]px`: [Name + context]
[Include all distinct border-radius values in use, from smallest to largest, with context]

## 6. Depth & Elevation

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat (Level 0) | No shadow | [Base content areas] |
| [Level 1] | `[shadow value]` | [What uses this elevation level] |
| [Level 2] | `[shadow value]` | [Higher elevation elements] |
| [Navigation / special] | `[backdrop-filter / special treatment]` | [Nav bar or modals] |
| Focus (Accessibility) | `[outline style]` | [Keyboard focus on all interactive elements] |

**Shadow Philosophy**: [2–3 sentences explaining why the shadows look the way they do — are they warm or cool? Diffuse or sharp? What physical metaphor are they invoking? Are they on-brand (e.g., Stripe's blue-tinted shadows)?]

### Decorative Depth (if present)
[Describe any non-shadow depth techniques — glassmorphism, background blur, layered imagery, gradient overlays, etc.]

## 7. Do's and Don'ts

### Do
- [Specific rule about a color or typography choice]
- [Specific rule about how to use the accent color]
- [Specific rule about spacing or layout]
- [Specific rule about image treatment or photography]
- [Specific rule about a component or animation]
[6–10 rules. Make them specific to THIS brand, not generic design advice.]

### Don't
- [Specific prohibition — reference values where possible]
- [What to avoid with typography]
- [What to avoid with color]
- [What to avoid with layout or whitespace]
- [What would "break" the brand character]
[6–10 rules, matching the Do list in specificity]

## 8. Responsive Behavior

### Breakpoints
| Name | Width | Key Changes |
|------|-------|-------------|
| Mobile | `<[px]` | [What changes at this breakpoint] |
| Tablet | `[px]–[px]` | [Key layout changes] |
| Desktop | `>[px]` | [Full layout description] |
[Add rows for every distinct breakpoint the site uses]

### Touch Targets
- Primary CTAs: [min tap size, padding approach]
- Navigation: [how it adapts for touch]
- [Other touch-sensitive elements]

### Collapsing Strategy
- [How headlines scale down — specific size progressions if observable]
- [How grids collapse — from N column to M column to 1 column]
- [How navigation behaves — hamburger menu, bottom bar, drawer, etc.]
- [How images scale — do they crop? Maintain aspect ratio? Swap sources?]

### Image Behavior
- [How product images behave on resize]
- [Whether images crop or scale proportionally]
- [Lazy loading behavior if observable]

## 9. Agent Prompt Guide

### Quick Color Reference
- Primary CTA: `[color]`
- Page background (light): `[color]`
- Page background (dark): `[color]` (or "N/A if no dark mode")
- Heading text: `[color]`
- Body text: `[color or rgba]`
- Link color: `[color]`
- Focus ring: `[color]`
- Card shadow: `[full shadow value]`
- [Any other frequently-needed values]

### Example Component Prompts

[3–5 copy-paste-ready prompts that an engineer or AI could use to build something in this brand's style. Be specific — include exact values, not descriptions.]

- "Create a hero section with [background color] background. Headline at [size] [font] weight [n], line-height [n], letter-spacing [value], color [color]. [Continue with full component spec...]"
- "Design a [card/button/nav] using [specific values]..."
- "Build the [brand] navigation: [complete spec with colors, height, typography, behavior]..."

### Iteration Guide
[6–10 numbered rules that an AI should internalize to stay on-brand. These are the "non-negotiable" brand constants — things that, if violated, would instantly make the output look off-brand.]

1. [Most important brand constant]
2. [Second most important]
3. [Typography rule]
4. [Color usage rule]
5. [Spacing or layout rule]
6. [Component or interaction rule]
[Continue for all critical constraints]
```

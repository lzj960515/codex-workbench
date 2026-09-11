---
name: improve-codebase-architecture
description: Find and compare worthwhile architectural refactoring opportunities in a codebase or subsystem, guided by change hotspots and concrete design friction. Use when the user asks where to refactor, wants an architecture health scan, or needs before-and-after proposals before choosing a candidate.
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities**: refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

This command is _informed_ by the project's domain model and built on a shared design vocabulary:

- Read [Codebase Design](../architecture-design-review/references/codebase-design.md) for the shared definitions and principles; apply them using the project's existing domain and framework names.
- The project's existing glossary, business map, and decision records give names to good seams and explain deliberate constraints. For business-relevant scope, use `semantic-atlas` to find and confirm the current business model; use current source to verify its leads.

## Process

### 1. Explore

**Scope before you scan: YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If the user named a direction (a module, a subsystem, a pain point), take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots, the files and areas that keep coming up, and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.

Read the owning domain documents and existing decisions in the selected area first. Use `CONTEXT.md` and `docs/adr/` when they are the project's established locations.

Then walk the selected code paths. For a broad scan with substantial independent areas, delegate those areas to sub-agents with a shared scope, the design criteria, and a requirement to cite concrete code. Continue the main investigation and verify returned candidates against callers and existing decisions before combining them. Inspect a small area or a tightly coupled path directly. Explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow**, with an interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** from Codebase Design: if deleting a wrapper makes complexity vanish, it may be redundant; if complexity reappears across callers, it is earning its keep. Preserve useful encapsulation and justify candidates with concrete source evidence. When no candidate offers a supported gain, report that conclusion and finish.

### 2. Present candidates visually

For several candidates or complex comparisons, write an HTML report in the project's temporary-artifact location and show it with the available file or browser viewer. Follow the project's storage convention; otherwise use `tmp/YYYY-MM-DD-architecture-review.html`. For a small comparison, present the same evidence and a before/after diagram directly in the response. Use the user's language.

The HTML report uses **Tailwind via CDN** for layout and styling, and **Mermaid via CDN** for diagrams where a graph/flow/sequence reliably communicates the structure. Mix Mermaid with hand-crafted CSS/SVG visuals: use Mermaid when relationships are graph-shaped (call graphs, dependencies, sequences), and hand-built divs/SVG when you want something more editorial (mass diagrams, cross-sections, collapse animations). Each candidate gets a **before/after visualisation**. Be visual.

For each candidate, render a card with:

- **Files**: which files/modules are involved
- **Problem**: why the current architecture is causing friction
- **Solution**: plain-language description of what would change
- **Benefits**: explained in terms of locality and leverage, and how tests would improve
- **Before / After diagram**: side-by-side, custom-drawn, illustrating the shallowness and the deepening
- **Recommendation strength**: one of `Strong`, `Worth exploring`, `Speculative`, rendered as a badge

End the report with a **Top recommendation** section: which candidate you'd tackle first and why.

**Use the existing domain vocabulary and the Codebase Design definitions.** Name the business concept being improved and link the concrete code symbols that implement it; preserve framework-native names where they identify the actual contract.

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly in the card (e.g. a warning callout: _"contradicts ADR-0007, but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

See [HTML-REPORT.md](HTML-REPORT.md) for the full HTML scaffold, diagram patterns, and styling guidance.

Keep this stage at the problem and proposed responsibility level. Recommend the strongest candidate with reasons, then let the user choose what to explore. When the user has already selected the candidate, continue into its design within that authorization.

### 3. Grilling loop

Once the user picks a candidate, use the `deep-discussion` skill to walk the decision tree with them: constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

As decisions crystallize, use [domain clarification](../deep-discussion/references/domain-modeling.md) to capture their meaning in the owning discussion or decision record:

- **Naming a deepened module after a new domain concept?** Capture the agreed meaning in its owning record; distinguish a design proposal from an implemented business fact.
- **Sharpening a fuzzy term during the conversation?** Record the clarification at the existing owner while its evidence is fresh.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing; skip ephemeral reasons ("not worth it right now") and self-evident ones.
- **Want to explore alternative interfaces?** Use [Design It Twice](../architecture-design-review/references/DESIGN-IT-TWICE.md) when real trade-offs justify multiple designs.

After the analysis, complete the observation and maintenance-disposition steps when the Semantic Atlas workflow was used. Propose canonical updates only when stable business meaning changed; implementation-local restructuring leaves the business map unchanged. Selected architecture work proceeds through `architecture-design-review`, and authorized implementation through `maintainable-implementation`.

# Design It Twice

When a chosen deepening candidate has materially different interface options, use this comparison process. Based on "Design It Twice" (Ousterhout): your first idea is unlikely to be the best.

Uses the vocabulary in [Codebase Design](codebase-design.md): **module**, **interface**, **seam**, **adapter**, **leverage**.

## Process

### 1. Frame the problem space

Before comparing alternatives, write a user-facing explanation of the problem space for the chosen candidate:

- The constraints any new interface would need to satisfy
- The dependencies it would rely on, and which category they fall into (see [DEEPENING.md](DEEPENING.md))
- A rough illustrative code sketch to ground the constraints, not a proposal, just a way to make the constraints concrete

Show this to the user, then proceed to Step 2 within the agreed design scope.

### 2. Develop contrasting designs

Develop **radically different** interfaces that address real trade-offs in the current task. For a consequential design with substantial, independently assessable alternatives, use sub-agents to explore the alternatives in parallel: independent first proposals can expose options a single line of reasoning misses. Choose the number of agents from the useful alternatives, and compare small or tightly coupled choices directly. Follow the user's explicit collaboration request.

Ground each design in the same technical facts (file paths, coupling details, dependency category from [DEEPENING.md](DEEPENING.md), what sits behind the seam). For delegated alternatives, give each sub-agent its own brief with those facts, one distinct design constraint, and the output contract below. Have them develop independent proposals for the lead agent to verify and compare. Choose contrasting constraints relevant to the agreed use cases:

- Minimal interface: "Minimize the interface: aim for 1–3 entry points max. Maximise leverage per entry point."
- Required variation: "Support the distinct use cases and variations already required by the task."
- Common caller: "Optimise for the most common caller: make the default case trivial."
- Cross-service dependency (if applicable): "Design around ports & adapters for cross-seam dependencies."

Use [Codebase Design](codebase-design.md) definitions and the project's existing domain vocabulary consistently across the designs.

For each design, show:

1. Interface (types, methods, params, plus invariants, ordering, error modes)
2. Usage example showing how callers use it
3. What the implementation hides behind the seam
4. Dependency strategy and adapters (see [DEEPENING.md](DEEPENING.md))
5. Trade-offs: where leverage is high, where it's thin

### 3. Present and compare

Present designs sequentially so the user can absorb each one, then compare them in prose. Contrast by **depth** (leverage at the interface), **locality** (where change concentrates), and **seam placement**.

After comparing, give your own recommendation: which design you think is strongest and why. If elements from different designs would combine well, propose a hybrid. Be opinionated: the user wants a strong read, not a menu.

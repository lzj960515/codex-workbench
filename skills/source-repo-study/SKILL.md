---
name: source-repo-study
description: Research a source code repository and turn it into a structured markdown study wiki. Use this skill whenever the user wants to understand a codebase systematically, build architecture notes, create feature maps, trace data flows, explain design rationale, or decompose one subsystem into a reusable set of wiki pages. Prefer this skill when the user wants source code to be taught through design questions, flow derivation, branch analysis, and architecture judgment rather than line-by-line code explanation.
---

# Source Repo Study

## Responsibility

Turn a source repository into a maintained study wiki that explains what the system contains, why its design exists, and how the implementation follows from its constraints.

The reader should be able to move from the architecture overview to one subsystem's concrete read or write path without reconstructing the repository from raw code each time.

## Source and knowledge boundaries

- Treat source code as immutable evidence unless the user also requests implementation changes.
- Use repository terminology discovered in entrypoints, registries, comments, tests, configuration, and user-facing surfaces.
- Cite real files near factual claims.
- Label confirmed behavior, evidence-backed synthesis, uncertainty, feature-gated behavior, and missing implementation distinctly.
- Keep raw sources, maintained wiki pages, and wiki conventions as separate layers.

## Two-layer operating model

Every task has a maintenance layer and one analysis mode.

### Maintenance layer

The maintenance layer keeps knowledge persistent and cumulative:

- preserve the source boundary;
- maintain the wiki as the interpretation layer;
- keep navigation and history current;
- file reusable answers back into the closest existing page;
- evolve structure only when the knowledge develops a stable boundary.

When the user wants a persistent study wiki, use this minimum base and adapt topic folders to the repository:

```text
wiki/
├── README.md
├── index.md
├── log.md
└── topics/
```

`README.md` defines scope and readers, `index.md` provides content-oriented navigation, and `log.md` records material study and revision work chronologically. On an ordinary first repository study, establish this base unless the user requests a narrower answer.

### Analysis layer

Choose the mode that matches the reader's current knowledge. The modes guide analysis rather than form a mechanical gate.

#### Map Mode

Use Map Mode when the repository is unfamiliar, the question is broad, or the current wiki lacks enough orientation for a deep explanation.

Build an objective map of:

- runtime modes and entry surfaces;
- user-visible features;
- background and cross-cutting systems;
- orchestration hubs and major flows;
- subsystem and ownership boundaries.

Create the architecture overview and project-wide feature inventory before deep dives. Give major subsystems their own page cluster when that improves navigation. Keep history and evolution claims limited to available evidence.

#### Study Mode

Use Study Mode for one concrete mechanism, subsystem, chain, branch, or design question after the reader has enough system context.

Develop the explanation through this reasoning path:

1. State the real question or design tension.
2. Establish the simplest workable model.
3. Introduce the constraint that breaks it.
4. Derive the mechanism required by that constraint.
5. Trace the main flow before branches, fallbacks, and state transitions.
6. Explain role ownership, invariants, and tradeoffs.
7. Connect the design back to minimal code evidence.

The explanation should teach the design rather than paraphrase files or functions. Read `references/source-study-pattern.md` before writing a deep Study Mode page.

#### Evolution Mode

Use Evolution Mode when the user asks how the architecture changed and the repository provides evidence such as versioned implementations, migrations, compatibility layers, historical documents, or residual patterns.

Separate verified history from a conceptual derivation used for teaching. When historical evidence remains incomplete, present the confirmed stages and mark the gap instead of inventing a narrative.

## Research workflow

### 1. Read the current knowledge state

Read repository instructions, the existing wiki, relevant conversation context, and the current index and log. Determine what the reader already understands and what the current page must add.

### 2. Trace the implementation top-down

Start with public entrypoints and orchestration hubs, then follow domain logic, persistence, events, background work, and external boundaries. Read tests and configuration when they define runtime behavior more precisely than implementation code.

For stateful or environment-sensitive mechanisms, inspect available runtime artifacts such as persisted records, session files, generated configuration, queue state, feature flags, and actual outputs. Let runtime evidence correct code-level inference.

### 3. Build the required map

Establish enough architecture and feature context for the current question. Reuse the existing map when it is sufficient; update it when new evidence changes subsystem boundaries or major flows.

### 4. Explain the mechanism

Use question-driven prose for causal reasoning. Introduce technical terms after the reader understands the situation they name. Use diagrams for multi-stage flows, branches, caches, state transitions, or ownership handoffs. Use code only to prove a judgment, branch, invariant, or contract.

### 5. Persist the result

Update an existing page for a local follow-up. Create a new page when the work forms a distinct topic, mechanism, or reading path. Update `index.md` after material page changes and append the study or revision to `log.md`.

## Output contract

Each deep explanation should make these questions answerable:

1. What problem does this mechanism solve?
2. Why does the design take this shape?
3. How does it run in the real system?

Use connected prose for the reasoning path and lists for genuinely parallel facts, file indexes, and reference summaries. Keep diagrams purposeful, code snippets small, and source references precise. Match the user's language while preserving source identifiers and established engineering terms.

## Completion criteria

The study wiki is healthy when:

- a new reader can navigate from architecture to the relevant subsystem and flow;
- the feature inventory exists before unrelated deep dives accumulate;
- main paths, meaningful branches, fallbacks, state changes, and ownership are visible;
- claims remain traceable to source or runtime evidence;
- uncertainty stays explicit;
- new knowledge updates the current wiki instead of becoming an isolated chat answer;
- the structure can grow without duplicating the same explanation across pages.

## References

- Read `references/source-study-pattern.md` for the complete Study Mode writing, diagram, code, and language pattern.
- Read `references/wiki-pattern.md` when establishing or repairing the persistent wiki layer.

---
name: maintainable-implementation
description: Choose and implement an appropriately sized solution for ordinary code changes, from mechanical wiring through local behavior and refactoring. Use when deciding whether a change should stay local or reshape responsibilities, choosing between an existing library and hand-written code, splitting methods or classes, reducing patch-like branches, or reviewing business flow, naming, reuse, error boundaries, and implementation quality.
---

# Maintainable Implementation

Turn an agreed requirement or root cause into code that a later reader can understand and extend without reconstructing the whole implementation. Treat the agreed business outcome as the delivery boundary, then make every change required to complete that outcome at its real owner.

This skill corrects two symmetric failure modes: patching behavior into the nearest file without understanding its owner, and expanding a task because additional functions, classes, states, compatibility paths, or workflow stages are possible. The target is the smallest complete boundary that expresses the required business action, owns its lifecycle, and leaves the next reader fewer decisions to reconstruct. A direct local implementation is a successful result when that boundary already exists; a cross-file or upstream refactor is in scope when it restores the owner required by the agreed outcome.

## 1. Establish The Delivery Boundary

Before editing, identify:

- the agreed business outcome, observable behavior, and acceptance evidence;
- the current entry point, owner, callers, and side effects;
- the upstream decisions and downstream effects required to make that outcome correct;
- whether the change is mechanical, local behavior, cross-responsibility behavior, or a new lifecycle;
- the stable invariants and any known Roadmap variation that affects the current responsibility boundary;
- the current code, internal capability, or dependency that already solves part of it;
- adjacent ideas that are useful candidates but are not required by the current outcome.

Every added product behavior, public API, dependency, state, persistence mechanism, configuration, fallback, compatibility path, or abstraction must be justified by the agreed outcome, an existing contract, or an observed risk. It is required when omitting it would make acceptance fail, violate an existing contract, or leave an observed risk unresolved. A useful enhancement, generic capability, or possible future reuse remains a separate follow-up candidate.

Choose reversible internal details autonomously when they preserve the agreed observable behavior, data, security, compatibility range, and runtime lifecycle. Keep unspecified user-visible behavior, support commitments, and lasting operational responsibilities outside the product scope as explicit follow-up candidates. When such a choice is necessary to make the requirement executable and current evidence does not decide it, ask the single question that changes the outcome.

Use current source, tests, product contracts, and the established root cause to prove necessity. Industry best practices and complete-lifecycle questions identify what to inspect; they do not by themselves require another product behavior, persistence mechanism, data operation, compatibility commitment, operational surface, or parallel entry-point change. When the repository or contract is unavailable, state the confirmed behavioral boundary and unresolved evidence instead of inventing a complete component model or acceptance suite.

Derive tests from confirmed behavior, existing invariants, and the proven failure mechanism. Test completeness strengthens evidence for the agreed result; it does not expand the result into additional interactions, platforms, data operations, or lifecycle guarantees.

A mechanical edit is a direct mapping, import, configuration wire, rename, or generated registration whose correctness can be fully understood locally. Implement it in place, review the changed mapping, and run the single lowest-cost check that directly proves it. A test earns its place when it protects project-owned behavior; a test that only repeats a value assignment or constructor argument does not add regression protection.

For a behavioral change, continue through the full workflow. Load [references/decision-guide.md](references/decision-guide.md) when the reuse or refactoring choice is not obvious.

## 2. Read The Complete Flow

1. Start from the public entry or business action, not from the first keyword match.
2. Trace decisions upstream and data, state, and side effects downstream.
3. Read adjacent implementations, tests, types, project instructions, and installed dependencies.
4. Identify the existing responsibility that should own the change.
5. Separate definition-time configuration, instance/call inputs, and runtime state when their lifecycles differ.

Use search to find exact code, then reason from the full lifecycle. A local patch is acceptable when the existing owner naturally contains the behavior; otherwise repair the responsibility boundary that made the patch awkward.

## 3. Decide Reuse Before Writing

Search in this order:

1. an existing domain operation in the same module;
2. an internal shared capability with matching semantics;
3. an already-installed, maintained library;
4. a small project-owned implementation.

Prefer reuse when the existing capability expresses the needed semantics, error model, lifecycle, and performance envelope without a large adaptation layer. Prefer a project-owned implementation when the behavior is small, domain-specific, and easier to understand than the dependency integration.

When adapting a library, keep its native terminology and options at the technical boundary. Wrap it only to express missing domain meaning or to isolate a real provider variation.

## 4. Decide Whether To Refactor

Refactor the relevant boundary when current structure would otherwise create one of these outcomes:

- a new behavior has no natural owner;
- multiple lifecycles or change frequencies are compressed into one abstraction;
- the same state management, scheduling, persistence, or conversion mechanism appears for the third time;
- the main flow requires nested branches, callbacks, or scattered flags to explain one business action;
- a new requirement repeats a known workaround or extends a patch chain;
- the caller must understand infrastructure details to perform a domain action.

Keep the change local when the existing owner is stable, the new behavior fits its vocabulary, and extraction would only rename a few lines without isolating variation or side effects.

Refactor the smallest complete boundary that restores ownership. When choosing the new module interface or where dependencies can vary, read [Codebase Design](../architecture-design-review/references/codebase-design.md). A known next phase can justify a stable responsibility seam, while its future behavior, runtime state, and extension mechanism remain outside the current implementation until required.

Split by responsibility, lifecycle, or independently meaningful failure behavior rather than by the number of code steps. Internal helpers can improve readability without becoming new domain objects, persistent states, Queue jobs, or framework stages.

## 5. Write A Readable Business Flow

1. Keep high-level methods at one abstraction level and order them by business sequence.
2. Name operations from the caller's and domain reader's perspective.
3. Give multi-step expressions and transformations intermediate names that expose meaning.
4. Use inline callbacks for immediately obvious local transformations; use named operations for business rules, side effects, or multi-stage asynchronous work.
5. Put input/output contracts and reusable types in an owned type boundary; keep implementation files focused on behavior.
6. Make each class own one stable, nameable responsibility. Introduce Strategy, Resolver, Repository, Factory, or Coordinator only when that relationship is real and reduces reader decisions.
7. Add comments for business reasons, lifecycle constraints, failure semantics, and non-obvious invariants that naming cannot express.

## 6. Match Error Handling To Evidence

Let errors propagate to the established application, Queue, task, or transport boundary by default.

Use `try/catch` where the code can perform a defined action:

- recover through an established fallback;
- convert an unstable technical error into a stable domain error;
- release a resource;
- add context unavailable to the outer boundary;
- preserve an explicitly accepted partial-success result.

After logging, rethrow when the operation still failed. Add retries, fallback branches, locks, or defensive normalization for observed failures, explicit contracts, or high-impact risks with a credible trigger. Keep the direct path for low-probability scenarios without evidence.

## 7. Review As The Next Reader

Before validation, read the changed path from its entry point and confirm:

- the business action and sequence are visible without opening every helper;
- every class and method has a clear reason to exist;
- code sits with the responsibility that owns it;
- dependencies point from domain behavior toward infrastructure boundaries;
- names describe intent rather than control flow or data structures;
- related changes can extend the existing responsibility without another patch or a speculative extension point;
- every lasting responsibility added by the change traces to the agreed outcome, an existing contract, or an observed risk;
- every new user-visible behavior or support commitment was confirmed or is strictly necessary for acceptance;
- the implementation contains no duplicate library capability, one-off abstraction, swallowed error, or unrelated cleanup.

For a mechanical edit, finish with the direct check selected in step 1 and the final changed-file review. For a behavioral change, use the task's testing Skill and `verification-before-completion` to produce evidence proportional to risk.

## Boundaries

- `deep-discussion` owns whether a proposed product goal should be pursued and when a candidate direction becomes a confirmed decision.
- `architecture-design-review` owns public APIs, shared frameworks, cross-module state models, and major lifecycle redesign.
- `systematic-debugging` owns Bug reproduction and root-cause discovery.
- `test-driven-development` owns regression-test and TDD decisions.
- `code-review` owns independent merge-readiness review.
- `verification-before-completion` owns evidence for the final completion claim.

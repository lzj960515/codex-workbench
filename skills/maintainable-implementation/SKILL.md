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

Every added product behavior, public API, dependency, state, persistence mechanism, configuration, fallback, compatibility path, or abstraction—and every existing one whose responsibility this task replaces—must be justified by the agreed outcome, an existing contract, or an observed risk. It is required when omitting it would make acceptance fail, violate an existing contract, or leave an observed risk unresolved. A useful enhancement, generic capability, or possible future reuse remains a separate follow-up candidate.

先区分功能目标、代理推荐方案和用户已批准的数据变更。按适用的 `AGENTS.md` 核对模型确认边界：必要性证据形成提案依据，明确授权决定哪些模型及其依赖实现可以开始。已批准范围直接执行；缺少确认时先交付调查充分的具体方案，并继续不依赖该决策的工作。在已确认行为、数据契约、安全、兼容范围和生命周期内，自主选择可逆实现细节；新增用户行为、支持承诺和长期运行责任仍以已确认范围为准。

Use current source, tests, product contracts, and the established root cause to prove necessity. Industry best practices and complete-lifecycle questions identify what to inspect; they do not by themselves require another product behavior, persistence mechanism, data operation, compatibility commitment, operational surface, or parallel entry-point change. When the repository or contract is unavailable, state the confirmed behavioral boundary and unresolved evidence instead of inventing a complete component model or acceptance suite.

Derive tests from confirmed behavior, existing invariants, and the proven failure mechanism. Test completeness strengthens evidence for the agreed result; it does not expand the result into additional interactions, platforms, data operations, or lifecycle guarantees.

A mechanical edit is a direct mapping, import, configuration wire, rename, or generated registration whose correctness can be fully understood locally. Implement it in place, review the changed mapping, and run the single lowest-cost check that directly proves it. A test earns its place when it protects project-owned behavior; a test that only repeats a value assignment or constructor argument does not add regression protection.

For a behavioral change, continue through the full workflow. Load [references/decision-guide.md](references/decision-guide.md) when the reuse or refactoring choice is not obvious.

## 2. Read The Complete Flow

1. Start from the public entry or business action, not from the first keyword match.
2. Trace decisions upstream and data, state, and side effects downstream.
3. 阅读同类实现与历史处理、测试、类型、项目约定及已有依赖，按当前影响追踪现有记录的使用方，包括相关界面和恢复流程。
4. 从已确认结果还原业务顺序，先验证现有模型的复用方案。具体名称或分类不同只是调查线索；新增独立来源或平行流程的依据，是现有契约无法承载的真实行为差异。
5. Identify the responsibility that should own the change; separate definition-time configuration, instance/call inputs, and runtime state when their lifecycles differ.
6. When a design choice depends on actual usage, cost, volume, or freshness, inspect bounded runtime evidence as well as callers. Distinguish a configured ceiling from requests sent, results returned, and useful outcomes. Keep unverified coverage or savings claims unresolved.

Use search to find exact code, then reason from the full lifecycle. A local patch is acceptable when the existing owner naturally contains the behavior; otherwise repair the responsibility boundary that made the patch awkward.

## 3. Decide Reuse Before Writing

Search in this order:

1. an existing domain operation in the same module;
2. an internal shared capability with matching semantics;
3. an already-installed, maintained library;
4. a small project-owned implementation.

先判断现有业务模型能否通过原地扩展完成目标，再决定库与实现方式。比较新增概念、持久状态、分支、迁移、使用方改动和长期维护成本；复用会破坏现有语义或约束时，给出具体场景和证据后再推荐新模型。局部小规则适合留在原职责内，必要的新职责按授权范围实现。

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

For a rewrite or responsibility replacement, decide what remains, changes in place, disappears, and temporarily coexists. Implement the target flow in its owner and switch its actual callers; retire the superseded branches, forwarding layers, registrations, configuration, and redundant tests or documentation within that boundary. Preserve useful platform mappings as functions or adapters according to their real responsibility. Update historical internal names to describe current behavior; preserve wire names when their consumers still require them.

Treat an ongoing supported protocol or public contract as part of the target model. For a path retained temporarily during this replacement, identify its consumers, deployed version combinations, replayable data, or rollback need, and record its owner and concrete exit condition in existing task notes or release documentation. Before retiring an entry point, check its registration, supported callers and relevant in-flight work. Repository-local zero references, an empty queue, or a quiet observation window each supplies only part of that evidence. Evidence gathering does not authorize production changes or data deletion.

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

Before validation, compare the complete task diff with its original baseline, then read the resulting flow from its entry point. For a rewrite, ask how the same agreed behavior would be expressed without having to keep the first implementation's structure. Use that comparison to simplify the candidate, keeping sound existing design; a second implementation or a net line reduction is not a completion requirement. Confirm:

- the business action and sequence are visible without opening every helper;
- every class and method has a clear reason to exist;
- code sits with the responsibility that owns it;
- dependencies point from domain behavior toward infrastructure boundaries;
- names describe intent rather than control flow or data structures;
- related changes can extend the existing responsibility without another patch or a speculative extension point;
- newly added responsibilities and retained transition paths have current evidence; the replaced responsibility has one clear owner, and superseded paths have exited or have a justified temporary lifetime;
- every new user-visible behavior or support commitment was confirmed or is strictly necessary for acceptance;
- 数据模型选择有现有方案的比较依据，实际变更符合已批准范围，受影响的记录读取、展示与恢复仍遵守原契约；
- the implementation contains no duplicate library capability, one-off abstraction, swallowed error, or unrelated cleanup.

When the user corrects the approach, remove or revise artifacts based on the rejected assumption across the full task diff. Stop once the agreed behavior and replacement are complete; keep unrelated debt outside the task.

For a mechanical edit, finish with the direct check selected in step 1 and the final changed-file review. For a behavioral change, use the task's testing Skill and `verification-before-completion` to produce evidence proportional to risk.

## Boundaries

- `deep-discussion` owns whether a proposed product goal should be pursued and when a candidate direction becomes a confirmed decision.
- `architecture-design-review` owns public APIs, shared frameworks, cross-module state models, and major lifecycle redesign.
- `systematic-debugging` owns Bug reproduction and root-cause discovery.
- `test-driven-development` owns regression-test and TDD decisions.
- `code-review` owns independent merge-readiness review.
- `verification-before-completion` owns evidence for the final completion claim.

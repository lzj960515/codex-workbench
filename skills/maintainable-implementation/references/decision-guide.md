# Implementation Decision Guide

Use this guide when the correct reuse, refactoring, or abstraction choice is not obvious from the local code.

## Change Classification

| Class | Evidence | Implementation response |
| --- | --- | --- |
| Mechanical | One-to-one mapping, no business branch, no new lifecycle | Make the direct local change and verify it directly |
| Local behavior | Existing owner and invariant are clear | Extend the owner with a named operation and focused regression protection |
| Responsibility change | Behavior spans owners or leaks infrastructure into callers | Refactor the smallest complete boundary before adding behavior |
| Lifecycle change | New state, scheduling, persistence, concurrency, or retry semantics | Model states and ownership explicitly; use architecture review when shared/public |

## Reuse Decision

Evaluate a candidate capability across these questions:

1. Does its semantic contract match the business need, including edge cases?
2. Does its error and cancellation model fit the caller's lifecycle?
3. Is it already owned, maintained, and used in the project?
4. Does it avoid adding another state store, scheduler, cache, parser, retry loop, or concurrency model?
5. Is the adaptation layer smaller and clearer than a domain implementation?
6. Can a future reader discover and understand the dependency from current project context?

### Prefer Existing Capability

- The project already uses it for the same responsibility.
- It owns difficult correctness concerns such as parsing, protocol compliance, concurrency, retries, security, caching, or serialization.
- Its API expresses the needed operation without exposing unrelated machinery.
- Its failure semantics can remain visible to the caller.

### Prefer A Small Project Implementation

- The behavior is a short domain rule or transformation.
- A dependency would require substantial adaptation, configuration, or new runtime ownership.
- The existing library solves a different semantic problem despite similar names.
- Keeping the rule beside its domain owner makes it easier to test and change.

Avoid copying a library's internal algorithm. Either use the capability at its supported boundary or implement the small domain requirement directly.

## Refactoring Decision

### Strong Signals

- A third implementation of the same lifecycle mechanism appears.
- A class changes for unrelated business reasons.
- Callers must coordinate several low-level objects in the same order.
- Runtime state is stored in definition-time configuration or shared singletons.
- Error recovery and the happy path are interleaved across the whole method.
- Each new requirement adds another flag to select a hidden mode.
- A method mixes policy decisions, persistence, data conversion, and external side effects.

### Keep It Local

- One owner already contains the invariant.
- The new branch is a real domain case with a clear name.
- Extraction would create a pass-through class or single-use interface.
- No separate lifecycle, state, provider, or future variation is introduced.

### Select The Refactoring Scope

1. Name the missing or overloaded responsibility.
2. Identify its inputs, outputs, state, failures, and owner.
3. Move the complete responsibility, including relevant tests and error semantics.
4. Keep public callers stable when the task does not require an API change.
5. Stop once the new behavior fits naturally; leave unrelated debt as a separate item.

## Choose The Execution Scale

Use the smallest execution boundary that owns the required behavior:

| Boundary | Use when | What remains shared |
| --- | --- | --- |
| Local expression or helper | A calculation or transformation needs a readable name | Caller lifecycle, memory, failure, and retry |
| Class or domain service | A stable responsibility owns rules, dependencies, or meaningful variation | Application process and invocation lifecycle |
| Queue job, Pipeline Node, or workflow stage | Work needs independent scheduling, retry, concurrency, rate limiting, recovery, or operational visibility | Only durable references and explicit business contracts |

A code sequence does not need a larger runtime boundary merely because its steps can be named separately. A distributed boundary earns its cost when independent execution is part of the required behavior and the input and completion result can be represented durably. When a unit needs numerous internal checkpoints or resume flags, first check whether it contains several independently meaningful business actions; when many tiny units only pass intermediate data, first check whether they are one business attempt that belongs in a single runtime boundary.

## Abstraction Choice

| Need | Useful shape |
| --- | --- |
| Several interchangeable algorithms with one caller contract | Strategy |
| Choose an owner or handler from input/domain state | Resolver |
| Isolate a real persistence contract across implementations | Repository |
| Construct variants with validated creation rules | Factory |
| Coordinate a multi-part lifecycle without owning each part's internals | Coordinator |
| Share a pure, stable calculation | Named function/module |

The pattern name follows the real collaboration. Do not introduce an interface, base class, or builder before there is a meaningful variation or lifecycle to isolate.

## Readable Main Flow

A high-level method should expose business sequence:

```typescript
async approveApplication(applicationId: string, actor: Actor) {
  const application = await this.loadApplicationForApproval(applicationId);
  this.assertActorCanApprove(application, actor);
  application.approve(actor.id);
  await application.save();
  await this.publishApproval(application);
  return application;
}
```

The example is useful because each line represents one business step. The lower-level methods should own the actual authorization, persistence, or event details instead of merely renaming single expressions.

## Defensive Code Review

For every fallback, catch, retry, optional chain, default value, or ignored error, ask:

- Which observed failure or explicit contract requires it?
- What result does the caller see when it activates?
- Could it hide corrupted state or turn failure into false success?
- Which boundary owns logging and retry?
- Is there a focused test for the accepted recovery semantics?

Remove protection that has no defined trigger or outcome. Preserve concise validation for real untrusted input and explicit external boundaries.

## Final Reader Check

- Can the entry method be summarized in one business sentence?
- Can each class be named by one responsibility?
- Does each dependency serve that responsibility?
- Are domain types and names more prominent than framework details?
- Are side effects and failure points visible?
- Is shared behavior truly shared rather than merely similar?
- Would the next likely change extend an existing boundary instead of adding another patch?

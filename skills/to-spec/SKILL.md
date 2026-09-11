---
name: to-spec
description: "Create or update a formal implementation spec from an existing discussion, decision map, or agreed requirements when the work needs a durable specification for implementation, handoff, or acceptance."
---

This skill takes the current conversation context and codebase understanding and produces a spec. Synthesize established decisions from the conversation and linked records, carrying their scope and evidence into the specification.

Follow the project's document ownership conventions. Update the existing specification for this topic; when a new one is needed, use the established specification location, or `tmp/YYYY-MM-DD-<topic>-spec.md` if none exists. The spec owns the deliverable contract; link decision records for their rationale and evidence. Record the source links and current status with the document, keeping drafts distinct from confirmed specifications.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching. When working from a decision map, read the linked decisions relevant to this spec in full. Separate confirmed decisions and existing contracts from proposals, assumptions, and unresolved questions. Record gaps under Further Notes; use the `deep-discussion` skill for a missing decision that materially changes the contract, while preserving the established parts of the draft.

2. Sketch out the seams at which you're going to test the feature: the public boundaries where its behavior can be observed. Reuse established testing decisions and prefer existing seams that cover the required behavior and failure cases. Choose additional seams when needed for that coverage. Record the observable acceptance criteria and relevant existing tests; make routine testing choices from repository evidence.

3. Write or update the spec using the template below. Check that every requirement follows from a confirmed decision or existing contract, and that the acceptance criteria demonstrate those requirements. Keep the status as draft while contract-changing decisions remain unresolved. Save the document and report its location, scope, and remaining decisions. Publishing to a tracker, creating tasks, or implementing the spec follows the user's authorization and the corresponding workflow.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A numbered list of user stories covering the confirmed behavior. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

Give each story observable acceptance criteria, including required failure behavior. Keep proposed additions under Further Notes until they are decided.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Describe implementation decisions through module responsibilities, interfaces, and contracts; keep source locations in evidence links, where they can be rechecked as the code changes.

If a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature, including unresolved decisions, working assumptions, and proposals, each with its status and what would settle it.

</spec-template>

---
name: to-spec
description: "Create or update a formal implementation spec from an existing discussion, decision map, or agreed requirements when the work needs a durable specification for implementation, handoff, or acceptance."
---

This skill takes the current conversation context and codebase understanding and produces a spec. Synthesize established decisions from the conversation and linked records, carrying their scope and evidence into the specification.

Follow the project's document ownership conventions. Update the existing specification for this topic; when a new one is needed, use the established specification location, or `tmp/YYYY-MM-DD-<topic>-spec.md` if none exists. The spec owns the deliverable contract; link decision records for their rationale and evidence. Record the source links and current status with the document, keeping drafts distinct from confirmed specifications.

## Process

1. 复用已有讨论、源码调查和决策记录，补足影响本次规格的证据。涉及业务流程或模型选择时，核实现有入口、写入、处理和使用方，按影响追踪展示、恢复及同类历史做法。沿用领域术语与相关 ADR；来自决策地图的事项读取完整依据。分别记录用户确认的目标、既有契约、代理推荐和未决事项，按适用的 `AGENTS.md` 核对数据模型的具体批准范围；缺口保留在 Further Notes，需要共同决定时使用 `deep-discussion`。

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

先说明现有业务怎样完成相关动作，以及复用方案能否满足本次目标，再记录推荐实现及依据。每项区分既有契约、用户已确认决策和待确认提案，确认状态来自用户的实际决定。内容可以包括：

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- 数据模型变更：具体表、字段或持久化结构的前后差异；复用现有结构的具体不足；受影响的使用方；确认状态与对应决定。保持结构时简要说明复用路径即可。
- API contracts
- Specific interactions

Describe implementation decisions through module responsibilities, interfaces, and contracts; keep source locations in evidence links, where they can be rechecked as the code changes.

原型片段能够更准确表达状态机、schema 或类型时，保留决定相关的部分并注明来源和确认状态。原型或测试中的结构仍按原决策状态记录，形成演示不代表获得实施授权。

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

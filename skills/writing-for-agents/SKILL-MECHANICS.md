# Skill mechanics

The skill-specific branch of [`writing-for-agents`](SKILL.md): what changes when the document is a skill (frontmatter, the invocation choice, and router skills). Everything else about writing it is the universal reference in `SKILL.md`.

## Invocation

Two choices, trading the two loads:

- A **model-invoked** skill keeps a `description`, so the agent can fire it autonomously, and other skills can reach it. You can still type its name: model-invocation always _includes_ user reach; a description only ever adds agent discovery, never removes the human's. The description is the skill's top-level context pointer, forced to stay loaded at all times: permanent context load in exchange for discoverability. A model-invoked skill whose content is all reference is also one home for shared reference: another skill can invoke it, so reference needed by several skills lives in one place. Write a model-facing description carrying the trigger branches (the pointer-writing rules in `SKILL.md` apply in full). In Claude, omit `disable-model-invocation` or set it to `false`; in Codex, keep `policy.allow_implicit_invocation` in `agents/openai.yaml` enabled (it defaults to `true`). Check discovery in the target product.
- A **user-invoked** skill is reserved for a workflow the user explicitly wants to start by name. It trades automatic discovery for the human remembering the entry. In Claude, `disable-model-invocation: true` controls this choice; in Codex, use `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. These settings control selection in their respective products; referenced files remain readable, so invocation settings are not file-access boundaries.

Use model-invocation by default in this personal Skill system, while keeping explicit invocation available. Choose user-invocation when the user has explicitly requested that workflow; judge context cost against reliable natural-language discovery.

Shared reference can live in a plain file with clear pointers from each consumer. Give it a separate skill entry when it also serves an independently useful user task; keep a single authoritative source in either arrangement.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a model-invoked skill when you have a distinct leading word that should trigger it on its own (a trigger word you actually use in your prompts), or another skill must reach it. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

A **router skill** can help a user who explicitly chooses a manual workflow remember several entries and when to use them. This personal system uses natural-language discovery by default: put the relevant trigger branches in each skill's description. Add a manual router only for an explicitly requested manual workflow, and verify its invocation behavior in the target product.

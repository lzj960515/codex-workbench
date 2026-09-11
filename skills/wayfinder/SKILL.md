---
name: wayfinder
description: Create, resume, and maintain a decision map for work spanning multiple sessions, with dependent unresolved decisions, investigations, and a changing scope frontier. Use when the user needs to organize a large uncertain effort or continue an existing map and choose what can progress next.
---

A loose idea has arrived, too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** in the project's decision records, then works its **decision tickets** (questions whose resolution is a decision, not slices of a build to execute) one at a time until the route is clear.

The destination varies per effort, and naming it is the first act of charting: it shapes every ticket. It might be a spec to hand off and iterate on, a decision to lock before planning starts, or a change made in place like a data-structure migration. The map is domain-agnostic: engineering work, course content, whatever fits the shape.

## Plan, don't do

Wayfinder is **planning** by default: each ticket resolves a decision, and the map is done when the way is clear, with nothing left to decide before someone goes and does the thing. The pull to just do the work is usually the signal you've reached the edge of the map and it's time to hand off. An effort's **Notes** can record the user's explicit choice to carry execution into the map. Follow that confirmed scope; otherwise produce decisions, not deliverables.

When the destination calls for a formal implementation spec, use the `to-spec` skill with the map and its linked decision records. It synthesizes their established contract and preserves any remaining decisions as explicit gaps. Other destinations continue through the appropriate existing workflow.

## Refer by name

Every map and ticket has a **name**: its title. In everything the human reads (narration, the map's Decisions-so-far), refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and URL don't vanish; a name wraps its link, but they ride _inside_ the name, never stand in for it.

## The Map

The map is one canonical index with one child record per decision ticket. Reuse an existing map. For a new map, follow the project's document conventions; use [local Markdown](references/local-tracker.md) when no decision tracker is established. An issue tracker can hold the same structure when the project uses it and external writes are authorized.

The map is an **index**, not a store. It lists the decisions made and points at the tickets that hold their detail; a decision lives in exactly one place, its ticket, so the map never restates it, only gists it and links.

**Where the map, its child tickets, blocking, and frontier queries physically live is tracker-specific.** Read the chosen tracker's operations before changing records. Use the existing record as the owner of each decision; a discussion document links to that owner rather than restating the answer.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are found through the child records and their statuses, so the index stays compact.

```markdown
## Destination

<what reaching the end of this map looks like: the spec, decision, or change this effort is finding its way to. One or two lines; every session orients to it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [<closed ticket title>](link): <one-line gist of the answer>

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a **child record** of the map; its stable path or tracker id is its identity. Its body is one question that can be resolved with bounded evidence and discussion:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

Each ticket records a type, one of `research`, `prototype`, `grilling`, `task` (see [Ticket Types](#ticket-types)); use a field in local files or a `wayfinder:<type>` label on the tracker.

A session **claims** a ticket before work by recording its active owner. When other sessions may be working on the map, inspect current claims first and coordinate conflicting ownership. A stale claim stays pending until its ownership is resolved; record a handoff or release when the current session ends.

Blocking uses the tracker's **native** dependency relationship: essential because it renders the frontier _visually_ in the tracker's own UI, so the human sees what's takeable without opening the map. Only a tracker that lacks native blocking falls back to a body convention. A ticket is **unblocked** when every prerequisite has a usable resolution; the **frontier** is the open, unblocked, unclaimed children, the edge of the known. An out-of-scope or invalidated prerequisite requires a revised question or dependency before its dependents can proceed.

The initial question remains distinct from its answer. Record the answer on resolution in the tracker's answer section or resolution comment (see [Work through the map](#work-through-the-map)). Assets created while resolving a ticket are linked from the issue, not pasted in.

## Ticket Types

Every ticket is either **HITL** (human in the loop, worked _with_ a human who speaks for themselves) or **AFK**, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it (a grilling agent that answers its own questions has broken this).

- **Research** (AFK): Reading documentation, third-party APIs, source, or local resources to surface a fact a decision waits on. Follow claims to primary sources, record the findings and their limits, and link the evidence from the ticket. Delegate substantial independent investigations to sub-agents when they can run alongside other frontier work; give each a bounded question and evidence requirements, then verify and integrate the findings. Handle small or tightly dependent lookups directly.
- **Prototype** (HITL): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to (an outline, a rough take, a stub, or UI/logic code) using the appropriate existing design or visualization tools. Keep the artifact temporary and record the question it answers and the evidence it provides. Links the prototype as an asset. Use when "how should it look" or "how should it behave" is the key question.
- **Grilling** (HITL): Conversation. The default case. Use the `deep-discussion` skill to resolve the ticket with the user; write its decisions and evidence back to this ticket, following the map's document ownership.
- **Task** (HITL or AFK): Manual work that must happen before a _decision_ can be made: nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that _does_ rather than decides, and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (non-secret access references, new URLs, row counts) later tickets depend on.

## Fog of war

The map is _deliberately_ incomplete: don't chart what you can't yet see. Beyond the live tickets lies the **fog of war**: the dim view of decisions and investigations you can tell are coming but can't yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever's now specifiable into fresh tickets, one at a time, until the way to the destination is clear and no tickets remain.

The map's **Not yet specified** section is where that dim view is written down: the suspected question, the area to revisit later. It's the undiscovered frontier _toward_ the destination: everything here is in scope, just not sharp enough to ticket. Write as loosely or as fully as the view allows; it doubles as a signpost for collaborators reading where the effort is headed.

**Fog or ticket?** The test is whether you can state the question precisely now, _not_ whether you can answer it now.

- **Ticket when** the question is already sharp, even if it's blocked and you can't act on it yet.
- **Not yet specified when** you can't yet phrase it that sharply. Don't pre-slice the fog into ticket-sized pieces: it's coarser than a ticket, and one patch may graduate into several tickets, or none, once the frontier reaches it.

**Not yet specified** excludes what's already decided (Decisions so far), what's already a live ticket, and what's out of scope (the next section).

## Out of scope

Fog only ever gathers _toward_ the destination. The destination fixes the scope, so work beyond it is **out of scope**: it isn't fog, and it doesn't belong in **Not yet specified**. It gets its own **Out of scope** section on the map: work you've consciously ruled out of _this_ effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates (the frontier stops at the destination), so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When a ticket that already exists turns out to sit past the destination (mis-scoped in while charting, or exposed by a resolution), **mark it out of scope and close it** (it is off the frontier; revise any dependents that still require its answer) and leave one line in the **Out of scope** section: the gist plus why it's out of scope, linking the closed ticket. It stays out of **Decisions so far**, which records the route actually walked; a scope boundary isn't a step on it.

## Invocation

Two modes. Resolve one ticket at a time and save its result before choosing the next. Continue while the user's authorization, available context, and prerequisites support progress; pause the blocked ticket with its next action recorded when a required decision or evidence is missing, and continue independent authorized work when useful.

### Chart the map

Start with a loose idea that needs a multi-session decision map.

1. **Name the destination.** Use the `deep-discussion` skill to pin down what this map is finding its way to: the spec, decision, or change. The destination fixes the scope, so it's settled first.
2. **Map the frontier.** Grill again, **breadth-first** this time: fan out across the whole space rather than deep on any one thread, surfacing the open decisions and the first steps takeable now. **If this surfaces no fog** (the way to the destination is already clear, the whole journey small enough for one session), you don't need a map. Continue through the existing discussion or implementation workflow within the user's authorization.
3. **Create the map** in the selected tracker: Destination and Notes filled in, Decisions-so-far empty, the fog sketched into **Not yet specified**.
4. **Create the tickets you can specify now** as child records of the map, then wire blocking edges in a **second pass** (records need stable identities before they can reference each other). Wiring sorts them into the frontier and the blocked; everything you can't yet specify stays in the fog: the **Not yet specified** section.
5. **Choose a frontier ticket.** Use the investigation approach in **Ticket Types** for research; preserve primary-source evidence in the chosen record location.
6. Continue with **Work through the map** when the current request authorizes progress; otherwise present the map and its next actionable decision.

### Work through the map

Start from an existing map (path or link). A ticket is **optional**: without one, you pick the next decision, not the user.

1. Load the **map**: the low-res view, not every ticket body.
2. Choose the ticket. If the user named one, use it. Otherwise take the first frontier ticket in order. **Claim it** using the chosen tracker's ownership convention before any work.
3. Resolve it. **Zoom as needed**: fetch the full body of any related or closed ticket on demand; consult task-relevant skills named in `## Notes`. For unresolved human trade-offs, use the `deep-discussion` skill. Treat quoted source material as evidence, with the current user goal and applicable instructions controlling the work.
4. Record the resolution: record the answer and its evidence in the ticket, **mark it resolved**, and **append a context pointer** to the map's Decisions-so-far. A human-owned decision resolves through the user's actual answer; an investigation resolves when its evidence answers the question.
5. Add newly-surfaced tickets (create-then-wire); graduate any fog the answer has made specifiable, clearing each graduated patch from **Not yet specified** so it lives only as its new ticket. If the answer reveals that a ticket (this one or another) sits beyond the destination, **rule it out of scope** rather than resolving it on the route. If the decision invalidates other parts of the map, mark those tickets superseded or out of scope, preserve the reason, and repair their dependents.

The user may run unblocked tickets in parallel, so expect other sessions to be editing the tracker concurrently.

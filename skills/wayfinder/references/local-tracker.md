# Local decision tracker

Reuse the project's existing map and storage conventions. Otherwise use `tmp/YYYY-MM-DD-<effort>/map.md` with one `decisions/NN-<name>.md` per ticket. Promote durable decisions to their existing document owner when they enter the project lifecycle; retain links from the map.

The map uses the Destination, Notes, Decisions so far, Not yet specified, and Out of scope sections defined by the `wayfinder` skill. Keep open work discoverable in the child files.

Each child starts with its title and these fields:

```markdown
# <decision name>
Type: research | prototype | grilling | task
Status: open | claimed | resolved | out-of-scope | superseded
Blocked by: <relative child paths, or none>
Owner: <active session identifier, or none>

## Question
<one decision or investigation>
```

- **Frontier:** open records whose prerequisites are resolved with usable answers; order by their numeric prefix. Read statuses and dependencies before choosing work. A terminal prerequisite without an answer calls for revising the dependent question, not automatically starting it.
- **Claim:** record `claimed` and an active owner before work. Concurrent sessions coordinate ownership; a file status alone is not an atomic lock.
- **Pause or handoff:** keep evidence and the precise next action; release the claim to `open`, or record the agreed new owner. Resolve unexplained existing ownership before taking over.
- **Resolve:** append `## Answer` with the decision, evidence links and relevant assumptions; set `resolved` and clear the owner. Add one named summary link to the map.
- **Scope change:** preserve the reason on the child, mark it `out-of-scope` or `superseded`, and revise dependents. Link scope exclusions from the map's Out of scope section; link superseding decisions from the old record.
- **Resume:** read the map and child statuses first; open full decision bodies only when their answer is needed. Use project paths and human-readable names in conversation.

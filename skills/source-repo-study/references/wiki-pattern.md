# Wiki Pattern

This reference captures the general pattern behind using an LLM to maintain a persistent markdown wiki rather than answering from raw documents ad hoc.

Core idea:

- raw sources stay immutable
- the wiki is the maintained interpretation layer
- the schema defines structure and workflow

Core operations:

- ingest new sources into the wiki
- answer by reading the wiki
- file reusable answers back into the wiki
- lint the wiki for contradictions, staleness, orphan pages, missing links, and gaps

Special navigation files:

- `index.md` for content-oriented navigation
- `log.md` for chronological history

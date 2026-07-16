# PAA Graph Knowledge Base — Project Status

**Date:** 2026-07-16
**Branch:** curation-ui

**Overall goal:** Build a graph-based knowledge base (CIDOC-CRM / Linked Art, in GraphDB) linking Perseus Art & Archaeology objects to Getty and Harvard Art Museums (HAM) records, with a path toward a curation UI for cleaning up legacy bibliographic/descriptive text.

## What's done (as of the last real work session, 2025-12-06)

1. **Getty integration** — `src/paa_graph_kb/utils/getty_reconciliation.py` + `fetch_getty_data.py` linked 120/125 Perseus objects to Getty Linked Art records (96%) via `owl:sameAs`. Had to pad BC-date years to 4 digits (`fix_getty_dates.py`) to satisfy XSD/rdflib.
2. **HAM integration** — `fetch_ham_data.py` + `ham_staging_from_cache.py` produced `ham_linked_art.ttl` (634k triples) and 118 Perseus↔HAM links.
3. **Bibliography dual-mode fix** — discovered 99.7% of Perseus bibliography fields are raw HTML/TEI. `perseus_staging_loader.py` now emits both a **Clean** (stripped) version → `crm:P190` for display, and a **Raw** version → `rdf:value`/`rdf:HTML` for future curation.
4. **Demo queries** in `queries/demos/` (01–04) show Getty dimensions, cross-dataset Perseus/Getty querying, and the clean/raw bibliography split.
5. Utility scripts consolidated into `src/paa_graph_kb/utils/`; Makefile has `graphdb-all`, `getty-bundle`, `graphdb-load-getty` targets.

## What's new since then (this branch, `curation-ui`, committed as `9aea0f6`)

The curation UI architecture had been sketched out but not committed until this session:

- `docs/curation_architecture_analysis.md` (+ `.org` twin) — the design doc. Key decisions:
  - Move from document-centric (editing blobs) to **graph-centric**, using **W3C Web Annotations** (`oa:Annotation`) layered on top of stable object nodes.
  - Three workflows: **Splitter** (explode HTML blobs into atomic citations/notes), **Resolver** (link citation strings to authority entities + external digital editions like HathiTrust), **Editor** (clean prose, tag entities inline, e.g. link "Herakles" to an AAT concept).
  - Storage: annotations as individual `.ttl` files under `data/annotations/`, git-versioned, with GraphDB as a queryable index synced from disk.
  - Planned stack: FastAPI backend, React frontend.
- `src/paa_graph_kb/utils/prototype_biblio_splitter.py` — a working prototype (Phase 1, "completed" per the doc) that heuristically splits a sample dirty bibliography blob into separate `oa:Annotation` citations using regex.

## Not yet started

- **Phase 2** (FastAPI curation backend) and **Phase 3** (React curation UI) haven't begun — the doc describes them but no code exists yet.
- Outstanding from the 2025-12-06 session: full `make graphdb-all` load/verification against a live GraphDB instance hadn't been confirmed done, and HAM's missing dimensions were flagged as unexplained.

## Immediate next step

Per prior notes, the logical pickup point is **Phase 2** — building the FastAPI layer with endpoints like `GET /object/{id}/annotations` and `POST /annotation` — or, if a sanity check is wanted first, rerunning `make graphdb-all` against GraphDB to confirm the data foundation is still intact before building the UI on top of it.

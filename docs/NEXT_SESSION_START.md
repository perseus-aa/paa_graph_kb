# Context Restoration for Next Session

**Project:** PAA Graph Knowledge Base
**Date:** 2025-12-06
**State:** Feature Complete (Data Loading & Reconciliation)

## Core State
- **Perseus Data:**
    - Staging: `data/staging/perseus_objects.ttl` (Regenerated with `stg:sourcesUsedClean`).
    - Linked Art: `data/perseus/perseus_linked_art.ttl` (138k triples).
    - **Key Feature:** Dual-mode text (Clean/Raw) for bibliographies implemented.
- **Getty Data:**
    - Cache: `data/getty/objects/*.json` (Dates padded to 4 digits).
    - Bundle: `data/staging/getty_bundle.json`.
    - Links: `data/reconciliation/perseus_getty_links.ttl` (120 links).
- **HAM Data:**
    - Cache: `data/ham/objects/*.json`.
    - Staging: `data/staging/ham_staging.ttl`.
    - Linked Art: `data/ham/ham_linked_art.ttl` (634k triples).
    - Links: `data/reconciliation/perseus_ham_links.ttl` (118 links).

## Environment
- **Scripts:** Utility scripts moved to `src/paa_graph_kb/utils/`.
- **Makefile:** Updated with `graphdb-load-getty`, `getty-bundle`, `graphdb-all`.
- **Demo Queries:** `queries/demos/` contains 4 verification queries.

## Critical "Gotchas" & Decisions
1.  **BC Dates:** Getty JSON-LD contains negative years (e.g. `-0500-01-01`). Python's `datetime` (and `rdflib`) logs warnings/errors.
    - *Resolution:* We padded years to 4 digits in cache (`fix_getty_dates.py`). We suppress warnings in loader scripts. Data is valid XSD, just not Python-friendly.
2.  **Bibliography:** `23_construct_perseus_sources.rq` maps `stg:sourcesUsedClean` to `P190` (display) and `stg:sourcesUsed` to `rdf:value` (curation).
3.  **Construct Logic:** `23_construct_perseus_sources.rq` has `OPTIONAL` block removed to workaround `rdflib` binding scoping issues.

## Immediate Action Items
1.  **Run Full Load:** Execute `make graphdb-all` to load everything into a fresh GraphDB repository.
2.  **Verify Loading:** Run queries in `queries/demos/` against the live GraphDB instance.
3.  **Curation UI:** Begin planning the UI for editing the `rdf:HTML` values in bibliographies.

## Quick Start
To resume work:
```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Load all data (if GraphDB is running)
make graphdb-all

# 3. Run demo query against local file (sanity check)
python -m paa_graph_kb.cli.test_graph_coexistence # (Note: this script was deleted during cleanup, recreate or use SPARQL)
```

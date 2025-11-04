# Perseus Linked Art / CIDOC-CRM Integration Project — Context Summary

## Objective
To integrate heterogeneous museum data sources (starting with the Harvard Art Museums API) into **Linked Art–compliant CIDOC-CRM graphs**, enabling a shared, semantically rich representation of cultural heritage objects.

---

## Phase 1 — Modeling Harvard Art Museums (HAM) Data

**Tools and approach**
- We use **Pydantic models** (`ham_vocab_models.py`) to describe the HAM JSON schema.
- These models normalize incoming records from the Harvard Art Museums API into Python objects with typed fields.
- A helper client (`HAMClient`) handles pagination, API keys, and retrieval.

**Outcome**
- We can instantiate validated `HAMObject` records directly from live API data.

---

## Phase 2 — Staging Graph

**Purpose**
The staging graph serves as a **neutral, low-friction vocabulary layer**—a bridge between Pydantic records and CIDOC-CRM.

**Components**
- Namespace: `https://aa.perseus.org/staging#`
- Core predicates include `stg:title`, `stg:aatType`, `stg:materialAAT`, `stg:periodLabel`, `stg:iiifManifest`, etc.
- Deterministic subject pattern:  
  `https://aa.perseus.org/staging/o/{source}:{objectid}`

**Implementation**
- `staging_loader.py`: transforms Pydantic `HAMObject` instances into `stg:` triples using light enrichment mappings (AAT IRIs for materials, techniques, culture, etc.).
- Output: `staging.ttl`

---

## Phase 3 — Transformation to Linked Art / CRM

**Approach**
We use **SPARQL CONSTRUCT templates** to translate staging data into proper CRM graphs.

**Template set**
1. `01_construct_object_core.rq` — creates `E22_Human-Made_Object` with types and titles.  
2. `02_construct_production_period_place.rq` — creates `E12_Production` linked to `E22`, with optional period/place.  
3. `03_construct_materials.rq` — adds `P45_consists_of` materials.  
4. `04_construct_techniques.rq` — adds `P32_used_general_technique` links.  
5. `05_construct_representations.rq` — links IIIF manifests and images via `la:digitally_shown_by`.  
6. `06_construct_notes.rq` — adds credit line and provenance notes as `E33_Linguistic_Object`.

**Identifiers**
- Deterministic IRIs using SHA256 hashes of `source:objectid` (no blank nodes).
- Stable minting for text content (e.g., title, creditline) via SHA256 of normalized literals.

**Runner**
- `run_constructs.py`: applies all `.rq` templates using `rdflib` and writes the merged graph to `linkedart.ttl`.

---

## Phase 4 — Validation

**Tools**
- **SHACL shapes** (`shapes_linkedart.ttl`) define minimal structural constraints:
  - Every `E22` must have a producing `E12`.
  - Every `E12` must link to at least one `E22`.
  - Period/place types enforced (`E4_Period`, `E53_Place`).
  - Appellations must have symbolic content.
- **Validator script** (`validate_shacl.py`) uses `pyshacl` to confirm graph integrity.

---

## Phase 5 — GraphDB Integration

**Purpose**
Allow scalable query and reasoning in a triplestore.

**Files**
- `graphdb_env.example`: connection variables for local GraphDB instance.
- `graphdb/load_staging.sh`: uploads staging triples into a named graph.
- `graphdb/run_constructs.sh`: template stub for executing CONSTRUCT → INSERT transformations (for interactive use via Workbench or REST).
- `graphdb/README.md`: operational guidance and next steps.

---

## Design Principles

- **Separation of concerns:** data normalization (Pydantic), staging, semantic transformation, validation, persistence.
- **Deterministic, opaque URIs** for cross-dataset merging.
- **Extensible mapping** via SPARQL; new datasets (e.g., other museums) can be added by defining additional staging schemas and templates.
- **Transparency:** every step produces inspectable TTL, enabling auditing and debugging.

---

## Planned Extensions

- Add templates for:
  - **Measurements** (`P43_has_dimension`, QUDT units)
  - **Agents and Roles** (`E21_Person`, `E39_Actor`, `P14_carried_out_by`)
  - **Exhibitions** (`E7_Activity`)
- Expand **staging_loader** with richer vocabulary resolution (AAT, TGN, ULAN).
- Integrate with **CollectionBuilder** or **eXist-db** for downstream publication.
- Automate **GraphDB CONSTRUCT → INSERT** workflow via SPARQL updates.

---

## Directory Summary

```
.
├── LICENSE
├── PROJECT_CONTEXT.md
├── README.md
├── data
│   └── staging
├── pdm.lock
├── pyproject.toml
├── pytest.ini
├── src
│   └── paa_graph_kb
│       ├── __init__.py
│       ├── __init__.py~
│       ├── __pycache__
│       │   └── __init__.cpython-312.pyc
│       ├── cli
│       │   ├── __init__.py
│       │   ├── run_constructs.py
│       │   ├── staging_loader.py
│       │   ├── staging_loader.py~
│       │   └── validate_shacl.py
│       ├── clients
│       │   ├── __init__.py
│       │   ├── __pycache__
│       │   │   ├── __init__.cpython-312.pyc
│       │   │   └── ham_client.cpython-312.pyc
│       │   ├── ham_client.py
│       │   ├── ham_client.py~
│       │   └── ham_client_patched.py~
│       ├── graphdb
│       │   ├── README.md
│       │   ├── graphdb_env.example
│       │   ├── load_staging.sh
│       │   └── run_constructs.sh
│       ├── harvesters
│       │   ├── __init__.py
│       │   ├── __init__.py~
│       │   ├── ham_harvester.py
│       │   └── ham_harvester.py~
│       ├── models
│       │   ├── __init__.py
│       │   ├── __pycache__
│       │   │   └── __init__.cpython-312.pyc
│       │   └── ham
│       │       ├── __init__.py
│       │       ├── __pycache__
│       │       │   ├── __init__.cpython-312.pyc
│       │       │   └── models.cpython-312.pyc
│       │       └── models.py
│       ├── resources
│       │   └── templates
│       │       ├── 01_construct_object_core.rq
│       │       ├── 02_construct_production_period_place.rq
│       │       ├── 03_construct_materials.rq
│       │       ├── 04_construct_techniques.rq
│       │       ├── 05_construct_representations.rq
│       │       └── 06_construct_notes.rq
│       ├── run_constructs.py
│       ├── shapes
│       │   ├── __init__.py
│       │   └── linkedart.ttl
│       └── vocabularies
│           └── stg_vocab.ttl
└── tests
    ├── __init__.py
    └── conftest.py

```

---

## Versioning Note
This document describes the toolkit as of October 2025. If additional vocabularies, templates, or loaders are added later, they should be registered in the same directory structure and noted here.

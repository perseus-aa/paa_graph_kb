# Perseus Art & Archaeology: Curation Workflow Architecture

## Problem Statement

The Perseus Art & Archaeology (PAA) dataset contains rich scholarly information—specifically iconographic descriptions and bibliographic references—that is currently trapped in unstructured, legacy formats.

-   **Legacy Format:** Data is stored as monolithic "blobs" of text mixed with obsolete HTML/TEI markup (e.g., `<P><bibl>Beazley 1963</bibl>, p. 45...</P>`).
-   **Lack of Connectivity:** Citations are string literals, not links. They do not connect to authoritative bibliographic entities or external digital editions (HathiTrust, Internet Archive).
-   **Maintenance Debt:** Editing a description currently requires modifying the core object record, risking data integrity.
-   **Missed Opportunity:** The lack of structured data prevents "Rich Hypertext" experiences, where users can seamlessly navigate from an object to its scholarly sources and parallel examples.

## Vision: The Graph-Centric Knowledge Base

We propose transitioning from a **Document-Centric** model (editing text blobs) to a **Graph-Centric** model based on **W3C Web Annotations**.

In this model, scholarly commentary is a distinct layer of "Annotations" that float on top of the stable Object Nodes.

**Goals:**
1.  **Decomposition:** Explode monolithic text blobs into distinct, addressable entities.
2.  **Resolution:** Link text strings to authoritative Entities (Books, People, Concepts).
3.  **Enrichment:** Connect citations to external digital resources (HathiTrust, Internet Archive).
4.  **Sustainability:** Enable distributed curation by Librarians, Students, and AI Agents, backed by version control.

## Architecture & Data Model

### 1. The Web Annotation Model (OA)

We will use the W3C Web Annotation Ontology (`oa:`) to structure all curation data.

#### A. The Iconographic Annotation

Replaces the legacy "Description" field.

-   **Type:** `oa:Annotation`
-   **Motivation:** `oa:describing`
-   **Target:** The Perseus Object URI (e.g., `https://aa.perseus.org/id/thing/UUID`)
-   **Body:**
    -   *Content:* Clean, semantic text (Markdown/Text).
    -   *Format:* `text/markdown` or `text/plain`.
-   **Provenance:** Created by (Agent), Created at (Time).

#### B. The Bibliographic Annotation

Replaces the legacy "Bibliography" field.

-   **Type:** `oa:Annotation`
-   **Motivation:** `oa:referencing`
-   **Target:** The Perseus Object URI
-   **Body:** A reference to a **Bibliographic Entity**.

#### C. The Bibliographic Entity (The "Rich Link")

Instead of a string, the annotation body points to a node representing the Work.

-   **Type:** `crm:E33_Linguistic_Object` (The Book/Article)
-   **Properties:**
    -   `dcterms:title`
    -   `dcterms:creator`
    -   `dcterms:date`
    -   `crm:P1_is_identified_by` → `crm:E42_Identifier` (The URL to HathiTrust/Internet Archive, with appropriate `dcterms:format` and `dcterms:type` for "digital edition").

### 2. Storage: Two-Way Sync

To ensure data safety and version control, the "System of Record" is the file system, not just the database.

-   **File System:** Each Annotation is serialized as a distinct Turtle (`.ttl`) file in `data/annotations/`. These files will be version-controlled (e.g., via Git).
-   **GraphDB:** Acts as the *Index*. When annotation files are modified on disk, they are automatically reloaded into the graph for querying and display.
-   **Benefit:** Enables robust versioning, collaboration, and simplified backup strategies.

## Curation Workflows

### Workflow 1: The "Splitter" (Decomposition)

*Objective:* Break legacy HTML blobs into distinct atomic units.

1.  **Input:** Legacy `stg:sourcesUsed` (HTML blob).
2.  **Process (AI/Heuristic):** An agent parses the text to identify individual citations vs. descriptive notes.
3.  **Review:** Curator (Student/Librarian) reviews the proposed split.
4.  **Output:** N new Web Annotation files are created for each identified item; the original legacy blob can be marked as "Processed" or deprecated.

### Workflow 2: The "Resolver" (Authority Linking)

*Objective:* Turn citation strings into graph links to authoritative bibliographic entities.

1.  **Input:** A clean citation string (e.g., "Beazley, ABV, p. 23").
2.  **Process:**
    -   Search local Authority Graph (is "ABV" known as a `crm:E33_Linguistic_Object`?).
    -   Search External APIs (WorldCat, CrossRef) for matching canonical works.
3.  **Action:** User selects the matching canonical bibliographic work.
4.  **Enrichment:** User adds specific URLs (e.g., HathiTrust page link) for digital editions.

### Workflow 3: The "Editor" (Content Cleanup & Tagging)

*Objective:* Clean up prose descriptions and semantically tag entities within them.

1.  **Input:** Raw iconographic text (or other prose description).
2.  **Process:**
    -   Strip obsolete HTML/TEI tags (e.g., `<hi>`, `<P>`) from the raw content to create a clean body.
    -   Apply semantic markdown or standardized plain text.
    -   **Entity Tagging:** Highlight keywords (e.g., "Herakles", "Chiton") and link them to relevant AAT or internal Authority nodes (e.g., `aat:300015505` for "Herakles").

## Technical Implementation Plan

### Phase 1: Prototype (Completed)

-   Scripting to "Explode" sample blobs (`prototype_biblio_splitter.py`).
-   Defined the conceptual RDF shapes for Annotations.

### Phase 2: The Curation Backend

-   **Framework:** FastAPI (Python).
-   **Role:** Acts as the API layer between the UI, the filesystem-backed GraphDB, and potentially external services.
-   **Endpoints:**
    -   `GET /object/{id}/annotations`: Retrieve all annotations targeting a specific object.
    -   `POST /annotation`: Create/Update a new annotation (writes to `.ttl` file, signals GraphDB update).
    -   `GET /annotation/dirty_bibliographies`: List objects with uncurated bibliographies.

### Phase 3: The Curation UI

-   **Framework:** React (or similar modern JS framework).
-   **Components:**
    -   **Workspace/Dashboard:** A "To-Do" list or queue of records needing curation.
    -   **Splitter View:** A user interface for Workflow 1, allowing review and confirmation of automated text splitting.
    -   **Resolver Widget:** An interactive component for Workflow 2, facilitating search and linking to bibliographic authorities.
    -   **Rich Text Editor with Semantic Tagging:** For Workflow 3, an editor that supports cleaning, formatting (e.g., Markdown), and inline linking of text to entities.

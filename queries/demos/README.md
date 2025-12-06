# Demonstration Queries

This directory contains SPARQL queries demonstrating the integrated Knowledge Base, highlighting the connection between Perseus, Getty, and Harvard Art Museums data, as well as the rich bibliographical and iconographic enrichments.

## Queries

*   **01_getty_data_sample.rq**: Retrieves sample object data directly from the Getty Linked Art graph (loaded from JSON-LD).
*   **02_perseus_getty_link.rq**: Demonstrates the `owl:sameAs` integration by fetching a Perseus object's label alongside its Getty equivalent's physical dimensions and images.
*   **03_bibliography_enrichment.rq**: Shows the dual-mode bibliographic data: the "clean" text for display and the "raw" HTML/TEI markup for curation.
*   **04_iconography_enrichment.rq**: Retrieves the detailed iconographic descriptions (narrative texts) extracted from Perseus data and classified with AAT codes.

## Running Queries

You can run these queries in the GraphDB workbench or using a command-line tool like `curl` or a python script against your local GraphDB instance.

Example (using curl):
```bash
# Ensure GraphDB is running
curl -X POST "http://localhost:7200/repositories/paa-kb" \
     -H "Content-Type: application/sparql-query" \
     -d @02_perseus_getty_link.rq
```

```
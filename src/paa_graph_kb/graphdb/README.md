# GraphDB Integration — HAM & Perseus Data

This directory contains scripts and configuration for loading data into GraphDB,
organizing data into named graphs for HAM, Perseus, and entity equivalences.

## Quick start (local dev with rdflib)
1) Generate staging from HAM:
```bash
make staging HAM_APIKEY=your_key
```
2) Build Linked Art:
```bash
make linkedart-local
```
3) Validate:
```bash
make validate
```

## GraphDB Setup

### 1. Configure GraphDB Connection
```bash
# Already configured if you've run make setup-graphdb
# Otherwise, copy the example:
cp src/paa_graph_kb/graphdb/graphdb_env.example src/paa_graph_kb/graphdb/graphdb_env
# Edit graphdb_env to set GRAPHDB_BASE, REPOSITORY
```

### 2. Named Graphs Organization

Data is loaded into separate named graphs for clarity and querying:

```
HAM Data:
  http://aa.perseus.org/graph/staging/HAM         - HAM staging data
  http://aa.perseus.org/graph/linkedart/HAM       - HAM CRM (Linked Art)

Perseus Data:
  http://aa.perseus.org/graph/staging/Perseus     - Perseus staging objects
  http://aa.perseus.org/graph/images/Perseus      - Perseus staging images
  http://aa.perseus.org/graph/linkedart/Perseus   - Perseus CRM (Linked Art)

Entity Resolution:
  http://aa.perseus.org/graph/equivalences        - owl:sameAs statements
```

## Loading Data to GraphDB

### Option 1: Using Makefile (Recommended)

**Load HAM data:**
```bash
make graphdb-all                    # Load HAM staging + run constructs
```

**Load Perseus data:**
```bash
make graphdb-load-all-perseus       # Load all Perseus data + equivalences
```

**Individual Perseus targets:**
```bash
make graphdb-load-perseus-staging   # Objects + images staging
make graphdb-load-perseus-linkedart # Perseus CRM data
make graphdb-load-equivalences      # Entity links (owl:sameAs)
```

### Option 2: Manual Loading

**Load any TTL file to a named graph:**
```bash
src/paa_graph_kb/graphdb/load_to_graph.sh <file.ttl> <graph-uri>
```

**Example:**
```bash
src/paa_graph_kb/graphdb/load_to_graph.sh \
  data/staging/perseus_objects.ttl \
  "http://aa.perseus.org/graph/staging/Perseus"
```

## Querying Multi-Source Data

### Query across all graphs:
```sparql
SELECT ?g (COUNT(*) AS ?count)
WHERE {
  GRAPH ?g { ?s ?p ?o }
}
GROUP BY ?g
ORDER BY ?g
```

### Find linked entities (using owl:sameAs):
```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?perseus ?ham
WHERE {
  GRAPH <http://aa.perseus.org/graph/equivalences> {
    ?perseus owl:sameAs ?ham .
    FILTER(CONTAINS(STR(?perseus), "perseus"))
  }
}
LIMIT 10
```

### Get combined data for a matched object:
```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?obj ?label ?source ?graph
WHERE {
  # Find equivalence
  GRAPH <http://aa.perseus.org/graph/equivalences> {
    ?perseus_obj owl:sameAs ?ham_obj .
  }

  # Get data from both sources
  VALUES ?obj { ?perseus_obj ?ham_obj }
  GRAPH ?graph {
    ?obj rdfs:label ?label .
  }

  BIND(IF(CONTAINS(STR(?graph), "Perseus"), "Perseus", "HAM") AS ?source)
}
LIMIT 20
```

## Design Principles
- Deterministic IRIs with SHA256 of salient keys
- No blank nodes for appellations/notes (mint by value)
- Multi-graph organization for source separation
- Entity resolution via owl:sameAs

## Next Steps
- Enable OWL reasoning to leverage owl:sameAs inferences
- Add reconciliation for external AAT/Geonames alignment
- Expand entity resolution to other institutions (Boston, Cleveland, etc.)

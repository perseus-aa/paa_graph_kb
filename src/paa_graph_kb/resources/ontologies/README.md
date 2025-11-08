# Ontologies Directory

This directory contains RDF/OWL ontologies used by the PAA Graph Knowledge Base project.

## CIDOC-CRM

The CIDOC Conceptual Reference Model (CRM) provides the semantic foundation for our Linked Art transformations.

### Download CIDOC-CRM Ontology

**Option 1: Official CIDOC-CRM Website**

Visit https://www.cidoc-crm.org/versions-of-the-cidoc-crm and download the RDFS version:

- **Version 7.1.3** (Latest): https://cidoc-crm.org/rdfs/7.1.3/CIDOC_CRM_v7.1.3.rdfs
- **Version 7.1.2**: https://cidoc-crm.org/rdfs/7.1.2/CIDOC_CRM_v7.1.2.rdfs

Save the file to this directory as `CIDOC_CRM_v7.1.3.rdfs` (or whichever version you download).

**Option 2: GitHub Mirror**

```bash
# Download from GitHub mirror if available
curl -L -o CIDOC_CRM_v7.1.3.rdfs \
  https://github.com/cidoc-crm/cidoc-crm/raw/master/rdfs/CIDOC_CRM_v7.1.3.rdfs
```

**Option 3: Manual Download**

1. Visit the CIDOC-CRM website
2. Navigate to "Versions of the CIDOC-CRM"
3. Download the RDFS file for version 7.1.3
4. Save it to `src/paa_graph_kb/resources/ontologies/CIDOC_CRM_v7.1.3.rdfs`

## Loading into GraphDB

### Option 1: Using Makefile (Recommended)

```bash
# Load ontology into GraphDB
make graphdb-load-ontology
```

### Option 2: Manual Loading via GraphDB Workbench

1. Open GraphDB Workbench: http://localhost:7200
2. Select your repository
3. Go to "Import" → "RDF"
4. Upload `CIDOC_CRM_v7.1.3.rdfs`
5. Import into named graph: `http://www.cidoc-crm.org/cidoc-crm/`
6. Click "Import"

### Option 3: Using curl

```bash
# Load ontology via GraphDB REST API
curl -X POST http://localhost:7200/repositories/YOUR_REPO/statements \
  -H "Content-Type: application/rdf+xml" \
  --data-binary @src/paa_graph_kb/resources/ontologies/CIDOC_CRM_v7.1.3.rdfs
```

## Enabling OWL Inferencing

After loading the ontology, enable reasoning in GraphDB:

1. Go to "Setup" → "Repositories"
2. Edit your repository
3. Set "Ruleset" to "OWL-Horst (Optimized)" or "OWL-Max"
4. Save and restart repository

### Benefits of Inferencing

With CIDOC-CRM ontology + inferencing enabled:

- ✅ **Inverse properties work automatically**
  - Query `?obj crm:P108i_was_produced_by ?prod` works even if data only has `?prod crm:P108_has_produced ?obj`

- ✅ **Class hierarchy reasoning**
  - Query for `crm:E70_Thing` returns all human-made objects (subclass)

- ✅ **Property domain/range validation**
  - Helps catch modeling errors

- ✅ **Richer queries**
  - Can query at higher abstraction levels

### Example Queries with Inferencing

```sparql
# Before inferencing: Must use exact property direction
?production crm:P108_has_produced ?obj .

# After inferencing: Can use either direction
?obj crm:P108i_was_produced_by ?production .
# OR
?production crm:P108_has_produced ?obj .
```

```sparql
# Query all "Things" (includes all E22_Human-Made_Object via hierarchy)
SELECT ?thing WHERE {
  ?thing a crm:E70_Thing .
}
```

## File Listing

Expected files in this directory:

- `CIDOC_CRM_v7.1.3.rdfs` - CIDOC-CRM ontology (you need to download this)
- `README.md` - This file

## References

- **CIDOC-CRM Official Site**: https://www.cidoc-crm.org/
- **CIDOC-CRM Documentation**: https://cidoc-crm.org/html/cidoc_crm_v7.1.3.html
- **Linked Art Uses CIDOC-CRM**: https://linked.art/model/
- **GraphDB OWL Reasoning**: https://graphdb.ontotext.com/documentation/

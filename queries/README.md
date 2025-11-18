# SPARQL Query Library

This directory contains curated SPARQL queries demonstrating research use cases enabled by the integrated Perseus + HAM knowledge graph.

## Overview

The queries showcase how entity resolution (via `owl:sameAs`) and multi-graph organization enable:
- **Cross-collection research** - Find objects across HAM and Perseus collections
- **Data enrichment** - Combine complementary metadata from multiple sources
- **Specialized searches** - Leverage domain-specific data (painters, iconography, shapes)
- **Image access** - Get IIIF URLs for high-resolution images

## Running Queries

### Using GraphDB Workbench

1. Open GraphDB at http://localhost:7200
2. Select your repository (default: `demo`)
3. Go to SPARQL tab
4. Copy query from `.rq` file and paste
5. Modify FILTER values as needed
6. Click Execute

### Using Command Line (with curl)

```bash
# Run a query via GraphDB SPARQL endpoint
curl -X POST http://localhost:7200/repositories/demo \
  -H "Content-Type: application/sparql-query" \
  -H "Accept: application/sparql-results+json" \
  --data-binary @queries/research/01_painter_attribution.rq
```

### Using Python (with rdflib)

```python
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore

# Connect to GraphDB
store = SPARQLStore("http://localhost:7200/repositories/demo")
g = Graph(store)

# Read and execute query
with open("queries/research/01_painter_attribution.rq") as f:
    query = f.read()

results = g.query(query)
for row in results:
    print(row)
```

## Query Catalog

### Research Queries

#### 01_painter_attribution.rq
**Find objects by painter across collections**

Searches for objects attributed to a specific painter (e.g., "Berlin Painter", "Exekias") across both HAM and Perseus. Demonstrates cross-collection attribution research.

**Key features:**
- Searches across both collections simultaneously
- Uses CIDOC-CRM production events (E12_Production)
- Shows painter attributions (E21_Person)
- Identifies source collection for each result

**Example usage:**
- Find all works by the Berlin Painter
- Compare painter attributions across institutions
- Research painter oeuvres

**Modify this line to search for different painters:**
```sparql
FILTER(CONTAINS(LCASE(?painterLabel), "berlin"))
```

---

#### 02_iconography_search.rq
**Search decoration descriptions for iconographic subjects**

Searches linguistic objects (notes, descriptions) for specific iconographic subjects or scenes. Particularly valuable for Perseus data which includes detailed decoration descriptions from the Beazley Archive.

**Key features:**
- Full-text search across descriptions
- Finds symposium scenes, deity depictions, mythological subjects
- Searches E33_Linguistic_Object content

**Example subjects to search:**
- Symposium/komos (drinking scenes)
- Deities: "athena", "herakles", "dionysus"
- Scenes: "warrior", "chariot", "sacrifice"
- Creatures: "sphinx", "siren", "gorgon"

**Modify this line:**
```sparql
FILTER(CONTAINS(LCASE(?description), "symposium"))
```

---

#### 03_shape_ware_analysis.rq
**Find objects by ceramic shape and ware type**

Searches for specific vase shapes and ceramic ware types. Essential for Greek vase scholarship and typological studies.

**Key features:**
- Searches object type classifications (P2_has_type)
- Finds specific shapes (amphora, kylix, krater, etc.)
- Finds ware types (black-figure, red-figure, etc.)

**Example shapes:**
- amphora, kylix, krater, hydria, lekythos, oinochoe, pelike

**Example wares:**
- Attic black-figure, Attic red-figure, white-ground, Corinthian

**Modify this line:**
```sparql
FILTER(
  CONTAINS(LCASE(?typeLabel), "amphora") ||
  CONTAINS(LCASE(?typeLabel), "black-figure")
)
```

---

#### 04_data_enrichment.rq
**Show how matched objects combine data from both sources**

Demonstrates the VALUE of entity resolution by showing how matched objects (linked via `owl:sameAs`) access properties from both HAM and Perseus graphs through OWL reasoning.

**Key features:**
- Finds only matched objects (those in equivalences graph)
- Counts total properties accessible via reasoning
- Shows which graphs contribute data
- Proves data enrichment is working

**Expected pattern:**
- Perseus contributes: painter, decoration, Beazley number, shape/ware
- HAM contributes: provenance, exhibitions, conservation, detailed classifications

**This query proves owl:sameAs reasoning is working!**

---

#### 05_iiif_image_access.rq
**Get IIIF image service URLs for objects**

Retrieves IIIF (International Image Interoperability Framework) image service URLs, enabling:
- Side-by-side image comparison
- Deep zoom into high-resolution images
- Custom image viewers
- Image annotations

**Key features:**
- Finds E36_Visual_Item entities (images)
- Extracts IIIF service base URLs
- Links images to objects

**IIIF Image API format:**
```
{scheme}://{server}{/prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}
```

**Use cases:**
- Build custom viewers comparing Perseus and HAM images of same object
- Download specific image regions or resolutions
- Create IIIF manifests for Mirador or other viewers

---

## Query Design Principles

1. **Named graphs** - All queries specify `GRAPH ?graph` to work across multiple graphs
2. **Source identification** - Queries use `BIND` to identify whether data comes from HAM, Perseus, or equivalences
3. **Optional matching** - Use `OPTIONAL` for properties that may not exist in all records
4. **Case-insensitive search** - Use `LCASE()` and `CONTAINS()` for flexible matching
5. **Reasoning-aware** - Queries leverage owl:sameAs inference automatically when enabled

## Graph Organization

Data is organized into named graphs:

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

## Customizing Queries

All queries include comments showing which lines to modify for different searches:

1. **FILTER clauses** - Change search terms, painters, shapes, subjects
2. **LIMIT values** - Adjust result set size
3. **Graph URIs** - Target specific named graphs if needed
4. **ORDER BY** - Change result sorting

## Next Steps

Potential query additions:
- Provenance tracking (find objects with shared provenance)
- Dating analysis (find objects by period/century)
- Material/technique searches
- Geographic origin searches
- Beazley Archive linkage (find objects with Beazley numbers)
- Exhibition history queries

## Technical Notes

### OWL Reasoning
GraphDB must have OWL-Horst reasoning enabled with `owl:sameAs` support for entity resolution queries to work correctly.

### Performance
- Queries with `CONTAINS()` on large text fields may be slow
- Use `LIMIT` to constrain result sets
- Consider adding indexes on frequently queried properties

### Federation
These queries could be extended to federate across multiple SPARQL endpoints (e.g., querying external LOD sources like AAT, Geonames, Wikidata).

# Quick Start for Next Session

## TL;DR - Where We Left Off

✅ **Completed:**
- Loaded CIDOC-CRM ontology into GraphDB → 5M inferred triples!
- Created 100% AAT mappings (60/60 terms)
  - 31 techniques → AAT
  - 29 classifications → AAT

⏭️ **Next Task:**
Update SPARQL templates to use AAT mappings

## 30-Second Context Restore

```bash
cd /Users/wulfmanc/repos/gh/perseus-aa/paa_graph_kb

# Read full session notes
cat docs/SESSION_2025-12-01.md

# Check AAT mappings we created
head -20 data/reconciliation/techniques_aat_manual.txt
head -20 data/reconciliation/classifications_aat_manual.txt

# Templates that need updating
ls -l src/paa_graph_kb/resources/templates/{04,11}_*.rq
```

## The Task: Add AAT Links to Templates

### Template 04: Techniques

**File:** `src/paa_graph_kb/resources/templates/04_construct_techniques.rq`

**Current:**
```sparql
?tech rdfs:label ?techniqueLabel .
```

**Needs to become:**
```sparql
?tech rdfs:label ?techniqueLabel ;
      owl:sameAs ?aatTech .

?aatTech a crm:E55_Type .
```

**Strategy:**
Use IF/CONTAINS pattern like template 17 does for roles, OR use VALUES clause to map strings → AAT URIs.

### Template 11: Classifications

**File:** `src/paa_graph_kb/resources/templates/11_construct_classification.rq`

**Current:**
```sparql
?classNode a crm:E55_Type ;
           rdfs:label ?classification .
```

**Needs to become:**
```sparql
?classNode a crm:E55_Type ;
           rdfs:label ?classification ;
           owl:sameAs ?aatClass .

?aatClass a crm:E55_Type .
```

**Strategy:**
Same as techniques - map classification string to AAT URI.

## Mapping Data Format

Format: `term: aat:ID  # comment`

Example from `data/reconciliation/techniques_aat_manual.txt`:
```
struck: aat:300053851          # striking (metalworking - coins)
red-figure: aat:300020201      # red-figure pottery
cast: aat:300053104            # casting (metal forming)
```

## Testing After Updates

```bash
# Regenerate Linked Art locally
make linkedart-local

# Check if owl:sameAs triples were created
python3 << 'EOF'
import rdflib
g = rdflib.Graph()
g.parse("data/linkedart/ham_linkedart.ttl", format="turtle")

# Query for AAT links
query = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX aat: <http://vocab.getty.edu/aat/>
SELECT (COUNT(*) as ?count) WHERE {
  ?s owl:sameAs ?aat .
  FILTER(STRSTARTS(STR(?aat), "http://vocab.getty.edu/aat/"))
}
"""
for row in g.query(query):
    print(f"AAT links created: {row.count}")
EOF

# Load to GraphDB
make graphdb-run-constructs

# Query in GraphDB
source src/paa_graph_kb/graphdb/graphdb_env
curl -X POST "$GRAPHDB_BASE/repositories/$REPOSITORY" \
  -H "Content-Type: application/sparql-query" \
  --data 'PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT (COUNT(*) AS ?count) WHERE {
  ?s owl:sameAs ?aat .
  FILTER(STRSTARTS(STR(?aat), "http://vocab.getty.edu/aat/"))
}'
```

## Expected Outcome

After template updates:
- ~31 technique concepts linked to AAT
- ~29 classification concepts linked to AAT
- Total: ~60 new owl:sameAs triples to Getty AAT

Example triple pattern:
```turtle
<https://aa.perseus.org/id/type/technique/...>
  a crm:E55_Type ;
  rdfs:label "red-figure" ;
  owl:sameAs aat:300020201 .

aat:300020201
  a crm:E55_Type .
```

## Alternative: If Template Updates Are Complex

If adding mappings to templates proves difficult, consider:
1. Create separate AAT enrichment template (template 30?)
2. Load AAT mappings as a separate graph
3. Use SPARQL UPDATE to add owl:sameAs links post-processing

## After AAT Work: IIIF Manifests

User expressed interest in IIIF manifest generation. This would involve:
- Creating IIIF Presentation API 3.0 manifests
- Linking images from Perseus/HAM to IIIF Image API
- Adding canvas, annotations, metadata
- Could use Linked Art's digital integration patterns

See: https://linked.art/model/digital/ for IIIF + Linked Art integration.

---

**Ready to code!** Start with template 04 or 11.

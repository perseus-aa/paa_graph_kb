# Ontologies Directory

This directory contains RDF/OWL ontologies used by the PAA Graph Knowledge Base project.

## CIDOC-CRM v7.1.3

The CIDOC Conceptual Reference Model (CRM) provides the semantic foundation for our Linked Art transformations.

**Official Source**: https://gitlab.isl.ics.forth.gr/cidoc-crm/cidoc_crm_rdf
**Version**: 7.1.3 (February 2024)
**License**: CC BY 4.0
**Created by**: FORTH-ICS

### Files in This Directory

This directory contains three CIDOC-CRM ontology files:

#### 1. CIDOC_CRM_v7.1.3.rdf (Main Ontology - 419KB)

The core CIDOC-CRM ontology with all classes and properties.

**Contains:**
- All 91 CRM classes (E1-E99)
- All properties with forward and inverse directions (e.g., `P14_carried_out_by` and `P14i_performed`)
- Class hierarchies and property domains/ranges
- Multilingual labels and scope notes
- OWL axioms for reasoning

**Key Features:**
- **Bidirectional properties**: each CRM property like "P2 has type (is type of)" is represented as two RDFS properties:
  - `P2_has_type` (domain → range direction)
  - `P2i_is_type_of` (range → domain direction)
- **Primitive values**: E60 Number, E61 Time Primitive, E62 String, E94 Space Primitive, E95 Spacetime Primitive interpreted as `rdfs:Literal`
- **Naming convention**: Underscores replace spaces (e.g., `E22_Human-Made_Object`)

**Example classes:**
```turtle
crm:E1_CRM_Entity         # Top-level class
crm:E22_Human-Made_Object # Physical objects made by humans
crm:E21_Person            # Individual people
crm:E12_Production        # Making/creating an object
crm:E52_Time-Span         # Temporal intervals
```

#### 2. CIDOC_CRM_v7.1.3_PC.rdf (Property Classes - 30KB)

Implements **property classes** for qualified/n-ary relationships (properties with properties).

**What are Property Classes?**

CIDOC-CRM allows properties to have additional qualifiers (called ".1 properties"). Since RDF doesn't support properties of properties directly, Property Classes provide a reification pattern.

**Example: Expressing roles in production**

```turtle
# Simple property (no role qualification)
:painting_sistine_chapel crm:P14_carried_out_by :Michelangelo .

# Qualified relationship using PC14 (WITH role)
:instanceOfPC14 a crm:PC14_carried_out_by ;
    crm:P01_has_domain :painting_sistine_chapel ;  # the activity
    crm:P02_has_range :Michelangelo ;              # the actor
    crm:P14.1_in_the_role_of :master_craftsman .   # the role qualifier

:master_craftsman a crm:E55_Type ;
    rdfs:label "Master Craftsman" .
```

**Property Classes Defined:**

| Property Class | Base Property | Qualifier Property | Use Case |
|----------------|---------------|-------------------|----------|
| `PC14_carried_out_by` | P14 | P14.1 in the role of | Actor roles in activities |
| `PC16_used_specific_object` | P16 | P16.1 mode of use | How object was used |
| `PC19_was_intended_use_of` | P19 | P19.1 mode of use | Intended use mode |
| `PC67_refers_to` | P67 | P67.1 has type | Type of reference |
| `PC138_represents` | P138 | P138.1 mode of representation | How representation was made |
| ...and 13 more |

**We Already Use This!**

See `templates/17_construct_person_production.rq` - it uses `PC14_carried_out_by` to express artist/maker roles:

```sparql
?roleAssignment a crm:PC14_carried_out_by ;
    crm:P01_has_domain ?prod ;
    crm:P02_has_range ?person ;
    crm:P14.1_in_the_role_of ?roleType .
```

**Important Implementation Note:**

When you create a PC instance, you **must also** create the base property triple:

```turtle
# Both of these should exist:
:painting crm:P14_carried_out_by :michelangelo .  # Base property
:pc1 a crm:PC14_carried_out_by ;                   # Property class instance
    crm:P01_has_domain :painting ;
    crm:P02_has_range :michelangelo ;
    crm:P14.1_in_the_role_of :artist_role .
```

Our template 17 does this correctly!

#### 3. CIDOC_CRM_v7.1.3_Supplement.rdf (Supplements - 3.3KB)

Additional property relationships that may cause OWL-DL inconsistencies in strict reasoners but are semantically valid.

**Contains:**

1. **`rdfs:label` as subPropertyOf `P1_is_identified_by`**
   - Justifies using standard `rdfs:label` as CIDOC-CRM appellation
   - Validates our extensive use of `rdfs:label` throughout templates!
   - Makes all our labels semantically valid CRM identifiers

2. **Three spatial/temporal subproperties:**
   - `P168_place_is_defined_by` subPropertyOf `P1_is_identified_by`
   - `P169i_spacetime_volume_is_defined_by` subPropertyOf `P1_is_identified_by`
   - `P170i_time_is_defined_by` subPropertyOf `P1_is_identified_by`

**Why are these "supplemental"?**

These create technical inconsistencies in strict OWL-DL:
- P168/P169i/P170i are datatype properties (range = literal)
- P1 is an object property (range = E41_Appellation)
- OWL-DL forbids mixing datatype and object property hierarchies

**Should you use it?**

✅ **YES, for GraphDB and most RDF stores** - they handle this fine
⚠️ **NO, for strict OWL-DL reasoners** - may cause inconsistency errors

GraphDB with OWL-Horst reasoning handles these without issues.

## Loading into GraphDB

### Recommended: Load All Three Files

```bash
# Using Makefile (recommended)
make graphdb-load-ontology

# Or manually via GraphDB Workbench:
# 1. Import CIDOC_CRM_v7.1.3.rdf (main ontology)
# 2. Import CIDOC_CRM_v7.1.3_PC.rdf (property classes)
# 3. Import CIDOC_CRM_v7.1.3_Supplement.rdf (supplements)
```

**Import settings:**
- **Named graph**: `http://www.cidoc-crm.org/cidoc-crm/`
- **Format**: RDF/XML (auto-detected from .rdf extension)
- **Context**: Same graph for all three files

### Manual Loading via curl

```bash
# Source GraphDB environment
source src/paa_graph_kb/graphdb/graphdb_env

# Load main ontology
curl -X POST "$GRAPHDB_BASE/repositories/$REPOSITORY/statements?context=%3Chttp://www.cidoc-crm.org/cidoc-crm/%3E" \
  -H "Content-Type: application/rdf+xml" \
  --data-binary @src/paa_graph_kb/resources/ontologies/CIDOC_CRM_v7.1.3.rdf

# Load property classes
curl -X POST "$GRAPHDB_BASE/repositories/$REPOSITORY/statements?context=%3Chttp://www.cidoc-crm.org/cidoc-crm/%3E" \
  -H "Content-Type: application/rdf+xml" \
  --data-binary @src/paa_graph_kb/resources/ontologies/CIDOC_CRM_v7.1.3_PC.rdf

# Load supplement
curl -X POST "$GRAPHDB_BASE/repositories/$REPOSITORY/statements?context=%3Chttp://www.cidoc-crm.org/cidoc-crm/%3E" \
  -H "Content-Type: application/rdf+xml" \
  --data-binary @src/paa_graph_kb/resources/ontologies/CIDOC_CRM_v7.1.3_Supplement.rdf
```

## Enabling OWL Inferencing

After loading the ontology, enable reasoning in GraphDB:

1. Go to **Setup** → **Repositories**
2. Edit your repository
3. Set **Ruleset** to **"OWL-Horst (Optimized)"** or **"OWL-Max"**
4. Save and **restart repository**

### Benefits of Inferencing

With CIDOC-CRM ontology + inferencing enabled:

✅ **Inverse properties work automatically**
```sparql
# Data has:          ?prod crm:P108_has_produced ?obj
# Can query with:    ?obj crm:P108i_was_produced_by ?prod
# Both work!
```

✅ **Class hierarchy reasoning**
```sparql
# Query for E70_Thing returns E22_Human-Made_Object (subclass)
?thing a crm:E70_Thing .
```

✅ **Property transitivity**
```sparql
# P9_consists_of is transitive
# If A consists_of B and B consists_of C, infer A consists_of C
```

✅ **rdfs:label becomes CRM identifier** (via Supplement)
```sparql
# rdfs:label inferred as P1_is_identified_by
?obj rdfs:label "Terracotta kylix" .
# Becomes:
?obj crm:P1_is_identified_by "Terracotta kylix" .
```

### Example Queries with Inferencing

**Query 1: Flexible property direction**
```sparql
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>

# Works regardless of which direction was asserted in data
SELECT ?person ?obj WHERE {
  ?person crm:P14i_performed ?prod .  # inverse direction
  ?prod crm:P108_has_produced ?obj .
}
```

**Query 2: Class hierarchy**
```sparql
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>

# Returns all temporal entities (E2) including subclasses
# E12_Production, E67_Birth, E69_Death, etc.
SELECT ?temporal WHERE {
  ?temporal a crm:E2_Temporal_Entity .
}
```

**Query 3: Our data using inferred properties**
```sparql
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>

# Query using inverse properties even though templates use forward direction
SELECT ?obj ?person WHERE {
  GRAPH <http://aa.perseus.org/graph/linkedart/HAM> {
    ?obj crm:P108i_was_produced_by ?prod .
    ?prod crm:P14_carried_out_by ?person .
  }
}
```

## File Listing

Files in this directory:

- `CIDOC_CRM_v7.1.3.rdf` - Main CIDOC-CRM ontology (419KB)
- `CIDOC_CRM_v7.1.3_PC.rdf` - Property Classes for qualified relationships (30KB)
- `CIDOC_CRM_v7.1.3_Supplement.rdf` - Supplementary property relations (3.3KB)
- `README.md` - This file
- `.gitkeep` - Ensures directory exists in git

## References

- **CIDOC-CRM Official Site**: https://www.cidoc-crm.org/
- **CIDOC-CRM v7.1.3 Documentation**: https://cidoc-crm.org/html/cidoc_crm_v7.1.3.html
- **CIDOC-CRM RDF Git Repository**: https://gitlab.isl.ics.forth.gr/cidoc-crm/cidoc_crm_rdf
- **Linked Art Uses CIDOC-CRM**: https://linked.art/model/
- **GraphDB OWL Reasoning**: https://graphdb.ontotext.com/documentation/10.7/reasoning.html
- **Property Classes Explained**: https://cidoc-crm.org/property-classes

## Technical Notes

### RDF/XML vs RDFS Format

These files use `.rdf` extension (RDF/XML format) rather than `.rdfs`. Both are valid; `.rdfs` typically indicates RDFS vocabulary definitions while `.rdf` is generic RDF/XML. The content is what matters - these are RDFS with OWL annotations.

### Namespace

All CIDOC-CRM resources use the namespace:
```
http://www.cidoc-crm.org/cidoc-crm/
```

In SPARQL queries, declare it as:
```sparql
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
```

### Property Naming Convention

- Forward direction: `P##_property_name` (e.g., `P2_has_type`)
- Inverse direction: `P##i_property_name` (e.g., `P2i_is_type_of`)
- Property qualifiers: `P##.1_qualifier` (e.g., `P14.1_in_the_role_of`)

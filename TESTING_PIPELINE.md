# Testing the Full Pipeline

This guide walks through testing the complete HAM → Staging → CRM transformation pipeline with all the new features.

## Prerequisites

Ensure dependencies are installed:
```bash
pdm install
```

## Step 1: Check Existing Staging Data

You already have a `staging.ttl` file that was generated with the new code! Verify it contains the new fields:

```bash
grep -E "stg:(dimensions|description|objectnumber|datebegin|classification|department|colorName|accessionyear)" staging.ttl | head -20
```

Expected output should show fields like:
- `stg:dimensions`
- `stg:datebegin`, `stg:dated`, `stg:dateend`
- `stg:classification`, `stg:style`
- `stg:department`, `stg:division`
- `stg:colorName`, `stg:hasColor`
- `stg:objectnumber`
- `stg:accessionyear`, `stg:accessionmethod`

## Step 2: Run All 14 SPARQL Templates

Transform the staging data into CRM using all templates:

```bash
pdm run python -m paa_graph_kb.cli.run_constructs \
  --staging staging.ttl \
  --templates src/paa_graph_kb/resources/templates \
  --out linkedart_new.ttl
```

Expected output:
```
→ Loading staging graph: staging.ttl
→ Found 14 template(s) under src/paa_graph_kb/resources/templates (recursive=True)
✓ 01_construct_object_core.rq: +XXX triples
✓ 02_construct_production_period_place.rq: +XXX triples
✓ 03_construct_materials.rq: +XXX triples
✓ 04_construct_techniques.rq: +XXX triples
✓ 05_construct_representations.rq: +XXX triples
✓ 06_construct_notes.rq: +XXX triples
✓ 07_construct_dimensions.rq: +XXX triples        ← NEW
✓ 08_construct_descriptions.rq: +XXX triples      ← NEW
✓ 09_construct_identifiers.rq: +XXX triples       ← NEW
✓ 10_construct_timespan.rq: +XXX triples          ← NEW
✓ 11_construct_classification.rq: +XXX triples    ← NEW
✓ 12_construct_department.rq: +XXX triples        ← NEW
✓ 13_construct_colors.rq: +XXX triples            ← NEW
✓ 14_construct_accession.rq: +XXX triples         ← NEW
✅ Wrote XXXX triples to linkedart_new.ttl (added XXXX from 14 template(s))
```

## Step 3: Verify New CRM Entities

Check that the new templates created the expected CRM entities:

### Dimensions (E54_Dimension)
```bash
grep -A 5 "crm:E54_Dimension" linkedart_new.ttl | head -20
```

Expected: Objects linked to dimension nodes with symbolic content

### Timespan (E52_Time-Span)
```bash
grep -A 5 "crm:E52_Time-Span" linkedart_new.ttl | head -20
```

Expected: Production events with begin/end dates in xsd:gYear format

### Identifiers (E42_Identifier)
```bash
grep -A 3 "crm:E42_Identifier" linkedart_new.ttl | head -15
```

Expected: Object numbers and reference numbers

### Classification (E55_Type)
```bash
grep -A 3 "crm:E55_Type" linkedart_new.ttl | head -15
```

Expected: Classification and style types

### Departments (E74_Group)
```bash
grep -A 3 "crm:E74_Group" linkedart_new.ttl | head -15
```

Expected: Department and division groups

### Colors (E26_Physical_Feature)
```bash
grep -A 3 "crm:E26_Physical_Feature" linkedart_new.ttl | head -15
```

Expected: Color features linked to objects

### Acquisition (E8_Acquisition)
```bash
grep -A 5 "crm:E8_Acquisition" linkedart_new.ttl | head -20
```

Expected: Acquisition events with year and method

### Descriptions (E33_Linguistic_Object)
```bash
grep -B 2 -A 3 '"Description"@en' linkedart_new.ttl | head -20
```

Expected: Description, commentary, and label text nodes

## Step 4: Validate with SHACL

Run SHACL validation to ensure graph structure is correct:

```bash
pdm run python -m paa_graph_kb.cli.validate_shacl \
  --data linkedart_new.ttl \
  --shapes src/paa_graph_kb/shapes/linkedart.ttl
```

Expected output:
```
✅ Validation passed! Graph conforms to SHACL shapes.
```

## Step 5: Compare Old vs New Output

Compare the new output with the old linkedart.ttl:

```bash
# Count triples
echo "Old: $(grep -c '^<http' linkedart.ttl || echo 0) triples"
echo "New: $(grep -c '^<http' linkedart_new.ttl) triples"

# Check for new entity types
echo "=== New Entity Types ==="
grep -E "E54_Dimension|E42_Identifier|E52_Time-Span.*Production|E8_Acquisition|E26_Physical_Feature" linkedart_new.ttl | wc -l
```

You should see significantly more triples in the new output due to:
- Dimensions for each object
- Identifiers (object numbers)
- Timespans with structured dates
- Classifications and styles
- Departments and divisions
- Color features
- Acquisition events
- Additional descriptions

## Step 6: Inspect a Complete Object

Pick an object and see its full CRM representation:

```bash
# Find an object ID
grep -m 1 "stg:objectid" staging.ttl | grep -o '[0-9]\{6\}'

# See its complete CRM representation (replace 262056 with your object ID)
grep -A 100 "ham:262056" linkedart_new.ttl | less
```

You should see a rich graph with:
- Core object (E22_Human-Made_Object)
- Production event (E12_Production)
- Timespan with dates (E52_Time-Span)
- Dimensions (E54_Dimension)
- Identifiers (E42_Identifier)
- Classifications (E55_Type)
- Department (E74_Group)
- Colors (E26_Physical_Feature)
- Acquisition (E8_Acquisition)
- Descriptions and notes (E33_Linguistic_Object)
- Materials and techniques
- IIIF manifests

## Expected Results Summary

### Before (6 templates)
- Basic object structure
- Production events
- Materials
- Techniques
- Representations
- Notes (credit line, provenance)

### After (14 templates) ✨
All of the above **PLUS**:
- Physical dimensions
- Multiple descriptions (description, commentary, labels)
- Object identifiers
- Structured temporal data (timespan with begin/end)
- Classifications and styles
- Institutional context (departments)
- Color information
- Acquisition/accession events

### Metrics to Check

Run these to verify the expansion:

```bash
# Count entities by type
echo "=== Entity Counts ==="
grep -c "crm:E22_Human-Made_Object" linkedart_new.ttl
grep -c "crm:E12_Production" linkedart_new.ttl
grep -c "crm:E52_Time-Span" linkedart_new.ttl
grep -c "crm:E54_Dimension" linkedart_new.ttl
grep -c "crm:E42_Identifier" linkedart_new.ttl
grep -c "crm:E55_Type" linkedart_new.ttl
grep -c "crm:E74_Group" linkedart_new.ttl
grep -c "crm:E26_Physical_Feature" linkedart_new.ttl
grep -c "crm:E8_Acquisition" linkedart_new.ttl
grep -c "crm:E33_Linguistic_Object" linkedart_new.ttl

# Count properties
echo "=== Property Usage ==="
grep -c "crm:P43_has_dimension" linkedart_new.ttl
grep -c "crm:P1_is_identified_by" linkedart_new.ttl
grep -c "crm:P4_has_time-span" linkedart_new.ttl
grep -c "crm:P82a_begin_of_the_begin" linkedart_new.ttl
grep -c "crm:P49_has_former_or_current_keeper" linkedart_new.ttl
grep -c "crm:P56_bears_feature" linkedart_new.ttl
grep -c "crm:P24i_changed_ownership_through" linkedart_new.ttl
```

## Troubleshooting

### If templates fail
Check the error message - it will indicate which template failed and why. Common issues:
- Syntax error in SPARQL
- Missing namespace prefix
- Invalid IRI construction

### If validation fails
SHACL will report which constraints are violated:
- Check that all required properties are present
- Verify entity types are correct
- Ensure cardinality constraints are met

### If output looks wrong
- Check staging.ttl has the expected stg: properties
- Verify template order (they should run 01 through 14)
- Look for error messages in the template execution

## Next Steps After Validation

Once everything validates correctly:

1. **Compare outputs**: Use a diff tool to see what changed
2. **Spot check objects**: Manually verify a few objects look correct
3. **Load into GraphDB**: Test in a triplestore
4. **Run queries**: Test SPARQL queries against the new structure
5. **Update documentation**: Document any findings or issues

## Performance Notes

- Staging generation: ~1-2 seconds per 100 objects
- Template application: ~5-10 seconds for all 14 templates
- SHACL validation: ~2-5 seconds
- Total pipeline: < 30 seconds for typical batch

## Success Criteria

✅ All 14 templates execute without errors
✅ SHACL validation passes
✅ New entity types present in output
✅ Object count matches staging
✅ No duplicate IRIs
✅ All dates in correct format (xsd:gYear)
✅ All required properties present
✅ Significantly more triples than before (2-3x)

When all criteria are met, the pipeline is working correctly! 🎉

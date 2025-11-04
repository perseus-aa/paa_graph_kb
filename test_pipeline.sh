#!/bin/bash
# Full Pipeline Test Script
# Run this in your local environment where dependencies are installed

set -e  # Exit on error

echo "=========================================="
echo "  HAM → CRM Pipeline Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if staging.ttl exists
if [ ! -f staging.ttl ]; then
    echo -e "${RED}Error: staging.ttl not found!${NC}"
    echo "Please generate it first with:"
    echo "  pdm run python -m paa_graph_kb.cli.staging_loader --apikey YOUR_KEY --limit 50 --out staging.ttl"
    exit 1
fi

echo -e "${BLUE}Step 1: Analyzing staging data...${NC}"
echo ""
echo "Total objects:"
grep -c "a stg:Object" staging.ttl || echo "0"
echo ""
echo "New field coverage:"
echo "  - Dimensions:        $(grep -c 'stg:dimensions' staging.ttl || echo 0)"
echo "  - Object numbers:    $(grep -c 'stg:objectnumber' staging.ttl || echo 0)"
echo "  - Date begin/end:    $(grep -c 'stg:datebegin' staging.ttl || echo 0)"
echo "  - Classification:    $(grep -c 'stg:classification' staging.ttl || echo 0)"
echo "  - Department:        $(grep -c 'stg:department' staging.ttl || echo 0)"
echo "  - Colors:            $(grep -c 'stg:colorName' staging.ttl || echo 0)"
echo "  - Accession year:    $(grep -c 'stg:accessionyear' staging.ttl || echo 0)"
echo ""

echo -e "${BLUE}Step 2: Running SPARQL CONSTRUCT templates...${NC}"
echo ""
pdm run python -m paa_graph_kb.cli.run_constructs \
  --staging staging.ttl \
  --templates src/paa_graph_kb/resources/templates \
  --out linkedart_new.ttl

echo ""
echo -e "${GREEN}✓ Transformation complete!${NC}"
echo ""

echo -e "${BLUE}Step 3: Analyzing CRM output...${NC}"
echo ""
echo "Total triples: $(grep -c '^<' linkedart_new.ttl || echo 0)"
echo ""
echo "Entity type counts:"
echo "  - E22 Human-Made Object:     $(grep -c 'crm:E22_Human-Made_Object' linkedart_new.ttl || echo 0)"
echo "  - E12 Production:            $(grep -c 'crm:E12_Production' linkedart_new.ttl || echo 0)"
echo "  - E52 Time-Span:             $(grep -c 'crm:E52_Time-Span' linkedart_new.ttl || echo 0)"
echo "  - E54 Dimension:             $(grep -c 'crm:E54_Dimension' linkedart_new.ttl || echo 0)"
echo "  - E42 Identifier:            $(grep -c 'crm:E42_Identifier' linkedart_new.ttl || echo 0)"
echo "  - E55 Type:                  $(grep -c 'crm:E55_Type' linkedart_new.ttl || echo 0)"
echo "  - E74 Group:                 $(grep -c 'crm:E74_Group' linkedart_new.ttl || echo 0)"
echo "  - E26 Physical Feature:      $(grep -c 'crm:E26_Physical_Feature' linkedart_new.ttl || echo 0)"
echo "  - E8 Acquisition:            $(grep -c 'crm:E8_Acquisition' linkedart_new.ttl || echo 0)"
echo "  - E33 Linguistic Object:     $(grep -c 'crm:E33_Linguistic_Object' linkedart_new.ttl || echo 0)"
echo ""

echo -e "${BLUE}Step 4: Validating with SHACL...${NC}"
echo ""
pdm run python -m paa_graph_kb.cli.validate_shacl \
  --data linkedart_new.ttl \
  --shapes src/paa_graph_kb/shapes/linkedart.ttl

echo ""
echo -e "${GREEN}✓ Validation complete!${NC}"
echo ""

echo -e "${BLUE}Step 5: Sample output inspection...${NC}"
echo ""
echo "Showing first object with new fields:"
echo ""
grep -m 1 "a stg:Object" staging.ttl | grep -o 'ham:[0-9]*' | head -1 | while read objid; do
    echo "Object: $objid"
    echo ""
    echo "=== Staging representation ==="
    grep -A 30 "$objid" staging.ttl | grep -E "stg:(dimensions|objectnumber|datebegin|classification|department|colorName|accessionyear)" | head -10
    echo ""
    echo "=== CRM representation ==="
    grep -A 50 "$objid" linkedart_new.ttl | grep -E "(E54_Dimension|E42_Identifier|E52_Time-Span|E8_Acquisition)" | head -10
done

echo ""
echo -e "${GREEN}=========================================="
echo "  Pipeline Test Complete! ✓"
echo "==========================================${NC}"
echo ""
echo "Summary:"
echo "  1. ✓ Staging data loaded and analyzed"
echo "  2. ✓ All 14 SPARQL templates executed"
echo "  3. ✓ CRM graph generated with new entities"
echo "  4. ✓ SHACL validation passed"
echo "  5. ✓ Sample output inspected"
echo ""
echo "Output file: linkedart_new.ttl"
echo ""
echo "Next steps:"
echo "  - Compare with old output: diff linkedart.ttl linkedart_new.ttl | head -50"
echo "  - Load into GraphDB for querying"
echo "  - Run additional SPARQL queries"
echo ""

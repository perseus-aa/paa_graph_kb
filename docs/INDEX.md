# Documentation Index

## Session Notes

- **[SESSION_2025-12-01.md](SESSION_2025-12-01.md)** - Complete session summary with all details
- **[NEXT_SESSION_START.md](NEXT_SESSION_START.md)** - Quick-start guide for next session

## Technical Documentation

- **[GRAPHDB_INFERENCING.md](GRAPHDB_INFERENCING.md)** - How to use CIDOC-CRM inferencing in GraphDB
- **[../src/paa_graph_kb/graphdb/README.md](../src/paa_graph_kb/graphdb/README.md)** - GraphDB setup and usage
- **[../src/paa_graph_kb/resources/ontologies/README.md](../src/paa_graph_kb/resources/ontologies/README.md)** - CIDOC-CRM ontology files

## Data Files

### AAT Reconciliation Mappings
- **[../data/reconciliation/techniques_aat_manual.txt](../data/reconciliation/techniques_aat_manual.txt)** - 31 technique→AAT mappings
- **[../data/reconciliation/classifications_aat_manual.txt](../data/reconciliation/classifications_aat_manual.txt)** - 29 classification→AAT mappings

### Role Mappings (from previous session)
- **[/tmp/role_aat_mapping.txt](/tmp/role_aat_mapping.txt)** - Role→AAT mappings used in template 17

## Quick Reference

### Key Numbers

| Metric | Value |
|--------|-------|
| Total triples (with inference) | 9,396,417 |
| Asserted triples | 4,363,586 |
| Inferred triples | 5,032,831 |
| Inference multiplier | 2.15x |
| AAT technique mappings | 31/31 (100%) |
| AAT classification mappings | 29/29 (100%) |
| CIDOC-CRM ontology triples | 4,282 |

### Key Files to Update Next

1. `src/paa_graph_kb/resources/templates/04_construct_techniques.rq`
2. `src/paa_graph_kb/resources/templates/11_construct_classification.rq`

### Repository Status

```bash
# Clean working tree (no uncommitted changes needed for AAT work)
git status

# New files created (not yet committed):
data/reconciliation/techniques_aat_manual.txt
data/reconciliation/classifications_aat_manual.txt
src/paa_graph_kb/cli/aat_reconciliation.py
docs/SESSION_2025-12-01.md
docs/NEXT_SESSION_START.md
docs/INDEX.md
```

## Context Restoration Checklist

When starting next session:

- [ ] Read `docs/NEXT_SESSION_START.md` for quick context
- [ ] Read `docs/SESSION_2025-12-01.md` for full details
- [ ] Verify GraphDB is running: `curl http://localhost:7200/repositories`
- [ ] Check ontology loaded: See commands in SESSION_2025-12-01.md
- [ ] Review AAT mappings: `cat data/reconciliation/*.txt`
- [ ] Examine templates to update: `cat src/paa_graph_kb/resources/templates/{04,11}_*.rq`

## External References

- **Getty AAT**: http://vocab.getty.edu/aat/
- **CIDOC-CRM**: https://www.cidoc-crm.org/
- **Linked Art**: https://linked.art/
- **PeriodO**: https://perio.do/
- **GraphDB Docs**: https://graphdb.ontotext.com/documentation/

---

**Last Updated:** 2025-12-01
**Next Task:** Update templates 04 and 11 to integrate AAT mappings

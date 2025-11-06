# CONSTRUCT Starter Kit — GraphDB Notes

## Quick start (local dev with rdflib)
1) Generate staging from HAM:
```
python staging_loader.py --apikey YOUR_KEY --params culture=Greek hasimage=1 --limit 50 --out staging.ttl
```
2) Build Linked Art:
```
python run_constructs.py --staging staging.ttl --templates . --out linkedart.ttl
```
3) Validate:
```
pip install pyshacl
python validate_shacl.py --data linkedart.ttl --shapes shapes_linkedart.ttl
```

## GraphDB
### Setup
1. Copy `graphdb_env.example` to `graphdb_env` and configure your GraphDB connection:
```bash
cd src/paa_graph_kb/graphdb
cp graphdb_env.example graphdb_env
# Edit graphdb_env to set GRAPHDB_BASE, REPOSITORY, etc.
```

### Loading Data
- Load staging (run from repository root):
```bash
src/paa_graph_kb/graphdb/load_staging.sh staging.ttl
```
Or from the `src/paa_graph_kb` directory:
```bash
graphdb/load_staging.sh ../staging.ttl
```
- Apply CONSTRUCT templates to generate Linked Art (run from repository root):
```bash
src/paa_graph_kb/graphdb/run_constructs.sh src/paa_graph_kb/templates
```
Or from the `src/paa_graph_kb` directory:
```bash
graphdb/run_constructs.sh templates
```

This will execute each `*.rq` SPARQL CONSTRUCT query and load the results into the configured `LINKEDART_GRAPH` in GraphDB.

> Note: Alternatively, you can open each `*.rq` in GraphDB Workbench and execute manually against the repository.

## Design
- Deterministic IRIs with SHA256 of salient keys.
- No blank nodes for appellations/notes (mint by value).
- Period/place prefer HAM authority IRIs when present.

## Next steps
- Add more templates (measurements, exhibitions, agents).
- Add reconciliation step for external AAT/Geonames alignment.
- Add SHACL shapes for material/technique constraints and IIIF.

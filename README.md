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
- Copy `graphdb/graphdb_env.example` to `graphdb/graphdb_env` and set values.
- Load staging:
```
graphdb/load_staging.sh ../staging.ttl
```
- Apply templates:
  - For now, open each `*.rq` in GraphDB Workbench and execute against the repository.
  - Target a **separate named graph** for results, e.g. `<http://aa.perseus.org/graph/linkedart/HAM>`.

> Note: Automating CONSTRUCT→INSERT via REST requires wrapping each template in an `INSERT { GRAPH <...> { ... } } WHERE { ... }` form. Some templates may need minor rewrites. The `run_constructs.sh` file includes a hint and should be adapted to your deployment.

## Design
- Deterministic IRIs with SHA256 of salient keys.
- No blank nodes for appellations/notes (mint by value).
- Period/place prefer HAM authority IRIs when present.

## Next steps
- Add more templates (measurements, exhibitions, agents).
- Add reconciliation step for external AAT/Geonames alignment.
- Add SHACL shapes for material/technique constraints and IIIF.

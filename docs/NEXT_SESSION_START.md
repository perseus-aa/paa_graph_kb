# Quick Start for Next Session

## TL;DR - Where We Left Off

✅ **Completed:**
- AAT Reconciliation verified.
- **Fixed Perseus Image Linking:** New template `25_link_perseus_images.rq` links Objects to Images via name matching.
- **Created IIIF Generator:** `src/paa_graph_kb/cli/iiif_manifest.py` generates valid IIIF v3 manifests.

## Quick Restore

```bash
# 1. Ensure GraphDB is running
curl http://localhost:7200/repositories

# 2. (Optional) Re-run constructs if data is stale
make graphdb-run-constructs
```

## Using the IIIF Tool

```bash
# Generate a manifest for a known object URI
# (Use browse_kb to find URIs)
python -m paa_graph_kb.cli.browse_kb search "red-figure"

# Generate
python -m paa_graph_kb.cli.iiif_manifest <URI_FROM_ABOVE> -o manifest.json
```

## Next Goals

1. **Test HAM Manifests:** Verify the tool works for Harvard Art Museums objects too.
2. **Batch Generation:** Consider generating static manifests for the whole collection.
3. **Viewer:** Maybe set up a simple HTML page with Mirador/UV to view these manifests.
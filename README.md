# PAA Graph Knowledge Base

Transforms Harvard Art Museums (HAM) data into Linked Art using SPARQL CONSTRUCT templates.

## Quick Start (Using Makefile)

The easiest way to use this project is via the Makefile:

```bash
# First time setup - configure your API key
make setup-env
# Edit .env to add your HAM_APIKEY

# See all available commands
make help

# Complete local workflow (using rdflib)
make local-all

# Complete GraphDB workflow
make setup-graphdb  # First time only - edit graphdb_env after
make graphdb-all
```

## Detailed Usage

### Local Development Workflow (using rdflib)

**Using Makefile (recommended):**
```bash
# First time: setup .env file
make setup-env
# Edit .env to add your HAM_APIKEY

# Run complete workflow (uses .env automatically)
make local-all

# Or run individual steps
make staging                    # Uses .env
make staging HAM_LIMIT=200     # Override default limit
make linkedart-local
make validate

# Override .env settings on command line
make staging HAM_APIKEY=different_key HAM_LIMIT=100
```

**Manual commands:**
1) Generate staging from HAM (reads HAM_APIKEY from .env):
```bash
# First time: copy dotenv to .env and edit
cp dotenv .env
# Edit .env to set HAM_APIKEY

# Run staging loader (automatically loads from .env)
python -m paa_graph_kb.cli.staging_loader \
  --params culture=Greek hasimage=1 \
  --limit 50 \
  --out staging.ttl

# Or override .env with command-line argument
python -m paa_graph_kb.cli.staging_loader \
  --apikey YOUR_KEY \
  --params culture=Greek hasimage=1 \
  --limit 50 \
  --out staging.ttl
```
2) Build Linked Art:
```bash
python -m paa_graph_kb.run_constructs \
  --staging staging.ttl \
  --templates src/paa_graph_kb/resources/templates \
  --out linkedart.ttl
```
3) Validate:
```bash
python -m paa_graph_kb.cli.validate_shacl \
  --data linkedart.ttl \
  --shapes src/paa_graph_kb/shapes/linkedart.ttl
```

### GraphDB Workflow

**Using Makefile (recommended):**
```bash
# First time setup
make setup-graphdb
# Edit src/paa_graph_kb/graphdb/graphdb_env with your GraphDB connection details

# Run complete GraphDB workflow
make graphdb-all

# Or run individual steps
make graphdb-load-staging
make graphdb-run-constructs
```

**Manual commands:**

See [src/paa_graph_kb/graphdb/README.md](src/paa_graph_kb/graphdb/README.md) for detailed GraphDB setup and usage instructions.

## Utilities

```bash
# Remove generated TTL files
make clean
```

## Design
- Deterministic IRIs with SHA256 of salient keys.
- No blank nodes for appellations/notes (mint by value).
- Period/place prefer HAM authority IRIs when present.
- Enhanced dimension template with AAT typing and Linked Art patterns.

## Next steps
- Add more templates (exhibitions, agents).
- Enhance measurements template to parse structured dimensions when available.
- Add reconciliation step for external AAT/Geonames alignment.
- Add SHACL shapes for material/technique constraints and IIIF.

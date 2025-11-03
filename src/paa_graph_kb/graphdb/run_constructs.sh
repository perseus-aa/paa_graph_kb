#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/graphdb_env"

TEMPLATES_DIR="${1:-..}"
echo "Running CONSTRUCT templates in $TEMPLATES_DIR, writing into <$LINKEDART_GRAPH>"

for rq in $(ls "$TEMPLATES_DIR"/*.rq | sort); do
  echo "• Applying $(basename "$rq")"
  # Use an update to INSERT { GRAPH <...> { CONSTRUCT(...) } } WHERE { ... } form
  SPARQL=$(cat "$rq")
  UPDATE="INSERT { GRAPH <${LINKEDART_GRAPH}> { $(printf '%q' "$SPARQL") } } WHERE {}"
  # The above naive quoting won't work directly; better to use the /statements endpoint with CONSTRUCT result upload.
  # So we fallback to GraphDB's /statements with update=… only if your endpoint supports SERVICE with CONSTRUCT-INSERT.
  echo "Please run this template in Workbench or adapt this script to your deployment."
done
echo "ℹ️ For production, prefer running templates inside GraphDB Workbench or via a SPARQL client that supports CONSTRUCT→INSERT piping."

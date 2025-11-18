#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/graphdb_env"

# Generic script to load a Turtle file into a named graph
# Usage: ./load_to_graph.sh <ttl_file> <graph_uri>

TTL_FILE="${1:?Error: TTL file path required}"
GRAPH_URI="${2:?Error: Graph URI required}"

echo "Loading $TTL_FILE into <$GRAPH_URI>"

# Check if the Turtle file exists
if [ ! -f "$TTL_FILE" ]; then
  echo "❌ Error: File not found: $TTL_FILE"
  exit 1
fi

# URL-encode the context parameter (encode < > as %3C %3E)
ENCODED_CONTEXT=$(printf '%s' "<$GRAPH_URI>" | sed 's/</%3C/g; s/>/%3E/g')

# Upload to GraphDB with timeout (increased for large files)
# Note: GraphDB returns 204 No Content on success, which is valid
HTTP_CODE=$(curl -s -w "%{http_code}" --max-time 120 -o /dev/null \
  -X POST "$GRAPHDB_BASE/repositories/$REPOSITORY/statements?context=$ENCODED_CONTEXT" \
  -H "Content-Type: text/turtle" \
  --data-binary "@$TTL_FILE")

if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Loaded successfully (HTTP $HTTP_CODE)"
else
  echo "❌ Failed to load. HTTP status: $HTTP_CODE"
  echo "   Is GraphDB running at $GRAPHDB_BASE?"
  exit 1
fi

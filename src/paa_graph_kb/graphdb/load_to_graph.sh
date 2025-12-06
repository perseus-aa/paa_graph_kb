#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/graphdb_env"

# Generic script to load a generic RDF file into a named graph
# Usage: ./load_to_graph.sh <file_path> <graph_uri> [content_type]
# Content-Type defaults to text/turtle if not provided.
# Examples:
#   ./load_to_graph.sh data.ttl urn:graph:mydata
#   ./load_to_graph.sh data.json urn:graph:mydata application/ld+json

DATA_FILE="${1:?Error: File path required}"
GRAPH_URI="${2:?Error: Graph URI required}"
CONTENT_TYPE="${3:-text/turtle}"

echo "Loading $DATA_FILE into <$GRAPH_URI> as $CONTENT_TYPE"

# Check if the file exists
if [ ! -f "$DATA_FILE" ]; then
  echo "❌ Error: File not found: $DATA_FILE"
  exit 1
fi

# URL-encode the context parameter (encode < > as %3C %3E)
ENCODED_CONTEXT=$(printf '%s' "<$GRAPH_URI>" | sed 's/</%3C/g; s/>/%3E/g')

# Upload to GraphDB with timeout (increased for large files)
# Note: GraphDB returns 204 No Content on success, which is valid
HTTP_CODE=$(curl -s -w "%{http_code}" --max-time 120 -o /dev/null \
  -X POST "$GRAPHDB_BASE/repositories/$REPOSITORY/statements?context=$ENCODED_CONTEXT" \
  -H "Content-Type: $CONTENT_TYPE" \
  --data-binary "@$DATA_FILE")

if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Loaded successfully (HTTP $HTTP_CODE)"
else
  echo "❌ Failed to load. HTTP status: $HTTP_CODE"
  echo "   Is GraphDB running at $GRAPHDB_BASE?"
  exit 1
fi
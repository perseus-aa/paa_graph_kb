#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/graphdb_env"

STAGING_TTL="${1:-../staging_sample.ttl}"

echo "Loading staging into <$STAGING_GRAPH> from $STAGING_TTL"

# Check if the Turtle file exists
if [ ! -f "$STAGING_TTL" ]; then
  echo "❌ Error: File not found: $STAGING_TTL"
  exit 1
fi

# URL-encode the context parameter (encode < > as %3C %3E)
ENCODED_CONTEXT=$(printf '%s' "<$STAGING_GRAPH>" | sed 's/</%3C/g; s/>/%3E/g')

# Upload to GraphDB with timeout (increased for large files)
# Note: GraphDB returns 204 No Content on success, which is valid
HTTP_CODE=$(curl -s -w "%{http_code}" --max-time 120 -o /dev/null \
  -X POST "$GRAPHDB_BASE/repositories/$REPOSITORY/statements?context=$ENCODED_CONTEXT" \
  -H "Content-Type: text/turtle" \
  --data-binary "@$STAGING_TTL")

if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Loaded staging successfully (HTTP $HTTP_CODE)"
else
  echo "❌ Failed to load staging. HTTP status: $HTTP_CODE"
  echo "   Is GraphDB running at $GRAPHDB_BASE?"
  exit 1
fi

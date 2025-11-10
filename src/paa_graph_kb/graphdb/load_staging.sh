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
if curl -s -f --max-time 120 -w "\n" \
  -X POST "$GRAPHDB_BASE/repositories/$REPOSITORY/statements?context=$ENCODED_CONTEXT" \
  -H "Content-Type: text/turtle" \
  --data-binary "@$STAGING_TTL"; then
  echo "✅ Loaded staging successfully"
else
  echo "❌ Failed to load staging. Is GraphDB running at $GRAPHDB_BASE?"
  exit 1
fi

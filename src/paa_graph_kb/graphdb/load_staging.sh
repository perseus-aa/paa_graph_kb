#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/graphdb_env"

STAGING_TTL="${1:-../staging_sample.ttl}"

echo "Loading staging into <$STAGING_GRAPH> from $STAGING_TTL"
curl -s -X POST "$GRAPHDB_BASE/repositories/$REPOSITORY/statements"   -H "Content-Type: text/turtle"   --data-binary "@$STAGING_TTL"   --data-urlencode "context=<$STAGING_GRAPH>"
echo
echo "✅ Loaded staging"

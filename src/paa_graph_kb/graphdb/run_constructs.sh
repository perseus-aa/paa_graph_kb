#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/graphdb_env"

TEMPLATES_DIR="${1:-..}"
echo "Running CONSTRUCT templates in $TEMPLATES_DIR, writing into <$LINKEDART_GRAPH>"
echo

# URL-encode the target graph (encode < > as %3C %3E)
ENCODED_GRAPH=$(printf '%s' "<$LINKEDART_GRAPH>" | sed 's/</%3C/g; s/>/%3E/g')

# Process each .rq file
shopt -s nullglob
for rq in "$TEMPLATES_DIR"/*.rq; do
  [ -f "$rq" ] || continue

  echo "• Applying $(basename "$rq")"

  # Execute CONSTRUCT query and upload results to the target graph
  # This uses a two-step approach:
  # 1. Execute CONSTRUCT query with Accept: text/turtle
  # 2. POST the result to the statements endpoint with the target context

  TEMP_TTL=$(mktemp)
  trap "rm -f $TEMP_TTL" EXIT

  # Execute CONSTRUCT query
  if curl -s -f --max-time 60 \
    -X POST "$GRAPHDB_BASE/repositories/$REPOSITORY" \
    -H "Content-Type: application/sparql-query" \
    -H "Accept: text/turtle" \
    --data-binary "@$rq" \
    -o "$TEMP_TTL"; then

    # Upload results to target graph
    if curl -s -f --max-time 30 -w "\n" \
      -X POST "$GRAPHDB_BASE/repositories/$REPOSITORY/statements?context=$ENCODED_GRAPH" \
      -H "Content-Type: text/turtle" \
      --data-binary "@$TEMP_TTL" > /dev/null; then
      echo "  ✅ Success"
    else
      echo "  ❌ Failed to upload results. Is GraphDB running at $GRAPHDB_BASE?"
      exit 1
    fi
  else
    echo "  ❌ Failed to execute CONSTRUCT query. Is GraphDB running at $GRAPHDB_BASE?"
    exit 1
  fi

  rm -f "$TEMP_TTL"
done

echo
echo "✅ All templates applied successfully"

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/examples/cli_fallback.sh"

REGISTRY="markpact://examples/22_markpact_weather/README.md"
FLOW_REF="${REGISTRY}#weather-health"

echo "== touri list $REGISTRY =="
run_cli touri list "$REGISTRY"

echo
echo "== touri call weather://markpact/Gdansk/14/html =="
run_cli touri call weather://markpact/Gdansk/14/html --registry "$REGISTRY"

echo
echo "== uri2flow expand $FLOW_REF =="
OUT="/tmp/weather-health.uri.graph.yaml"
run_cli uri2flow expand "$FLOW_REF" --out "$OUT"
grep -E "workflow_graph|browser://chrome/page/open" "$OUT"

echo
echo "== uri3 validate-workflow $OUT =="
run_cli uri3 validate-workflow "$OUT"

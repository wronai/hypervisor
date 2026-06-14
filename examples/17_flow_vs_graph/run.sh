#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/examples/cli_fallback.sh"

echo "=== 1. nl2uri flow ==="
run_cli nl2uri flow -p "wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome" \
  > /tmp/weather.uri.flow.yaml

echo "=== 2. uri3 expand-flow ==="
run_cli uri3 expand-flow examples/17_flow_vs_graph/weather.uri.flow.yaml \
  --out output/weather.uri.graph.yaml

echo "=== 3. uri3 run-flow dry-run ==="
run_cli uri3 run-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --dry-run

echo "=== 4. uri3 run-flow mock execute ==="
run_cli uri3 run-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --approve --browser mock

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROMPT="$(cat "$ROOT/examples/18_llm_flow_planner/prompt.txt")"
FLOW="/tmp/weather.uri.flow.yaml"

cd "$ROOT"
source "$ROOT/scripts/examples/cli_fallback.sh"
mkdir -p output

echo "== rule-based compact flow =="
run_cli nl2uri flow -p "$PROMPT" --validate > "$FLOW"
echo "wrote $FLOW"

echo
echo "== uri3 expand-flow + dry-run =="
run_cli uri3 expand-flow "$FLOW" --out output/weather.uri.graph.yaml
run_cli uri3 run-flow "$FLOW" --dry-run

if [[ -n "${OPENROUTER_API_KEY:-}" ]]; then
  echo
  echo "== LLM compact flow (--llm) =="
  run_cli nl2uri flow -p "$PROMPT" --llm --validate
else
  echo
  echo "Skipping LLM demo: OPENROUTER_API_KEY is not set"
fi

echo
echo "== mock execute =="
run_cli uri3 run-flow "$FLOW" --approve --browser mock

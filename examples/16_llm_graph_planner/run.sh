#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/examples/cli_fallback.sh"
PROMPT="$(cat "$ROOT/examples/16_llm_graph_planner/prompt.txt")"

echo "== rule-based graph =="
run_cli nl2uri graph -p "$PROMPT" --validate --dry-run

if [[ -n "${OPENROUTER_API_KEY:-}" ]]; then
  echo
  echo "== LLM graph (--llm) =="
  run_cli nl2uri graph -p "$PROMPT" --llm --validate --dry-run
else
  echo
  echo "Skipping LLM demo: OPENROUTER_API_KEY is not set"
fi

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/examples/cli_fallback.sh"
GRAPH="examples/14_workflow_executor_mock/task_graph.yaml"

echo "=== validate ==="
run_cli uri3 validate-workflow "$GRAPH"

echo
echo "=== plan ==="
run_cli uri3 plan-workflow "$GRAPH" | head -n 25

echo
echo "=== dry-run execute ==="
run_cli uri3 run-workflow "$GRAPH" --dry-run | head -n 40

echo
echo "=== execute without approve (should block command node) ==="
if run_cli uri3 run-workflow "$GRAPH"; then
  echo "unexpected success"
  exit 1
else
  echo "blocked as expected"
fi

echo
echo "=== execute with approve (mock adapters) ==="
run_cli uri3 run-workflow "$GRAPH" --approve --browser mock

echo
echo "=== event log ==="
wc -l output/events/workflows/check-agent-health.jsonl
tail -n 3 output/events/workflows/check-agent-health.jsonl

echo
echo "Done."

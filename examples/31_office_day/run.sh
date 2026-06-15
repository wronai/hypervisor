#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/examples/cli_fallback.sh"
GRAPH="examples/31_office_day/task_graph.yaml"
PROMPT_FILE="examples/31_office_day/prompt.txt"
TASKS=(
  "examples/31_office_day/portal_report.browser.yaml"
  "examples/31_office_day/invoice_review.pcwin.yaml"
  "examples/31_office_day/bank_token.android.yaml"
)

echo "=== persona prompt ==="
cat "$PROMPT_FILE"

echo
echo "=== nl2uri classify ==="
run_cli nl2uri classify -p "$(cat "$PROMPT_FILE")"

echo "=== validate ==="
run_cli uri3 validate-workflow "$GRAPH"

echo
echo "=== dry-run ==="
run_cli uri3 run-workflow "$GRAPH" --dry-run | head -n 30

echo
echo "=== execute mock (browser + android adapters) ==="
run_cli uri3 run-workflow "$GRAPH" --approve --browser mock

for task in "${TASKS[@]}"; do
  echo
  echo "=== uri2ops validate: $task ==="
  python -m uri2ops.cli validate "$task"

  echo
  echo "=== uri2ops plan: $task ==="
  python -m uri2ops.cli plan "$task" | head -n 80

  echo
  echo "=== uri2ops run mock: $task ==="
  python -m uri2ops.cli run "$task" --adapter mock --approve | head -n 120
done

echo
echo "=== artifacts ==="
find output/artifacts/operator output/events/operator \
  \( -path '*office-*' -o -path '*open_supplier_portal*' -o -path '*read_report_page*' \) \
  -type f 2>/dev/null | tail -n 30 || true

echo
echo "Done — office day Marta (portal → faktury → bank checkpoint mock)."

#!/usr/bin/env bash
# Landing-page office workflow URIs — supplier report, ZUS portal, bank batch (mock).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/examples/cli_fallback.sh"

GRAPHS=(
  "examples/33_office_workflows/supplier_report_monthly.yaml"
  "examples/33_office_workflows/portal_zus_form.yaml"
  "examples/33_office_workflows/bank_batch_transfer.yaml"
)
WORKFLOWS=(
  "workflow://office/supplier-report/monthly"
  "workflow://portal/zus-form/dry-run"
  "workflow://portal/zus-form"
  "workflow://bank/batch-transfer/dry-run"
  "workflow://invoices/batch/dry-run"
)

echo "== 33_office_workflows =="
echo "=== chat prompts (landing cards) ==="
run_cli uri ask "Wejdź na stronę dostawcy, pobierz raport CSV za ten miesiąc i zapisz w rozliczeniach." | head -n 20
run_cli uri ask "Zaloguj się do portalu klienta, uzupełnij formularz ZUS i wyślij — najpierw pokaż podgląd." | head -n 20

for graph in "${GRAPHS[@]}"; do
  echo
  echo "=== validate: $graph ==="
  run_cli uri3 validate-workflow "$graph"
  echo "=== dry-run: $graph ==="
  run_cli uri3 run-workflow "$graph" --dry-run | head -n 25
done

for wf in "${WORKFLOWS[@]}"; do
  echo
  echo "=== uri run dry-run: $wf ==="
  run_cli uri run "$wf" --dry-run | head -n 20
done

echo
echo "PASS examples/33_office_workflows"

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/examples/cli_fallback.sh"

echo "== 1. Call URI =="
run_cli uri call shell://echo --payload '{"args":["golden-path"]}' --dry-run

echo "== 2. Agent status (may skip if agent not running) =="
run_cli uri agent status weather-map-agent.local || true

echo "== 3. Ask — ecosystem intent =="
run_cli uri ask "stwórz agenta pogodowego z healthcheckiem" | head -20

echo "== 4. Ask — dashboard-agent intent =="
run_cli uri ask "stwórz web UI agenta hypervisor-dashboard do pokazywania procesów hypervisora" | head -25

echo "== 5. Repair diagnose (read-only, may report degraded agent) =="
run_cli uri repair diagnose weather-map-agent.local || true

echo "== 6. Doctor (informational; optional deps may warn) =="
run_cli uri doctor || true

echo "OK: golden path smoke complete"

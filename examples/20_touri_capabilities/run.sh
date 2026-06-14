#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/examples/cli_fallback.sh"
bash scripts/ci/ensure_editable_install.sh
run_cli touri validate examples/20_touri_capabilities/weather_forecast.uri.capability.yaml
run_cli touri list examples/20_touri_capabilities
run_cli touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities
run_cli touri call echo://Adam --registry examples/20_touri_capabilities

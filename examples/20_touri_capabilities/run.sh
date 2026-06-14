#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
bash scripts/ci/ensure_editable_install.sh
touri validate examples/20_touri_capabilities/weather_forecast.uri.capability.yaml
touri list examples/20_touri_capabilities
touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities
touri call echo://Adam --registry examples/20_touri_capabilities

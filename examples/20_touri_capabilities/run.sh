#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
# Install workspace deps (touri pulls uri2pact, uri2run, uri2verify from packages/*)
pip install -q -e "$ROOT/packages/uri2pact" -e "$ROOT/packages/uri2run" -e "$ROOT/packages/uri2verify" -e "$ROOT/packages/touri"
touri validate examples/20_touri_capabilities/weather_forecast.uri.capability.yaml
touri list examples/20_touri_capabilities
touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities
touri call echo://Adam --registry examples/20_touri_capabilities

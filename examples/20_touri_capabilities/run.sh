#!/usr/bin/env bash
set -euo pipefail
pip install -e packages/touri
touri validate examples/20_touri_capabilities/weather_forecast.uri.capability.yaml
touri list examples/20_touri_capabilities
touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities
touri call echo://Adam --registry examples/20_touri_capabilities

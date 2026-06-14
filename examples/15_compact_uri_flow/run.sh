#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

python -m uri2flow.cli validate examples/15_compact_uri_flow/weather.uri.flow.yaml
python -m uri2flow.cli expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
cat output/weather.uri.graph.yaml

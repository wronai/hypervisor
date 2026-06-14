#!/usr/bin/env bash
# Ensure monorepo editable install when examples run outside a prepared venv.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${PY:-python}"

if "$PY" -c "import touri, uri2run, uri3, uri2ops, uri2flow, uri2verify, uri2pact, urigen" 2>/dev/null; then
  exit 0
fi

echo "Installing workspace packages (editable)…" >&2
pip install -q -e "$ROOT"

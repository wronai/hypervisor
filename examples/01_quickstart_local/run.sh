#!/usr/bin/env bash
set -euo pipefail
pip install -e .[dev]
make uri-tree
make validate
make graph
pytest -q

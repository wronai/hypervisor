#!/usr/bin/env bash

if [[ -z "${ROOT:-}" ]]; then
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fi

if [[ -d "$ROOT/packages" ]]; then
  PACKAGE_PYTHONPATH="$(find "$ROOT/packages" -maxdepth 1 -mindepth 1 -type d | paste -sd: -)"
  export PYTHONPATH="$PACKAGE_PYTHONPATH${PYTHONPATH:+:$PYTHONPATH}"
fi

run_cli() {
  local name="$1"
  shift

  if command -v "$name" >/dev/null 2>&1; then
    "$name" "$@"
    return
  fi

  local module=""
  case "$name" in
    hypervisor) module="hypervisor.cli" ;;
    nl2uri) module="nl2uri.cli" ;;
    touri) module="touri.cli" ;;
    uri) module="urish.cli" ;;
    uri2flow) module="uri2flow.cli" ;;
    uri3) module="uri3.cli" ;;
    urish) module="urish.cli" ;;
    *) echo "unknown CLI fallback: $name" >&2; return 127 ;;
  esac

  local python_bin="${PY:-}"
  if [[ -z "$python_bin" ]]; then
    if command -v python >/dev/null 2>&1; then
      python_bin="python"
    elif command -v python3 >/dev/null 2>&1; then
      python_bin="python3"
    else
      echo "python not found" >&2
      return 127
    fi
  fi

  URI_EXAMPLE_CLI_MODULE="$module" "$python_bin" - "$@" <<'PY'
from __future__ import annotations

import importlib
import inspect
import os
import sys

module = importlib.import_module(os.environ["URI_EXAMPLE_CLI_MODULE"])
main = getattr(module, "main")
if inspect.signature(main).parameters:
    result = main(sys.argv[1:])
else:
    result = main()
raise SystemExit(0 if result is None else result)
PY
}

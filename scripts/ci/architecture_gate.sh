#!/usr/bin/env bash
# Architecture gate: boundary tests + uri3 doctor governance checks.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PY="${PY:-python}"
PACKAGE_PATHS=()
for package_dir in "${ROOT}"/packages/*; do
  if [ -d "$package_dir" ]; then
    PACKAGE_PATHS+=("$package_dir")
  fi
done
PACKAGE_PYTHONPATH="$(IFS=:; echo "${PACKAGE_PATHS[*]}"):${ROOT}/examples/21_touri_voice"
export PYTHONPATH="${PACKAGE_PYTHONPATH}${PYTHONPATH:+:${PYTHONPATH}}"

if [ -x "${ROOT}/.venv/bin/pytest" ]; then
  PYTEST="${ROOT}/.venv/bin/pytest"
  URI3="${ROOT}/.venv/bin/uri3"
else
  PYTEST="pytest"
  URI3="uri3"
fi

echo "== architecture tests =="
"$PYTEST" tests/architecture -q

echo "== uri3 doctor =="
export DOCTOR_JSON="$("$URI3" doctor --json)"
echo "$DOCTOR_JSON"
"$PY" <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["DOCTOR_JSON"])
checks = payload.get("checks") or []
failed = [item for item in checks if not item.get("ok")]
if payload.get("ok"):
    print(f"uri3 doctor ok ({len(checks)} checks)")
    sys.exit(0)
print("uri3 doctor FAILED")
for item in failed:
    detail = item.get("violation_count") or item.get("failures") or item.get("errors") or item.get("mismatches")
    print(f"  - {item.get('id')}: {detail}")
sys.exit(1)
PY

echo "architecture gate: ok"

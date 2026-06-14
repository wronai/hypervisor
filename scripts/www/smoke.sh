#!/usr/bin/env bash
# Smoke test for www chat API + static UI.
set -euo pipefail

BASE="${1:-http://localhost:8788}"

echo "→ GET $BASE/health"
curl -fsS "$BASE/health" | grep -q '"agent":"hypervisor-dashboard"'

echo "→ GET $BASE/www/"
curl -fsS "$BASE/www/" | grep -q "Hypervisor Chat"

echo "→ POST $BASE/api/ask"
curl -fsS -X POST "$BASE/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"stwórz dashboard agenta hypervisor"}' \
  | grep -q "dashboard-agent"

echo "smoke ok — $BASE/www/"

#!/usr/bin/env bash
# Smoke test for www chat API + static UI.
set -euo pipefail

BASE="${1:-http://localhost:8788}"

echo "→ GET $BASE/health"
curl -fsS "$BASE/health" | grep -q '"agent":"hypervisor-dashboard"'

echo "→ GET $BASE/www/"
curl -fsS "$BASE/www/" | grep -q "Taskinity"
curl -fsS "$BASE/www/" | grep -q "Autonomia w praktyce"
curl -fsS "$BASE/www/" | grep -q "tour-live-strip"
curl -fsS "$BASE/www/" | grep -q "tour-copy-chat"
curl -fsS "$BASE/www/" | grep -q "scenario-lab"
curl -fsS "$BASE/www/" | grep -q "scenario-terminal"
curl -fsS "$BASE/www/" | grep -q "system-map"
curl -fsS "$BASE/www/" | grep -q "Deployment registry"
curl -fsS "$BASE/www/chat.html" | grep -q "Taskinity Chat"
curl -fsS "$BASE/www/chat.html" | grep -q "copy-chat-btn"

echo "→ POST $BASE/api/ask"
curl -fsS -X POST "$BASE/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"stwórz dashboard agenta hypervisor"}' \
  | grep -q "dashboard-agent"

echo "smoke ok — $BASE/www/"

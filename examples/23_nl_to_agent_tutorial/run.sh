#!/usr/bin/env bash
# End-to-end tutorial: natural language → URI plan → execution → agent HTTP.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-$LANG}"
mkdir -p output/tutorial

# head/tail w pipe kończy wcześniej — nie traktuj SIGPIPE jako błąd
set +o pipefail

TASK_PROMPT='otwórz Chrome i sprawdź localhost:8101/health'
FLOW_PROMPT="$(cat examples/23_nl_to_agent_tutorial/prompt.txt)"
OUT=output/tutorial

section() {
  printf '\n══════════════════════════════════════════════════\n'
  printf '  %s\n' "$1"
  printf '══════════════════════════════════════════════════\n\n'
}

section "0. Wymagania"
if ! command -v nl2uri >/dev/null 2>&1; then
  echo "Instalacja pakietów dev…"
  pip install -e '.[dev]' >/dev/null
fi
echo "Repo: $ROOT"
echo "UTF-8: LANG=$LANG"

section "1. Rejestry URI"
echo "── Scheme registry (uri3) — poprawne schematy URI:"
uri3 list --schemes | head -n 12
echo "  … (więcej: uri3 list --schemes)"

echo
echo "── Operation registry (uri2ops) — dozwolone operacje na URI:"
uri2ops registry list | head -n 8
echo "  Przykład: uri2ops operations describe browser open"

echo
echo "── Deployment registry (hypervisor) — gdzie działają agenci:"
hypervisor deployments | head -n 20

section "2. NL → task_graph (operator: Chrome → DOM → assertion)"
echo "Prompt: $TASK_PROMPT"
nl2uri classify -p "$TASK_PROMPT"
nl2uri task -p "$TASK_PROMPT" --validate > "$OUT/task_graph.yaml"
echo "Zapisano: $OUT/task_graph.yaml"
head -n 25 "$OUT/task_graph.yaml"

echo
echo "Plan wykonania (dry-run, command nodes bez --approve są blokowane):"
uri3 plan-workflow "$OUT/task_graph.yaml" | head -n 20

echo
echo "Wykonanie mock (bez prawdziwego Chrome):"
uri3 run-workflow "$OUT/task_graph.yaml" --approve --browser mock | tail -n 5

section "3. NL → uri_flow (sekwencja: generuj agenta → uruchom → health)"
echo "Prompt: $FLOW_PROMPT"
nl2uri classify -p "$FLOW_PROMPT"
nl2uri flow -p "$FLOW_PROMPT" --validate > "$OUT/weather.uri.flow.yaml"
echo "Zapisano: $OUT/weather.uri.flow.yaml"
cat "$OUT/weather.uri.flow.yaml"

echo
echo "Expand → workflow graph:"
uri3 expand-flow "$OUT/weather.uri.flow.yaml" --out "$OUT/weather.uri.graph.yaml"
echo "Zapisano: $OUT/weather.uri.graph.yaml"

echo
echo "Dry-run całego flow:"
uri3 run-flow "$OUT/weather.uri.flow.yaml" --dry-run | head -n 25

echo
echo "Mock execute flow (hypervisor step = plan/dry-run w mock):"
uri3 run-flow "$OUT/weather.uri.flow.yaml" --approve --browser mock | tail -n 5

section "4. Generacja agenta HTTP (nl2a) — jeśli brak artefaktów"
AGENT_DIR="agents/generated/weather_map_agent"
if [[ -d "$AGENT_DIR" && -f deployments/agent_deployments.yaml ]]; then
  echo "Agent już wygenerowany: $AGENT_DIR"
else
  echo "Generuję weather-map agent (nl2a --no-llm)…"
  make nl2a-weather >/dev/null
  make verify >/dev/null
fi
hypervisor deployments | grep -q weather-map-agent.local
echo "Kontrakt: contracts/agents/weather_map_agent.yaml"
echo "Kod:     $AGENT_DIR/"

section "5. Uruchomienie agenta pod URL"

agent_health_ok() {
  local base="$1"
  curl -sf --max-time 2 "${base}/health" 2>/dev/null \
    | python -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('agent')=='weather-map-agent' and d.get('ok') else 1)" 2>/dev/null
}

resolve_running_agent_base() {
  local status_json
  status_json="$(hypervisor agent-status weather-map-agent.local --no-health 2>/dev/null || true)"
  [[ -n "$status_json" ]] || return 1
  printf '%s' "$status_json" | python -c "
import json
import sys

data = json.load(sys.stdin)
state = data.get('runtime_state') or {}
health = state.get('health_uri') or data.get('health_uri')
runtime = str(data.get('runtime_status') or '')
if runtime == 'stale':
    raise SystemExit(2)
if not health:
    raise SystemExit(1)
print(str(health).rstrip('/'))
"
}

RUNTIME_STATUS="$(hypervisor agent-status weather-map-agent.local --no-health 2>/dev/null \
  | python -c "import json,sys; print(json.load(sys.stdin).get('runtime_status',''))" 2>/dev/null || true)"
if [[ "$RUNTIME_STATUS" == "stale" ]]; then
  echo "Czyszczenie nieaktualnego runtime state (stale)…"
  hypervisor stop-agent weather-map-agent.local >/dev/null 2>&1 || true
fi

AGENT_PORT="${TUTORIAL_AGENT_PORT:-}"
AGENT_BASE=""

if EXISTING_BASE="$(resolve_running_agent_base 2>/dev/null || true)" && agent_health_ok "$EXISTING_BASE"; then
  AGENT_BASE="$EXISTING_BASE"
  echo "Agent weather-map już działa — używam $AGENT_BASE"
else
  if [[ -z "$AGENT_PORT" ]]; then
    if agent_health_ok "http://localhost:8101"; then
      AGENT_PORT=8101
    else
      AGENT_PORT="$(python - <<'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
)"
    fi
  fi
  AGENT_BASE="http://localhost:${AGENT_PORT}"

  if agent_health_ok "$AGENT_BASE"; then
    echo "Agent weather-map już odpowiada na $AGENT_BASE"
  elif [[ "$AGENT_PORT" != "8101" ]]; then
    echo "Port 8101 zajęty przez inny serwis — używam --port $AGENT_PORT"
    hypervisor run-agent weather-map-agent.local --detach --port "$AGENT_PORT" | tail -n 20
  else
    echo "Start w tle: hypervisor run-agent weather-map-agent.local --detach"
    hypervisor run-agent weather-map-agent.local --detach | tail -n 20
  fi
fi

for _ in $(seq 1 30); do
  if agent_health_ok "$AGENT_BASE"; then
    break
  fi
  sleep 0.5
done

echo
if agent_health_ok "$AGENT_BASE"; then
  echo "Health ($AGENT_BASE):"
  curl -sf "${AGENT_BASE}/health" | python -m json.tool

  echo
  echo "Agent card (A2A discovery):"
  curl -sf "${AGENT_BASE}/.well-known/agent-card.json" | python -m json.tool | head -n 25

  echo
  echo "Przykład skill (odczyt mapy pogody — wymaga resource runtime na :8000):"
  curl -sf "${AGENT_BASE}/skills/read_weather_map?place=Gdansk&days=14" | python -m json.tool | head -n 15 \
    || echo "  (skill wymaga działającego RESOURCE_RUNTIME_URL — to normalne w tutorialu)"
else
  echo "Nie udało się potwierdzić health agenta na $AGENT_BASE."
  echo "Sprawdź: hypervisor agent-status weather-map-agent.local"
  echo "Jeśli port 8101 jest zajęty: TUTORIAL_AGENT_PORT=8111 bash examples/23_nl_to_agent_tutorial/run.sh"
fi

section "6. Interakcja przez shell"
cat <<'EOF'
# lifecycle agenta
hypervisor agent-status weather-map-agent.local
hypervisor logs weather-map-agent.local --limit 20
hypervisor stop-agent weather-map-agent.local

# operator uri2ops (pojedynczy task YAML)
uri2ops run examples/10_browser_operator/task.health.yaml --adapter mock --approve

# daemon A2A/MCP (rejestr operacji + wykonanie HTTP)
uri2ops serve --port 8791
curl http://127.0.0.1:8791/registry
EOF

section "Gotowe"
set -euo pipefail
echo "Artefakty tutorialu: $OUT/"
echo "Dokumentacja:       examples/23_nl_to_agent_tutorial/README.md"
echo "Pełny indeks:      examples/README.md"

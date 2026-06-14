#!/usr/bin/env bash
# Run all hypervisor examples sequentially and report pass/fail/skip.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="${ROOT}/packages/resource-agent-factory:${ROOT}/packages/resource-agent-hypervisor:${ROOT}/packages/nl2uri:${ROOT}/packages/uri3:${ROOT}/packages/uri2flow:${ROOT}/packages/uri2ops:${ROOT}/packages/touri:${ROOT}/packages/uri2voice:${ROOT}/packages/uri2pact:${ROOT}/packages/uri2verify${PYTHONPATH:+:$PYTHONPATH}"
mkdir -p output

PASS=0
FAIL=0
SKIP=0
RESULTS=()

log() { printf '%s\n' "$*"; }

run_example() {
  local id="$1"
  local name="$2"
  shift 2
  log ""
  log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  log "▶ Example $id: $name"
  log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  if "$@"; then
    RESULTS+=("PASS  $id  $name")
    PASS=$((PASS + 1))
    log "✓ PASS: $id $name"
  else
    local ec=$?
    if [[ "$ec" -eq 77 ]]; then
      RESULTS+=("SKIP  $id  $name")
      SKIP=$((SKIP + 1))
      log "⊘ SKIP: $id $name"
    else
      RESULTS+=("FAIL  $id  $name")
      FAIL=$((FAIL + 1))
      log "✗ FAIL: $id $name (exit $ec)"
    fi
  fi
}

skip() {
  log "⊘ SKIP: $*"
  exit 77
}

# ── 01 quickstart ──
ex01() { bash examples/01_quickstart_local/run.sh; }

# ── 02 scan HTTP (needs agent on :8101) ──
ex02() {
  if curl -sf --max-time 2 http://localhost:8101/health >/dev/null 2>&1; then
    uri3 scan http://localhost:8101
  else
    log "No agent on :8101 — trying uri3 scan http (may fail gracefully)"
    uri3 scan http 2>/dev/null || skip "no HTTP agent running on localhost:8101"
  fi
}

# ── 03 docker SSH testenv ──
ex03() {
  command -v docker >/dev/null || skip "docker not available"
  docker info >/dev/null 2>&1 || skip "docker daemon not running"
  make docker-testenv-up
  HYPERVISOR_SSH_PASSWORD="${HYPERVISOR_SSH_PASSWORD:-deploy}" uri3 scan ssh
  make docker-testenv-down
}

# ── 04 nl2a weather ──
ex04() { bash examples/04_nl2a_weather_map/run.sh; }

# ── 05 meta repair ──
ex05() {
  python -m meta_agent.cli repair examples/05_meta_repair/broken_agent.yaml | grep -q 'changed: true'
}

# ── 06 orders contract ──
ex06() {
  python -m generator.validate examples/06_orders_agent | grep -q "Validated 1"
}

# ── 07 invoices plan ──
ex07() {
  python -m meta_agent.cli plan "$(cat examples/07_invoices_agent/create_invoices_agent_prompt.txt)" \
    | grep -q "contracts/agents"
}

# ── 08 evolution ──
ex08() { make evolution-check; }

# ── 09 hypervisor lifecycle (dry-run only) ──
ex09() { bash examples/09_run_agent_hypervisor/run.sh; }

# ── 10-22 with run.sh ──
run_sh() {
  local dir="$1"
  bash "$dir/run.sh"
}

# ── 15_playwright (mock path, no Playwright install required) ──
ex15pw() {
  uri3 validate-workflow examples/14_workflow_executor_mock/task_graph.yaml
  uri3 run-workflow examples/14_workflow_executor_mock/task_graph.yaml \
    --approve --browser mock >/dev/null
}

# ── 11 playwright (needs playwright + chromium) ──
ex11() {
  python -c "import playwright" 2>/dev/null || skip "playwright not installed (pip install -e '.[browser]' && playwright install chromium)"
  bash examples/11_playwright_browser/run.sh
}

log "Hypervisor examples test run"
log "Root: $ROOT"
log "Date: $(date -Iseconds)"

run_example "01" "quickstart_local (uri-tree/validate/graph)" ex01
run_example "04" "nl2a_weather_map" ex04
run_example "05" "meta_repair" ex05
run_example "06" "orders_agent" ex06
run_example "07" "invoices_agent" ex07
run_example "08" "evolution" ex08
run_example "09" "run_agent_hypervisor (dry-run)" ex09
run_example "10" "browser_operator" run_sh examples/10_browser_operator
run_example "12" "android_operator (mock)" run_sh examples/12_android_operator
run_example "13op" "pcwin_operator (mock)" run_sh examples/13_pcwin_operator
run_example "13nl" "nl2uri_multi_uri_graph" run_sh examples/13_nl2uri_multi_uri_graph
run_example "14wf" "workflow_executor_mock" run_sh examples/14_workflow_executor_mock
run_example "14srv" "uri2ops_serve" run_sh examples/14_uri2ops_serve
run_example "15cf" "compact_uri_flow" run_sh examples/15_compact_uri_flow
run_example "15pw" "playwright_browser (mock via uri3)" ex15pw
run_example "16" "llm_graph_planner" run_sh examples/16_llm_graph_planner
run_example "17" "flow_vs_graph" run_sh examples/17_flow_vs_graph
run_example "18" "llm_flow_planner" run_sh examples/18_llm_flow_planner
run_example "20" "touri_capabilities" run_sh examples/20_touri_capabilities
run_example "21" "touri_voice" run_sh examples/21_touri_voice
run_example "22" "markpact_weather" run_sh examples/22_markpact_weather
run_example "23" "nl_to_agent_tutorial" run_sh examples/23_nl_to_agent_tutorial
run_example "11" "playwright_browser (real)" ex11
run_example "02" "uri3_scan_http" ex02
run_example "03" "ssh_remote_agent (docker)" ex03

log ""
log "══════════════════════════════════════════════════"
log "SUMMARY"
log "══════════════════════════════════════════════════"
for row in "${RESULTS[@]}"; do log "$row"; done
log ""
log "PASS=$PASS  FAIL=$FAIL  SKIP=$SKIP  TOTAL=$((PASS + FAIL + SKIP))"

if [[ "$FAIL" -gt 0 ]]; then exit 1; fi
exit 0

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "== 38_autonomous_agents =="
ADAPTER="${ADAPTER:-mock}"

if [[ "$ADAPTER" == "gnome" ]]; then
  export DISPLAY="${DISPLAY:-:0}"
  export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
fi

hypervisor run-agent desktop-operator.local --detach --wait-healthy --if-running reuse
hypervisor run-agent remote-deploy-agent.local --detach --wait-healthy --if-running reuse
hypervisor run-agent gnome-programmer-agent.local --detach --wait-healthy --if-running reuse
hypervisor run-agent screenshot-analysis-agent.local --detach --wait-healthy --if-running reuse

echo "== agent reports =="
python scripts/examples/audit_agent_reports.py >/tmp/taskinity-audit-38.log
tail -3 /tmp/taskinity-audit-38.log

echo "== remote deploy plan (ssh-dev) =="
curl -s -X POST "http://localhost:8135/skills/plan_remote_deploy" \
  -H 'Content-Type: application/json' \
  -d '{"deployment_id":"weather-map-agent.ssh-dev","wait_healthy":false}' \
  >/tmp/taskinity-remote-plan.json
python3 - <<'PY'
import json
from pathlib import Path
data = json.loads(Path("/tmp/taskinity-remote-plan.json").read_text())
assert data.get("ok"), data
assert data["plan"]["steps"][0]["action"] == "rsync"
print("remote_plan_ok", data["deployment_id"])
PY

echo "== gnome programmer session =="
GNOME_URL="http://localhost:8136"
curl -s -X POST "$GNOME_URL/skills/run_programmer_session" \
  -H 'Content-Type: application/json' \
  -d "{\"operator_url\":\"http://localhost:8791\",\"adapter\":\"$ADAPTER\",\"approve\":true,\"command_text\":\"echo autonomy\"}" \
  >/tmp/taskinity-gnome-session.json

echo "== screenshot collaboration =="
ANALYZER_URL="http://localhost:8134"
curl -s -X POST "$ANALYZER_URL/skills/capture_and_analyze" \
  -H 'Content-Type: application/json' \
  -d "{\"operator_url\":\"http://localhost:8791\",\"target_url\":\"http://localhost:8788/www/\",\"adapter\":\"$ADAPTER\",\"approve\":true,\"run_label\":\"example38\"}" \
  >/tmp/taskinity-screenshot-38.json

python3 - <<'PY'
import json
from pathlib import Path

gnome = json.loads(Path("/tmp/taskinity-gnome-session.json").read_text())
shot = json.loads(Path("/tmp/taskinity-screenshot-38.json").read_text())
assert gnome.get("ok"), gnome
assert shot.get("ok"), shot
assert Path("output/analysis/gnome-programmer/programmer-session-latest.json").exists()
assert Path("output/analysis/screenshots/screenshot-analysis.jsonl").exists()
print("gnome_session_ok", gnome.get("adapter"))
print("screenshot_collab_ok", shot.get("artifact_uri"))
PY

echo "PASS examples/38_autonomous_agents"

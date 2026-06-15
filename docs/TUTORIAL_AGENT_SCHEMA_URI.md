# Tutorial: checker agent — schema, URI, step by step

Guide: how the **observer agent** (`hypervisor-dashboard`) starts a fleet, **fetches schemas** of other agents via URI, and **“talks” to them** by invoking capabilities from agent-card / contract.

Polish version: [`TUTORIAL_AGENT_SCHEMA_URI.pl.md`](./TUTORIAL_AGENT_SCHEMA_URI.pl.md)

See also: [`TUTORIAL_THREE_AGENTS.md`](./TUTORIAL_THREE_AGENTS.md), [`URI_COOKBOOK.md`](./URI_COOKBOOK.md)

---

## Can you get a specific agent's schema via URI?

**Yes.** The shortest runtime path is `schema://agent/{deployment_id}`. It returns one envelope with deployment metadata, runtime card, source contract, capabilities, and `input_schema` / `output_schema` references.

| Goal | URI / command |
|------|----------------|
| Aggregated agent schema | `uri call schema://agent/{deployment_id}` |
| Source contract (callable) | `uri call contract://agent/{agent_name}` |
| Validate one contract | `uri call contract://agent/{agent_name}/validate` |
| Validate full registry | `uri call contract://registry/validate` |
| Generate agent package (dry-run) | `uri call contract://agent/{agent_name}/generate?dry_run=1` |
| Generate agent package | `uri call contract://agent/{agent_name}/generate` |
| List related artifacts | `uri call contract://agent/{agent_name}/artifacts` |
| Runtime agent-card | `http://localhost:{port}/.well-known/agent-card.json` |
| Endpoint discovery | `uri3 scan http://localhost:{port}` |
| Source contract YAML | `uri call contract://agent/{agent_name}` or `file://{repo}/contracts/agents/{agent}.yaml` → `uri3 resolve` |
| Fleet inspection + card | `hypervisor inspect-agent {deployment_id}` |
| Diagnosis envelope | `uri call repair://agent/{id}/diagnose` |
| Health | `uri call health://agent/{id}` |
| Process view | `uri call view://process/agent/{id}/latest` |

**Not available yet:** callable `readiness://agent/{id}`, or `uri call http://…` (use curl / inspect instead).

---

## Verified scenario: NL → new agent → file/device/robot/cron

Use `urish agent generate` when you want an arbitrary new resource agent from NL. `urish ecosystem` is still profile-oriented; this command wraps `resource-agent-factory`.

```bash
uri agent generate \
  "create a new schema-collab-agent that reads file:// README, checks device://device/sensor-1/status and robot://robot/amr-1/state, and has a cron monitor command" \
  --name schema-collab-agent \
  --approve \
  --overwrite \
  --json
```

Generated artifacts:

| Artifact | Path / URI |
|----------|------------|
| Contract | `contracts/agents/schema_collab_agent.yaml` |
| Package | `agents/generated/schema_collab_agent/` |
| Deployment | `schema-collab-agent.local` |
| Agent ref | `agent://schema-collab-agent` |
| Health | `http://localhost:8131/health` |

Start two collaborating agents and the observer:

```bash
hypervisor run-agent device-robot-operator.local --detach --wait-healthy
hypervisor run-agent schema-collab-agent.local --detach --wait-healthy
hypervisor run-agent hypervisor-dashboard.local --detach --wait-healthy --if-running reuse
```

Check schema and collaboration:

```bash
uri call schema://agent/schema-collab-agent.local --json
uri call schema://agent/device-robot-operator.local --json
uri call health://agent/schema-collab-agent.local --json
uri call view://process/agent/schema-collab-agent.local/latest --json

curl -s http://localhost:8131/skills/read_markpact_source | python3 -m json.tool
curl -s http://localhost:8131/skills/read_device_status | python3 -m json.tool
curl -s http://localhost:8131/skills/read_robot_state | python3 -m json.tool
curl -s -X POST http://localhost:8131/skills/run_cron_monitor \
  -H 'Content-Type: application/json' \
  -d '{"dry_run": true}' | python3 -m json.tool
```

In Chat (`http://localhost:8788/www/chat.html`), use the same URIs:

```text
schema://agent/schema-collab-agent.local
file:///app/contracts/agents/schema_collab_agent.yaml
health://agent/schema-collab-agent.local
repair://agent/schema-collab-agent.local/diagnose
view://process/agent/schema-collab-agent.local/latest
```

`file://` is runtime-local: host CLI paths usually start with `file:///home/...`, while the chat container sees `file:///app/...`. Use the `contract_uri` returned by `schema://agent/...` for the active runtime.

---

## Checker agent

Use **`hypervisor-dashboard`** (`hypervisor-dashboard.local`, port 8788). Roles: `observer`, `renderer`, `controller`.

```bash
make start
hypervisor run-agent weather-map-agent.local --detach --wait-healthy --if-running reuse
hypervisor run-agent invoices-agent.local --detach --wait-healthy --if-running reuse
```

---

## Schema discovery flow

```bash
uri call schema://agent/weather-map-agent.local --json
uri call contract://agent/weather-map-agent --json
uri call contract://agent/weather-map-agent/validate --json
uri call contract://agent/weather-map-agent/generate?dry_run=1 --json
uri call contract://agent/weather-map-agent/artifacts --json
uri3 scan http://localhost:8105
curl -s http://localhost:8105/.well-known/agent-card.json | python3 -m json.tool
uri3 resolve "file://$(pwd)/contracts/agents/weather_map_agent.yaml"
hypervisor inspect-agent weather-map-agent.local
```

Note: `uri call --json` wraps the system URI payload in the standard `urish` envelope, so schema fields are under `data.*`. Dashboard API may return the same payload directly or under `data`, depending on the endpoint.

---

## Checker “conversation” via system URIs

```bash
uri call health://agent/weather-map-agent.local
uri call repair://agent/invoices-agent.local/diagnose
uri call view://process/agent/weather-map-agent.local/latest
```

Logical order: list deployments → health → scan card → read capabilities → invoke URIs from card → diagnose on failure.

---

## Chat batch (NL → plan → run)

```bash
uri ask $'pokaż proces agenta weather-map-agent.local\nzdiagnozuj agenta invoices-agent.local'
```

API: `POST /api/ask` then `POST /api/plan/run` with `planned_uris` and `auto_repair: true`.

Chat UI: http://localhost:8788/www/chat.html

---

## Schema-driven data access

From agent-card fields:

| Field | Meaning |
|-------|---------|
| `uri: resource://…` | Resource read |
| `uri: file://…` | File access via `uri3 resolve` |
| `input_schema` / `output_schema` | Protobuf in `contracts/proto/` |
| `command: …` | Mutation (needs `--approve`) |

Example with `file://` capability: `codex-uri-smoke-agent` contract.

---

## Full demo script

```bash
make ensure-dev && make start
hypervisor run-agent weather-map-agent.local --detach --wait-healthy --if-running reuse
hypervisor run-agent invoices-agent.local --detach --wait-healthy --if-running reuse
uri3 scan http://localhost:8105
uri call health://agent/weather-map-agent.local
uri call repair://agent/invoices-agent.local/diagnose
uri ask $'pokaż proces agenta weather-map-agent.local\nzdiagnozuj agenta invoices-agent.local'
```

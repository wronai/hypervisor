# Tutorial: three agents + chat monitoring + markpact export

End-to-end walkthrough (~20 min): start three HTTP agents, observe them in Taskinity Chat, locate every artifact on disk, and **import declarations into another system** via `markpact://` README registries.

Polish version: [`TUTORIAL_THREE_AGENTS.pl.md`](./TUTORIAL_THREE_AGENTS.pl.md)

## What you will run

| Agent | Deployment id | Port (default) | Source |
|-------|---------------|----------------|--------|
| Weather map | `weather-map-agent.local` | 8118 | `nl2a` / `domains/weather_map` |
| Invoices | `invoices-agent.local` | 8123 | `contracts/agents/invoices_agent.yaml` |
| User demo | `user-agent.local` | 8102 | `contracts/agents/user_agent.yaml` |
| Dashboard (monitor) | `hypervisor-dashboard.local` | 8788 | `packages/hypervisor-dashboard-agent` |

The dashboard is the **fourth** process — it lists the other three and merges their health into `/api/events`.

## Prerequisites

```bash
cd hypervisor
pip install -e '.[dev]'   # includes uvicorn for hypervisor run-agent
uri doctor
hypervisor deployments
```

Ensure the **same Python** that runs `hypervisor` can `import uvicorn`.

## Step 1 — Start the dashboard (monitoring UI)

```bash
make start
# full stack (dashboard + 3 agents):
make start-full
# or: uri www serve
```

Open:

- Chat: http://localhost:8788/www/chat.html
- Agent UI: http://localhost:8788/ui/agents

Verify:

```bash
curl -s http://localhost:8788/health | python3 -m json.tool
curl -s http://localhost:8788/api/agents | python3 -m json.tool
```

## Step 2 — Start three agents

Each deployment is independent (own port, PID, runtime state file):

```bash
make start-agents
# or manually:
hypervisor run-agent weather-map-agent.local --detach --if-running reuse --wait-healthy
hypervisor run-agent invoices-agent.local --detach --if-running reuse --wait-healthy
hypervisor run-agent user-agent.local --detach --if-running reuse --wait-healthy
```

Check readiness (process **and** health — not the same thing):

```bash
hypervisor inspect-agent weather-map-agent.local
hypervisor inspect-agent invoices-agent.local
hypervisor inspect-agent user-agent.local
```

Quick HTTP probe:

```bash
curl -s http://localhost:8118/health   # weather (port may rebound — check inspect output)
curl -s http://localhost:8123/health   # invoices
curl -s http://localhost:8102/health     # user-agent
```

If a port was busy, hypervisor rebounding updates `output/runtime/agents/{id}/state.json` with `effective_health_uri`.

## Step 3 — Monitor in chat (sidebar + batch plan)

1. Open http://localhost:8788/www/chat.html
2. Sidebar **Agents** — click a deployment → process view URI
3. Sidebar **Events** — live feed via SSE (`agent.health`, `monitor.snapshot`, `log.event`, `incident.created`)

Batch NL (one command per line):

```text
pokaż proces agenta weather-map-agent.local
zdiagnozuj agenta invoices-agent.local
pokaż health agenta user-agent.local
```

Or CLI equivalent:

```bash
uri ask $'pokaż proces agenta weather-map-agent.local\nzdiagnozuj agenta invoices-agent.local'
```

After the plan appears, click **Run plan (dry-run)**. On agent step failure the API runs `repair://agent/{id}/auto` when `auto_repair: true` (default), then optionally retries.

Optional: check **speak result** for mock TTS after ask/plan.

API check without browser:

```bash
curl -s http://localhost:8788/api/events?limit=12 | python3 -m json.tool
```

## Step 4 — CLI fleet watch (parallel)

```bash
hypervisor deployments
uri watch health://agent/weather-map-agent.local --count 3
uri watch health://agent/invoices-agent.local --count 3
uri3 logs 'log://hypervisor?grep=weather-map-agent.local&limit=20'
```

Bounded repair loop:

```bash
hypervisor repair heal weather-map-agent.local
hypervisor repair heal invoices-agent.local --repair auto --learn
```

## Where data is stored

All paths are relative to the repo root unless noted.

### Source of truth (versioned in git)

| Path | Contents | URI / access |
|------|----------|--------------|
| `contracts/agents/*.yaml` | Agent contracts (capabilities, resources) | edit → regenerate |
| `domains/{domain}/` | Domain Pack (uri tree, handlers) | `domain://…` |
| `agents/generated/{agent}/` | Generated FastAPI code + README | `local://agents/generated/…` |
| `agents/generated/{agent}/README.md` | Human docs + **markpact blocks** | `markpact://agents/generated/…/README.md` |
| `agents/scenarios/` | Pointer to domain scenario registries |
| `domains/office/scenario_registry.yaml` | Office NL scenario registry (canonical) |
| `domains/office/README.md` | **markpact:scenario** export for external import |
| `deployments/agent_deployments.yaml` | Deployment registry (ports, targets) | `hypervisor deployments` |
| `deployments/README.md` | **markpact:deploy** export for external import | `markpact://deployments/README.md` |
| `examples/*/*.uri.capability.yaml` | Touri capability manifests (YAML alternative to markpact) | `touri list examples/20_touri_capabilities` |
| `config/*.uri.yaml` | LLM, CLI shortcuts, policy | `config://…` |
| `schemas/*.schema.json` | Incident, runtime, ticket, … | `$schema` in artifacts |

### Runtime output (local, often gitignored)

| Path | Contents | Surfaces in |
|------|----------|-------------|
| `output/runtime/agents/{deployment}/state.json` | PID, effective port, health URI, log paths | `inspect-agent`, `runtime://agent/…/state` |
| `output/logs/*.jsonl` | Pipeline + hypervisor structured logs | `uri3 logs`, `/api/events` as `log.event` |
| `output/logs/agents/{deployment}.process.log` | uvicorn stdout/stderr | `log://file/output/logs/agents/…` |
| `output/incidents/{date}/{agent}/inc_*.yaml` | Failure incidents | `/api/events`, `incident://…` |
| `output/monitoring/*.json` | WWW landing monitor snapshots | `/api/events` as `monitor.snapshot` |
| `output/artifacts/workflows/` | Workflow run artifacts | `workflow://…` results |
| `output/proposals/`, `output/ecosystems/` | urigen plan/generate output | `ecosystem://…` |
| `evolution/proposals/` | Evolution YAML | `evolution://proposal/…` |

Example runtime state fields:

```json
{
  "kind": "RuntimeState",
  "uri": { "self": "runtime://agent/weather-map-agent.local/state" },
  "network": { "effective_port": 8118, "effective_health_uri": "http://localhost:8118/health" },
  "process": { "pid": 66273, "log_uri": "log://file/output/logs/agents/weather-map-agent.local.process.log" }
}
```

### Docker WWW mounts

`make start` bind-mounts `deployments/`, `agents/generated/`, `output/`, `packages/` into the dashboard container so chat repair/run sees the same files as the host. See `www/docker-compose.yml`.

## Import into other systems via markpact

**Markpact** here means: fenced YAML blocks inside a Markdown README, referenced by URI:

```text
markpact://path/to/README.md#optional-fragment
```

Hypervisor **does not** depend on the external `markpact` Python package at runtime. Loaders in `uri2pact` parse blocks locally; `touri` and `uri2flow` validate and execute through their normal backends.

```text
README.md  →  markpact block  →  validate  →  touri / uri2flow / your importer
```

### Block types today

| Block | Consumer | Purpose |
|-------|----------|---------|
| `markpact:capability` | `touri list/call` | Portable capability manifest |
| `markpact:flow` | `uri2flow expand/validate` | Compact URI workflow |
| `markpact:agent_generation` | `uri2pact.extract_markpact_blocks` | Contract hash, generator command, package path |
| `markpact:run_log` | `uri2pact.extract_markpact_blocks` | Inspect command, `log://` URIs for ops |

Generated agents already embed provenance — see [`agents/generated/weather_map_agent/README.md`](../agents/generated/weather_map_agent/README.md).

### A. Import capabilities into another touri runtime

Copy or submodule the README (or whole example dir), then:

```bash
# List capabilities declared in Markdown
touri list markpact://examples/22_markpact_weather/README.md

# Call through that registry
touri call weather://markpact/Gdansk/14/html \
  --registry markpact://examples/22_markpact_weather/README.md

# Single block by fragment
touri list markpact://examples/22_markpact_weather/README.md#weather.forecast.markpact
```

Equivalent for your own agent README if you add a `markpact:capability` block (pattern in example 22).

YAML registries work too — no markpact required:

```bash
touri list examples/20_touri_capabilities
```

### B. Import workflows into uri2flow / uri3

```bash
uri2flow validate markpact://examples/22_markpact_weather/README.md#weather-health
uri2flow expand markpact://examples/22_markpact_weather/README.md#weather-health \
  --out /tmp/weather-health.uri.graph.yaml
uri3 validate-workflow /tmp/weather-health.uri.graph.yaml
uri3 run-workflow /tmp/weather-health.uri.graph.yaml --dry-run
```

Another system can store only the README + graph YAML — no hypervisor checkout required for **declaration** import; execution still needs backends (`python://…`, `hypervisor://…`, etc.) or mocks.

### C. Import agent provenance (generation + ops)

Extract blocks programmatically:

```python
from pathlib import Path
import yaml
from uri2pact import extract_markpact_blocks

readme = Path("agents/generated/invoices_agent/README.md").read_text(encoding="utf-8")
for block in extract_markpact_blocks(readme, "agent_generation"):
    data = yaml.safe_load(block["body"])
    print(data["agent"]["id"], data["source"]["contract_hash"])
```

Use the parsed YAML to:

- Reproduce the agent in CI (`generator.command`)
- Register deployment metadata in an external CMDB
- Wire log collectors to `logs.process` / `logs.hypervisor` URIs

`markpact:run_log` gives `inspect.command` and `view://process/agent/…` for dashboards outside Taskinity.

### D. Export pack for a foreign monorepo

Minimal portable bundle:

```text
contracts/agents/my_agent.yaml          # source contract
agents/generated/my_agent/README.md     # markpact:agent_generation + run_log
examples/20_touri_capabilities/*.yaml   # or markpact:capability in README
deployments/agent_deployments.yaml      # slice for one deployment id
```

In the foreign system:

1. **Capabilities** — `touri list markpact://…/README.md` or copy `*.uri.capability.yaml`
2. **Flows** — `uri2flow expand markpact://…#flow-id`
3. **Agent code** — run generator command from `markpact:agent_generation`, or copy `agents/generated/`
4. **Runtime telemetry** — poll `GET /health` + ingest `output/runtime/agents/*/state.json` or stream `/api/events`

Planned (not shipped): `markpact:scenario`, `uri3 scan markpact://…` — see [`TODO.md`](../TODO.md).

### E. HTTP / JSON export (no markpact)

For systems that prefer APIs over README blocks:

| Data | Export |
|------|--------|
| Deployment list | `GET /api/agents` or `hypervisor deployments` |
| Event feed | `GET /api/events`, SSE `/api/events/stream` |
| Agent health | `GET http://localhost:{port}/health` |
| Agent card | `GET /.well-known/agent-card.json` |
| Logs | `uri3 logs 'log://…'` → JSON lines |
| Incidents | copy `output/incidents/**/*.yaml` (schema-valid) |

Map JSON events to your SIEM; map markpact blocks to your internal service catalog.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `uvicorn` not found | `pip install 'uvicorn>=0.27'` in hypervisor venv |
| Health fails but PID exists | `hypervisor inspect-agent …` — wait for `/health` or check process log |
| Wrong port in docs | Use `effective_health_uri` from inspect / runtime state |
| Chat sidebar empty | `make start`; check `/api/events` |
| markpact block not found | Use `#fragment` matching capability/flow id |

## Related docs

- [`AGENTS_AND_MONITORING.md`](./AGENTS_AND_MONITORING.md) — FAQ: real agents, fleet ops
- [`MARKPACT_WITH_TOURI.md`](./MARKPACT_WITH_TOURI.md) — block syntax reference
- [`ARTIFACT_STANDARD.md`](./ARTIFACT_STANDARD.md) — YAML envelope for incidents/runtime
- [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md) — chat API details
- [`examples/22_markpact_weather/`](../examples/22_markpact_weather/) — working markpact registry
- [`examples/30_golden_path/`](../examples/30_golden_path/) — break → repair → ticket

# Real agents, communication, evolution, and multi-agent monitoring

Status verified on 2026-06-14 against the current repo (`deployments/agent_deployments.yaml`, `hypervisor` CLI, dashboard API).

## Short answers

| Question | Answer |
|----------|--------|
| Can you create **real** agents? | **Yes** — contract-first HTTP agents via `nl2a`, `urigen` / `uri ecosystem`, or evolution proposals. Artifacts land in `contracts/agents/`, `agents/generated/`, and `deployments/agent_deployments.yaml`. |
| Is there **communication** with them? | **Yes** — each agent exposes `/health`, `/.well-known/agent-card.json`, and resource routes. The hypervisor and dashboard call them through URI schemes (`health://`, `repair://`, `view://`) and HTTP probes. |
| Can agents be **improved**? | **Yes, in a controlled loop** — diagnose → repair → incident → evolution proposal → regenerate → verify → apply. Agents do not mutate production code without approval. |
| Do **several agents run at once**? | **Yes** — each deployment has its own port/PID/runtime state. Example: `weather-map-agent.local` on `:8118` and `invoices-agent.local` on `:8123` concurrently. |
| What **software monitors** many agents? | **`hypervisor`** (registry, inspect, supervise), **`hypervisor-dashboard-agent`** (WWW UI + `/api/events`), **`uri3`** (`logs`, `scan`, `doctor`, `watch`), plus artifacts in `output/logs/`, `output/incidents/`, `output/monitoring/`. |

## 1. Creating real agents

Three supported paths:

### A. Domain Pack pipeline (`nl2a`) — most common for HTTP agents

```bash
nl2a --no-llm -p "generuj mape pogody dwa tygodnie do przodu w html"
make verify
hypervisor run-agent weather-map-agent.local --detach --wait-healthy
```

Produces:

```text
domains/{domain}/uri_tree.yaml
contracts/agents/{agent}.yaml
agents/generated/{agent}/
deployments/agent_deployments.yaml   # new or updated deployment id
```

Tutorial: [`examples/04_nl2a_weather_map/`](../examples/04_nl2a_weather_map/) · [`examples/23_nl_to_agent_tutorial/`](../examples/23_nl_to_agent_tutorial/)

### B. URI ecosystem (`urigen` / `uri ecosystem`) — isolated packages

```bash
uri ask "stwórz agenta pogodowego z healthcheckiem"
uri ecosystem plan "…" --profile minimal --out output/proposals/weather.yaml
uri ecosystem generate output/proposals/weather.yaml --out output/ecosystems/weather
uri ecosystem verify output/ecosystems/weather/ecosystem.yaml
uri ecosystem apply output/ecosystems/weather/ecosystem.yaml --plan
uri ecosystem apply output/ecosystems/weather/ecosystem.yaml --approve
```

Profiles: `minimal`, `voice`, `dashboard-agent` — see [`PROFILES.md`](./PROFILES.md).

### C. Evolution proposal — extend the fleet

```bash
make evolution-check
uri evolve from-incident output/incidents/.../inc_*.yaml
uri proposal verify evolution/proposals/from_incident_*.yaml
uri proposal apply … --sandbox
```

Examples: [`examples/08_evolution/`](../examples/08_evolution/) · [`EVOLUTION.md`](./EVOLUTION.md)

**Rule:** do not edit `agents/generated/` by hand. Change contracts, domain packs, or proposals, then regenerate.

## 2. Communication model

Agents are thin FastAPI services. The system talks to them on several layers:

```text
┌─────────────┐     URI / HTTP      ┌──────────────────┐
│ urish chat  │ ──────────────────► │ hypervisor       │
│ CLI / WWW   │                     │ (lifecycle)      │
└─────────────┘                     └────────┬─────────┘
                                             │ inspect / run / repair
                                             ▼
                    ┌────────────────────────────────────────┐
                    │  weather-map :8118   invoices :8123    │
                    │  user-agent  :8102   dashboard :8788   │
                    └────────────────────────────────────────┘
```

| Layer | Mechanism | Example |
|-------|-----------|---------|
| HTTP probe | `GET /health`, agent card | `curl http://localhost:8118/health` |
| URI scheme | resolver → hypervisor backend | `health://agent/weather-map-agent.local` |
| Dashboard API | policy-gated calls | `POST /api/uri/call`, `POST /api/plan/run` |
| A2A-style card | `/.well-known/agent-card.json` | `uri3 scan http://localhost:8118` |
| Logs | `log://` resolver | `uri3 logs 'log://hypervisor?grep=weather-map-agent.local'` |
| Process view | read-only HTML envelope | `view://process/agent/weather-map-agent.local/latest` |

Chat and CLI use the **same** backends. Chat plans on Enter; execution requires **Run plan** or **Run URI** (dry-run default).

## 3. Improving agents (repair + evolution)

Improvement is **not** silent self-modification. The supported loop:

```text
observe → diagnose → repair → incident → evolution proposal → regenerate → verify → apply → redeploy
```

| Step | Tool | Notes |
|------|------|-------|
| Observe | `hypervisor inspect-agent`, `uri watch`, `/api/events` | Separates process running vs health OK |
| Diagnose | `uri repair diagnose`, `repair://agent/{id}/diagnose` | Read-only RepairPlan |
| Auto-repair | `hypervisor supervise --repair auto`, `repair://agent/{id}/auto` | Bounded restart / sync_health / port rebound |
| Plan run auto-repair | `POST /api/plan/run` with `auto_repair: true` | On step failure → repair → optional retry |
| Incident | `output/incidents/{date}/{agent}/inc_*.yaml` | Schema-valid artifact |
| Evolve | `uri evolve from-incident`, `uri evolve from-ticket` | Proposal YAML, not direct code edit |
| Apply | `uri proposal apply --sandbox` / `--approve` | Regenerates agents, runs contract tests |

Gap (roadmap): full closed loop `incident → classify logs → regenerate → redeploy → learn` for every failure family. See [`TODO.md`](../TODO.md) (uri-healer).

## 4. Running multiple agents at once

Registry: [`deployments/agent_deployments.yaml`](../deployments/agent_deployments.yaml)

| Deployment | Port (preferred) | Source |
|------------|------------------|--------|
| `hypervisor-dashboard.local` | 8788 | system agent (`packages/hypervisor-dashboard-agent`) |
| `weather-map-agent.local` | 8118 (rebound if busy) | `nl2a` / domain `weather_map` |
| `invoices-agent.local` | 8123 | contract `invoices_agent.yaml` |
| `user-agent.local` | 8102 | contract `user_agent.yaml` |

Start several agents:

```bash
hypervisor run-agent weather-map-agent.local --detach --if-running reuse
hypervisor run-agent invoices-agent.local --detach --if-running reuse
hypervisor run-agent user-agent.local --detach --if-running reuse
hypervisor deployments
hypervisor inspect-agent weather-map-agent.local
hypervisor inspect-agent invoices-agent.local
```

If a preferred port is taken, hypervisor **rebinds** to a free port and stores the effective health URI in runtime state (`output/runtime/agents/*/state.json`). Use `repair apply … --playbook sync_health_uri` to align the registry.

**Verified:** `weather-map-agent.local` and `invoices-agent.local` both report `service_status: healthy` when started with `--detach`.

## 5. Monitoring many agents — what to use

### Primary: `hypervisor` (lifecycle + inspection)

```bash
hypervisor deployments
hypervisor inspect-agent weather-map-agent.local
hypervisor supervise weather-map-agent.local --repair auto
hypervisor agent-status invoices-agent.local
uri watch health://agent/weather-map-agent.local --count 5
```

- Registry: all deployment ids, target URIs, health URIs
- `inspect-agent`: process, health, card probe, log errors, incidents, effective port
- `supervise --watch` — long-running loop: `hypervisor supervise {id} --watch --repair auto --interval 15` (JSONL → `output/logs/hypervisor-watch.jsonl`, visible in `/api/events`)

### Dashboard agent (WWW + API)

After `make start` or `uri www serve`:

| Surface | Purpose |
|---------|---------|
| `http://localhost:8788/ui/agents` | Deployment list + process views |
| `http://localhost:8788/www/chat.html` | NL ops, Run plan, sidebar agents/events |
| `GET /api/agents` | JSON deployment list |
| `GET /api/events` | Merged feed: incidents, monitor snapshots, **log events**, live agent health |
| `GET /api/events/stream` | SSE sidebar refresh (~8s poll) |

Chat plan run supports `auto_repair` and optional `speak_summary` (mock TTS). Voice: `/api/voice/transcribe`, `/api/voice/speak`.

### `uri3` — logs, scan, doctor

```bash
uri3 logs 'log://hypervisor?level=ERROR&limit=50'
uri3 logs 'log://file/output/logs/agents/weather-map-agent.local.process.log'
uri3 scan http://localhost:8118
uri3 doctor
uri3 doctor --strict
```

Log files: `output/logs/*.jsonl` (pipeline, agents, hypervisor). Error-level `LogEvent` lines appear in `/api/events`.

### WWW landing monitors (product pages)

```bash
make www-monitor
bash scripts/www/run_monitors.sh
python scripts/www/monitor_landing.py --url http://localhost:8788/www/
```

Snapshots land in `output/monitoring/*.json` and surface in `/api/events` as `monitor.snapshot`.

### Operator runtime (`uri2ops`) — task graphs, not agent fleet

Use `uri2ops` for browser/OS **tasks** (health check page, screenshot). For **agent fleet** health, prefer `hypervisor` + dashboard.

### What is not a full multi-agent control plane yet

- No Kubernetes-style orchestrator — local/Docker/SSH targets in registry
- `hypervisor supervise --watch` daemon — **shipped** (`--interval`, `--count`, JSONL events); use one process per deployment or orchestrate externally
- `/api/events` includes durable lifecycle/repair/watch `LogEvent` records, but
  not yet every workflow step from every backend
- SSH auto-deploy — registry entry only (`status: planned`)

## 6. Quick verification checklist

```bash
hypervisor deployments
hypervisor run-agent weather-map-agent.local --detach --if-running reuse
hypervisor run-agent invoices-agent.local --detach --if-running reuse
hypervisor run-agent user-agent.local --detach --if-running reuse
curl -s http://localhost:8788/api/events?limit=10
```

Step-by-step tutorial (3 agents + chat + markpact export): [`TUTORIAL_THREE_AGENTS.md`](./TUTORIAL_THREE_AGENTS.md)

## 7. Where data lives (summary)

| Layer | Paths |
|-------|-------|
| Contracts & code | `contracts/agents/`, `agents/generated/`, `domains/` |
| Registry | `deployments/agent_deployments.yaml` |
| Runtime | `output/runtime/agents/{deployment}/state.json` |
| Logs & events | `output/logs/*.jsonl`, `output/incidents/`, `output/monitoring/` |
| Markpact export | `agents/generated/*/README.md`, `examples/22_markpact_weather/README.md` |

Import to other systems: [`MARKPACT_WITH_TOURI.md`](./MARKPACT_WITH_TOURI.md) · [`TUTORIAL_THREE_AGENTS.md`](./TUTORIAL_THREE_AGENTS.md) (section «Import via markpact»).

## Related docs

- [`HYPERVISOR_WORKFLOW.md`](./HYPERVISOR_WORKFLOW.md) — generation → run-agent
- [`DEPLOYMENT.md`](./DEPLOYMENT.md) — local, Docker, SSH, port rebound
- [`AUTONOMY_LOOP.md`](./AUTONOMY_LOOP.md) — incident → repair → evolution
- [`DASHBOARD.md`](./DASHBOARD.md) — WWW API and chat
- [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md) — NL, plan run, voice
- [`MARKPACT_WITH_TOURI.md`](./MARKPACT_WITH_TOURI.md) — markpact block types and import
- [`TUTORIAL_THREE_AGENTS.md`](./TUTORIAL_THREE_AGENTS.md) — hands-on walkthrough
- [`examples/09_run_agent_hypervisor/`](../examples/09_run_agent_hypervisor/)
- [`examples/30_golden_path/`](../examples/30_golden_path/) — break → repair → ticket

Polish summary: [`AGENTS_AND_MONITORING.pl.md`](./AGENTS_AND_MONITORING.pl.md)

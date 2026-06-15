# Getting started (15 minutes)

Learn **one model**, not every package:

```text
URI → plan → verify → apply/run → observe → repair/evolve
```

## One entry point

Use **`uri`** or **`urish`** — the same binary. Everything else is a backend:

| You type | Backend |
|----------|---------|
| `urish ask` | nl2uri + urigen intent |
| `urish call` | uri2run |
| `urish explain` | uri3 explain |
| `urish run` | uri2flow / uri2ops |
| `urish ecosystem` | urigen |
| `urish agent` | hypervisor lifecycle |
| `urish repair` | repair supervisor |
| `urish ticket` / `evolve` | planfile + evolution |
| `urish dashboard` | dashboard-agent workflow |

Install:

```bash
pip install -e '.[dev]'
# dev extra includes uvicorn (required for hypervisor run-agent on host)
uri doctor
```

## Interactive URI shell

Start the REPL (same as `uri shell`):

```bash
urish
# or
make uri-shell
```

Inside the shell, paste a URI or type natural language:

```text
uri[local-dev|dev]> view://process/agent/weather-map-agent.local/latest
uri[local-dev|dev]> health://agent/invoices-agent.local
uri[local-dev|dev]> workflow://portal/zus-form/dry-run
uri[local-dev|dev]> zdiagnozuj agenta invoices-agent.local
```

Tips:

- Default mode is **real** (mutations get `--approve` under policy=dev). Toggle with `.dry-run on` for safe preview.
- Output format: `.json`, `.yaml`, or `.text`
- Exit: `exit`, `quit`, or `:q`
- One-shot from bash (no REPL): `uri 'view://process/agent/weather-map-agent.local/latest'`

## System flow (one page)

```text
Human / LLM / Ticket
        ↓
      urish
        ↓
  URI / proposal / flow
        ↓
 verify / dry-run / policy
        ↓
 run / apply / observe
        ↓
 logs / incident / repair / evolution
        ↓
 dashboard view
```

## Five learning paths

### 1. Call a URI

```bash
uri call shell://echo --payload '{"args":["hello"]}'
uri call python://uri2voice.stt:transcribe --payload '{"text":"test"}'
```

### 2. Check an agent

```bash
uri agent status weather-map-agent.local
uri agent health weather-map-agent.local
uri logs log://hypervisor?grep=weather-map-agent.local
```

### 3. Create an agent (ecosystem)

```bash
uri ask "stwórz agenta pogodowego z healthcheckiem"
uri ecosystem plan "stwórz agenta pogodowego" --profile minimal \
  --out output/proposals/weather.ecosystem.proposal.yaml
uri ecosystem generate output/proposals/weather.ecosystem.proposal.yaml \
  --out output/ecosystems/weather
uri ecosystem verify output/ecosystems/weather/ecosystem.yaml
uri ecosystem apply output/ecosystems/weather/ecosystem.yaml --plan
```

### 4. Repair a problem

```bash
uri repair diagnose weather-map-agent.local
uri repair apply weather-map-agent.local --dry-run
uri repair apply weather-map-agent.local --approve
```

### 5. Open the dashboard

```bash
uri dashboard create hypervisor-dashboard --plan-only
uri agent run hypervisor-dashboard.local --wait-healthy --approve
uri dashboard open
# or: uri call browser://chrome/page/open --payload '{"url":"http://localhost:8788/ui"}' --approve
```

### 6. Chat and office workflows (WWW or CLI)

```bash
make start   # http://localhost:8788/www/chat.html

# Single office prompt (matches landing card)
uri ask "Wejdź na stronę dostawcy, pobierz raport CSV za ten miesiąc i zapisz w rozliczeniach."
uri run workflow://office/supplier-report/monthly --dry-run

# Batch: paste three lines in chat, or:
uri ask $'pokaż proces agenta weather-map-agent.local\nzdiagnozuj agenta invoices-agent.local'

# Compact flow (author YAML — not via chat)
bash examples/15_compact_uri_flow/run.sh
uri3 run-workflow output/weather.uri.graph.yaml --approve --browser mock
```

See [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md) · [`examples/33_office_workflows/`](../examples/33_office_workflows/).

### 7. Multiple agents and monitoring

```bash
hypervisor deployments
hypervisor run-agent weather-map-agent.local --detach --if-running reuse
hypervisor run-agent invoices-agent.local --detach --if-running reuse
hypervisor inspect-agent weather-map-agent.local
curl -s http://localhost:8788/api/events?limit=10
```

Each deployment has its own port and runtime state. Use `hypervisor` for lifecycle,
dashboard `/api/events` for a merged sidebar feed, `uri3 logs` for log:// queries.

See [`AGENTS_AND_MONITORING.md`](./AGENTS_AND_MONITORING.md) · hands-on [`TUTORIAL_THREE_AGENTS.md`](./TUTORIAL_THREE_AGENTS.md) (3 agents + markpact export) · [`TUTORIAL_AGENT_SCHEMA_URI.md`](./TUTORIAL_AGENT_SCHEMA_URI.md) (NL-generated agent + `schema://agent`).

## Command levels

| Level | Who | Examples |
|-------|-----|----------|
| 1 User | first day | `uri ask`, `uri agent status`, `uri dashboard open` |
| 2 Operator | daily ops | `uri ecosystem verify`, `uri repair`, `uri watch` |
| 3 Developer | extend system | `uri3 explain`, `uri2run call`, `urigen verify` |
| 4 Architect | governance | `uri doctor --strict`, `hypervisor artifacts check` |

## Shortcuts hide details

Common aliases live in `config/cli_shortcuts.uri.yaml`. They can include a URI,
description, and default payload, so a first-day user can run:

```bash
uri hwa
uri weather-process
uri dashboard-ui --approve
```

The full URI is still available when needed:

```bash
uri call browser://chrome/page/open --payload '{"url":"http://localhost:8788/ui"}' --approve
```

## Golden path (end-to-end)

See [`examples/30_golden_path/README.md`](../examples/30_golden_path/README.md) — weather agent, break, incident, repair, ticket, dashboard.

## Next docs

- [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md) — chat, office cards, batch NL, uri2flow
- [`MENTAL_MODEL.md`](./MENTAL_MODEL.md) — 7 core concepts
- [`URI_COOKBOOK.md`](./URI_COOKBOOK.md) — “I want to…” recipes
- [`PROFILES.md`](./PROFILES.md) — minimal, dashboard-agent, voice, …
- [`ARTIFACT_STANDARD.md`](./ARTIFACT_STANDARD.md) — YAML envelope
- [`AUTONOMY_LOOP.md`](./AUTONOMY_LOOP.md) — incident → repair → ticket → evolution
- [`DASHBOARD.md`](./DASHBOARD.md) — Web UI as system agent
- [`CLI_REFERENCE.md`](./CLI_REFERENCE.md) — full command map

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
uri doctor
```

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

## Command levels

| Level | Who | Examples |
|-------|-----|----------|
| 1 User | first day | `uri ask`, `uri agent status`, `uri dashboard open` |
| 2 Operator | daily ops | `uri ecosystem verify`, `uri repair`, `uri watch` |
| 3 Developer | extend system | `uri3 explain`, `uri2run call`, `urigen verify` |
| 4 Architect | governance | `uri doctor --strict`, `hypervisor artifacts check` |

## Golden path (end-to-end)

See [`examples/30_golden_path/README.md`](../examples/30_golden_path/README.md) — weather agent, break, incident, repair, ticket, dashboard.

## Next docs

- [`MENTAL_MODEL.md`](./MENTAL_MODEL.md) — 7 core concepts
- [`URI_COOKBOOK.md`](./URI_COOKBOOK.md) — “I want to…” recipes
- [`PROFILES.md`](./PROFILES.md) — minimal, dashboard-agent, voice, …
- [`ARTIFACT_STANDARD.md`](./ARTIFACT_STANDARD.md) — YAML envelope
- [`AUTONOMY_LOOP.md`](./AUTONOMY_LOOP.md) — incident → repair → ticket → evolution
- [`DASHBOARD.md`](./DASHBOARD.md) — Web UI as system agent
- [`CLI_REFERENCE.md`](./CLI_REFERENCE.md) — full command map

# Tutorial: trzech agentów + monitoring w czacie + eksport markpact

Przewodnik (~20 min): uruchom trzech agentów HTTP, obserwuj w Taskinity Chat, znajdź artefakty na dysku i **importuj deklaracje do innego systemu** przez `markpact://`.

Wersja EN: [`TUTORIAL_THREE_AGENTS.md`](./TUTORIAL_THREE_AGENTS.md)

## Co uruchomisz

| Agent | Deployment | Port | Źródło |
|-------|------------|------|--------|
| Mapa pogody | `weather-map-agent.local` | 8118 | `domains/weather_map` / nl2a |
| Faktury | `invoices-agent.local` | 8123 | `contracts/agents/invoices_agent.yaml` |
| User demo | `user-agent.local` | 8102 | `contracts/agents/user_agent.yaml` |
| Dashboard | `hypervisor-dashboard.local` | 8788 | monitor + chat |

## Kroki 1–4 (skrót)

```bash
pip install -e '.[dev]'
make start                                    # dashboard :8788
hypervisor run-agent weather-map-agent.local --detach --wait-healthy
hypervisor run-agent invoices-agent.local --detach --wait-healthy
hypervisor run-agent user-agent.local --detach --wait-healthy
hypervisor inspect-agent weather-map-agent.local
curl -s http://localhost:8788/api/events?limit=12
```

Chat: http://localhost:8788/www/chat.html — sidebar Agents + Events (SSE).

Batch NL w czacie (jedna komenda na linię):

```text
pokaż proces agenta weather-map-agent.local
zdiagnozuj agenta invoices-agent.local
pokaż health agenta user-agent.local
```

→ **Run plan (dry-run)** (auto-repair domyślnie włączone).

## Gdzie są przechowywane dane

### W repozytorium (git)

| Ścieżka | Zawartość |
|---------|-----------|
| `contracts/agents/*.yaml` | Kontrakt agenta |
| `agents/generated/{agent}/` | Wygenerowany kod + README z blokami markpact |
| `deployments/agent_deployments.yaml` | Rejestr wdrożeń |
| `deployments/README.md` | Eksport **markpact:deploy** do importu |
| `domains/{domain}/` | Domain Pack |
| `agents/scenarios/` | Scenariusze NL (biuro) |
| `examples/*/*.uri.capability.yaml` | Manifesty touri (alternatywa dla markpact) |
| `schemas/*.schema.json` | Schematy incydentów, runtime, ticketów |

### Runtime (lokalnie, często poza git)

| Ścieżka | Zawartość | Gdzie widać |
|---------|-----------|-------------|
| `output/runtime/agents/{id}/state.json` | PID, effective port, health URI | `inspect-agent` |
| `output/logs/*.jsonl` | Logi strukturalne | `uri3 logs`, `/api/events` |
| `output/logs/agents/*.process.log` | stdout uvicorn | `log://file/…` |
| `output/incidents/` | Incydenty YAML | sidebar, `incident://` |
| `output/monitoring/` | Snapshoty monitorów WWW | `monitor.snapshot` |
| `output/artifacts/workflows/` | Wyniki workflow | artefakty uri3 |

Docker (`make start`) montuje `deployments/`, `agents/generated/`, `output/` do kontenera dashboardu.

## Import do innych systemów przez markpact

**Markpact** = bloki YAML w README, odwołanie URI:

```text
markpact://ścieżka/do/README.md#fragment
```

Parser: pakiet `uri2pact` (bez zewnętrznego runtime markpact).

### Typy bloków

| Blok | Konsument | Cel |
|------|-----------|-----|
| `markpact:capability` | `touri` | capability manifest |
| `markpact:flow` | `uri2flow` | compact workflow |
| `markpact:agent_generation` | `uri2pact` | kontrakt, hash, komenda generatora |
| `markpact:run_log` | `uri2pact` | inspect, log:// URIs |

Każdy wygenerowany agent ma bloki w `agents/generated/*/README.md`.

### Import capability (touri)

```bash
touri list markpact://examples/22_markpact_weather/README.md
touri call weather://markpact/Gdansk/14/html \
  --registry markpact://examples/22_markpact_weather/README.md
```

### Import workflow (uri2flow → uri3)

```bash
uri2flow expand markpact://examples/22_markpact_weather/README.md#weather-health \
  --out /tmp/graph.yaml
```

### Import provenance agenta (Python)

```python
from pathlib import Path
import yaml
from uri2pact import extract_markpact_blocks

text = Path("agents/generated/invoices_agent/README.md").read_text(encoding="utf-8")
for b in extract_markpact_blocks(text, "agent_generation"):
    print(yaml.safe_load(b["body"]))
```

### Pakiet eksportu do obcego repo

```text
contracts/agents/my_agent.yaml
agents/generated/my_agent/README.md    # markpact provenance
deployments/agent_deployments.yaml     # wpis deployment
```

### Eksport HTTP (bez markpact)

- `GET /api/agents`, `/api/events`, SSE `/api/events/stream`
- `GET /health`, `/.well-known/agent-card.json` na każdym agencie
- `uri3 logs 'log://…'` → JSONL

## Powiązane

- [`MARKPACT_WITH_TOURI.md`](./MARKPACT_WITH_TOURI.md)
- [`AGENTS_AND_MONITORING.pl.md`](./AGENTS_AND_MONITORING.pl.md)
- [`examples/22_markpact_weather/`](../examples/22_markpact_weather/)

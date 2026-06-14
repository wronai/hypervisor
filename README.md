# Resource Agent System v0.6


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.5.22-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$13.80-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-10.1h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $13.7980 (21 commits)
- 👤 **Human dev:** ~$1011 (10.1h @ $100/h, 30min dedup)

Generated on 2026-06-14 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

Monorepo: **uri3**, **nl2uri**, **uri2flow**, **uri2ops**, **hypervisor**, **agent factory** — contract-first thin agents z pipeline `prompt → URI plan → Domain Pack → generated agent`, plus warstwa operatora URI.

**Nowy użytkownik:** zacznij od [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) — jeden model `URI → plan → verify → apply/run → observe → repair/evolve` i jedna powłoka `uri` / `urish`.

## Architektura

```txt
uri3       = URI, discovery, routing, skanowanie, graf, workflow executor, log://, schema, doctor
nl2uri     = natural language / query → URI plan (single, list, tree, task, graph)
uri2flow   = compact URI flow → expanded workflow graph (bez wykonania)
uri2ops    = operation registry + operator adapters + policy + serve (A2A/MCP)
uri2voice  = STT/TTS/voice command execution (mock MVP; touri manifests)
uri2pact   = markpact:// README import (capabilities + flows)
uri2run    = neutral runtime transport layer (python/shell/http/stdio/sse/ws/docker/ssh/mcp/a2a/flow/graph)
uri2verify = data quality gates, workflow replay, regression tests
urigen     = URI ecosystem generator: proposals, artifacts, verify/explain/apply gates
urish      = unified URI shell (`uri`): ask, ecosystem, dashboard, ticket/evolve/repair, policy
touri      = capability matching, fallbacks, data quality → delegates execution to uri2run
nl2a       = prompt → URI Tree → Domain Pack → agent contract → generated agent
hypervisor = registry, policy, deployment, lifecycle
generator  = deterministyczny kod agenta z YAML
domains/*  = logika domenowa (Domain Pack)
agents/generated/* = artefakty — nie edytować ręcznie
```

Szczegóły: [`docs/ARCHITECTURE_V0_5.md`](docs/ARCHITECTURE_V0_5.md) · [`docs/URI2FLOW.md`](docs/URI2FLOW.md) · [`docs/URI2OPS.md`](docs/URI2OPS.md) · [`packages/README.md`](packages/README.md)

## Instalacja

```bash
pip install -e '.[dev]'
# opcjonalnie:
pip install -e '.[browser]'   # Playwright
pip install -e '.[windows]'   # pywinauto / Windows UIA
# lub
uv sync
```

## Zewnętrzne paczki

`hypervisor` nie ma teraz runtime dependency na `markpact`, `pactown`,
`iterun`, `intract`, `nlp2dsl` ani `semcod/nlp2uri`. Bezpośrednio używane
zewnętrzne paczki z `semcod/*` to narzędzia dev: `goal`, `costs`, `pfix`.

Integracje `markpact://` w `touri` i `uri2flow` parsują fenced blocki
`markpact:*` z README i walidują je lokalnie; nie uruchamiają runtime'u
`markpact`.

Szczegóły audytu wersji i zalecane akcje: [`docs/EXTERNAL_PACKAGES.md`](docs/EXTERNAL_PACKAGES.md).

## Szybki start

```bash
make uri-tree
make validate
make graph
make test
```

Lub jednym skryptem (pipeline bez pełnego pytest):

```bash
bash examples/01_quickstart_local/run.sh
```

Pełny pipeline weather-map (bez LLM):

```bash
bash examples/04_nl2a_weather_map/run.sh
# lub skrót:
make nl2a-weather
```

Ręcznie krok po kroku:

```bash
nl2uri -p "generuj mape pogody dwa tygodnie do przodu w html" \
  --out domains/weather_map/uri_tree.yaml
uri3 validate-tree domains/weather_map/uri_tree.yaml
uri3 graph domains/weather_map/uri_tree.yaml
nl2a -p "generuj mape pogody dwa tygodnie do przodu w html"
```

## nl2uri — multi-output + LLM graph

```bash
nl2uri plan -p "otwórz Chrome i sprawdź localhost:8101/health"
nl2uri task -p "otwórz Chrome i sprawdź localhost:8101/health" --validate --dry-run
nl2uri graph -p "wygeneruj agenta i uruchom go jeśli health OK" --llm --validate
```

Zobacz [`docs/NL2URI.md`](docs/NL2URI.md) · [`examples/13_nl2uri_multi_uri_graph/`](examples/13_nl2uri_multi_uri_graph/README.md).

## uri2flow — compact flow → workflow graph

```bash
uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml
uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
uri3 validate-workflow output/weather.uri.graph.yaml
uri3 run-workflow output/weather.uri.graph.yaml --approve --browser mock
```

`uri2flow` **nie wykonuje** flow — tylko rozwija krótki format URI do `workflow_graph` dla `uri3`.

Zobacz [`docs/URI2FLOW.md`](docs/URI2FLOW.md) · [`examples/15_compact_uri_flow/`](examples/15_compact_uri_flow/README.md).

## uri3 — skanowanie, workflow, logi

```bash
uri3 scan http://localhost:8101
uri3 logs 'log://hypervisor?level=ERROR&limit=50'
uri3 schema 'log://'
uri3 schema --list
uri3 resolve env://OPENROUTER_API_KEY

# workflow executor (v0.6)
uri3 validate-workflow examples/14_workflow_executor_mock/task_graph.yaml
uri3 plan-workflow examples/14_workflow_executor_mock/task_graph.yaml
uri3 run-workflow examples/14_workflow_executor_mock/task_graph.yaml --dry-run
uri3 run-workflow examples/14_workflow_executor_mock/task_graph.yaml --approve --browser playwright

# governance (Sprint 4)
uri3 doctor
uri3 doctor --build-registry
uri3 explain weather://forecast/Gdansk/14/html
touri explain weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities
uri2verify replay check-agent-health
```

## uri2verify — data quality, replay, verification

```bash
uri2verify replay check-agent-health
uri2verify capability-plan .
uri2verify data-quality examples/20_touri_capabilities weather://forecast/Gdansk/14/html
uri3 doctor --capability-plan --replay-failures
```

Zobacz [`docs/URI3.md`](docs/URI3.md) · [`packages/uri2verify/README.md`](packages/uri2verify/README.md) · [`docs/PACKAGE_BOUNDARIES.md`](docs/PACKAGE_BOUNDARIES.md).

## urigen — URI Ecosystem Generator

`urigen` generuje izolowany pakiet ekosystemu URI: proposal, `ecosystem.yaml`,
capability manifests, compact flows, kontrakty, deployment fragment, README
markpact i test plan. Nie jest runtime'em i nie wykonuje backendów bezpośrednio.

Profile: `minimal`, `voice`, `dashboard-agent` (hypervisor dashboard system agent).

```bash
urigen plan -p "stworz agenta pogodowego z healthcheckiem" \
  --out output/proposals/weather.ecosystem.proposal.yaml

urigen plan -p "stwórz web UI agenta hypervisor-dashboard" \
  --profile dashboard-agent \
  --out output/proposals/hypervisor-dashboard.ecosystem.proposal.yaml

urigen generate output/proposals/weather.ecosystem.proposal.yaml \
  --out output/ecosystems/weather

urigen verify output/ecosystems/weather/ecosystem.yaml
urigen explain output/ecosystems/weather/ecosystem.yaml
urigen apply output/ecosystems/weather/ecosystem.yaml --plan
urigen apply output/ecosystems/weather/ecosystem.yaml --approve
urigen apply output/ecosystems/weather/ecosystem.yaml --rollback
```

`plan` i `verify` są side-effect safe. `generate` pisze tylko do wskazanego
`--out`. `apply --plan` zapisuje diff; `apply --approve` mutuje repo
transakcyjnie z rollback manifestem przy błędzie.

Zobacz [`packages/urigen/README.md`](packages/urigen/README.md).

## uri2run — runtime transports

```bash
uri2run call python://uri2voice.stt:transcribe --payload '{"text":"test"}'
uri2run call shell://echo --payload '{"args":["hello"]}'
```

`touri` keeps capability matching, fallbacks and data quality gates; backend execution is delegated to `uri2run`.

## Testy i CI

```bash
make architecture-gate   # tests/architecture + uri3 doctor (boundaries, envelope, transports)
make test                # pełny pytest (~420 testów)
make examples-test       # integracja examples/* (run.sh + inline demos)
make ci-gate             # architecture-gate + test + examples-test
bash scripts/test-all-examples.sh   # 25 przykładów sekwencyjnie (shell smoke)
```

Integracja examples jest w `tests/examples/` — katalog `catalog.py`, parametryzowane `run.sh`, smoke manifestów touri i importów stacku (`uri2run`, `uri3`, `touri`). CI (`.github/workflows/ci.yml`) uruchamia osobny job **Examples integration** po pełnym pytest.

Markery pytest: `examples`, `docker` (ex03), `slow` (ex23 tutorial). Ex11 (Playwright) wymaga `pip install -e '.[browser]' && playwright install chromium`.

Zobacz [`examples/README.md`](examples/README.md) · [`docs/PACKAGE_BOUNDARIES.md`](docs/PACKAGE_BOUNDARIES.md) · [`docs/CLI_MAP.md`](docs/CLI_MAP.md).

## uri2ops — operator runtime

```bash
uri2ops validate examples/10_browser_operator/task.health.yaml
uri2ops run examples/10_browser_operator/task.health.yaml --adapter mock --approve
uri2ops serve --port 8791
uri2ops registry list
```

Zobacz [`docs/URI2OPS.md`](docs/URI2OPS.md) · [`packages/uri2ops/README.md`](packages/uri2ops/README.md).

## Meta-agent

```bash
make meta-pipeline
make meta-repair
make run-meta-agent
```

Przykładowe prompty i kontrakty: [`examples/`](examples/README.md).

## Przykłady (`examples/*/*`)

Każdy katalog z `run.sh` można uruchomić bezpośrednio; pełna lista:

```bash
bash scripts/test-all-examples.sh
pytest tests/examples -q
```

| # | Katalog | Opis | Start |
|---|---------|------|-------|
| 01 | [`examples/01_quickstart_local`](examples/01_quickstart_local/) | Lokalny start bez Dockera | `bash examples/01_quickstart_local/run.sh` |
| 02 | [`examples/02_uri3_scan_http`](examples/02_uri3_scan_http/) | Skan HTTP/A2A-like | inline / wymaga agenta |
| 03 | [`examples/03_ssh_remote_agent`](examples/03_ssh_remote_agent/) | Docker + SSH testenv | `make docker-testenv-up` |
| 04 | [`examples/04_nl2a_weather_map`](examples/04_nl2a_weather_map/) | Prompt weather-map | `bash examples/04_nl2a_weather_map/run.sh` |
| 05 | [`examples/05_meta_repair`](examples/05_meta_repair/) | Naprawa uszkodzonego kontraktu | inline |
| 06 | [`examples/06_orders_agent`](examples/06_orders_agent/) | Kontrakt agenta zamówień | inline |
| 07 | [`examples/07_invoices_agent`](examples/07_invoices_agent/) | Prompt agenta faktur | inline |
| 08 | [`examples/08_evolution`](examples/08_evolution/) | Evolution proposals | `make evolution-check` |
| 09 | [`examples/09_run_agent_hypervisor`](examples/09_run_agent_hypervisor/) | run-agent / lifecycle | `bash examples/09_run_agent_hypervisor/run.sh` |
| 10 | [`examples/10_browser_operator`](examples/10_browser_operator/) | uri2ops mock browser | `run.sh` |
| 11 | [`examples/11_playwright_browser`](examples/11_playwright_browser/) | uri2ops Playwright | `run.sh` (+ browser extra) |
| 12 | [`examples/12_android_operator`](examples/12_android_operator/) | uri2ops Android ADB | `run.sh` |
| 13 | [`examples/13_pcwin_operator`](examples/13_pcwin_operator/) | uri2ops Windows UIA | `run.sh` |
| 13 | [`examples/13_nl2uri_multi_uri_graph`](examples/13_nl2uri_multi_uri_graph/) | nl2uri multi-output | `run.sh` |
| 14 | [`examples/14_uri2ops_serve`](examples/14_uri2ops_serve/) | uri2ops HTTP daemon | `run.sh` |
| 14 | [`examples/14_workflow_executor_mock`](examples/14_workflow_executor_mock/) | uri3 workflow executor | `run.sh` |
| 15 | [`examples/15_compact_uri_flow`](examples/15_compact_uri_flow/) | Skrócony przepływ URI | `run.sh` |
| 15 | [`examples/15_playwright_browser`](examples/15_playwright_browser/) | uri3 Playwright workflow | inline (mock via uri3) |
| 16 | [`examples/16_llm_graph_planner`](examples/16_llm_graph_planner/) | LLM graph planner | `run.sh` |
| 17 | [`examples/17_flow_vs_graph`](examples/17_flow_vs_graph/) | Compact flow vs expanded graph | `run.sh` |
| 18 | [`examples/18_llm_flow_planner`](examples/18_llm_flow_planner/) | LLM compact flow planner | `run.sh` |
| 20 | [`examples/20_touri_capabilities`](examples/20_touri_capabilities/) | `touri` capability manifests | `run.sh` |
| 21 | [`examples/21_touri_voice`](examples/21_touri_voice/) | STT/TTS/voice jako capability pack | `run.sh` |
| 22 | [`examples/22_markpact_weather`](examples/22_markpact_weather/) | `markpact://` capability + flow README | `run.sh` |
| 23 | [`examples/23_nl_to_agent_tutorial`](examples/23_nl_to_agent_tutorial/) | **Tutorial NL → URI → wykonanie → agent HTTP** | `run.sh` |

Docker + SSH testenv:

```bash
make docker-ssh-up
make scan-http
make docker-ssh-down
```

## Deployment registry

Rejestr wdrożeń: [`deployments/agent_deployments.yaml`](deployments/agent_deployments.yaml)

```bash
hypervisor deployments
hypervisor run-agent weather-map-agent.local --dry-run
hypervisor run-agent weather-map-agent.local --detach --if-running reuse
hypervisor inspect-agent weather-map-agent.local
hypervisor supervise weather-map-agent.local --repair auto
hypervisor run-agent weather-map-agent.local --detach --wait-healthy --supervise-repair auto
make run-weather-agent
```

`inspect-agent` rozdziela stan procesu od zdrowia usługi (`readiness.process`
vs `readiness.health`) i dołącza probe agent card oraz ostatnie błędy z `log://`.
`supervise --repair auto` klasyfikuje incydenty (port/health drift, stale pid)
i wykonuje ograniczoną pętlę restart / sync_health. `--wait-healthy` na
`run-agent` kończy się dopiero gdy usługa odpowiada na `/health`, nie tylko gdy PID istnieje.

Ewolucyjny self-healing (`hypervisor repair`):

```bash
hypervisor repair diagnose weather-map-agent.local
hypervisor repair apply weather-map-agent.local --safe
hypervisor supervise weather-map-agent.local --repair auto --learn
hypervisor repair learn output/incidents/.../inc_*.yaml
```

Incydenty są artefaktami ze schemą (`schemas/incident.schema.json`); nierozwiązane awarie
generują propozycję ewolucji w `evolution/proposals/from_incident_*.yaml`.

**urish** — unified URI shell (`uri` command):

Dashboard-agent powstaje przez kontrolowany pipeline URI (nie ręczną aplikację webową):

```bash
uri ask "stwórz web UI agenta hypervisor-dashboard do pokazywania procesów"
# → Subtype: dashboard-agent, profile, planned URIs, next steps z ecosystem generate

uri ecosystem plan "..." --profile dashboard-agent \
  --out output/proposals/hypervisor-dashboard.ecosystem.proposal.yaml
uri ecosystem generate output/proposals/hypervisor-dashboard.ecosystem.proposal.yaml \
  --out output/ecosystems/hypervisor-dashboard
uri ecosystem verify output/ecosystems/hypervisor-dashboard/ecosystem.yaml
uri ecosystem apply output/ecosystems/hypervisor-dashboard/ecosystem.yaml --plan
uri ecosystem apply output/ecosystems/hypervisor-dashboard/ecosystem.yaml --approve
uri agent run hypervisor-dashboard.local --wait-healthy --approve
uri dashboard create hypervisor-dashboard --plan-only   # skrót orkiestracji
```

Ticket → evolution → ecosystem (gdy ticket opisuje dashboard):

```bash
uri ticket show ticket://feature/PL-10
uri evolve from-ticket ticket://feature/PL-10
uri proposal verify evolution/proposals/proposal_from_ticket_PL-10.yaml
uri proposal apply evolution/proposals/proposal_from_ticket_PL-10.yaml --sandbox
```

Pozostałe komendy:

```bash
uri call python://uri2voice.stt:transcribe --payload '{"text":"test"}'
uri explain weather://forecast/Gdansk/14/html
uri ask "stworz agenta pogodowego z healthcheckiem"
uri watch health://agent/weather-map-agent.local --count 3
uri shell
uri agent health weather-map-agent.local
uri repair diagnose weather-map-agent.local
uri ticket list
uri doctor
uri doctor --strict   # + walidacja incidents/tickets/evolution i lifecycle envelope
uri ecosystem plan "stworz agenta pogodowego" --out output/proposals/weather.yaml
```

Policy: `--dry-run`, `--approve`, `--policy safe|dev|prod`, `--readonly`, `--sandbox`.
Piping: `--stdin`, `--stdin-envelope`, `uri select data.text`.

Skróty: `config/cli_shortcuts.uri.yaml` (`uri wh`, `uri hwa`, `uri rwa`).

Zobacz [`packages/urish/README.md`](packages/urish/README.md).

Standaryzacja artefaktów (URI3 Artifact YAML):

```bash
hypervisor artifacts schemas          # walidacja schemas/*.schema.json
hypervisor artifacts check            # walidacja output/incidents, evolution/proposals, runtime state
hypervisor artifacts lifecycle        # raport pokrycia $schema/apiVersion/kind/uri.self
hypervisor artifacts lifecycle --strict
hypervisor ticket import planfile.yaml
hypervisor evolution propose-from-ticket PL-1
hypervisor evolution propose-from-incident output/incidents/.../inc_*.yaml
```

Runtime state (`output/runtime/agents/*/state.json`) i logi (`log://`) używają wspólnego
envelope (`apiVersion`, `kind`, `$schema`). Tickety planfile (`ticket://feature/PL-1`) i
incydenty (`incident://...`) są dwoma źródłami ewolucji przez `evolution://proposal/from-*`.
Configi `config/*.uri.yaml` też są canonical URI3 config artifacts; stare pola konfiguracyjne
są pod `spec`, a loadery zachowują kompatybilny odczyt.
`artifacts lifecycle` skanuje configi, deploymenty, kontrakty, domain packi, runtime state,
workflow outputs, incydenty, tickety i propozycje, żeby pokazać, które pliki nadal są legacy
albo luźnymi JSON/YAML bez stabilnego URI.

Zobacz [`examples/09_run_agent_hypervisor/`](examples/09_run_agent_hypervisor/README.md).

## Ważna zasada

Nie edytuj `agents/generated/` ręcznie. Zmieniaj `contracts/agents/*.yaml` lub pipeline domeny, potem regeneruj.

## Dokumentacja

Pełny indeks: [`docs/README.md`](docs/README.md)

Architektura i podział paczek: [`docs/PACKAGE_BOUNDARIES.md`](docs/PACKAGE_BOUNDARIES.md)

Przepływ generacji i uruchomienia agenta: [`docs/HYPERVISOR_WORKFLOW.md`](docs/HYPERVISOR_WORKFLOW.md)

Konfiguracja URI: [`docs/CONFIG_URI_YAML.md`](docs/CONFIG_URI_YAML.md) · [`config/llm.uri.yaml`](config/llm.uri.yaml)

### Aktualne (v0.5–v0.6)

- [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) — **start tutaj** (15 min, jeden cykl życia)
- [`docs/MENTAL_MODEL.md`](docs/MENTAL_MODEL.md) · [`docs/URI_COOKBOOK.md`](docs/URI_COOKBOOK.md)
- [`docs/HYPERVISOR_WORKFLOW.md`](docs/HYPERVISOR_WORKFLOW.md) — generacja + uruchomienie przez hypervisor
- [`docs/CONFIG_URI_YAML.md`](docs/CONFIG_URI_YAML.md) — konwencja `*.uri.yaml`
- [`docs/URI3.md`](docs/URI3.md) — uri3 CLI, workflow, schematy URI
- [`docs/NL2URI.md`](docs/NL2URI.md) — prompt → URI plan (multi-output, LLM graph)
- [`docs/URI2FLOW.md`](docs/URI2FLOW.md) — compact URI flow → workflow graph
- [`docs/URI2OPS.md`](docs/URI2OPS.md) — operator runtime, serve, adaptery
- [`docs/OPERATOR_RUNTIME.md`](docs/OPERATOR_RUNTIME.md) · [`docs/URI_OPERATION_REGISTRY.md`](docs/URI_OPERATION_REGISTRY.md)
- [`docs/NL2A_DOMAIN_PACKS.md`](docs/NL2A_DOMAIN_PACKS.md) — Domain Pack pipeline
- [`docs/META_AGENT.md`](docs/META_AGENT.md) — meta-agent CLI/API
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — wdrożenie lokalne i Docker
- [`docs/AUTO_EVOLUTION_PIPELINE.md`](docs/AUTO_EVOLUTION_PIPELINE.md) — kontrolowana autoewolucja
- [`docs/EVOLUTION.md`](docs/EVOLUTION.md) — evolution proposals
- [`docs/STANDARDS.md`](docs/STANDARDS.md) — MCP, Protobuf, JSON Schema
- [`docs/CONTRACTS.md`](docs/CONTRACTS.md) — format kontraktów YAML
- [`docs/GENERATOR.md`](docs/GENERATOR.md) — generator agentów
- [`docs/EXTERNAL_PACKAGES.md`](docs/EXTERNAL_PACKAGES.md) — audyt lokalnych `semcod/*` i `wronai/*` integracji
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — roadmap wersji
- [`CHANGELOG.md`](CHANGELOG.md) · [`TODO.md`](TODO.md)

### Historyczne

Starsze wersje (`docs/HYPERVISOR_V0_2.md` … `V0_4.md`, `docs/URI2LLM.md`) opisują wcześniejsze etapy API. Resolver URI jest dziś w paczce `uri3` (`uri3.resolvers`).

## License

Licensed under Apache-2.0.

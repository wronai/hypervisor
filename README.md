# Resource Agent System v0.6


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.5.28-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$20.35-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-14.5h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $20.3507 (33 commits)
- 👤 **Human dev:** ~$1454 (14.5h @ $100/h, 30min dedup)

Generated on 2026-06-15 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

Monorepo: **uri3**, **nl2uri**, **uri2flow**, **uri2ops**, **hypervisor**, **agent factory** — contract-first thin agents with pipeline `prompt → URI plan → Domain Pack → generated agent`, plus the URI operator layer.

**New user:** start with [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) — one model `URI → plan → verify → apply/run → observe → repair/evolve` and one shell `uri` / `urish`.

**Repository map:** [`docs/README.md`](docs/README.md) (index of `docs/*`) · [`docs/SYSTEM_MAP.md`](docs/SYSTEM_MAP.md) (current structure from `project/map.toon.yaml`) · [`examples/README.md`](examples/README.md) (index of `examples/*/*`) · [`TODO.md`](TODO.md) · [`CHANGELOG.md`](CHANGELOG.md) · [`www/README.md`](www/README.md) (product pages)

Polish README: [`README.pl.md`](README.pl.md)

## Taskinity WWW (product pages)

After `make start` (Docker `:8788`) or `urish www serve`:

| URL | File | Description |
|-----|------|-------------|
| http://localhost:8788/www/ | [`www/index.html`](www/index.html) | Landing — tour, integrations, office examples, offer |
| http://localhost:8788/www/chat.html | [`www/chat.html`](www/chat.html) | NL chat → URI plan → run (dry-run default; not auto-execute) |
| http://localhost:8788/www/przyklady.html | [`www/przyklady.html`](www/przyklady.html) | Integration lab — PASS cards, filters, commands from `examples/` |
| http://localhost:8788/www/docs/examples.html | [`www/docs/examples.html`](www/docs/examples.html) | **Docs examples** — full `examples/*/*` content (README + YAML/SH) |
| http://localhost:8788/www/demo.html | [`www/demo.html`](www/demo.html) | Technical URI demo (static) |

Regenerate docs examples: `make www-docs` · WWW tests: `make www-test` · smoke: `make www-smoke`

Default language is **English**; PL and DE are available via the language toggle on the landing page.

Details: [`www/README.md`](www/README.md) · [`docs/DASHBOARD.md`](docs/DASHBOARD.md) · [`docs/CHAT_AND_WORKFLOWS.md`](docs/CHAT_AND_WORKFLOWS.md)

### Real agents, communication, monitoring (FAQ)

| Question | Short answer |
|----------|----------------|
| Create real HTTP agents? | **Yes** — `nl2a`, `uri ecosystem`, evolution proposals → `agents/generated/` + `deployments/agent_deployments.yaml` |
| Communicate with them? | **Yes** — `/health`, agent card, URI schemes (`health://`, `repair://`, `view://`), dashboard `POST /api/uri/call` |
| Improve / evolve? | **Yes, gated** — `supervise --repair auto`, incidents, `uri evolve` → regenerate with approval |
| Several agents at once? | **Yes** — independent ports/PIDs (e.g. weather `:8118`, invoices `:8123`) |
| Monitor many agents? | **`hypervisor`** + **dashboard** (`/api/events`, SSE) + **`uri3 logs`** + `output/logs/` / `output/incidents/` |

Full guide: [`docs/AGENTS_AND_MONITORING.md`](docs/AGENTS_AND_MONITORING.md) · PL: [`docs/AGENTS_AND_MONITORING.pl.md`](docs/AGENTS_AND_MONITORING.pl.md)

**Tutorial (3 agents + chat + markpact export):** [`docs/TUTORIAL_THREE_AGENTS.md`](docs/TUTORIAL_THREE_AGENTS.md) · PL: [`docs/TUTORIAL_THREE_AGENTS.pl.md`](docs/TUTORIAL_THREE_AGENTS.pl.md)

**Tutorial (NL-generated agent + `schema://` + file/device/robot/cron):** [`docs/TUTORIAL_AGENT_SCHEMA_URI.md`](docs/TUTORIAL_AGENT_SCHEMA_URI.md) · PL: [`docs/TUTORIAL_AGENT_SCHEMA_URI.pl.md`](docs/TUTORIAL_AGENT_SCHEMA_URI.pl.md)

```bash
hypervisor deployments
hypervisor run-agent weather-map-agent.local --detach --if-running reuse
hypervisor run-agent invoices-agent.local --detach --if-running reuse
curl -s http://localhost:8788/api/events?limit=10
```

### Desktop autonomy

`agent://desktop-operator` is a generic capability agent backed by `uri2ops`.
It exposes browser, screen, input, Windows UI Automation and Android operations
through CLI, A2A and MCP endpoints. Domain logic stays in `domains/*`; the
desktop operator stays in [`agents/operators/desktop_operator.yaml`](agents/operators/desktop_operator.yaml).
The generic capability domain is documented in
[`domains/desktop_ops/`](domains/desktop_ops/), with cards for browser, screen,
input, pcwin and Android operations.

Guide: [`docs/DESKTOP_AUTONOMY.md`](docs/DESKTOP_AUTONOMY.md)

```bash
taskinity proof view://process/agent/weather-map-agent.local/latest
uri proof view://process/agent/weather-map-agent.local/latest
hypervisor run-agent desktop-operator.local --detach --wait-healthy
uri2ops serve --host 127.0.0.1 --port 8791
curl -s http://127.0.0.1:8791/.well-known/agent-card.json
```

### Physical autonomy

`agent://device-robot-operator` is a generic capability agent for robots and
field devices. It uses `robot://` for actors with motion, pose, missions and
safety state, and `device://` for sensors, actuators, PLC-like devices and
register reads/writes. Mutating physical actions require approval and should
include a `human://operator/safety/approve` gate in plans.

Guide: [`docs/PHYSICAL_AUTONOMY.md`](docs/PHYSICAL_AUTONOMY.md) · domain:
[`domains/physical_ops/`](domains/physical_ops/) · example:
[`examples/36_physical_ops/`](examples/36_physical_ops/)

```bash
hypervisor run-agent device-robot-operator.local --detach --wait-healthy
uri2ops run examples/36_physical_ops/task.robot.yaml --adapter mock --approve
uri2ops run examples/36_physical_ops/task.device.yaml --adapter mock --approve
```

### Chat and office workflows (summary)

```text
NL  →  uri ask / POST /api/ask  →  planned URIs + next_steps (markdown)
User  →  uri run … --dry-run  or  --approve  →  touri / uri3 / hypervisor
```

- **Batch:** one NL command per line in chat → `Detected N commands`
- **Office:** six landing cards ↔ [`domains/office/`](domains/office/) ↔ [`examples/33_office_workflows/`](examples/33_office_workflows/)
- **Compact flow (ex15):** `uri2flow expand` → `uri3 run-workflow` (separate from chat NL path)

```bash
uri ask "Wejdź na stronę dostawcy, pobierz raport CSV za ten miesiąc i zapisz w rozliczeniach."
uri run workflow://office/supplier-report/monthly --dry-run
bash examples/33_office_workflows/run.sh
```

## Architecture

Current structural snapshot from `project/map.toon.yaml`: **731 modules**,
**2269 functions**, average CC **3.7**, **0 dependency cycles**. The main watch
points are orchestration fan-out (`createVoiceController`, `generate_ecosystem`,
`parse_duplication`, `register_call_commands`, `register_ecosystem_commands`)
and large UI/runtime files (`www/landing.js`, `www/landing-i18n.js`,
`deployment_registry/lifecycle.py`). See
[`docs/SYSTEM_MAP.md`](docs/SYSTEM_MAP.md).

```txt
uri3       = URI, discovery, routing, scan, graph, workflow executor, log://, schema, doctor
nl2uri     = natural language / query → URI plan (single, list, tree, task, graph)
uri2flow   = compact URI flow → expanded workflow graph (no execution)
uri2ops    = operation registry + operator adapters + policy + serve (A2A/MCP)
uri2voice  = STT/TTS/voice command execution (mock + Whisper STT; touri manifests)
uri2pact   = markpact:// README import (capabilities + flows)
uri2run    = neutral runtime transport layer (python/shell/http/stdio/sse/ws/docker/ssh/mcp/a2a/flow/graph)
uri2verify = data quality gates, workflow replay, regression tests
urigen     = URI ecosystem generator: proposals, artifacts, verify/explain/apply gates
urish      = unified URI shell (`uri`): ask/nl, ecosystem (plan/generate/verify/apply), agent (run/health/status/repair), repair (diagnose/apply/learn), doctor, explain, watch, call – **jedyna komenda do pełnej kontroli systemu i agentów z examples z poziomu shell** (wdrażanie, weryfikacja separacji wyodrębniania, procesów runtime/health/repair loops)
touri      = capability matching, fallbacks, data quality → delegates execution to uri2run
nl2a       = prompt → URI Tree → Domain Pack → agent contract → generated agent
hypervisor = registry, policy, deployment, lifecycle
generator  = deterministic agent code from YAML
domains/*  = domain logic (Domain Pack)
agents/generated/* = artifacts — do not edit manually
```

Details: [`docs/ARCHITECTURE_V0_5.md`](docs/ARCHITECTURE_V0_5.md) · [`docs/URI2FLOW.md`](docs/URI2FLOW.md) · [`docs/URI2OPS.md`](docs/URI2OPS.md) · [`packages/README.md`](packages/README.md)

## Installation

```bash
pip install -e '.[dev]'
# optionally:
pip install -e '.[browser]'   # Playwright
pip install -e '.[windows]'   # pywinauto / Windows UIA
# lub
uv sync
```

Local agents (`hypervisor run-agent`, `make start-agents`) need **uvicorn** — it is included in the `dev` extra.

## External packages

`hypervisor` no longer has a runtime dependency on `markpact`, `pactown`,
`iterun`, `intract`, `nlp2dsl` or `semcod/nlp2uri`. External packages from `semcod/*`
used directly are dev tools: `goal`, `costs`, `pfix`.

## Wdrażanie i weryfikacja agentów z examples wyłącznie via `urish`

( po aktualizacji refaktorów i reanalizie )

Użyj tylko `urish` (shell) do deploy i check:

- `urish ecosystem plan examples/06_orders_agent --profile agent` + apply --approve (generuje proposal z domains/agents/caps/flows/deployments)
- `urish agent run weather-map-agent.local` (lub --dry-run); podobnie dashboard, desktop-operator, orders/invoices via plans
- Verify extraction (wyodrębnianie): `urish doctor --strict`, `urish explain agent://...` – agenty poprawnie w agents/generated/* (z contracts/domains w examples/), capabilities w examples/20_touri_capabilities (touri registry), brak domain vocab pollution w core (nl2uri, hypervisor cli). Card ma "generated_from" contract.
- Verify processes (realizacja): `urish agent health <id>`, `urish agent status`, `urish repair diagnose`, `urish watch health://...`, `urish call <health_uri>` – pids running, uvicorn cmds z planu, health/card 200 z capabilities z contract, runtime_state, readiness ok (małe drift), zero errors, repair clean (no incidents). Lifecycle i state centralized działają.

Aktualne: weather-map-agent.local, hypervisor-dashboard.local, desktop-operator.local healthy/running. Plany dla orders/invoices poprawne (apply może wymagać clean verify + approve). Przykłady 05(meta_repair), 09(run_agent), 16www(monitor), 20-23, 30-33 PASS w harness.

Zobacz docs/DEPLOYMENT.md dla szczegółów wyłącznie-urish flow. To potwierdza, że po refaktorach (thinning lifecycle/cli, centralizacja state/now_iso/unwrap, dedupy) agenty są poprawnie wyodrębniane i procesy realizowane autonomicznie.

`markpact://` integrations in `touri` and `uri2flow` parse fenced `markpact:*`
blocks from README and validate them locally; they do not run the `markpact` runtime.

Version audit details and recommended actions: [`docs/EXTERNAL_PACKAGES.md`](docs/EXTERNAL_PACKAGES.md).

## Quick start

```bash
make uri-tree
make validate
make graph
make test
```

Or one script (pipeline without full pytest):

```bash
bash examples/01_quickstart_local/run.sh
```

Full weather-map pipeline (no LLM):

```bash
bash examples/04_nl2a_weather_map/run.sh
# or shortcut:
make nl2a-weather
```

Manual step by step:

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

See [`docs/NL2URI.md`](docs/NL2URI.md) · [`examples/13_nl2uri_multi_uri_graph/`](examples/13_nl2uri_multi_uri_graph/README.md).

## uri2flow — compact flow → workflow graph

```bash
uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml
uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
uri3 validate-workflow output/weather.uri.graph.yaml
uri3 run-workflow output/weather.uri.graph.yaml --approve --browser mock
```

`uri2flow` does **not execute** the flow — it only expands the compact URI format into a `workflow_graph` for `uri3`.

See [`docs/URI2FLOW.md`](docs/URI2FLOW.md) · [`examples/15_compact_uri_flow/`](examples/15_compact_uri_flow/README.md).

## uri3 — scan, workflow, logs

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

See [`docs/URI3.md`](docs/URI3.md) · [`packages/uri2verify/README.md`](packages/uri2verify/README.md) · [`docs/PACKAGE_BOUNDARIES.md`](docs/PACKAGE_BOUNDARIES.md).

## urigen — URI Ecosystem Generator

`urigen` generates an isolated URI ecosystem package: proposal, `ecosystem.yaml`,
capability manifests, compact flows, contracts, deployment fragment, markpact README
and test plan. It is not a runtime and does not execute backends directly.

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

`plan` and `verify` are side-effect safe. `generate` writes only to the specified
`--out`. `apply --plan` saves a diff; `apply --approve` mutates the repo
transactionally with a rollback manifest on failure.

See [`packages/urigen/README.md`](packages/urigen/README.md).

## uri2run — runtime transports

```bash
uri2run call python://uri2voice.stt:transcribe --payload '{"text":"test"}'
uri2run call shell://echo --payload '{"args":["hello"]}'
```

`touri` keeps capability matching, fallbacks and data quality gates; backend execution is delegated to `uri2run`.

## Tests and CI

```bash
make architecture-gate   # tests/architecture + uri3 doctor (boundaries, envelope, transports)
make test                # full pytest (~420 tests)
make examples-test       # examples/* integration (run.sh + inline demos)
make ci-gate             # architecture-gate + test + examples-test
bash scripts/test-all-examples.sh   # 27 checks sequentially (shell smoke)
```

Examples integration is in `tests/examples/` — catalog `catalog.py`, parameterized `run.sh`, touri manifest smoke and stack imports (`uri2run`, `uri3`, `touri`). CI (`.github/workflows/ci.yml`) runs a separate **Examples integration** job after full pytest.

Pytest markers: `examples`, `docker` (ex03), `slow` (ex23 tutorial). Ex11 (Playwright) requires `pip install -e '.[browser]' && playwright install chromium`.

See [`examples/README.md`](examples/README.md) · [`docs/PACKAGE_BOUNDARIES.md`](docs/PACKAGE_BOUNDARIES.md) · [`docs/CLI_MAP.md`](docs/CLI_MAP.md).

## uri2ops — operator runtime

```bash
uri2ops validate examples/10_browser_operator/task.health.yaml
uri2ops run examples/10_browser_operator/task.health.yaml --adapter mock --approve
uri2ops serve --port 8791
uri2ops registry list
```

See [`docs/URI2OPS.md`](docs/URI2OPS.md) · [`packages/uri2ops/README.md`](packages/uri2ops/README.md).

## Meta-agent

```bash
make meta-pipeline
make meta-repair
make run-meta-agent
```

Example prompts and contracts: [`examples/`](examples/README.md).

## Examples (`examples/*/*`)

Each directory with `run.sh` can be run directly; full list:

```bash
bash scripts/test-all-examples.sh
pytest tests/examples -q
```

| # | Directory | Description | Start |
|---|-----------|-------------|-------|
| 01 | [`examples/01_quickstart_local`](examples/01_quickstart_local/) | Local start without Docker | `bash examples/01_quickstart_local/run.sh` |
| 02 | [`examples/02_uri3_scan_http`](examples/02_uri3_scan_http/) | HTTP/A2A-like scan | inline / requires agent |
| 03 | [`examples/03_ssh_remote_agent`](examples/03_ssh_remote_agent/) | Docker + SSH testenv | `make docker-testenv-up` |
| 04 | [`examples/04_nl2a_weather_map`](examples/04_nl2a_weather_map/) | Weather-map prompt | `bash examples/04_nl2a_weather_map/run.sh` |
| 05 | [`examples/05_meta_repair`](examples/05_meta_repair/) | Broken contract repair | inline |
| 06 | [`examples/06_orders_agent`](examples/06_orders_agent/) | Orders agent contract | inline |
| 07 | [`examples/07_invoices_agent`](examples/07_invoices_agent/) | Invoices agent prompt | inline |
| 08 | [`examples/08_evolution`](examples/08_evolution/) | Evolution proposals | `make evolution-check` |
| 09 | [`examples/09_run_agent_hypervisor`](examples/09_run_agent_hypervisor/) | run-agent / lifecycle | `bash examples/09_run_agent_hypervisor/run.sh` |
| 10 | [`examples/10_browser_operator`](examples/10_browser_operator/) | uri2ops mock browser | `run.sh` |
| 11 | [`examples/11_playwright_browser`](examples/11_playwright_browser/) | uri2ops Playwright | `run.sh` (+ browser extra) |
| 12 | [`examples/12_android_operator`](examples/12_android_operator/) | uri2ops Android ADB | `run.sh` |
| 13 | [`examples/13_pcwin_operator`](examples/13_pcwin_operator/) | uri2ops Windows UIA | `run.sh` |
| 13 | [`examples/13_nl2uri_multi_uri_graph`](examples/13_nl2uri_multi_uri_graph/) | nl2uri multi-output | `run.sh` |
| 14 | [`examples/14_uri2ops_serve`](examples/14_uri2ops_serve/) | uri2ops HTTP daemon | `run.sh` |
| 14 | [`examples/14_workflow_executor_mock`](examples/14_workflow_executor_mock/) | uri3 workflow executor | `run.sh` |
| 15 | [`examples/15_compact_uri_flow`](examples/15_compact_uri_flow/) | Compact URI flow | `run.sh` |
| 15 | [`examples/15_playwright_browser`](examples/15_playwright_browser/) | uri3 Playwright workflow | inline (mock via uri3) |
| 16 | [`examples/16_llm_graph_planner`](examples/16_llm_graph_planner/) | LLM graph planner | `run.sh` |
| 17 | [`examples/17_flow_vs_graph`](examples/17_flow_vs_graph/) | Compact flow vs expanded graph | `run.sh` |
| 18 | [`examples/18_llm_flow_planner`](examples/18_llm_flow_planner/) | LLM compact flow planner | `run.sh` |
| 20 | [`examples/20_touri_capabilities`](examples/20_touri_capabilities/) | `touri` capability manifests | `run.sh` |
| 21 | [`examples/21_touri_voice`](examples/21_touri_voice/) | STT/TTS/voice as capability pack | `run.sh` |
| 22 | [`examples/22_markpact_weather`](examples/22_markpact_weather/) | `markpact://` capability + flow README | `run.sh` |
| 23 | [`examples/23_nl_to_agent_tutorial`](examples/23_nl_to_agent_tutorial/) | **Tutorial NL → URI → execution → HTTP agent** | `run.sh` |
| 30 | [`examples/30_golden_path`](examples/30_golden_path/) | **15 min onboarding (urish golden path)** | `run.sh` |
| 31 | [`examples/31_office_day`](examples/31_office_day/) | **Office: portal → invoices → bank → Android** | `run.sh` |
| — | [`examples/22_dashboard_agent`](examples/22_dashboard_agent/) | capability/flow for dashboard-agent | [`README`](examples/22_dashboard_agent/README.md) |
| — | [`examples/16_www_landing_monitor`](examples/16_www_landing_monitor/) | landing monitor (task graph) | [`README`](examples/16_www_landing_monitor/README.md) |

**WWW (readable form):** [`www/docs/examples.html`](www/docs/examples.html) — full content of all READMEs + source files · [`www/przyklady.html`](www/przyklady.html) — PASS lab + filters.

Docker + SSH testenv:

```bash
make docker-ssh-up
make scan-http
make docker-ssh-down
```

## Deployment registry

Deployment registry: [`deployments/agent_deployments.yaml`](deployments/agent_deployments.yaml)

```bash
hypervisor deployments
hypervisor run-agent weather-map-agent.local --dry-run
hypervisor run-agent weather-map-agent.local --detach --if-running reuse
hypervisor inspect-agent weather-map-agent.local
hypervisor supervise weather-map-agent.local --repair auto
hypervisor supervise weather-map-agent.local --watch --repair auto --interval 15
hypervisor run-agent weather-map-agent.local --detach --wait-healthy --supervise-repair auto
make run-weather-agent
```

`inspect-agent` separates process state from service health (`readiness.process`
vs `readiness.health`) and includes agent card probe and recent errors from `log://`.
`supervise --repair auto` classifies incidents (port/health drift, stale pid)
and runs a limited restart / sync_health loop. `--wait-healthy` on
`run-agent` completes only when the service responds on `/health`, not just when the PID exists.
`supervise --watch` keeps the loop running, writes deduped `LogEvent` JSONL to
`output/logs/hypervisor-watch.jsonl`, applies repair backoff for repeated failures
and makes watch events visible in `/api/events` / SSE.

Evolutionary self-healing (`hypervisor repair`):

```bash
hypervisor repair diagnose weather-map-agent.local
hypervisor repair apply weather-map-agent.local --safe
hypervisor supervise weather-map-agent.local --repair auto --learn
hypervisor repair learn output/incidents/.../inc_*.yaml
```

Incidents are artifacts with a schema (`schemas/incident.schema.json`); unresolved failures
generate an evolution proposal in `evolution/proposals/from_incident_*.yaml`.

**urish** — unified URI shell (`uri` command):

The dashboard-agent is created through a controlled URI pipeline (not a hand-written web app):

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
uri dashboard create hypervisor-dashboard --plan-only   # orchestration shortcut
uri www create "stwórz prosty chat markdown połączony z API systemu" --plan-only
uri www serve                                          # http://localhost:8788/www/
```

Ticket → evolution → ecosystem (when the ticket describes a dashboard):

```bash
uri ticket show ticket://feature/PL-10
uri evolve from-ticket ticket://feature/PL-10
uri proposal verify evolution/proposals/proposal_from_ticket_PL-10.yaml
uri proposal apply evolution/proposals/proposal_from_ticket_PL-10.yaml --sandbox
```

Other commands:

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
uri doctor --strict   # + validate incidents/tickets/evolution and lifecycle envelope
uri ecosystem plan "stworz agenta pogodowego" --out output/proposals/weather.yaml
```

Policy: `--dry-run`, `--approve`, `--policy safe|dev|prod`, `--readonly`, `--sandbox`.
Piping: `--stdin`, `--stdin-envelope`, `uri select data.text`.

Shortcuts: `config/cli_shortcuts.uri.yaml` (`uri wh`, `uri hwa`, `uri rwa`).

See [`packages/urish/README.md`](packages/urish/README.md).

Artifact standardization (URI3 Artifact YAML):

```bash
hypervisor artifacts schemas          # validate schemas/*.schema.json
hypervisor artifacts check            # validate output/incidents, evolution/proposals, runtime state
hypervisor artifacts lifecycle        # report $schema/apiVersion/kind/uri.self coverage
hypervisor artifacts lifecycle --strict
hypervisor ticket import planfile.yaml
hypervisor evolution propose-from-ticket PL-1
hypervisor evolution propose-from-incident output/incidents/.../inc_*.yaml
```

Runtime state (`output/runtime/agents/*/state.json`) and logs (`log://`) use a shared
envelope (`apiVersion`, `kind`, `$schema`). Planfile tickets (`ticket://feature/PL-1`) and
incidents (`incident://...`) are two evolution sources via `evolution://proposal/from-*`.
Configs `config/*.uri.yaml` are also canonical URI3 config artifacts; legacy config fields
live under `spec`, and loaders preserve compatible reads.
`artifacts lifecycle` scans configs, deployments, contracts, domain packs, runtime state,
workflow outputs, incidents, tickets and proposals to show which files are still legacy
or loose JSON/YAML without a stable URI.

See [`examples/09_run_agent_hypervisor/`](examples/09_run_agent_hypervisor/README.md).

## Important rule

Do not edit `agents/generated/` manually. Change `contracts/agents/*.yaml` or the domain pipeline, then regenerate.

## Documentation

Full index: [`docs/README.md`](docs/README.md) · project status: [`TODO.md`](TODO.md) · history: [`CHANGELOG.md`](CHANGELOG.md) · completed sprints: [`docs/DONE.md`](docs/DONE.md)

### Start and daily use

| Document | Description |
|----------|-------------|
| [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) | **Start here** (15 min) |
| [`docs/AGENTS_AND_MONITORING.md`](docs/AGENTS_AND_MONITORING.md) | **Real agents, multi-agent ops, monitoring stack** |
| [`docs/TUTORIAL_THREE_AGENTS.md`](docs/TUTORIAL_THREE_AGENTS.md) | **Tutorial: 3 agents, data storage, markpact import** |
| [`docs/CHAT_AND_WORKFLOWS.md`](docs/CHAT_AND_WORKFLOWS.md) | Chat, office cards, batch NL, workflows |
| [`docs/MENTAL_MODEL.md`](docs/MENTAL_MODEL.md) | 7 core concepts |
| [`docs/URI_COOKBOOK.md`](docs/URI_COOKBOOK.md) | “I want to…” recipes |
| [`docs/PROFILES.md`](docs/PROFILES.md) | Ecosystem profiles |
| [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) | `urish` / `uri` commands |
| [`docs/CLI_MAP.md`](docs/CLI_MAP.md) | CLI backend map |
| [`docs/DASHBOARD.md`](docs/DASHBOARD.md) | Web UI as system agent |
| [`docs/AUTONOMY_LOOP.md`](docs/AUTONOMY_LOOP.md) | incident → repair → evolution |
| [`docs/ARTIFACT_STANDARD.md`](docs/ARTIFACT_STANDARD.md) | YAML envelope + statuses |

### v0.6 — workflow, operator, touri

| Document | Description |
|----------|-------------|
| [`docs/NL2URI.md`](docs/NL2URI.md) | NL → URI plan (task/graph/flow) |
| [`docs/FLOW_FORMAT.md`](docs/FLOW_FORMAT.md) | Compact URI flow |
| [`docs/URI2FLOW.md`](docs/URI2FLOW.md) | flow → workflow graph |
| [`docs/URI3.md`](docs/URI3.md) | uri3 CLI, workflow, doctor |
| [`docs/URI2OPS.md`](docs/URI2OPS.md) | Operator runtime + serve |
| [`docs/OPERATOR_RUNTIME.md`](docs/OPERATOR_RUNTIME.md) | validate → plan → run |
| [`docs/URI_OPERATION_REGISTRY.md`](docs/URI_OPERATION_REGISTRY.md) | Rejestr operacji |
| [`docs/OPERATOR_SECURITY.md`](docs/OPERATOR_SECURITY.md) | Polityka, redaction |
| [`docs/TOURI.md`](docs/TOURI.md) | Capability manifests |
| [`docs/MARKPACT_WITH_TOURI.md`](docs/MARKPACT_WITH_TOURI.md) | markpact:// |
| [`docs/VOICE_WITH_TOURI.md`](docs/VOICE_WITH_TOURI.md) | STT/TTS/voice |
| [`docs/SERVICE_RESULT.md`](docs/SERVICE_RESULT.md) | Result envelope |
| [`docs/ANTI_TELLM.md`](docs/ANTI_TELLM.md) | LLM safeguards |
| [`docs/URI2RUN_ARCHITECTURE.md`](docs/URI2RUN_ARCHITECTURE.md) | uri2run layer |
| [`docs/PACKAGE_BOUNDARIES.md`](docs/PACKAGE_BOUNDARIES.md) | Package boundaries |
| [`docs/PACKAGE_BOUNDARIES.yaml`](docs/PACKAGE_BOUNDARIES.yaml) | Import rules (YAML) |
| [`docs/ARCHITECTURE_RUNTIME_AND_TESTING.md`](docs/ARCHITECTURE_RUNTIME_AND_TESTING.md) | Runtime + CI |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Version roadmap |
| [`docs/EXTERNAL_PACKAGES.md`](docs/EXTERNAL_PACKAGES.md) | External package audit |

### v0.5 — hypervisor, generation, deployment

| Document | Description |
|----------|-------------|
| [`docs/HYPERVISOR_WORKFLOW.md`](docs/HYPERVISOR_WORKFLOW.md) | Generation + run-agent |
| [`docs/CONFIG_URI_YAML.md`](docs/CONFIG_URI_YAML.md) | `*.uri.yaml` convention |
| [`docs/ARCHITECTURE_V0_5.md`](docs/ARCHITECTURE_V0_5.md) | Package split v0.5 |
| [`docs/NL2A_DOMAIN_PACKS.md`](docs/NL2A_DOMAIN_PACKS.md) | Domain Pack pipeline |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Local, Docker, SSH |
| [`docs/META_AGENT.md`](docs/META_AGENT.md) | meta-agent CLI/API |
| [`docs/EVOLUTION.md`](docs/EVOLUTION.md) | Evolution proposals |
| [`docs/AUTO_EVOLUTION_PIPELINE.md`](docs/AUTO_EVOLUTION_PIPELINE.md) | Auto-evolution |
| [`docs/STANDARDS.md`](docs/STANDARDS.md) | MCP, Protobuf, JSON Schema |

### Contracts and generator

| Document | Description |
|----------|-------------|
| [`docs/CONTRACTS.md`](docs/CONTRACTS.md) | Agent YAML format |
| [`docs/GENERATOR.md`](docs/GENERATOR.md) | Agent factory |
| [`docs/CONTRACT_REGISTRY.md`](docs/CONTRACT_REGISTRY.md) | Contract registry |
| [`docs/CONTRACT_REGISTRY_SCHEMA.md`](docs/CONTRACT_REGISTRY_SCHEMA.md) | Registry schema |
| [`docs/COMPATIBILITY_GOVERNANCE.md`](docs/COMPATIBILITY_GOVERNANCE.md) | Compatibility |
| [`docs/CAPABILITY_VERIFICATION.md`](docs/CAPABILITY_VERIFICATION.md) | Capability verification |

### Historical

| Document | Description |
|----------|-------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | General architecture |
| [`docs/ARCHITECTURE_META_FACTORY.md`](docs/ARCHITECTURE_META_FACTORY.md) | Meta-factory |
| [`docs/URI2LLM.md`](docs/URI2LLM.md) | → today `uri3.resolvers` |
| [`docs/HYPERVISOR_V0_2.md`](docs/HYPERVISOR_V0_2.md) · [`V0_3`](docs/HYPERVISOR_V0_3.md) · [`V0_4`](docs/HYPERVISOR_V0_4.md) | Earlier API |

### Examples (`examples/*/*`)

| Resource | Description |
|----------|-------------|
| [`examples/README.md`](examples/README.md) | Index of all repo examples |
| [`www/docs/examples.html`](www/docs/examples.html) | Full README + source files (WWW) |
| [`www/przyklady.html`](www/przyklady.html) | Integration lab — PASS + commands |
| [`examples/30_golden_path/`](examples/30_golden_path/) | 15 min tutorial |
| [`examples/23_nl_to_agent_tutorial/`](examples/23_nl_to_agent_tutorial/) | NL → HTTP agent |
| [`examples/31_office_day/`](examples/31_office_day/) | Office persona: web portal, ERP, bank, Android token |

Architecture and package split: [`docs/PACKAGE_BOUNDARIES.md`](docs/PACKAGE_BOUNDARIES.md)

Agent generation and run flow: [`docs/HYPERVISOR_WORKFLOW.md`](docs/HYPERVISOR_WORKFLOW.md)

URI configuration: [`docs/CONFIG_URI_YAML.md`](docs/CONFIG_URI_YAML.md) · [`config/llm.uri.yaml`](config/llm.uri.yaml)

### Packages (README + TODO + CHANGELOG)

| Package | README | TODO | CHANGELOG |
|---------|--------|------|-----------|
| uri2ops | [`packages/uri2ops/README.md`](packages/uri2ops/README.md) | [`TODO.md`](packages/uri2ops/TODO.md) | [`CHANGELOG.md`](packages/uri2ops/CHANGELOG.md) |
| uri2flow | [`packages/uri2flow/README.md`](packages/uri2flow/README.md) | [`TODO.md`](packages/uri2flow/TODO.md) | [`CHANGELOG.md`](packages/uri2flow/CHANGELOG.md) |
| touri | [`packages/touri/README.md`](packages/touri/README.md) | — | [`CHANGELOG.md`](packages/touri/CHANGELOG.md) |
| urish | [`packages/urish/README.md`](packages/urish/README.md) | — | — |
| urigen | [`packages/urigen/README.md`](packages/urigen/README.md) | — | — |
| hypervisor-dashboard-agent | [`packages/hypervisor-dashboard-agent/README.md`](packages/hypervisor-dashboard-agent/README.md) | — | — |
| All | [`packages/README.md`](packages/README.md) | [`TODO.md`](TODO.md) | [`CHANGELOG.md`](CHANGELOG.md) |

Older API versions: [`docs/HYPERVISOR_V0_2.md`](docs/HYPERVISOR_V0_2.md) … [`V0_4`](docs/HYPERVISOR_V0_4.md), [`docs/URI2LLM.md`](docs/URI2LLM.md). The URI resolver is today in `uri3.resolvers`.

## License

Licensed under Apache-2.0.

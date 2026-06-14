# Resource Agent System v0.6


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.5.16-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$9.27-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-7.9h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $9.2729 (15 commits)
- 👤 **Human dev:** ~$789 (7.9h @ $100/h, 30min dedup)

Generated on 2026-06-14 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

Monorepo: **uri3**, **nl2uri**, **uri2flow**, **uri2ops**, **hypervisor**, **agent factory** — contract-first thin agents z pipeline `prompt → URI plan → Domain Pack → generated agent`, plus warstwa operatora URI.

## Architektura

```txt
uri3       = URI, discovery, routing, skanowanie, graf, workflow executor, log://, schema
nl2uri     = natural language / query → URI plan (single, list, tree, task, graph)
uri2flow   = compact URI flow → expanded workflow graph (bez wykonania)
uri2ops    = operation registry + operator adapters + policy + serve (A2A/MCP)
uri2voice  = STT/TTS/voice command execution (mock MVP; touri manifests)
uri2pact   = markpact:// README import (capabilities + flows)
uri2verify = data quality gates, workflow replay, regression tests
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

Pełny pipeline weather-map (bez LLM):

```bash
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

| # | Katalog | Opis |
|---|---------|------|
| 01 | [`examples/01_quickstart_local`](examples/01_quickstart_local/) | Lokalny start bez Dockera |
| 02 | [`examples/02_uri3_scan_http`](examples/02_uri3_scan_http/) | Skan HTTP/A2A-like |
| 03 | [`examples/03_ssh_remote_agent`](examples/03_ssh_remote_agent/) | Docker + SSH testenv |
| 04 | [`examples/04_nl2a_weather_map`](examples/04_nl2a_weather_map/) | Prompt weather-map |
| 05 | [`examples/05_meta_repair`](examples/05_meta_repair/) | Naprawa uszkodzonego kontraktu |
| 06 | [`examples/06_orders_agent`](examples/06_orders_agent/) | Kontrakt agenta zamówień |
| 07 | [`examples/07_invoices_agent`](examples/07_invoices_agent/) | Prompt agenta faktur |
| 08 | [`examples/08_evolution`](examples/08_evolution/) | Evolution proposals |
| 09 | [`examples/09_run_agent_hypervisor`](examples/09_run_agent_hypervisor/) | run-agent / lifecycle |
| 10 | [`examples/10_browser_operator`](examples/10_browser_operator/) | uri2ops mock browser |
| 11 | [`examples/11_playwright_browser`](examples/11_playwright_browser/) | uri2ops Playwright |
| 12 | [`examples/12_android_operator`](examples/12_android_operator/) | uri2ops Android ADB |
| 13 | [`examples/13_pcwin_operator`](examples/13_pcwin_operator/) | uri2ops Windows UIA |
| 13 | [`examples/13_nl2uri_multi_uri_graph`](examples/13_nl2uri_multi_uri_graph/) | nl2uri multi-output |
| 14 | [`examples/14_uri2ops_serve`](examples/14_uri2ops_serve/) | uri2ops HTTP daemon |
| 14 | [`examples/14_workflow_executor_mock`](examples/14_workflow_executor_mock/) | uri3 workflow executor |
| 15 | [`examples/15_compact_uri_flow`](examples/15_compact_uri_flow/) | Skrócony przepływ URI |
| 15 | [`examples/15_playwright_browser`](examples/15_playwright_browser/) | uri3 Playwright workflow |
| 16 | [`examples/16_llm_graph_planner`](examples/16_llm_graph_planner/) | LLM graph planner |
| 17 | [`examples/17_flow_vs_graph`](examples/17_flow_vs_graph/) | Compact flow vs expanded graph |
| 18 | [`examples/18_llm_flow_planner`](examples/18_llm_flow_planner/) | LLM compact flow planner |
| 20 | [`examples/20_touri_capabilities`](examples/20_touri_capabilities/) | `touri` capability manifests |
| 21 | [`examples/21_touri_voice`](examples/21_touri_voice/) | STT/TTS/voice jako capability pack |
| 22 | [`examples/22_markpact_weather`](examples/22_markpact_weather/) | `markpact://` capability + flow README |
| 23 | [`examples/23_nl_to_agent_tutorial`](examples/23_nl_to_agent_tutorial/) | **Tutorial NL → URI → wykonanie → agent HTTP** |

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
make run-weather-agent
```

Zobacz [`examples/09_run_agent_hypervisor/`](examples/09_run_agent_hypervisor/README.md).

## Ważna zasada

Nie edytuj `agents/generated/` ręcznie. Zmieniaj `contracts/agents/*.yaml` lub pipeline domeny, potem regeneruj.

## Dokumentacja

Pełny indeks: [`docs/README.md`](docs/README.md)

Architektura i podział paczek: [`docs/PACKAGE_BOUNDARIES.md`](docs/PACKAGE_BOUNDARIES.md)

Przepływ generacji i uruchomienia agenta: [`docs/HYPERVISOR_WORKFLOW.md`](docs/HYPERVISOR_WORKFLOW.md)

Konfiguracja URI: [`docs/CONFIG_URI_YAML.md`](docs/CONFIG_URI_YAML.md) · [`config/llm.uri.yaml`](config/llm.uri.yaml)

### Aktualne (v0.5–v0.6)

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

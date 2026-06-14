# Resource Agent System v0.5.7


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.5.9-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$2.99-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-3.4h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $2.9911 (8 commits)
- 👤 **Human dev:** ~$337 (3.4h @ $100/h, 30min dedup)

Generated on 2026-06-14 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

Monorepo: **uri3**, **nl2uri**, **hypervisor**, **agent factory** — contract-first thin agents z pipeline `prompt → URI Tree → Domain Pack → generated agent`.

## Architektura

```txt
uri3       = URI, discovery, routing, skanowanie, graf, log://, schema introspection
nl2uri     = natural language / query → URI Tree
nl2a       = prompt → URI Tree → Domain Pack → agent contract → generated agent
hypervisor = registry, policy, deployment, lifecycle
generator  = deterministyczny kod agenta z YAML
domains/*  = logika domenowa (Domain Pack)
agents/generated/* = artefakty — nie edytować ręcznie
```

Szczegóły: [`docs/ARCHITECTURE_V0_5.md`](docs/ARCHITECTURE_V0_5.md) · [`packages/README.md`](packages/README.md)

## Instalacja

```bash
pip install -e '.[dev]'
# lub
uv sync
```

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

## uri3 — skanowanie, logi, schema

```bash
uri3 scan http://localhost:8101
uri3 logs 'log://hypervisor?level=ERROR&limit=50'
uri3 schema 'log://'
uri3 schema --list
uri3 resolve env://OPENROUTER_API_KEY
```

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

Przepływ generacji i uruchomienia agenta: [`docs/HYPERVISOR_WORKFLOW.md`](docs/HYPERVISOR_WORKFLOW.md)

Konfiguracja URI: [`docs/CONFIG_URI_YAML.md`](docs/CONFIG_URI_YAML.md) · [`config/llm.uri.yaml`](config/llm.uri.yaml)

### Aktualne (v0.5)

- [`docs/HYPERVISOR_WORKFLOW.md`](docs/HYPERVISOR_WORKFLOW.md) — generacja + uruchomienie przez hypervisor
- [`docs/CONFIG_URI_YAML.md`](docs/CONFIG_URI_YAML.md) — konwencja `*.uri.yaml`
- [`docs/URI3.md`](docs/URI3.md) — uri3 CLI i schematy URI
- [`docs/NL2URI.md`](docs/NL2URI.md) — prompt → URI Tree
- [`docs/NL2A_DOMAIN_PACKS.md`](docs/NL2A_DOMAIN_PACKS.md) — Domain Pack pipeline
- [`docs/META_AGENT.md`](docs/META_AGENT.md) — meta-agent CLI/API
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — wdrożenie lokalne i Docker
- [`docs/AUTO_EVOLUTION_PIPELINE.md`](docs/AUTO_EVOLUTION_PIPELINE.md) — kontrolowana autoewolucja
- [`docs/EVOLUTION.md`](docs/EVOLUTION.md) — evolution proposals
- [`docs/STANDARDS.md`](docs/STANDARDS.md) — MCP, Protobuf, JSON Schema
- [`docs/CONTRACTS.md`](docs/CONTRACTS.md) — format kontraktów YAML
- [`docs/GENERATOR.md`](docs/GENERATOR.md) — generator agentów
- [`CHANGELOG.md`](CHANGELOG.md) · [`TODO.md`](TODO.md)

### Historyczne

Starsze wersje (`docs/HYPERVISOR_V0_2.md` … `V0_4.md`, `docs/URI2LLM.md`) opisują wcześniejsze etapy API. Resolver URI jest dziś w paczce `uri3` (`uri3.resolvers`).

## License

Licensed under Apache-2.0.

# Examples

Przykłady są uporządkowane według schematu `examples/*/*` — każdy katalog ma własny `README.md`.

**Wymagania wspólne** (z katalogu repo):

```bash
pip install -e '.[dev]'
# opcjonalnie dla operatora:
pip install -e '.[browser]'   # Playwright
pip install -e '.[windows]'   # Windows UIA
```

## Przegląd — agent factory & hypervisor

| # | Katalog | Typ | Start |
|---|---------|-----|-------|
| 01 | [`01_quickstart_local`](./01_quickstart_local/) | pipeline | `make uri-tree` → `make test` |
| 02 | [`02_uri3_scan_http`](./02_uri3_scan_http/) | skan HTTP | wymaga agenta → [`03`](./03_ssh_remote_agent/) lub [`09`](./09_run_agent_hypervisor/) |
| 03 | [`03_ssh_remote_agent`](./03_ssh_remote_agent/) | Docker + SSH | `make docker-testenv-up` / `down` |
| 04 | [`04_nl2a_weather_map`](./04_nl2a_weather_map/) | generacja | `make nl2a-weather` |
| 05 | [`05_meta_repair`](./05_meta_repair/) | naprawa kontraktu | `make meta-repair` |
| 06 | [`06_orders_agent`](./06_orders_agent/) | wzorzec YAML | walidacja kontraktu |
| 07 | [`07_invoices_agent`](./07_invoices_agent/) | prompt NL | `meta_agent plan` / `pipeline` |
| 08 | [`08_evolution`](./08_evolution/) | propozycje | `make evolution-check` |
| 09 | [`09_run_agent_hypervisor`](./09_run_agent_hypervisor/) | lifecycle | `run-agent` / `stop-agent` / `logs` |

## Przegląd — uri2ops operator

| # | Katalog | Typ | Start |
|---|---------|-----|-------|
| 10 | [`10_browser_operator`](./10_browser_operator/) | mock browser | `uri2ops run … --adapter mock --approve` |
| 11 | [`11_playwright_browser`](./11_playwright_browser/) | Playwright | `--adapter playwright` |
| 12 | [`12_android_operator`](./12_android_operator/) | Android ADB | `--adapter adb` (device/emulator) |
| 13 | [`13_pcwin_operator`](./13_pcwin_operator/) | Windows UIA | `--adapter uia` |
| 14 | [`14_uri2ops_serve`](./14_uri2ops_serve/) | HTTP daemon | `uri2ops serve` + `run.sh` |

## Przegląd — nl2uri + uri3 workflow

| # | Katalog | Typ | Start |
|---|---------|-----|-------|
| 13 | [`13_nl2uri_multi_uri_graph`](./13_nl2uri_multi_uri_graph/) | nl2uri multi-output | `nl2uri plan/task/graph`, `uri3 validate-workflow` |
| 14 | [`14_workflow_executor_mock`](./14_workflow_executor_mock/) | uri3 executor | `uri3 run-workflow --dry-run/--approve` |
| 15 | [`15_compact_uri_flow`](./15_compact_uri_flow/) | uri2flow compact | `uri2flow expand` → `uri3 run-workflow` |
| 15 | [`15_playwright_browser`](./15_playwright_browser/) | uri3 Playwright | `--browser playwright` |
| 17 | [`17_flow_vs_graph`](./17_flow_vs_graph/) | flow vs graph | `nl2uri flow`, `uri3 expand-flow/run-flow` |

> **Uwaga:** numery 13–15 są współdzielone między ścieżkami (operator vs workflow) — używaj pełnej nazwy katalogu.

## Szybki start (pełny stack testenv)

```bash
# 1. Hasło SSH (raz, przez uri3)
uri3 call 'env://HYPERVISOR_SSH_PASSWORD?action=set&value=deploy&persist=1'

# 2. Docker + SSH testenv
make docker-testenv-up

# 3. Sprawdzenie
uri3 scan --all
hypervisor verify-agent weather-map-agent.ssh-dev

# 4. Logi kontenera
uri3 call 'docker://stack/ssh-testenv?action=logs&tail=50'

# 5. Stop
make docker-testenv-down
```

## Zasada architektury

```txt
uri3     = skanowanie, routing, discovery, workflow executor, logi, docker:// call
nl2uri   = natural language -> URI plan (single, list, tree, task, graph)
uri2flow = compact URI flow -> expanded workflow graph (no execution)
uri2ops  = operation registry + adapters + policy + serve
hypervisor = registry, policy, lifecycle agentów (run/stop/deploy/verify)
nl2a     = pipeline prompt -> URI Tree -> Domain Pack -> agent
```

## Najczęstsze komendy

```bash
uri3 list
uri3 scan http
make uri-tree
make nl2a-weather
nl2uri plan -p "otwórz Chrome i sprawdź health"
nl2uri flow -p "wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome"
uri3 expand-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
uri3 run-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --dry-run
uri3 run-workflow examples/14_workflow_executor_mock/task_graph.yaml --approve
uri2ops run examples/10_browser_operator/task.health.yaml --adapter mock --approve
hypervisor run-agent weather-map-agent.local --dry-run
python -m pytest -q
```

# Examples

Przykłady są uporządkowane według schematu `examples/*/*` — każdy katalog ma własny `README.md`.

**Dokumentacja WWW (pełna treść):** [`www/docs/examples.html`](../www/docs/examples.html) — wszystkie README + pliki YAML/TXT/SH · [`www/przyklady.html`](../www/przyklady.html) — lab PASS + komendy.

**Indeks repo:** [`README.md`](./README.md) · [`docs/README.md`](../docs/README.md) · [`TODO.md`](../TODO.md) · [`CHANGELOG.md`](../CHANGELOG.md)

Regeneracja strony docs: `make www-docs` (`scripts/www/build_examples_docs.py`).

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
| 01 | [`01_quickstart_local`](./01_quickstart_local/) | pipeline | `bash examples/01_quickstart_local/run.sh` |
| 02 | [`02_uri3_scan_http`](./02_uri3_scan_http/) | skan HTTP | wymaga agenta → [`03`](./03_ssh_remote_agent/) lub [`09`](./09_run_agent_hypervisor/) |
| 03 | [`03_ssh_remote_agent`](./03_ssh_remote_agent/) | Docker + SSH | `make docker-testenv-up` / `down` |
| 04 | [`04_nl2a_weather_map`](./04_nl2a_weather_map/) | generacja | `bash examples/04_nl2a_weather_map/run.sh` |
| 05 | [`05_meta_repair`](./05_meta_repair/) | naprawa kontraktu | `make meta-repair` |
| 06 | [`06_orders_agent`](./06_orders_agent/) | wzorzec YAML | walidacja kontraktu |
| 07 | [`07_invoices_agent`](./07_invoices_agent/) | prompt NL | `meta_agent plan` / `pipeline` |
| 08 | [`08_evolution`](./08_evolution/) | propozycje | `make evolution-check` |
| 09 | [`09_run_agent_hypervisor`](./09_run_agent_hypervisor/) | lifecycle | `bash examples/09_run_agent_hypervisor/run.sh` |

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
| 16 | [`16_llm_graph_planner`](./16_llm_graph_planner/) | LLM graph plan | `bash examples/16_llm_graph_planner/run.sh` |
| 17 | [`17_flow_vs_graph`](./17_flow_vs_graph/) | flow vs graph | `nl2uri flow`, `uri3 expand-flow/run-flow` |
| 18 | [`18_llm_flow_planner`](./18_llm_flow_planner/) | LLM compact flow | `nl2uri flow --llm --validate`, `uri3 run-flow` |
| 20 | [`20_touri_capabilities`](./20_touri_capabilities/) | touri manifests | `touri validate/list/call` |
| 21 | [`21_touri_voice`](./21_touri_voice/) | STT/TTS/voice → nl2uri | `touri call stt://...`, `voice://command/from-text` |
| 22 | [`22_markpact_weather`](./22_markpact_weather/) | markpact README → touri + uri2flow | `touri list/call markpact://...`, `uri2flow expand markpact://...#flow` |
| 23 | [`23_nl_to_agent_tutorial`](./23_nl_to_agent_tutorial/) | **tutorial NL → agent HTTP** | `bash examples/23_nl_to_agent_tutorial/run.sh` |
| 30 | [`30_golden_path`](./30_golden_path/) | **15 min onboarding (urish)** | `bash examples/30_golden_path/run.sh` |
| 31 | [`31_office_day`](./31_office_day/) | **Biuro: portal → faktury → bank → Android** | `bash examples/31_office_day/run.sh` |
| 32 | [`32_ecommerce_integrations`](./32_ecommerce_integrations/) | **WooCommerce → BaseLinker → ERP** | `bash examples/32_ecommerce_integrations/run.sh` |
| 33 | [`33_office_workflows`](./33_office_workflows/) | **Karty biurowe landingu → workflow URI** | `bash examples/33_office_workflows/run.sh` |
| 34 | [`34_cron_uri`](./34_cron_uri/) | **`cron://` harmonogramy via touri → shell** | `bash examples/34_cron_uri/run.sh` |
| 35 | [`35_website_screenshot_schedule`](./35_website_screenshot_schedule/) | **Harmonogram screenshotów strony (chat → workflow)** | `bash examples/35_website_screenshot_schedule/run.sh` |
| 36 | [`36_physical_ops`](./36_physical_ops/) | **Robot/device — operacje fizyczne (mock)** | `bash examples/36_physical_ops/run.sh` |
| 37 | [`37_agent_screenshot_analysis`](./37_agent_screenshot_analysis/) | **Dwóch agentów: screenshot → plik analizy** | `bash examples/37_agent_screenshot_analysis/run.sh` |
| 38 | [`38_autonomous_agents`](./38_autonomous_agents/) | **Multi-agent: remote deploy + GNOME programmer + analiza screenshotów** | `bash examples/38_autonomous_agents/run.sh` |
| — | [`22_dashboard_agent`](./22_dashboard_agent/) | capability/flow dashboard-agent | [`README`](./22_dashboard_agent/README.md) |
| — | [`16_www_landing_monitor`](./16_www_landing_monitor/) | monitor landing WWW | [`README`](./16_www_landing_monitor/README.md) |

> **WWW:** pełna treść wszystkich katalogów → [`www/docs/examples.html`](../www/docs/examples.html)

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
nl2uri   -> uri2flow -> uri3 (orchestration, explain, doctor)
touri    -> uri2run (transport) -> uri2ops / python / shell / http / ...
uri2verify = data quality, envelope checks (separate from uri2run execution)
hypervisor = lifecycle, deployment registry
uri3     = skanowanie, routing, discovery, workflow executor, logi, docker:// call
uri2flow = compact URI flow -> expanded workflow graph (no execution)
nl2a     = pipeline prompt -> URI Tree -> Domain Pack -> agent
```

## Testy examples

Wszystkie przykłady są objęte integracją CI:

```bash
bash scripts/test-all-examples.sh   # sekwencyjny smoke (PASS/FAIL/SKIP)
python3 scripts/examples/comprehensive_test.py   # pełna macierz + raport możliwości hosta
make examples-comprehensive
make examples-comprehensive-mock
pytest tests/examples -q
make examples-test
make ci-gate
```

Przewodnik: [`docs/EXAMPLES_TESTING.md`](../docs/EXAMPLES_TESTING.md) · raporty: `output/examples/comprehensive_report.md`

Katalog testów: `tests/examples/catalog.py` — każdy `examples/*/run.sh` musi być w katalogu.
Markery: `@pytest.mark.docker` (ex03), `@pytest.mark.slow` (ex23), Playwright (ex11, wymaga `[browser]`).

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
bash examples/23_nl_to_agent_tutorial/run.sh
make ci-gate
```

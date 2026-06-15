# Examples

Examples follow the `examples/*/*` layout — each directory has its own `README.md`.

Polish index: [`README.pl.md`](./README.pl.md)

**WWW documentation (full content):** [`www/docs/examples.html`](../www/docs/examples.html) — all READMEs + YAML/TXT/SH files · [`www/przyklady.html`](../www/przyklady.html) — PASS lab + commands.

**Repo index:** [`README.md`](../README.md) · [`docs/README.md`](../docs/README.md) · [`TODO.md`](../TODO.md) · [`CHANGELOG.md`](../CHANGELOG.md)

Regenerate docs page: `make www-docs` (`scripts/www/build_examples_docs.py`).

### `ABOUT.md` — landing `#integracje` cards

Optional per example: `examples/<id>/ABOUT.md` (YAML frontmatter + markdown/HTML body).
Built into [`www/index.html`](../www/index.html) `#integracje` by `scripts/www/build_landing_integrations.py`.
See [`www/README.md`](../www/README.md) for the schema. Examples with cards today:
`23_nl_to_agent_tutorial`, `31_office_day`, `32_ecommerce_integrations`, `33_office_workflows`, `34_cron_uri`, `35_website_screenshot_schedule`.

**Common requirements** (from repo root):

```bash
pip install -e '.[dev]'
# optional for operator:
pip install -e '.[browser]'   # Playwright
pip install -e '.[windows]'   # Windows UIA
```

## Overview — agent factory & hypervisor

| # | Directory | Type | Start |
|---|-----------|------|-------|
| 01 | [`01_quickstart_local`](./01_quickstart_local/) | pipeline | `bash examples/01_quickstart_local/run.sh` |
| 02 | [`02_uri3_scan_http`](./02_uri3_scan_http/) | HTTP scan | requires agent → [`03`](./03_ssh_remote_agent/) or [`09`](./09_run_agent_hypervisor/) |
| 03 | [`03_ssh_remote_agent`](./03_ssh_remote_agent/) | Docker + SSH | `make docker-testenv-up` / `down` |
| 04 | [`04_nl2a_weather_map`](./04_nl2a_weather_map/) | generation | `bash examples/04_nl2a_weather_map/run.sh` |
| 05 | [`05_meta_repair`](./05_meta_repair/) | contract repair | `make meta-repair` |
| 06 | [`06_orders_agent`](./06_orders_agent/) | YAML pattern | contract validation |
| 07 | [`07_invoices_agent`](./07_invoices_agent/) | NL prompt | `meta_agent plan` / `pipeline` |
| 08 | [`08_evolution`](./08_evolution/) | proposals | `make evolution-check` |
| 09 | [`09_run_agent_hypervisor`](./09_run_agent_hypervisor/) | lifecycle | `bash examples/09_run_agent_hypervisor/run.sh` |

## Overview — uri2ops operator

| # | Directory | Type | Start |
|---|-----------|------|-------|
| 10 | [`10_browser_operator`](./10_browser_operator/) | mock browser | `uri2ops run … --adapter mock --approve` |
| 11 | [`11_playwright_browser`](./11_playwright_browser/) | Playwright | `--adapter playwright` |
| 12 | [`12_android_operator`](./12_android_operator/) | Android ADB | `--adapter adb` (device/emulator) |
| 13 | [`13_pcwin_operator`](./13_pcwin_operator/) | Windows UIA | `--adapter uia` |
| 14 | [`14_uri2ops_serve`](./14_uri2ops_serve/) | HTTP daemon | `uri2ops serve` + `run.sh` |

## Overview — nl2uri + uri3 workflow

| # | Directory | Type | Start |
|---|-----------|------|-------|
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
| 23 | [`23_nl_to_agent_tutorial`](./23_nl_to_agent_tutorial/) | **tutorial NL → HTTP agent** | `bash examples/23_nl_to_agent_tutorial/run.sh` |
| 30 | [`30_golden_path`](./30_golden_path/) | **15 min onboarding (urish)** | `bash examples/30_golden_path/run.sh` |
| 31 | [`31_office_day`](./31_office_day/) | **Office: portal → invoices → bank → Android** | `bash examples/31_office_day/run.sh` |
| 32 | [`32_ecommerce_integrations`](./32_ecommerce_integrations/) | **WooCommerce → BaseLinker → ERP** | `bash examples/32_ecommerce_integrations/run.sh` |
| 33 | [`33_office_workflows`](./33_office_workflows/) | **Landing office cards → workflow URIs** | `bash examples/33_office_workflows/run.sh` |
| 34 | [`34_cron_uri`](./34_cron_uri/) | **`cron://` schedules via touri → shell** | `bash examples/34_cron_uri/run.sh` |
| 35 | [`35_website_screenshot_schedule`](./35_website_screenshot_schedule/) | **Website screenshot schedule (chat → workflow)** | `bash examples/35_website_screenshot_schedule/run.sh` |
| 36 | [`36_physical_ops`](./36_physical_ops/) | **Robot/device physical ops (mock)** | `bash examples/36_physical_ops/run.sh` |
| 37 | [`37_agent_screenshot_analysis`](./37_agent_screenshot_analysis/) | **Two agents: screenshot capture → analysis file** | `bash examples/37_agent_screenshot_analysis/run.sh` |
| 38 | [`38_autonomous_agents`](./38_autonomous_agents/) | **Multi-agent: remote deploy + GNOME programmer + screenshot analysis** | `bash examples/38_autonomous_agents/run.sh` |
| — | [`22_dashboard_agent`](./22_dashboard_agent/) | capability/flow dashboard-agent | [`README`](./22_dashboard_agent/README.md) |
| — | [`16_www_landing_monitor`](./16_www_landing_monitor/) | WWW landing monitor | [`README`](./16_www_landing_monitor/README.md) |

> **WWW:** full content of all directories → [`www/docs/examples.html`](../www/docs/examples.html)

> **Note:** numbers 13–15 are shared between paths (operator vs workflow) — use the full directory name.

## Quick start (full stack testenv)

```bash
# 1. SSH password (once, via uri3)
uri3 call 'env://HYPERVISOR_SSH_PASSWORD?action=set&value=deploy&persist=1'

# 2. Docker + SSH testenv
make docker-testenv-up

# 3. Verify
uri3 scan --all
hypervisor verify-agent weather-map-agent.ssh-dev

# 4. Container logs
uri3 call 'docker://stack/ssh-testenv?action=logs&tail=50'

# 5. Stop
make docker-testenv-down
```

## Architecture principle

```txt
nl2uri   -> uri2flow -> uri3 (orchestration, explain, doctor)
touri    -> uri2run (transport) -> uri2ops / python / shell / http / ...
uri2verify = data quality, envelope checks (separate from uri2run execution)
hypervisor = lifecycle, deployment registry
uri3     = scan, routing, discovery, workflow executor, logs, docker:// call
uri2flow = compact URI flow -> expanded workflow graph (no execution)
nl2a     = pipeline prompt -> URI Tree -> Domain Pack -> agent
```

## Example tests

All examples are covered by CI integration:

```bash
bash scripts/test-all-examples.sh   # sequential shell smoke (PASS/FAIL/SKIP)
python3 scripts/examples/comprehensive_test.py   # full matrix + capability report
make examples-comprehensive         # same as above
make examples-comprehensive-mock    # mock/dry-run only
pytest tests/examples -q            # pytest: run.sh + inline + smoke + real matrix
make examples-test                  # Makefile shortcut
make ci-gate                        # architecture-gate + pytest + examples-test
```

Full guide: [`docs/EXAMPLES_TESTING.md`](../docs/EXAMPLES_TESTING.md) · reports in `output/examples/comprehensive_report.md`

Test catalog: `tests/examples/catalog.py` — every `examples/*/run.sh` must be listed.
Office chains gallery: `examples/office_chains.yaml` → `www/generated/examples-manifest.js`.
Markers: `@pytest.mark.docker` (ex03), `@pytest.mark.slow` (ex23), Playwright (ex11, requires `[browser]`).

## Common commands

```bash
uri3 list
uri3 scan http
make uri-tree
make nl2a-weather
nl2uri plan -p "open Chrome and check health"
nl2uri flow -p "generate weather agent, run locally and check health in Chrome"
uri3 expand-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
uri3 run-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --dry-run
uri3 run-workflow examples/14_workflow_executor_mock/task_graph.yaml --approve
uri2ops run examples/10_browser_operator/task.health.yaml --adapter mock --approve
hypervisor run-agent weather-map-agent.local --dry-run
bash examples/23_nl_to_agent_tutorial/run.sh
make ci-gate
```

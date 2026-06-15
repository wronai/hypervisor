# Examples — comprehensive testing

How to run **all commands from `examples/`**, verify they execute correctly, and discover which **real-mode** automations work on your machine (browser, scan, monitors, agents).

## Quick commands

```bash
# Mock/dry-run/validate — CI-safe (default)
make examples-test
make examples-comprehensive-mock

# Full matrix: mock + real attempts + capability report
make examples-comprehensive

# Real-mode variants only (skip when requirements missing)
make examples-real-report

# Sequential shell smoke (human-readable log)
bash scripts/test-all-examples.sh

# Real browser proof for example 15pw, including optional PNG screenshot check
make examples-playwright-proof
```

Reports are written to:

- `output/examples/comprehensive_report.json`
- `output/examples/comprehensive_report.md`
- `output/examples/capabilities.json`

## Test tiers

| Tier | Meaning | CI default |
|------|---------|------------|
| **validate** | YAML/manifest checks only | yes |
| **dry-run** | Plan without side effects | yes |
| **mock** | Execute with mock adapters (`--browser mock`, `--adapter mock`) | yes |
| **real** | Live browser, agent, ADB, Docker SSH, LLM | opt-in |

**Chat plans, does not auto-run workflows.** Example `run.sh` scripts use mock/dry-run unless documented otherwise.

## Machine capability probes

Before real-mode tests, the runner probes:

| ID | What it checks |
|----|----------------|
| `cli_uri` | `uri` / `urish` available |
| `cli_uri3` | `uri3` available |
| `cli_hypervisor` | `hypervisor` available |
| `cli_uri2flow` | `uri2flow` available |
| `cli_nl2uri` | `nl2uri` available |
| `docker` | Docker daemon running |
| `playwright` | Playwright import + real Chromium launch |
| `agent_http_8101` | `curl localhost:8101/health` |
| `agent_http_any` | Any agent on ports 8101–8130 |
| `www_8788` | Taskinity WWW (`make start`) |
| `openrouter` | `OPENROUTER_API_KEY` set |
| `adb` | `adb devices` with connected device |
| `uia` | Windows + pywinauto |
| `curl` | curl in PATH |

Skipped real commands list missing requirements in the report.

## What works locally vs remotely

### Usually green on any dev machine (mock/dry-run)

All `examples/*/run.sh` (22 examples), plus inline:

- meta repair, contract validate, evolution check
- touri validate/list (ex20–22)
- uri2flow expand (ex15)
- office NL ask + workflow dry-run (ex33)
- ecommerce explain + mock run (ex32)

### Needs local stack

| Example | Requirement | Command |
|---------|-------------|---------|
| 02 scan HTTP | Agent on :8101 | `uri3 scan http://localhost:8101` |
| 03 SSH scan | Docker testenv | `make docker-testenv-up && uri3 scan ssh` |
| 16www monitor | WWW :8788 | `uri3 run-workflow … --dry-run` |
| 30 golden path | Optional agent/www | `bash examples/30_golden_path/run.sh` |
| Chat API | WWW :8788 | `curl POST /api/ask` |

### Real automations (website scan + notify)

| Automation | Works without remote | Notes |
|------------|---------------------|-------|
| `scripts/www/monitor_landing.py` | **Yes** (HTTP fetch) | Price/uptime diff, webhook via `MONITOR_WEBHOOK_URL` |
| `scripts/www/monitor_url.py` | **Yes** | PAGE_DOWN detection + stderr `[NOTIFY]` |
| `scripts/www/run_monitors.sh` | **Yes** | Host cron bundle |
| `make www-monitor-test` | **Yes** (WWW up) | Full notify + webhook test |
| ex16 workflow **playwright** | **Yes** (local :8788) | Real DOM assertions (prices in PLN) |
| ex16 workflow **mock browser** | **No** | Mock returns stub text — use dry-run or playwright |
| ex11 / ex10 playwright | **Yes** | In-process or uri2ops playwright |
| ex15pw real browser | **Yes** | Uses `hypervisor inspect-agent` to open the effective weather health URL, not a hardcoded port |
| ex12 Android / ex13 PCWin real | **No** | Need ADB device or Windows UIA |
| ex16/18 LLM planners | **Optional** | Needs `OPENROUTER_API_KEY` |
| Remote ERP/Woo/Allegro (ex32) | **No** | Mock in `run.sh`; live APIs need credentials |

### Website screenshot schedules (chat NL)

NL prompts like “screenshot softreck.com every 5 minutes” plan a **workflow URI** via `uri ask`. Execution requires:

1. `uri run workflow://graph/website-screenshot-schedule/dry-run` (always local)
2. `uri run workflow://graph/website-screenshot-schedule --approve --adapter playwright` for real captures (needs Playwright)
3. Cron/n8n on host for recurring runs — not auto-started by chat

Example bundle: [`examples/35_website_screenshot_schedule/`](../examples/35_website_screenshot_schedule/)

## Pytest markers

```bash
pytest tests/examples -q                           # all examples (default CI)
pytest tests/examples -m "not real" -q             # skip real-mode matrix
pytest tests/examples/test_comprehensive.py -q     # command catalog
pytest tests/examples/test_comprehensive.py -m real -q  # real only
python3 scripts/examples/comprehensive_test.py --mock-only
python3 scripts/examples/comprehensive_test.py --real-only
```

Markers: `examples`, `docker`, `slow`, `real`, `www`, `monitor`.

## Source files

| File | Role |
|------|------|
| `tests/examples/catalog.py` | Example IDs, run.sh paths, markers |
| `tests/examples/command_catalog.py` | Every command (mock + real variants) |
| `tests/examples/capabilities.py` | Host probes |
| `scripts/examples/comprehensive_test.py` | Standalone runner + reports |
| `scripts/examples/effective_weather_playwright.py` | Real Playwright proof using the effective agent health URL |
| `scripts/examples/run_uri3_workflow.py` | Run uri3 workflow graphs with the selected Python interpreter |
| `scripts/test-all-examples.sh` | Sequential shell smoke |

## DOQL registry (env2llm)

Podgląd **aktualnego stanu hosta** w rejestrze DOQL (semcod `env2llm`):

```bash
make doql-registry
# → .nlp2dsl/registry/environment.doql.less
```

Bloki: `host`, `host_cron[]` (w tym `# taskinity-www-monitor`), `host_endpoint[]`, `schedules[]`, `host_examples_test` (z `output/examples/comprehensive_report.json`).

```bash
ENV2LLM_HOST_PROBE=1 env2llm . --probe-host
grep -E '^host|^schedules' .nlp2dsl/registry/environment.doql.less
```

## Fixing failures

1. Read `output/examples/comprehensive_report.md` — check **Machine capabilities** table.
2. For `agent_http_8101`: `hypervisor run-agent weather-map-agent.local --detach --wait-healthy`
3. For rebound ports: use `python3 scripts/examples/effective_weather_playwright.py`, which reads `effective_health_uri` from `hypervisor inspect-agent`.
4. For `www_8788`: `make start`
5. For `playwright`: `pip install -e '.[browser]' && playwright install chromium`
6. For ex16 content assertions: use **playwright** execute, not mock browser.

Polish index: [`README.pl.md`](./README.pl.md) · Chat/office flows: [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md)

# TellMesh v0.6

WronAI resource agent monorepo — uri3, nl2uri, uri2flow, uri2ops, touri, hypervisor, agent factory

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `tellmesh`
- **version**: `0.5.28`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(3), app.doql.less, goal.yaml, .env.example, Dockerfile, docker-compose.yml, project/(3 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: tellmesh;
  version: 0.5.28;
}

dependencies {
  runtime: "fastapi>=0.115, uvicorn>=0.27, httpx>=0.27, jinja2>=3.1, jsonschema>=4.23, markdown>=3.5, pydantic>=2.0, python-dotenv>=1.0.0, pyyaml>=6.0, typer>=0.26.7, uri3, nl2uri, uri2flow, uri2ops, touri, uri2voice, uri2pact, uri2run, uri2verify, urigen, urish, resource-agent-hypervisor, resource-agent-factory, hypervisor-dashboard-agent";
  dev: "pytest>=7.0, pytest-cov>=4.0, pytest-asyncio>=0.21.0, ruff>=0.1.0, mypy>=1.0, build>=1.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60, rich>=13.0.0, uvicorn>=0.27";
  browser: playwright>=1.40;
  windows: pywinauto>=0.6;
  server: uvicorn>=0.27;
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="hypervisor"] {
  entry: hypervisor.cli:main;
}
interface[type="cli"] page[name="uri3"] {
  entry: uri3.cli:main;
}
interface[type="cli"] page[name="uri2ops"] {
  entry: uri2ops.cli:main;
}
interface[type="cli"] page[name="uri2flow"] {
  entry: uri2flow.cli:main;
}
interface[type="cli"] page[name="uri2run"] {
  entry: uri2run.cli:main;
}
interface[type="cli"] page[name="uri"] {
  entry: urish.cli:main;
}
interface[type="cli"] page[name="urish"] {
  entry: urish.cli:main;
}
interface[type="cli"] page[name="taskinity"] {
  entry: urish.cli:main;
}
interface[type="cli"] page[name="touri"] {
  entry: touri.cli:main;
}
interface[type="cli"] page[name="uri2verify"] {
  entry: uri2verify.cli:main;
}
interface[type="cli"] page[name="urigen"] {
  entry: urigen.cli:main;
}
interface[type="cli"] page[name="nl2uri"] {
  entry: nl2uri.cli:main;
}
interface[type="cli"] page[name="nl2a"] {
  entry: nl2a.cli:main;
}

workflow[name="validate"] {
  trigger: manual;
  step-1: run cmd=python -m generator.validate contracts;
}

workflow[name="generate"] {
  trigger: manual;
  step-1: run cmd=python -m generator.agent_generator contracts/agents/*.yaml;
}

workflow[name="verify"] {
  trigger: manual;
  step-1: run cmd=python -m generator.verify agents/generated;
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=pytest -q;
}

workflow[name="architecture-test"] {
  trigger: manual;
  step-1: run cmd=pytest tests/architecture -q;
}

workflow[name="architecture-responsibility-audit"] {
  trigger: manual;
  step-1: run cmd=python3 scripts/architecture_responsibility_audit.py --top 30;
}

workflow[name="doctor"] {
  trigger: manual;
  step-1: run cmd=uri3 doctor --json;
}

workflow[name="architecture-gate"] {
  trigger: manual;
  step-1: run cmd=bash scripts/ci/architecture_gate.sh;
}

workflow[name="ci-gate"] {
  trigger: manual;
  step-1: depend target=architecture-gate;
  step-2: depend target=www-docs-check;
  step-3: depend target=test;
  step-4: depend target=examples-test;
}

workflow[name="examples-test"] {
  trigger: manual;
  step-1: run cmd=pytest tests/examples -q;
}

workflow[name="examples-comprehensive"] {
  trigger: manual;
  step-1: run cmd=python3 scripts/examples/comprehensive_test.py;
}

workflow[name="examples-real-report"] {
  trigger: manual;
  step-1: run cmd=python3 scripts/examples/comprehensive_test.py --real-only;
}

workflow[name="doql-registry"] {
  trigger: manual;
  step-1: run cmd=bash scripts/examples/doql_host_preview.sh;
}

workflow[name="examples-comprehensive-mock"] {
  trigger: manual;
  step-1: run cmd=python3 scripts/examples/comprehensive_test.py --mock-only;
}

workflow[name="examples-playwright-proof"] {
  trigger: manual;
  step-1: run cmd=python3 scripts/examples/effective_weather_playwright.py;
  step-2: run cmd=python3 scripts/examples/effective_weather_playwright.py --legacy-screenshot;
}

workflow[name="uri2flow-test"] {
  trigger: manual;
  step-1: run cmd=pytest tests/uri2flow -q;
}

workflow[name="uri2flow-validate"] {
  trigger: manual;
  step-1: run cmd=uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml;
}

workflow[name="uri2flow-expand"] {
  trigger: manual;
  step-1: run cmd=mkdir -p output;
  step-2: run cmd=uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml;
}

workflow[name="uri3-flow-dry-run"] {
  trigger: manual;
  step-1: run cmd=uri3 run-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --dry-run;
}

workflow[name="nl2uri-flow-validate"] {
  trigger: manual;
  step-1: run cmd=nl2uri flow -p "wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome" --validate;
}

workflow[name="example-18"] {
  trigger: manual;
  step-1: run cmd=bash examples/18_llm_flow_planner/run.sh;
}

workflow[name="touri-test"] {
  trigger: manual;
  step-1: run cmd=pytest tests/touri -q;
}

workflow[name="touri-demo"] {
  trigger: manual;
  step-1: run cmd=touri validate examples/20_touri_capabilities/weather_forecast.uri.capability.yaml;
  step-2: run cmd=touri list examples/20_touri_capabilities;
  step-3: run cmd=touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities;
  step-4: run cmd=touri call echo://Adam --registry examples/20_touri_capabilities;
}

workflow[name="voice-test"] {
  trigger: manual;
  step-1: run cmd=pytest tests/touri/test_voice_capabilities.py -q;
}

workflow[name="voice-demo"] {
  trigger: manual;
  step-1: run cmd=touri validate examples/21_touri_voice/stt_mock.uri.capability.yaml;
  step-2: run cmd=touri list examples/21_touri_voice;
  step-3: run cmd=touri call stt://mock/transcribe --registry examples/21_touri_voice --payload '{"text":"otwórz Chrome i sprawdź health"}';
  step-4: run cmd=touri call voice://command/from-text --registry examples/21_touri_voice --payload '{"text":"wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome"}';
  step-5: run cmd=touri call tts://mock/speak --registry examples/21_touri_voice --payload '{"text":"Agent działa poprawnie"}';
}

workflow[name="uri-tree"] {
  trigger: manual;
  step-1: run cmd=python -m nl2uri.cli tree --no-llm -p "$(WEATHER_PROMPT)" --out domains/weather_map/uri_tree.yaml;
}

workflow[name="graph"] {
  trigger: manual;
  step-1: run cmd=uri3 graph domains/weather_map/uri_tree.yaml;
}

workflow[name="nl2a-weather"] {
  trigger: manual;
  step-1: run cmd=python -m nl2a.cli --no-llm -p "$(WEATHER_PROMPT)";
}

workflow[name="run-user-agent"] {
  trigger: manual;
  step-1: run cmd=uvicorn agents.generated.user_agent.main:app --reload --port 8101;
}

workflow[name="run-meta-agent"] {
  trigger: manual;
  step-1: run cmd=uvicorn meta_agent.api:app --reload --port 8200;
}

workflow[name="meta-plan"] {
  trigger: manual;
  step-1: run cmd=python -m meta_agent.cli plan "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia";
}

workflow[name="meta-pipeline"] {
  trigger: manual;
  step-1: run cmd=python -m meta_agent.cli pipeline "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia";
}

workflow[name="meta-repair"] {
  trigger: manual;
  step-1: run cmd=python -m meta_agent.cli repair examples/05_meta_repair/broken_agent.yaml --write;
}

workflow[name="docker-ssh-up"] {
  trigger: manual;
  step-1: run cmd=python -m hypervisor.cli call 'docker://stack/ssh-testenv?action=up&build=1';
}

workflow[name="docker-ssh-down"] {
  trigger: manual;
  step-1: run cmd=python -m hypervisor.cli call 'docker://stack/ssh-testenv?action=down&remove_volumes=1';
}

workflow[name="docker-testenv-up"] {
  trigger: manual;
  step-1: depend target=docker-ssh-up;
}

workflow[name="docker-testenv-down"] {
  trigger: manual;
  step-1: depend target=docker-ssh-down;
}

workflow[name="scan-http"] {
  trigger: manual;
  step-1: run cmd=python -m uri3.cli scan http;
}

workflow[name="scan-ssh"] {
  trigger: manual;
  step-1: run cmd=HYPERVISOR_SSH_PASSWORD=$${HYPERVISOR_SSH_PASSWORD:-deploy} python -m uri3.cli scan ssh;
}

workflow[name="scan-all"] {
  trigger: manual;
  step-1: run cmd=HYPERVISOR_SSH_PASSWORD=$${HYPERVISOR_SSH_PASSWORD:-deploy} python -m uri3.cli scan --all;
}

workflow[name="evolution-check"] {
  trigger: manual;
  step-1: run cmd=python -m hypervisor.evolution.cli examples/08_evolution/proposals/add_orders_agent.yaml examples/08_evolution/proposals/add_invoices_agent.yaml;
}

workflow[name="examples"] {
  trigger: manual;
  step-1: run cmd=echo "See examples/README.md for the full catalog (01–09).";
}

workflow[name="run-weather-agent"] {
  trigger: manual;
  step-1: run cmd=python -m hypervisor.cli run-agent weather-map-agent.local;
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=rm -rf agents/generated/* output/* .pytest_cache;
  step-2: run cmd=find . -type d -name __pycache__ -prune -exec rm -rf {} +;
}

workflow[name="ensure-dev"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -c "import uvicorn" 2>/dev/null || { \;
  step-2: run cmd=echo "Installing dev deps into project Python…"; \;
  step-3: run cmd=$(PYTHON) -m pip install -q -e ".[dev]"; \;
  step-4: run cmd=};
  step-5: run cmd=$(PYTHON) -c "import sys, uvicorn; import typer._click.decorators; print('ok: uvicorn + typer', typer.__version__, 'via', sys.executable)" 2>/dev/null || { \;
  step-6: run cmd=echo "Repairing typer (need >=0.26.7 with bundled click)…"; \;
  step-7: run cmd=$(PYTHON) -m pip install -q 'typer>=0.26.7'; \;
  step-8: run cmd=};
  step-9: run cmd=$(PYTHON) -c "import sys, uvicorn, typer; import typer._click.decorators; print('ok: uvicorn + typer', typer.__version__, 'via', sys.executable)";
}

workflow[name="agent-health"] {
  trigger: manual;
  step-1: run cmd=echo "Agents:";
  step-2: run cmd=for id in weather-map-agent.local invoices-agent.local user-agent.local; do \;
  step-3: run cmd=uri=$$($(HYPERVISOR) inspect-agent $$id 2>/dev/null | $(PYTHON) -c "import json,sys; print(json.load(sys.stdin).get('effective_health_uri',''))" 2>/dev/null || true); \;
  step-4: run cmd=if [ -n "$$uri" ]; then \;
  step-5: run cmd=echo "  $$id -> $$uri"; \;
  step-6: run cmd=curl -fsS "$$uri" 2>/dev/null | $(PYTHON) -m json.tool || echo "    (unreachable)"; \;
  step-7: run cmd=fi; \;
  step-8: run cmd=done;
}

workflow[name="start"] {
  trigger: manual;
  step-1: run cmd=$(WWW_COMPOSE) up -d --build;
  step-2: run cmd=echo "Waiting for www chat health on $(WWW_BASE)…";
  step-3: run cmd=for i in $$(seq 1 30); do \;
  step-4: run cmd=if curl -fsS "$(WWW_BASE)/health" >/dev/null 2>&1; then break; fi; \;
  step-5: run cmd=if [ "$$i" -eq 30 ]; then echo "timeout waiting for health"; exit 1; fi; \;
  step-6: run cmd=sleep 1; \;
  step-7: run cmd=done;
  step-8: run cmd=curl -fsS "$(WWW_BASE)/health" | python3 -m json.tool;
  step-9: run cmd=echo "Chat UI: $(WWW_BASE)/www/";
  step-10: run cmd=echo "Tip: run local agents with: make start-agents";
}

workflow[name="start-agents"] {
  trigger: manual;
  step-1: run cmd=$(HYPERVISOR) run-agent weather-map-agent.local --detach --if-running reuse --wait-healthy;
  step-2: run cmd=$(HYPERVISOR) run-agent invoices-agent.local --detach --if-running reuse --wait-healthy;
  step-3: run cmd=$(HYPERVISOR) run-agent user-agent.local --detach --if-running reuse --wait-healthy;
  step-4: run cmd=$(MAKE) agent-health;
}

workflow[name="start-full"] {
  trigger: manual;
  step-1: depend target=start;
  step-2: depend target=start-agents;
}

workflow[name="uri-shell"] {
  trigger: manual;
  step-1: run cmd=urish;
}

workflow[name="stop"] {
  trigger: manual;
  step-1: run cmd=$(WWW_COMPOSE) down;
}

workflow[name="www-test"] {
  trigger: manual;
  step-1: run cmd=pytest tests/hypervisor/test_chat_www.py -q;
}

workflow[name="www-docs"] {
  trigger: manual;
  step-1: run cmd=python3 scripts/www/build_examples_docs.py;
  step-2: run cmd=python3 scripts/www/build_landing_integrations.py;
  step-3: run cmd=python3 scripts/www/build_examples_manifest.py;
}

workflow[name="www-docs-check"] {
  trigger: manual;
  step-1: run cmd=python3 scripts/www/build_examples_docs.py --check;
  step-2: run cmd=python3 scripts/www/build_landing_integrations.py --check;
  step-3: run cmd=python3 scripts/www/build_examples_manifest.py --check;
  step-4: run cmd=python3 scripts/www/check_examples_links.py;
}

workflow[name="examples-shell"] {
  trigger: manual;
  step-1: run cmd=python3 tests/examples/shell_runner.py;
}

workflow[name="www-smoke"] {
  trigger: manual;
  step-1: run cmd=bash scripts/www/smoke.sh "$(WWW_BASE)";
}

workflow[name="www-monitor"] {
  trigger: manual;
  step-1: run cmd=bash scripts/www/run_monitors.sh;
}

workflow[name="www-monitor-reset"] {
  trigger: manual;
  step-1: run cmd=python3 scripts/www/monitor_landing.py --url "$(WWW_BASE)/www/" --reset-baseline;
}

workflow[name="www-monitor-test"] {
  trigger: manual;
  step-1: run cmd=bash scripts/www/test_monitors.sh;
}

workflow[name="www-logs"] {
  trigger: manual;
  step-1: run cmd=$(WWW_COMPOSE) logs -f --tail=100;
}

tests {
  import: testql-scenarios/**/*.testql.toon.yaml;
}

env_vars {
  keys: OPENROUTER_API_KEY, LLM_MODEL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, RESOURCE_RUNTIME_URL, HYPERVISOR_SSH_PASSWORD;
}

deploy {
  target: docker-compose;
  compose_file: docker-compose.yml;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  template_file: .env.example;
  python_version: >=3.10;
  vars: HYPERVISOR_SSH_PASSWORD, LLM_BASE_URL, LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE, OPENROUTER_API_KEY, RESOURCE_RUNTIME_URL;
  runtime_llm: OPENROUTER_API_KEY;
}
```

## Interfaces

### CLI Entry Points

- `hypervisor`
- `uri3`
- `uri2ops`
- `uri2flow`
- `uri2run`
- `uri`
- `urish`
- `taskinity`
- `touri`
- `uri2verify`
- `urigen`
- `nl2uri`
- `nl2a`

### testql Scenarios

#### `testql-scenarios/generated-api-smoke.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-api-smoke.testql.toon.yaml
# SCENARIO: Auto-generated API Smoke Tests
# TYPE: api
# GENERATED: true
# DETECTORS: FastAPIDetector, ConfigEndpointDetector

CONFIG[5]{key, value}:
  base_url, http://localhost:8101
  timeout_ms, 10000
  retry_count, 3
  retry_backoff_ms, 1000
  detected_frameworks, FastAPIDetector, ConfigEndpointDetector

# Wait for service to be ready
WAIT 1000

# Health check
API GET /api/health 200
ASSERT_STATUS 200

# Capture useful values from responses for subsequent tests
# CAPTURE request_id FROM 'headers.x-request-id'
# CAPTURE session_token FROM 'body.token'

ASSERT[2]{field, operator, expected}:
  _status, <, 500
  _status, >=, 200

# Conditional flow for error handling
FLOW[2]{condition, action}:
  _status >= 500, LOG 'Server error detected'
  _status == 429, WAIT 2000  # Rate limit - wait and retry


# Summary by Framework:
#   docker: 2 endpoints
```

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m hypervisor
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m hypervisor --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m hypervisor --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m hypervisor --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 4 assertions from pytest
ASSERT[4]{field, operator, expected}:
  result.error, ==, "RESOURCE_RUNTIME_UNAVAILABLE"
  r.target.package, ==, "httpx"
  result.error, ==, "RESOURCE_RUNTIME_UNAVAILABLE"
  r.target.package, ==, "httpx"
```

## Workflows

## Configuration

```yaml
project:
  name: tellmesh
  version: 0.5.28
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
fastapi>=0.115
uvicorn>=0.27
httpx>=0.27
jinja2>=3.1
jsonschema>=4.23
markdown>=3.5
pydantic>=2.0
python-dotenv>=1.0.0
pyyaml>=6.0
typer>=0.26.7
uri3
nl2uri
uri2flow
uri2ops
touri
uri2voice
uri2pact
uri2run
uri2verify
urigen
urish
resource-agent-hypervisor
resource-agent-factory
hypervisor-dashboard-agent
```

### Development

```text markpact:deps python scope=dev
pytest>=7.0
pytest-cov>=4.0
pytest-asyncio>=0.21.0
ruff>=0.1.0
mypy>=1.0
build>=1.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
rich>=13.0.0
uvicorn>=0.27
```

## Deployment

```bash markpact:run
pip install tellmesh

# development install
pip install -e .[dev]
```

### Docker

- **base image**: `python:3.11-slim`
- **entrypoint**: `["uvicorn", "meta_agent.api:app", "--host", "0.0.0.0", "--port", "8200"]`

### Docker Compose (`docker-compose.yml`)

- **meta-agent** image=`.` ports: `8200:8200`
- **user-agent** image=`.` ports: `8101:8101`

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `sk-or-v1-...` |  |
| `LLM_MODEL` | `llm://openrouter/qwen/qwen3-coder-next` |  |
| `LLM_BASE_URL` | `https://openrouter.ai/api/v1` |  |
| `LLM_TEMPERATURE` | `0.1` |  |
| `LLM_MAX_TOKENS` | `8000` |  |
| `RESOURCE_RUNTIME_URL` | `http://localhost:8000` |  |
| `HYPERVISOR_SSH_PASSWORD` | `deploy` |  |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`hypervisor`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `venv/lib/python3.13/site-packages/cryptography/__init__.py:__version__`

## Makefile Targets

- `PYTHON` — Prefer repo .venv so start-agents works outside an activated shell (conda base often lacks uvicorn).
- `HYPERVISOR`
- `validate`
- `generate`
- `verify`
- `test`
- `architecture-test`
- `architecture-responsibility-audit`
- `doctor`
- `architecture-gate`
- `ci-gate`
- `examples-test`
- `examples-comprehensive`
- `examples-real-report`
- `doql-registry`
- `examples-comprehensive-mock`
- `examples-playwright-proof`
- `uri2flow-test`
- `uri2flow-validate`
- `uri2flow-expand`
- `uri3-flow-dry-run`
- `nl2uri-flow-validate`
- `example-18`
- `touri-test`
- `touri-demo`
- `voice-test`
- `voice-demo`
- `uri-tree`
- `graph`
- `nl2a-weather`
- `run-user-agent`
- `run-meta-agent`
- `meta-plan`
- `meta-pipeline`
- `meta-repair`
- `docker-ssh-up`
- `docker-ssh-down`
- `docker-testenv-up`
- `docker-testenv-down`
- `scan-http`
- `scan-ssh`
- `scan-all`
- `evolution-check`
- `examples`
- `run-weather-agent`
- `clean`
- `ensure-dev`
- `agent-health`
- `start`
- `start-agents`
- `start-full`
- `uri-shell`
- `stop`
- `www-test`
- `www-docs`
- `www-docs-check`
- `examples-shell`
- `www-smoke`
- `www-monitor`
- `www-monitor-reset`
- `www-monitor-test`
- `www-logs`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# hypervisor | 586f 53448L | python:521,shell:41,javascript:17,css:6,less:1 | 2026-06-15
# stats: 2109 func | 96 cls | 586 mod | CC̄=4.0 | critical:133 | cycles:0
# alerts[5]: CC _render_markdown=70; CC test_all_about_cards_reused_on_website=27; CC _capture_screenshot=26; CC _validate_deployments=26; CC _validate_example=25
# hotspots[5]: analyze_artifact fan=22; open_page fan=22; generate_agent fan=21; describe_agent fan=21; supervise_watch fan=20
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[586]:
  agents/__init__.py,2
  agents/custom/__init__.py,1
  agents/custom/gnome_programmer_agent/__init__.py,1
  agents/custom/gnome_programmer_agent/agent_card.py,29
  agents/custom/gnome_programmer_agent/main.py,13
  agents/custom/gnome_programmer_agent/programmer.py,185
  agents/custom/gnome_programmer_agent/routes.py,74
  agents/custom/remote_deploy_agent/__init__.py,1
  agents/custom/remote_deploy_agent/agent_card.py,41
  agents/custom/remote_deploy_agent/deploy.py,91
  agents/custom/remote_deploy_agent/main.py,13
  agents/custom/remote_deploy_agent/routes.py,70
  agents/custom/screenshot_analysis_agent/__init__.py,3
  agents/custom/screenshot_analysis_agent/agent_card.py,56
  agents/custom/screenshot_analysis_agent/analysis.py,266
  agents/custom/screenshot_analysis_agent/main.py,13
  agents/custom/screenshot_analysis_agent/routes.py,81
  agents/generated/__init__.py,1
  agents/generated/codex_nl_plan_agent/__init__.py,5
  agents/generated/codex_nl_plan_agent/agent_card.py,42
  agents/generated/codex_nl_plan_agent/main.py,21
  agents/generated/codex_nl_plan_agent/routes.py,147
  agents/generated/codex_nl_plan_agent/tests/test_contract.py,21
  agents/generated/codex_nl_smoke_agent/__init__.py,5
  agents/generated/codex_nl_smoke_agent/agent_card.py,42
  agents/generated/codex_nl_smoke_agent/main.py,21
  agents/generated/codex_nl_smoke_agent/routes.py,147
  agents/generated/codex_nl_smoke_agent/tests/test_contract.py,21
  agents/generated/codex_uri_smoke_agent/__init__.py,5
  agents/generated/codex_uri_smoke_agent/agent_card.py,39
  agents/generated/codex_uri_smoke_agent/main.py,20
  agents/generated/codex_uri_smoke_agent/routes.py,147
  agents/generated/codex_uri_smoke_agent/tests/test_contract.py,21
  agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/__init__.py,5
  agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/agent_card.py,21
  agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/main.py,20
  agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py,139
  agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/tests/test_contract.py,21
  agents/generated/gnome_programmer_agent/__init__.py,5
  agents/generated/gnome_programmer_agent/agent_card.py,43
  agents/generated/gnome_programmer_agent/main.py,20
  agents/generated/gnome_programmer_agent/routes.py,153
  agents/generated/gnome_programmer_agent/tests/test_contract.py,21
  agents/generated/hypervisor_dashboard_agent/__init__.py,5
  agents/generated/hypervisor_dashboard_agent/agent_card.py,68
  agents/generated/hypervisor_dashboard_agent/main.py,20
  agents/generated/hypervisor_dashboard_agent/routes.py,166
  agents/generated/hypervisor_dashboard_agent/tests/test_contract.py,21
  agents/generated/invoices_agent/__init__.py,5
  agents/generated/invoices_agent/agent_card.py,42
  agents/generated/invoices_agent/main.py,20
  agents/generated/invoices_agent/routes.py,149
  agents/generated/invoices_agent/tests/test_contract.py,21
  agents/generated/remote_deploy_agent/__init__.py,5
  agents/generated/remote_deploy_agent/agent_card.py,62
  agents/generated/remote_deploy_agent/main.py,20
  agents/generated/remote_deploy_agent/routes.py,167
  agents/generated/remote_deploy_agent/tests/test_contract.py,21
  agents/generated/schema_collab_agent/__init__.py,5
  agents/generated/schema_collab_agent/agent_card.py,51
  agents/generated/schema_collab_agent/main.py,22
  agents/generated/schema_collab_agent/routes.py,151
  agents/generated/schema_collab_agent/tests/test_contract.py,21
  agents/generated/screenshot_analysis_agent/__init__.py,5
  agents/generated/screenshot_analysis_agent/agent_card.py,43
  agents/generated/screenshot_analysis_agent/main.py,20
  agents/generated/screenshot_analysis_agent/routes.py,153
  agents/generated/screenshot_analysis_agent/tests/test_contract.py,21
  agents/generated/user_agent/__init__.py,5
  agents/generated/user_agent/agent_card.py,48
  agents/generated/user_agent/main.py,20
  agents/generated/user_agent/routes.py,156
  agents/generated/user_agent/tests/test_contract.py,21
  agents/generated/weather_map_agent/__init__.py,5
  agents/generated/weather_map_agent/agent_card.py,32
  agents/generated/weather_map_agent/main.py,20
  agents/generated/weather_map_agent/routes.py,145
  agents/generated/weather_map_agent/tests/test_contract.py,21
  agents/operators/__init__.py,2
  agents/operators/browser_operator/__init__.py,1
  agents/operators/browser_operator/adapters/__init__.py,1
  agents/operators/browser_operator/adapters/browser_mock.py,78
  agents/operators/browser_operator/adapters/browser_playwright.py,322
  agents/operators/browser_operator/adapters/browser_playwright_worker.py,86
  agents/operators/browser_operator/adapters/browser_router.py,89
  agents/operators/browser_operator/main.py,12
  agents/operators/common/__init__.py,2
  agents/operators/common/assertion.py,13
  agents/operators/desktop_operator/__init__.py,1
  agents/operators/desktop_operator/adapters/__init__.py,1
  agents/operators/desktop_operator/adapters/android_adb.py,144
  agents/operators/desktop_operator/adapters/android_mock.py,57
  agents/operators/desktop_operator/adapters/android_router.py,55
  agents/operators/desktop_operator/adapters/android_uri.py,27
  agents/operators/desktop_operator/adapters/input_gnome.py,52
  agents/operators/desktop_operator/adapters/input_mock.py,13
  agents/operators/desktop_operator/adapters/input_router.py,37
  agents/operators/desktop_operator/adapters/pcwin_mock.py,39
  agents/operators/desktop_operator/adapters/pcwin_router.py,50
  agents/operators/desktop_operator/adapters/pcwin_uia.py,94
  agents/operators/desktop_operator/adapters/pcwin_uri.py,48
  agents/operators/desktop_operator/adapters/screen_gnome.py,140
  agents/operators/desktop_operator/adapters/screen_mock.py,11
  agents/operators/desktop_operator/adapters/screen_router.py,37
  agents/operators/desktop_operator/main.py,12
  agents/operators/device_robot_operator/__init__.py,1
  agents/operators/device_robot_operator/adapters/__init__.py,1
  agents/operators/device_robot_operator/adapters/physical_mock.py,134
  agents/operators/device_robot_operator/main.py,12
  agents/operators/operator_runtime.py,34
  agents/system/__init__.py,2
  agents/system/hypervisor_dashboard/__init__.py,2
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/__init__.py,1
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/agent_card.py,75
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py,388
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py,286
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/main.py,25
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/models.py,83
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/monitor_webhook.py,128
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/paths.py,14
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/plan_runner.py,174
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/policy.py,55
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/presentation.py,83
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py,417
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/static/dashboard.css,63
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/static/dashboard.js,62
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py,335
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/view_builder.py,71
  agents/system/hypervisor_dashboard/main.py,8
  app.doql.less,431
  domains/__init__.py,1
  domains/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html/__init__.py,1
  domains/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html/handlers/__init__.py,1
  domains/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html/handlers/run.py,6
  domains/weather_map/__init__.py,1
  domains/weather_map/handlers/__init__.py,1
  domains/weather_map/handlers/generate_weather_map.py,31
  domains/weather_map/planner.py,62
  examples/01_quickstart_local/run.sh,9
  examples/04_nl2a_weather_map/run.sh,8
  examples/09_run_agent_hypervisor/run.sh,8
  examples/10_browser_operator/run.sh,6
  examples/11_playwright_browser/run.sh,86
  examples/12_android_operator/run.sh,9
  examples/13_nl2uri_multi_uri_graph/run.sh,46
  examples/13_pcwin_operator/run.sh,9
  examples/14_uri2ops_serve/run.sh,21
  examples/14_workflow_executor_mock/run.sh,40
  examples/15_compact_uri_flow/run.sh,8
  examples/16_llm_graph_planner/run.sh,20
  examples/17_flow_vs_graph/run.sh,20
  examples/18_llm_flow_planner/run.sh,35
  examples/20_touri_capabilities/run.sh,11
  examples/21_touri_voice/run.sh,77
  examples/21_touri_voice/touri_examples_voice/__init__.py,1
  examples/21_touri_voice/touri_examples_voice/stt.py,8
  examples/21_touri_voice/touri_examples_voice/tts.py,6
  examples/21_touri_voice/touri_examples_voice/voice_command.py,6
  examples/22_markpact_weather/run.sh,27
  examples/23_nl_to_agent_tutorial/run.sh,205
  examples/30_golden_path/run.sh,26
  examples/31_office_day/run.sh,55
  examples/32_ecommerce_integrations/run.sh,18
  examples/33_office_workflows/run.sh,42
  examples/34_cron_uri/run.sh,35
  examples/35_website_screenshot_schedule/run.sh,38
  examples/36_physical_ops/run.sh,15
  examples/37_agent_screenshot_analysis/run.sh,87
  examples/38_autonomous_agents/run.sh,94
  packages/resource-agent-factory/agents/generated/orders_agent/__init__.py,5
  packages/resource-agent-factory/agents/generated/orders_agent/agent_card.py,37
  packages/resource-agent-factory/agents/generated/orders_agent/main.py,16
  packages/resource-agent-factory/agents/generated/orders_agent/routes.py,90
  packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py,18
  packages/resource-agent-factory/agents/generated/user_agent/__init__.py,5
  packages/resource-agent-factory/agents/generated/user_agent/agent_card.py,63
  packages/resource-agent-factory/agents/generated/user_agent/main.py,16
  packages/resource-agent-factory/agents/generated/user_agent/routes.py,96
  packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py,18
  packages/resource-agent-factory/generator/__init__.py,1
  packages/resource-agent-factory/generator/agent_generator.py,133
  packages/resource-agent-factory/generator/hashutil.py,10
  packages/resource-agent-factory/generator/header.py,57
  packages/resource-agent-factory/generator/model.py,95
  packages/resource-agent-factory/generator/paths.py,13
  packages/resource-agent-factory/generator/validate.py,70
  packages/resource-agent-factory/generator/verify.py,84
  packages/resource-agent-hypervisor/hypervisor/__init__.py,14
  packages/resource-agent-hypervisor/hypervisor/_version.py,21
  packages/resource-agent-hypervisor/hypervisor/agent_describe.py,678
  packages/resource-agent-hypervisor/hypervisor/artifacts/__init__.py,4
  packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py,309
  packages/resource-agent-hypervisor/hypervisor/cli.py,564
  packages/resource-agent-hypervisor/hypervisor/cli_commands.py,160
  packages/resource-agent-hypervisor/hypervisor/compatibility/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/compatibility/checker.py,44
  packages/resource-agent-hypervisor/hypervisor/config/__init__.py,25
  packages/resource-agent-hypervisor/hypervisor/config/config_checks.py,51
  packages/resource-agent-hypervisor/hypervisor/config/defaults.py,64
  packages/resource-agent-hypervisor/hypervisor/config/env.py,55
  packages/resource-agent-hypervisor/hypervisor/config/loader.py,97
  packages/resource-agent-hypervisor/hypervisor/config/models.py,159
  packages/resource-agent-hypervisor/hypervisor/config/uri_config.py,41
  packages/resource-agent-hypervisor/hypervisor/config/validators.py,34
  packages/resource-agent-hypervisor/hypervisor/contract_registry/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cli.py,42
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py,66
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/__init__.py,10
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/capabilities.py,69
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/proto_index.py,17
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/resources.py,23
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py,43
  packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py,81
  packages/resource-agent-hypervisor/hypervisor/contract_registry/merge_helpers.py,62
  packages/resource-agent-hypervisor/hypervisor/contract_registry/merger.py,27
  packages/resource-agent-hypervisor/hypervisor/contract_registry/models.py,57
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py,61
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/__init__.py,5
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/capabilities.py,60
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/resources.py,27
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_exporter.py,30
  packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py,55
  packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py,563
  packages/resource-agent-hypervisor/hypervisor/contract_registry/validate.py,14
  packages/resource-agent-hypervisor/hypervisor/core.py,85
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/__init__.py,66
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/aliases.py,35
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/docker_runner.py,77
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/env.py,51
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_config.py,29
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_merge.py,32
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py,67
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/__init__.py,14
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py,185
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/pipeline.py,232
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/probe.py,149
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/readiness.py,93
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py,424
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle_status.py,68
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py,88
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py,121
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_verify.py,40
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py,125
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_conflict.py,78
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_utils.py,63
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/process.py,58
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/process_discovery.py,125
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/registry_sync.py,69
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/remote_runner.py,17
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py,305
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_plans.py,34
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/runner.py,38
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py,296
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/selector.py,77
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_deploy.py,96
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_helpers.py,15
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_run.py,119
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_verify.py,39
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py,189
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py,240
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py,200
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py,409
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py,46
  packages/resource-agent-hypervisor/hypervisor/domain_pack/__init__.py,32
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/agent_contract.py,49
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/commands.py,19
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/handlers.py,11
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/proto.py,9
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/renderers.py,15
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/resources.py,25
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/views.py,17
  packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py,76
  packages/resource-agent-hypervisor/hypervisor/domain_pack/model.py,26
  packages/resource-agent-hypervisor/hypervisor/domain_pack/pack_writer.py,94
  packages/resource-agent-hypervisor/hypervisor/domain_pack/parser.py,18
  packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py,122
  packages/resource-agent-hypervisor/hypervisor/domain_pack/writer.py,12
  packages/resource-agent-hypervisor/hypervisor/events.py,87
  packages/resource-agent-hypervisor/hypervisor/evolution/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/evolution/cli.py,34
  packages/resource-agent-hypervisor/hypervisor/evolution/models.py,33
  packages/resource-agent-hypervisor/hypervisor/evolution/proposal_from_source.py,128
  packages/resource-agent-hypervisor/hypervisor/evolution/validator.py,46
  packages/resource-agent-hypervisor/hypervisor/integrations/planfile/__init__.py,14
  packages/resource-agent-hypervisor/hypervisor/integrations/planfile/ticket_mapper.py,96
  packages/resource-agent-hypervisor/hypervisor/paths.py,77
  packages/resource-agent-hypervisor/hypervisor/policy_gate/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py,27
  packages/resource-agent-hypervisor/hypervisor/repair/__init__.py,18
  packages/resource-agent-hypervisor/hypervisor/repair/classifier.py,139
  packages/resource-agent-hypervisor/hypervisor/repair/healer.py,36
  packages/resource-agent-hypervisor/hypervisor/repair/incident.py,182
  packages/resource-agent-hypervisor/hypervisor/repair/models.py,64
  packages/resource-agent-hypervisor/hypervisor/repair/plan_builder.py,109
  packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py,135
  packages/resource-agent-hypervisor/hypervisor/repair/policy.py,72
  packages/resource-agent-hypervisor/hypervisor/repair/proposal_builder.py,36
  packages/resource-agent-hypervisor/hypervisor/repair/registry.py,59
  packages/resource-agent-hypervisor/hypervisor/repair/sandbox.py,50
  packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py,382
  packages/resource-agent-hypervisor/hypervisor/repair/validator.py,52
  packages/resource-agent-hypervisor/hypervisor/routing/__init__.py,40
  packages/resource-agent-hypervisor/hypervisor/routing/dispatcher.py,74
  packages/resource-agent-hypervisor/hypervisor/routing/explain.py,75
  packages/resource-agent-hypervisor/hypervisor/routing/models.py,64
  packages/resource-agent-hypervisor/hypervisor/routing/policy.py,138
  packages/resource-agent-hypervisor/hypervisor/routing/registry_bridge.py,60
  packages/resource-agent-hypervisor/hypervisor/routing/resolver.py,148
  packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py,176
  packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py,306
  packages/resource-agent-hypervisor/hypervisor/routing/system_request.py,51
  packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py,139
  packages/resource-agent-hypervisor/hypervisor/routing/views/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/routing/views/process.py,105
  packages/resource-agent-hypervisor/hypervisor/uri/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/uri/client.py,74
  packages/resource-agent-hypervisor/hypervisor/uri2llm/__init__.py,16
  packages/resource-agent-hypervisor/hypervisor/uri2llm/env_resolver.py,6
  packages/resource-agent-hypervisor/hypervisor/uri2llm/function_resolver.py,6
  packages/resource-agent-hypervisor/hypervisor/uri2llm/llm_resolver.py,6
  packages/resource-agent-hypervisor/hypervisor/uri2llm/protocol_resolver.py,11
  packages/resource-agent-hypervisor/hypervisor/uri2llm/pypi_resolver.py,6
  packages/resource-agent-hypervisor/hypervisor/uri2llm/router.py,6
  packages/resource-agent-hypervisor/hypervisor/verifier/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/verifier/capability_tests.py,9
  packages/resource-agent-hypervisor/hypervisor/verifier/cli.py,29
  packages/resource-agent-hypervisor/meta_agent/__init__.py,2
  packages/resource-agent-hypervisor/meta_agent/api.py,84
  packages/resource-agent-hypervisor/meta_agent/cli.py,52
  packages/resource-agent-hypervisor/meta_agent/cli_commands.py,70
  packages/resource-agent-hypervisor/meta_agent/domain_planner/__init__.py,2
  packages/resource-agent-hypervisor/meta_agent/domain_planner/domain_pack_generator.py,17
  packages/resource-agent-hypervisor/meta_agent/domain_planner/llm_planner.py,16
  packages/resource-agent-hypervisor/meta_agent/models.py,44
  packages/resource-agent-hypervisor/meta_agent/orchestrator.py,74
  packages/resource-agent-hypervisor/meta_agent/planner.py,160
  packages/resource-agent-hypervisor/meta_agent/repair/__init__.py,4
  packages/resource-agent-hypervisor/meta_agent/repair/loader.py,18
  packages/resource-agent-hypervisor/meta_agent/repair/pipeline.py,40
  packages/resource-agent-hypervisor/meta_agent/repair/rules.py,83
  packages/resource-agent-hypervisor/runtime_client/__init__.py,1
  packages/resource-agent-hypervisor/runtime_client/client.py,48
  packages/uri2flow/uri2flow/__init__.py,17
  packages/uri2flow/uri2flow/cli.py,76
  packages/uri2flow/uri2flow/expander.py,82
  packages/uri2flow/uri2flow/loaders/__init__.py,20
  packages/uri2flow/uri2flow/loaders/markpact_loader.py,24
  packages/uri2flow/uri2flow/models.py,48
  packages/uri2flow/uri2flow/parser.py,100
  packages/uri2flow/uri2flow/resolver.py,111
  packages/uri2flow/uri2flow/utils.py,39
  packages/uri2flow/uri2flow/validator.py,65
  project.sh,59
  scripts/architecture_audit/__init__.py,21
  scripts/architecture_audit/areas.py,157
  scripts/architecture_audit/audit.py,145
  scripts/architecture_audit/checks_domain.py,143
  scripts/architecture_audit/checks_structure.py,279
  scripts/architecture_audit/cli.py,93
  scripts/architecture_audit/models.py,54
  scripts/architecture_audit/parsers.py,171
  scripts/architecture_audit/render.py,84
  scripts/architecture_responsibility_audit.py,29
  scripts/ci/architecture_gate.sh,57
  scripts/ci/ensure_editable_install.sh,20
  scripts/examples/audit_agent_reports.py,428
  scripts/examples/cli_fallback.sh,66
  scripts/examples/comprehensive_test.py,391
  scripts/examples/doql_host_preview.sh,75
  scripts/examples/effective_weather_playwright.py,467
  scripts/examples/run_uri3_workflow.py,59
  scripts/fix-generated-ownership.sh,19
  scripts/tellmesh/fix_and_publish.py,130
  scripts/tellmesh/move_tests.py,138
  scripts/tellmesh/split_packages.py,280
  scripts/tellmesh/sync_www.py,86
  scripts/test-all-examples.sh,6
  scripts/www/about_parser.py,54
  scripts/www/build_examples_docs.py,327
  scripts/www/build_examples_manifest.py,171
  scripts/www/build_landing_integrations.py,320
  scripts/www/check_examples_links.py,112
  scripts/www/install-cron.sh,151
  scripts/www/md_html.py,49
  scripts/www/monitor_landing.py,134
  scripts/www/monitor_notify.py,90
  scripts/www/monitor_url.py,84
  scripts/www/run_monitors.sh,48
  scripts/www/site_nav.py,78
  scripts/www/smoke.sh,29
  scripts/www/test_monitors.sh,180
  scripts/www/verify_agents.sh,35
  scripts/www/www_root.py,19
  testenv/ssh_agent_host/entrypoint.sh,8
  testenv/ssh_agent_host/mock_agent_server.py,58
  tests/__init__.py,1
  tests/architecture/envelope_helpers.py,41
  tests/architecture/import_scanner.py,17
  tests/architecture/test_doctor_contract.py,33
  tests/architecture/test_doctor_gate.py,14
  tests/architecture/test_explain_contract.py,43
  tests/architecture/test_import_boundaries.py,11
  tests/architecture/test_result_envelope_contract.py,65
  tests/architecture/test_technical_ok_business_fail.py,54
  tests/architecture/test_uri2run_envelope.py,28
  tests/capabilities/weather_forecast/test_fixtures.py,23
  tests/conftest.py,122
  tests/domain_pack/__init__.py,2
  tests/domain_pack/test_generator.py,84
  tests/examples/capabilities.py,220
  tests/examples/catalog.py,135
  tests/examples/command_catalog.py,381
  tests/examples/conftest.py,133
  tests/examples/shell_runner.py,341
  tests/examples/test_comprehensive.py,118
  tests/examples/test_effective_weather_playwright.py,42
  tests/examples/test_examples_smoke.py,71
  tests/examples/test_inline_examples.py,204
  tests/examples/test_run_sh_examples.py,32
  tests/generator/__init__.py,2
  tests/generator/test_headers.py,78
  tests/hypervisor/__init__.py,2
  tests/hypervisor/test_agent_describe.py,106
  tests/hypervisor/test_agent_factory_uri.py,101
  tests/hypervisor/test_agent_lifecycle.py,164
  tests/hypervisor/test_agent_runner.py,662
  tests/hypervisor/test_artifact_standards.py,163
  tests/hypervisor/test_autonomous_agents.py,29
  tests/hypervisor/test_browser_operator_separation.py,66
  tests/hypervisor/test_browser_ops_domain.py,55
  tests/hypervisor/test_chat_flow_view.py,82
  tests/hypervisor/test_chat_www.py,819
  tests/hypervisor/test_config.py,82
  tests/hypervisor/test_contract_uri.py,159
  tests/hypervisor/test_dashboard_agent.py,390
  tests/hypervisor/test_dashboard_policy.py,33
  tests/hypervisor/test_dashboard_routing_api.py,72
  tests/hypervisor/test_deployment_aliases.py,24
  tests/hypervisor/test_deployment_registry.py,132
  tests/hypervisor/test_deployment_selector.py,21
  tests/hypervisor/test_desktop_operator_separation.py,87
  tests/hypervisor/test_desktop_ops_domain.py,112
  tests/hypervisor/test_docker_runner.py,22
  tests/hypervisor/test_events_service.py,195
  tests/hypervisor/test_graph_hypervisor_routing.py,44
  tests/hypervisor/test_health_uri.py,41
  tests/hypervisor/test_hypervisor_cli.py,197
  tests/hypervisor/test_inspection_probe.py,80
  tests/hypervisor/test_local_run_plan.py,59
  tests/hypervisor/test_markpact_deployments.py,22
  tests/hypervisor/test_monitor_landing.py,71
  tests/hypervisor/test_monitor_url.py,139
  tests/hypervisor/test_operator_agent_packages.py,49
  tests/hypervisor/test_physical_operator_separation.py,70
  tests/hypervisor/test_plan_runner.py,129
  tests/hypervisor/test_port_conflict.py,83
  tests/hypervisor/test_presentation_uri.py,86
  tests/hypervisor/test_registry_sync.py,77
  tests/hypervisor/test_remote_runner.py,64
  tests/hypervisor/test_repair_supervisor.py,167
  tests/hypervisor/test_routing_pipeline.py,147
  tests/hypervisor/test_routing_policy.py,47
  tests/hypervisor/test_runtime_state.py,102
  tests/hypervisor/test_schema_collab_contract.py,16
  tests/hypervisor/test_screenshot_analysis_agent.py,72
  tests/hypervisor/test_sprint1_autonomy.py,246
  tests/hypervisor/test_supervise_watch.py,140
  tests/hypervisor/test_system_agent_packages.py,46
  tests/hypervisor/test_system_routing.py,72
  tests/hypervisor/test_tutorial_three_agents_smoke.py,45
  tests/hypervisor/test_uri_exchange_schema.py,77
  tests/hypervisor/test_uri_healer.py,23
  tests/hypervisor/test_view_routing.py,32
  tests/hypervisor/test_www_integrations_build.py,202
  tests/integration/__init__.py,2
  tests/integration/test_flow_to_workflow_execution.py,39
  tests/integration/test_nl2a_e2e.py,93
  tests/integration/test_uri3_uri2ops_delegation.py,43
  tests/meta_agent/__init__.py,2
  tests/meta_agent/test_repair.py,80
  tests/nl2uri/test_domain_planner.py,32
  tests/nl2uri/test_flow_planner.py,50
  tests/nl2uri/test_flow_planner_llm.py,70
  tests/nl2uri/test_flow_repair.py,97
  tests/nl2uri/test_graph_planner.py,75
  tests/nl2uri/test_graph_planner_llm.py,119
  tests/nl2uri/test_weather_forecast.py,60
  tests/resource_agent_factory/test_default_port.py,15
  tests/scripts/test_architecture_responsibility_audit.py,260
  tests/test_capability_tests.py,11
  tests/test_contract_registry.py,21
  tests/test_cross_validation_v03.py,6
  tests/test_dependencies.py,15
  tests/test_evolution_proposal.py,9
  tests/test_generate.py,11
  tests/test_hypervisor.py,87
  tests/test_meta_agent.py,63
  tests/test_nl2uri.py,10
  tests/test_operator_task.py,23
  tests/test_policy_gate.py,19
  tests/test_registry_builder_v03.py,21
  tests/test_runtime_client.py,9
  tests/test_schema_validation_v03.py,8
  tests/test_uri2llm_v04.py,22
  tests/test_uri3.py,12
  tests/test_uri_tree_validator.py,5
  tests/test_validate.py,9
  tests/uri2flow/conftest.py,15
  tests/uri2flow/test_cli.py,13
  tests/uri2flow/test_expand_branching_flow.py,14
  tests/uri2flow/test_expand_linear_flow.py,15
  tests/uri2flow/test_flow_defaults.py,58
  tests/uri2flow/test_parser_forms.py,16
  tests/uri2flow/test_uri2flow_markpact_loader.py,125
  tests/uri2pact/test_markpact_scenarios.py,35
  tests/uri2run/test_protocol_transports.py,201
  tests/uri2run/test_stream_transports.py,83
  tests/uri2run/test_transport_matrix.py,145
  tests/uri2run/test_uri2run.py,115
  tests/uri2run/test_voice_resolver.py,32
  tests/uri2run/test_workflow_transport.py,44
  tests/uri3/__init__.py,2
  tests/uri3/test_browser_adapter.py,109
  tests/uri3/test_cli.py,88
  tests/uri3/test_dispatch.py,23
  tests/uri3/test_docker_control.py,115
  tests/uri3/test_doctor.py,43
  tests/uri3/test_envelope_migrate.py,30
  tests/uri3/test_explain_extended.py,72
  tests/uri3/test_explain_uri.py,42
  tests/uri3/test_file_resolver.py,29
  tests/uri3/test_http_scanner.py,43
  tests/uri3/test_lifecycle_envelope.py,33
  tests/uri3/test_llm_profiles.py,34
  tests/uri3/test_log_reader_meta.py,20
  tests/uri3/test_log_uri.py,87
  tests/uri3/test_replay.py,60
  tests/uri3/test_resolvers.py,107
  tests/uri3/test_result_envelope.py,58
  tests/uri3/test_router_call.py,20
  tests/uri3/test_schema.py,99
  tests/uri3/test_service_result.py,32
  tests/uri3/test_ssh_auth.py,55
  tests/uri3/test_ssh_scanner.py,65
  tests/uri3/test_uri_yaml.py,39
  tests/uri3/test_workflow_executor.py,148
  tests/uri3/test_workflow_graph.py,53
  tests/urigen/test_urigen_cycle.py,217
  tests/urish/test_agent_backend.py,27
  tests/urish/test_agent_factory.py,106
  tests/urish/test_ask_dashboard.py,183
  tests/urish/test_call_routing.py,27
  tests/urish/test_desktop_policy.py,53
  tests/urish/test_office_intent.py,76
  tests/urish/test_office_scenarios.py,80
  tests/urish/test_physical_policy.py,40
  tests/urish/test_prompt_split.py,34
  tests/urish/test_render.py,51
  tests/urish/test_repl.py,130
  tests/urish/test_scenario_registry_boundary.py,21
  tests/urish/test_ticket_workflow.py,139
  tests/urish/test_urish_cli.py,466
  tests/urish/test_workflow_run.py,126
  tree.sh,2
  www/api-bridge/bridge.py,200
  www/app.js,732
  www/assets/api-client.js,216
  www/assets/app.js,261
  www/assets/config.js,14
  www/assets/styles.css,148
  www/chat-flow-view.js,274
  www/chat-markdown.js,81
  www/chat-uri.js,183
  www/chat-voice.js,158
  www/docs-examples.js,60
  www/examples-gallery.js,145
  www/flow-chat.css,551
  www/flow-chat.js,226
  www/generated/examples-manifest.js,478
  www/generated/integrations-i18n.js,1144
  www/landing-i18n.js,720
  www/landing.css,2998
  www/landing.js,837
  www/office-cards-i18n.js,307
  www/site-shell.css,168
  www/styles.css,490
D:
  agents/__init__.py:
  agents/custom/__init__.py:
  agents/custom/gnome_programmer_agent/__init__.py:
  agents/custom/gnome_programmer_agent/agent_card.py:
  agents/custom/gnome_programmer_agent/main.py:
  agents/custom/gnome_programmer_agent/programmer.py:
    e: repo_root,_post_json,_operator_task,observe_desktop,type_on_desktop,programmer_session,_extract_artifact
    repo_root()
    _post_json(url;payload)
    _operator_task()
    observe_desktop()
    type_on_desktop()
    programmer_session()
    _extract_artifact(result)
  agents/custom/gnome_programmer_agent/routes.py:
    e: health,well_known_agent_card_json,capabilities,skill_observe_desktop,skill_type_on_desktop,skill_run_programmer_session,OperatorRequest,TypeRequest,SessionRequest
    OperatorRequest:
    TypeRequest:
    SessionRequest:
    health()
    well_known_agent_card_json()
    capabilities()
    skill_observe_desktop(payload)
    skill_type_on_desktop(payload)
    skill_run_programmer_session(payload)
  agents/custom/remote_deploy_agent/__init__.py:
  agents/custom/remote_deploy_agent/agent_card.py:
  agents/custom/remote_deploy_agent/deploy.py:
    e: repo_root,_resolve_deployment,plan_remote_deploy,apply_remote_deploy,verify_remote_agent,start_remote_agent,deploy_verify_start
    repo_root()
    _resolve_deployment(deployment_id)
    plan_remote_deploy(deployment_id)
    apply_remote_deploy(deployment_id)
    verify_remote_agent(deployment_id)
    start_remote_agent(deployment_id)
    deploy_verify_start(deployment_id)
  agents/custom/remote_deploy_agent/main.py:
  agents/custom/remote_deploy_agent/routes.py:
    e: health,well_known_agent_card_json,capabilities,skill_plan_remote_deploy,skill_apply_remote_deploy,skill_verify_remote_agent,skill_start_remote_agent,skill_deploy_verify_start,DeploymentRequest
    DeploymentRequest:
    health()
    well_known_agent_card_json()
    capabilities()
    skill_plan_remote_deploy(payload)
    skill_apply_remote_deploy(payload)
    skill_verify_remote_agent(payload)
    skill_start_remote_agent(payload)
    skill_deploy_verify_start(payload)
  agents/custom/screenshot_analysis_agent/__init__.py:
  agents/custom/screenshot_analysis_agent/agent_card.py:
  agents/custom/screenshot_analysis_agent/analysis.py:
    e: repo_root,_path_from_file_uri,resolve_observation_path,_png_size,_json_summary,_read_previous,_append_markdown,analyze_artifact,_post_json,_extract_screenshot_artifact,capture_with_operator
    repo_root()
    _path_from_file_uri(uri)
    resolve_observation_path(uri)
    _png_size(data)
    _json_summary(data)
    _read_previous(jsonl_path)
    _append_markdown(path;observation)
    analyze_artifact(artifact_uri)
    _post_json(url;payload)
    _extract_screenshot_artifact(result)
    capture_with_operator()
  agents/custom/screenshot_analysis_agent/main.py:
  agents/custom/screenshot_analysis_agent/routes.py:
    e: health,well_known_agent_card_json,well_known_agent_json,capabilities,skill_analyze_screenshot,skill_capture_and_analyze,skill_run_scheduled_capture_analysis,AnalyzeScreenshotRequest,CaptureAndAnalyzeRequest
    AnalyzeScreenshotRequest:
    CaptureAndAnalyzeRequest:
    health()
    well_known_agent_card_json()
    well_known_agent_json()
    capabilities()
    skill_analyze_screenshot(payload)
    skill_capture_and_analyze(payload)
    skill_run_scheduled_capture_analysis(payload)
  agents/generated/__init__.py:
  agents/generated/codex_nl_plan_agent/__init__.py:
  agents/generated/codex_nl_plan_agent/agent_card.py:
  agents/generated/codex_nl_plan_agent/main.py:
  agents/generated/codex_nl_plan_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_read_markpact_source,skill_read_device_status,skill_run_cron_monitor,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_read_markpact_source()
    skill_read_device_status()
    skill_run_cron_monitor(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/codex_nl_plan_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/codex_nl_smoke_agent/__init__.py:
  agents/generated/codex_nl_smoke_agent/agent_card.py:
  agents/generated/codex_nl_smoke_agent/main.py:
  agents/generated/codex_nl_smoke_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_read_markpact_source,skill_read_device_status,skill_run_cron_monitor,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_read_markpact_source()
    skill_read_device_status()
    skill_run_cron_monitor(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/codex_nl_smoke_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/codex_uri_smoke_agent/__init__.py:
  agents/generated/codex_uri_smoke_agent/agent_card.py:
  agents/generated/codex_uri_smoke_agent/main.py:
  agents/generated/codex_uri_smoke_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_read_markpact_source,skill_read_device_status,skill_run_cron_monitor,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_read_markpact_source()
    skill_read_device_status()
    skill_run_cron_monitor(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/codex_uri_smoke_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/__init__.py:
  agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/agent_card.py:
  agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/main.py:
  agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_run,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_run(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/gnome_programmer_agent/__init__.py:
  agents/generated/gnome_programmer_agent/agent_card.py:
  agents/generated/gnome_programmer_agent/main.py:
  agents/generated/gnome_programmer_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_observe_desktop,skill_type_on_desktop,skill_programmer_session,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_observe_desktop(payload)
    skill_type_on_desktop(payload)
    skill_programmer_session(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/gnome_programmer_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/hypervisor_dashboard_agent/__init__.py:
  agents/generated/hypervisor_dashboard_agent/agent_card.py:
  agents/generated/hypervisor_dashboard_agent/main.py:
  agents/generated/hypervisor_dashboard_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_process_view,skill_workflow_timeline,skill_incident_explain,skill_repair_diagnose,skill_repair_action,skill_uri_call,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_process_view(agent_id)
    skill_workflow_timeline(workflow_id)
    skill_incident_explain(incident_id)
    skill_repair_diagnose(agent_id)
    skill_repair_action(payload)
    skill_uri_call(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/hypervisor_dashboard_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/invoices_agent/__init__.py:
  agents/generated/invoices_agent/agent_card.py:
  agents/generated/invoices_agent/main.py:
  agents/generated/invoices_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_read_invoice,skill_read_invoice_events,skill_create_invoice,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_read_invoice(invoice_id)
    skill_read_invoice_events(invoice_id)
    skill_create_invoice(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/invoices_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/remote_deploy_agent/__init__.py:
  agents/generated/remote_deploy_agent/agent_card.py:
  agents/generated/remote_deploy_agent/main.py:
  agents/generated/remote_deploy_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_plan_remote_deploy,skill_apply_remote_deploy,skill_verify_remote_agent,skill_start_remote_agent,skill_deploy_verify_start,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_plan_remote_deploy(payload)
    skill_apply_remote_deploy(payload)
    skill_verify_remote_agent(payload)
    skill_start_remote_agent(payload)
    skill_deploy_verify_start(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/remote_deploy_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/schema_collab_agent/__init__.py:
  agents/generated/schema_collab_agent/agent_card.py:
  agents/generated/schema_collab_agent/main.py:
  agents/generated/schema_collab_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_read_markpact_source,skill_read_device_status,skill_read_robot_state,skill_run_cron_monitor,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_read_markpact_source()
    skill_read_device_status()
    skill_read_robot_state()
    skill_run_cron_monitor(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/schema_collab_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/screenshot_analysis_agent/__init__.py:
  agents/generated/screenshot_analysis_agent/agent_card.py:
  agents/generated/screenshot_analysis_agent/main.py:
  agents/generated/screenshot_analysis_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_analyze_screenshot,skill_capture_and_analyze,skill_scheduled_capture_analysis,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_analyze_screenshot(payload)
    skill_capture_and_analyze(payload)
    skill_scheduled_capture_analysis(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/screenshot_analysis_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/user_agent/__init__.py:
  agents/generated/user_agent/agent_card.py:
  agents/generated/user_agent/main.py:
  agents/generated/user_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_read_user,skill_read_user_roles,skill_create_user,skill_assign_user_role,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_read_user(user_id)
    skill_read_user_roles(user_id)
    skill_create_user(payload)
    skill_assign_user_role(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/user_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/weather_map_agent/__init__.py:
  agents/generated/weather_map_agent/agent_card.py:
  agents/generated/weather_map_agent/main.py:
  agents/generated/weather_map_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_read_weather_map,skill_generate_weather_map,_uri_allowed,_read_uri,_command_uri,_dispatch_command,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_read_weather_map(place;days)
    skill_generate_weather_map(payload)
    _uri_allowed(uri;templates)
    _read_uri(uri)
    _command_uri(command)
    _dispatch_command(command;payload)
  agents/generated/weather_map_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/operators/__init__.py:
  agents/operators/browser_operator/__init__.py:
  agents/operators/browser_operator/adapters/__init__.py:
  agents/operators/browser_operator/adapters/browser_mock.py:
    e: _artifact_root,_session,_mock_page_text,open_page,extract_dom,screenshot,capture_page,click
    _artifact_root(context)
    _session(context)
    _mock_page_text(url)
    open_page(payload;context)
    extract_dom(payload;context)
    screenshot(payload;context)
    capture_page(payload;context)
    click(payload;context)
  agents/operators/browser_operator/adapters/browser_playwright.py:
    e: playwright_install_hint,playwright_browsers_hint,playwright_import_error,playwright_browsers_error,playwright_available,json_dumps,_playwright_worker,_run_sync,probe_playwright_ready,_session,_task_context,close_playwright_session,open_page,extract_dom,screenshot,click,capture_page,execute,_PlaywrightWorker
    _PlaywrightWorker: __init__(0),_loop(0),run(1)  # Dedicated thread for sync Playwright (greenlet-safe, asyncio
    playwright_install_hint()
    playwright_browsers_hint()
    playwright_import_error(exc)
    playwright_browsers_error(exc)
    playwright_available()
    json_dumps(payload)
    _playwright_worker()
    _run_sync(work)
    probe_playwright_ready()
    _session(context)
    _task_context(context)
    close_playwright_session(context)
    open_page(payload;context)
    extract_dom(payload;context)
    screenshot(payload;context)
    click(payload;context)
    capture_page(payload;context)
    execute(payload;context)
  agents/operators/browser_operator/adapters/browser_playwright_worker.py:
    e: capture_page,main
    capture_page(payload;context)
    main()
  agents/operators/browser_operator/adapters/browser_router.py:
    e: _playwright_ready,playwright_ready,resolve_adapter_mode,_dispatch,open_page,extract_dom,screenshot,capture_page,click,cleanup_browser_session
    _playwright_ready()
    playwright_ready()
    resolve_adapter_mode(scheme;context)
    _dispatch(operation;payload;context)
    open_page(payload;context)
    extract_dom(payload;context)
    screenshot(payload;context)
    capture_page(payload;context)
    click(payload;context)
    cleanup_browser_session(context)
  agents/operators/browser_operator/main.py:
  agents/operators/common/__init__.py:
  agents/operators/common/assertion.py:
    e: check
    check(payload;context)
  agents/operators/desktop_operator/__init__.py:
  agents/operators/desktop_operator/adapters/__init__.py:
  agents/operators/desktop_operator/adapters/android_adb.py:
    e: _task_context,_run_adb,adb_available,device_ready,list_devices,screenshot,dump_ui,tap,_find_selector_bounds
    _task_context(context)
    _run_adb(device_id)
    adb_available()
    device_ready(device_id)
    list_devices()
    screenshot(payload;context)
    dump_ui(payload;context)
    tap(payload;context)
    _find_selector_bounds(xml;selector)
  agents/operators/desktop_operator/adapters/android_mock.py:
    e: _task_context,screenshot,dump_ui,tap
    _task_context(context)
    screenshot(payload;context)
    dump_ui(payload;context)
    tap(payload;context)
  agents/operators/desktop_operator/adapters/android_router.py:
    e: _adb_ready,resolve_adapter_mode,_dispatch,screenshot,dump_ui,tap
    _adb_ready()
    resolve_adapter_mode(scheme;context)
    _dispatch(operation;payload;context)
    screenshot(payload;context)
    dump_ui(payload;context)
    tap(payload;context)
  agents/operators/desktop_operator/adapters/android_uri.py:
    e: parse_android_uri,device_id_from_payload
    parse_android_uri(uri)
    device_id_from_payload(payload)
  agents/operators/desktop_operator/adapters/input_gnome.py:
    e: gnome_input_available,type_text
    gnome_input_available()
    type_text(payload;context)
  agents/operators/desktop_operator/adapters/input_mock.py:
    e: type_text
    type_text(payload;context)
  agents/operators/desktop_operator/adapters/input_router.py:
    e: _gnome_ready,resolve_adapter_mode,type_text
    _gnome_ready()
    resolve_adapter_mode(scheme;context)
    type_text(payload;context)
  agents/operators/desktop_operator/adapters/pcwin_mock.py:
    e: _task_context,focus,click
    _task_context(context)
    focus(payload;context)
    click(payload;context)
  agents/operators/desktop_operator/adapters/pcwin_router.py:
    e: _uia_ready,resolve_adapter_mode,_dispatch,focus,click
    _uia_ready()
    resolve_adapter_mode(scheme;context)
    _dispatch(operation;payload;context)
    focus(payload;context)
    click(payload;context)
  agents/operators/desktop_operator/adapters/pcwin_uia.py:
    e: _task_context,uia_available,_session,_focused_window,focus,click
    _task_context(context)
    uia_available()
    _session(context)
    _focused_window(context)
    focus(payload;context)
    click(payload;context)
  agents/operators/desktop_operator/adapters/pcwin_uri.py:
    e: _pcwin_segments,parse_pcwin_uri,window_id_from_payload,automation_id_from_payload
    _pcwin_segments(uri)
    parse_pcwin_uri(uri)
    window_id_from_payload(payload)
    automation_id_from_payload(payload)
  agents/operators/desktop_operator/adapters/screen_gnome.py:
    e: gnome_available,_task_context,observe,_desktop_env,_capture_screenshot,_list_windows
    gnome_available()
    _task_context(context)
    observe(payload;context)
    _desktop_env()
    _capture_screenshot(target)
    _list_windows()
  agents/operators/desktop_operator/adapters/screen_mock.py:
    e: observe
    observe(payload;context)
  agents/operators/desktop_operator/adapters/screen_router.py:
    e: _gnome_ready,resolve_adapter_mode,observe
    _gnome_ready()
    resolve_adapter_mode(scheme;context)
    observe(payload;context)
  agents/operators/desktop_operator/main.py:
  agents/operators/device_robot_operator/__init__.py:
  agents/operators/device_robot_operator/adapters/__init__.py:
  agents/operators/device_robot_operator/adapters/physical_mock.py:
    e: _path_parts,_target_id,robot_state,robot_move,robot_stop,robot_mission_start,device_status,device_read,device_write
    _path_parts(target_uri)
    _target_id(payload;fallback)
    robot_state(payload;context)
    robot_move(payload;context)
    robot_stop(payload;context)
    robot_mission_start(payload;context)
    device_status(payload;context)
    device_read(payload;context)
    device_write(payload;context)
  agents/operators/device_robot_operator/main.py:
  agents/operators/operator_runtime.py:
    e: operator_package_root,repo_root_from_operator,create_operator_app
    operator_package_root(module_file)
    repo_root_from_operator(module_file)
    create_operator_app(module_file)
  agents/system/__init__.py:
  agents/system/hypervisor_dashboard/__init__.py:
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/__init__.py:
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/agent_card.py:
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py:
    e: _header_lines,_identity_lines,_planned_lines,_next_step_lines,_format_action_block,format_ask_markdown,_uri_result_status_label,_uri_result_header_lines,_diagnosis_detail_lines,_workflow_plan_lines,_uri_result_body_lines,_envelope_json_block,format_uri_result_markdown,format_uri_result_summary,_next_step_hint,_display_planned,_runtime_result_lines,_first_dict,_status_lines,_action_lines,_incident_lines,_log_lines,_log_entry_preview_lines,_shorten_log_message
    _header_lines(data)
    _identity_lines(data)
    _planned_lines(data)
    _next_step_lines(data)
    _format_action_block(index;action)
    format_ask_markdown(data)
    _uri_result_status_label(result)
    _uri_result_header_lines(result)
    _diagnosis_detail_lines(result)
    _workflow_plan_lines(body)
    _uri_result_body_lines(body)
    _envelope_json_block(result)
    format_uri_result_markdown(result)
    format_uri_result_summary(result)
    _next_step_hint(body)
    _display_planned(planned;subtype)
    _runtime_result_lines(data)
    _first_dict()
    _status_lines(inspection;payload)
    _action_lines(data)
    _incident_lines(inspection;payload)
    _log_lines(inspection;payload)
    _log_entry_preview_lines(data)
    _shorten_log_message(message)
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py:
    e: _parse_ts,_extract_agent_id,_extract_incident_id,_extract_summary,_build_incident_event,_incident_events,_monitor_events,_derive_service_status,_health_summary,_agent_health_event,_agent_health_events,_should_include_log_event,_agent_id_from_log_subject,_log_event_from_payload,_recent_jsonl_lines,_events_from_jsonl_path,_log_jsonl_events,collect_system_events,filter_events_since
    _parse_ts(value)
    _extract_agent_id(metadata;path)
    _extract_incident_id(metadata;path)
    _extract_summary(symptoms)
    _build_incident_event(path;root;payload)
    _incident_events(root)
    _monitor_events(root)
    _derive_service_status(inspection;health_ok)
    _health_summary(service_status;incidents)
    _agent_health_event(root;deployment)
    _agent_health_events(root)
    _should_include_log_event(payload)
    _agent_id_from_log_subject(subject)
    _log_event_from_payload(payload)
    _recent_jsonl_lines(path)
    _events_from_jsonl_path(path)
    _log_jsonl_events(root)
    collect_system_events()
    filter_events_since(events;since)
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/main.py:
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/models.py:
    e: UriAction,ProcessViewModel,ViewEnvelope
    UriAction: to_dict(0)
    ProcessViewModel: to_dict(0)
    ViewEnvelope: to_dict(0)
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/monitor_webhook.py:
    e: _safe_slug,_event_name,_summary,_monitor_path,_write_log_event,write_monitor_webhook
    _safe_slug(value;default)
    _event_name(payload)
    _summary(payload;event)
    _monitor_path(root;source)
    _write_log_event(root)
    write_monitor_webhook(payload)
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/paths.py:
    e: repo_www_dir
    repo_www_dir()
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/plan_runner.py:
    e: agent_id_from_uri,_execute_uri,_attempt_auto_repair,run_planned_uris,format_plan_run_markdown,PlanRunOptions
    PlanRunOptions:
    agent_id_from_uri(uri)
    _execute_uri(uri)
    _attempt_auto_repair(agent_id)
    run_planned_uris(options)
    format_plan_run_markdown(results)
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/policy.py:
    e: decision_for_uri,preview_action,ApprovalDecision
    ApprovalDecision:
    decision_for_uri(uri)
    preview_action(uri)
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/presentation.py:
    e: _uri_path_parts,source_view_uri,resolve_html_presentation,resolve_markdown_presentation
    _uri_path_parts(uri)
    source_view_uri(presentation_uri)
    resolve_html_presentation(presentation_uri)
    resolve_markdown_presentation(presentation_uri)
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py:
    e: root,chat_page_redirect,health,capabilities,well_known_agent_json,well_known_agent_card_json,ui_root,ui_agents,ui_agent_detail,api_process_view,api_ask,api_uri_preview,api_uri_explain,api_uri_call,api_plan_run,_speak_plan_summary,api_voice_transcribe,api_voice_speak,api_agents,api_events,api_monitor_webhook,api_events_stream,PlanRunRequest,VoiceSpeakRequest,VoiceTranscribeRequest,UriCallRequest,AskRequest
    PlanRunRequest:
    VoiceSpeakRequest:
    VoiceTranscribeRequest:
    UriCallRequest:
    AskRequest:
    root()
    chat_page_redirect()
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    ui_root()
    ui_agents(request)
    ui_agent_detail(request;agent_id)
    api_process_view(agent_id)
    api_ask(body)
    api_uri_preview(body)
    api_uri_explain(body)
    api_uri_call(body)
    api_plan_run(body)
    _speak_plan_summary(payload)
    api_voice_transcribe(body)
    api_voice_speak(body)
    api_agents()
    api_events(limit;since)
    api_monitor_webhook(request)
    api_events_stream(limit;interval_s)
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py:
    e: _repo_root,uri_implies_dry_run,list_agent_deployments,resolve_view_uri,_is_presentation_request,_html_request,_markdown_request,_is_touri_run_request,_touri_run_request,_is_http_request,_infer_operator_operation,_is_operator_request,explain_system_uri,_operator_request,_is_chat_request,_chat_request,_is_nl_request,_nl_request,_http_request,_presentation_request,_select_dashboard_uri_handler,call_system_uri,_SystemUriRequest
    _SystemUriRequest:
    _repo_root(root)
    uri_implies_dry_run(uri)
    list_agent_deployments()
    resolve_view_uri(view_uri)
    _is_presentation_request(request)
    _html_request(request)
    _markdown_request(request)
    _is_touri_run_request(request)
    _touri_run_request(request)
    _is_http_request(request)
    _infer_operator_operation(parts)
    _is_operator_request(request)
    explain_system_uri(uri)
    _operator_request(request)
    _is_chat_request(request)
    _chat_request(request)
    _is_nl_request(request)
    _nl_request(request)
    _http_request(request)
    _presentation_request(request)
    _select_dashboard_uri_handler(request)
    call_system_uri(uri)
  agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/view_builder.py:
    e: _process_model_from_data,build_process_view,render_process_html,_dashboard_view_renderer,register_dashboard_view_renderer
    _process_model_from_data(data)
    build_process_view(agent_id)
    render_process_html(model)
    _dashboard_view_renderer(view_uri;data)
    register_dashboard_view_renderer()
  agents/system/hypervisor_dashboard/main.py:
  domains/__init__.py:
  domains/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html/__init__.py:
  domains/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html/handlers/__init__.py:
  domains/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html/handlers/run.py:
    e: handler
    handler(payload)
  domains/weather_map/__init__.py:
  domains/weather_map/handlers/__init__.py:
  domains/weather_map/handlers/generate_weather_map.py:
    e: handler
    handler(payload)
  domains/weather_map/planner.py:
    e: is_weather_prompt,deterministic_weather_plan
    is_weather_prompt(prompt)
    deterministic_weather_plan(prompt)
  examples/21_touri_voice/touri_examples_voice/__init__.py:
  examples/21_touri_voice/touri_examples_voice/stt.py:
  examples/21_touri_voice/touri_examples_voice/tts.py:
  examples/21_touri_voice/touri_examples_voice/voice_command.py:
  packages/resource-agent-factory/agents/generated/orders_agent/__init__.py:
  packages/resource-agent-factory/agents/generated/orders_agent/agent_card.py:
  packages/resource-agent-factory/agents/generated/orders_agent/main.py:
  packages/resource-agent-factory/agents/generated/orders_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_read_order,skill_read_order_events,_uri_allowed,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_read_order(order_id)
    skill_read_order_events(order_id)
    _uri_allowed(uri;templates)
  packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  packages/resource-agent-factory/agents/generated/user_agent/__init__.py:
  packages/resource-agent-factory/agents/generated/user_agent/agent_card.py:
  packages/resource-agent-factory/agents/generated/user_agent/main.py:
  packages/resource-agent-factory/agents/generated/user_agent/routes.py:
    e: health,capabilities,well_known_agent_json,well_known_agent_card_json,read_resource,dispatch_command,skill_read_user,skill_read_user_roles,skill_create_user,skill_assign_user_role,_uri_allowed,CommandRequest
    CommandRequest:
    health()
    capabilities()
    well_known_agent_json()
    well_known_agent_card_json()
    read_resource(uri)
    dispatch_command(request)
    skill_read_user(user_id)
    skill_read_user_roles(user_id)
    skill_create_user(payload)
    skill_assign_user_role(payload)
    _uri_allowed(uri;templates)
  packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  packages/resource-agent-factory/generator/__init__.py:
  packages/resource-agent-factory/generator/agent_generator.py:
    e: _default_port_for_agent,render_template,generate_agent,expand_paths,main
    _default_port_for_agent(spec;repo)
    render_template(env;template_name;dest;context)
    generate_agent(spec_path)
    expand_paths(patterns)
    main(argv)
  packages/resource-agent-factory/generator/hashutil.py:
    e: file_sha256
    file_sha256(path)
  packages/resource-agent-factory/generator/header.py:
    e: contract_source_ref,python_file_header,dockerfile_header,markdown_generated_banner,generated_marker_payload
    contract_source_ref(spec_path;root)
    python_file_header(source_ref;contract_hash)
    dockerfile_header(source_ref;contract_hash)
    markdown_generated_banner(source_ref;contract_hash)
    generated_marker_payload(source_ref;contract_hash)
  packages/resource-agent-factory/generator/model.py:
    e: load_agent_spec,spec_to_plain_dict,Capability,AgentSpec
    Capability:
    AgentSpec: output_dir_name(0)
    load_agent_spec(path)
    spec_to_plain_dict(spec;contract_hash)
  packages/resource-agent-factory/generator/paths.py:
    e: project_root
    project_root()
  packages/resource-agent-factory/generator/validate.py:
    e: validate_agent,iter_agent_specs,main
    validate_agent(path)
    iter_agent_specs(root)
    main(argv)
  packages/resource-agent-factory/generator/verify.py:
    e: verify_generated_agent,_agent_dirs,verify_generated,main
    verify_generated_agent(agent_dir)
    _agent_dirs(root)
    verify_generated(root)
    main(argv)
  packages/resource-agent-hypervisor/hypervisor/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/_version.py:
  packages/resource-agent-hypervisor/hypervisor/agent_describe.py:
    e: describe_agent,_deployment_health_label,_safe_run_plan,_find_contract_path,_find_domain_pack,_package_relative_path,_list_package_files,_agent_kind,_capability_backing_note,_skill_invoke_example,_file_role,_extract_markpact_blocks,_read_yaml,_rel,_render_markdown,AgentDescribeReport
    AgentDescribeReport: write(1)
    describe_agent(selector)
    _deployment_health_label(deployment_item)
    _safe_run_plan(deployment;repo)
    _find_contract_path(repo;agent_name;deployment)
    _find_domain_pack(repo;contract_path;deployment;contract)
    _package_relative_path(deployment;repo)
    _list_package_files(package_dir)
    _agent_kind(deployment)
    _capability_backing_note()
    _skill_invoke_example(cap)
    _file_role(rel)
    _extract_markpact_blocks(readme_path)
    _read_yaml(path)
    _rel(repo;path)
    _render_markdown()
  packages/resource-agent-hypervisor/hypervisor/artifacts/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py:
    e: validate_config_dict,validate_runtime_environments_dict,_validate_path,check_artifacts,_read_structured_mapping,_artifact_lifecycle_result,_collect_lifecycle_results,_lifecycle_summary,_lifecycle_samples,check_lifecycle_coverage,check_schemas,ArtifactCheckResult,ArtifactLifecycleResult
    ArtifactCheckResult:
    ArtifactLifecycleResult:
    validate_config_dict(data;repo_root)
    validate_runtime_environments_dict(data;repo_root)
    _validate_path(path;repo_root;schema;validator)
    check_artifacts(repo_root)
    _read_structured_mapping(path)
    _artifact_lifecycle_result(path;repo_root;category)
    _collect_lifecycle_results(repo_root)
    _lifecycle_summary(results)
    _lifecycle_samples(noncanonical)
    check_lifecycle_coverage(repo_root)
    check_schemas(repo_root)
  packages/resource-agent-hypervisor/hypervisor/cli.py:
    e: _load_json_payload,call,explain,scan,resolve,status,config_cmd,deployments_list,run_agent_cmd,stop_agent_cmd,restart_agent_cmd,agent_status_cmd,inspect_agent_cmd,describe_agent_cmd,supervise_cmd,repair_diagnose_cmd,repair_apply_cmd,repair_heal_cmd,repair_learn_cmd,artifacts_check_cmd,artifacts_schemas_cmd,artifacts_lifecycle_cmd,ticket_import_cmd,evolution_propose_from_ticket_cmd,evolution_propose_from_incident_cmd,logs_cmd,deploy_agent_cmd,verify_agent_cmd,docker_cmd,replay_failure_cmd,main
    _load_json_payload(payload;payload_file)
    call(uri;payload;payload_file;approve;environment)
    explain(uri;payload;payload_file)
    scan(uri)
    resolve(uri)
    status()
    config_cmd(path)
    deployments_list()
    run_agent_cmd(selector;port;host;reload;detach;dry_run;if_running;wait_healthy;approve;supervise_repair)
    stop_agent_cmd(selector)
    restart_agent_cmd(selector;port;host;reload;detach)
    agent_status_cmd(selector;no_health)
    inspect_agent_cmd(selector;timeout;log_limit)
    describe_agent_cmd(selector;output;json_out)
    supervise_cmd(selector;repair;watch;interval;count;repair_backoff_ticks;max_attempts;timeout;log_limit;learn)
    repair_diagnose_cmd(selector;timeout;log_limit)
    repair_apply_cmd(selector;safe;approve;playbook)
    repair_heal_cmd(selector;repair;learn;max_attempts;timeout;log_limit)
    repair_learn_cmd(incident_path;sandbox)
    artifacts_check_cmd(path)
    artifacts_schemas_cmd()
    artifacts_lifecycle_cmd(strict;sample_limit)
    ticket_import_cmd(strategy;sprint)
    evolution_propose_from_ticket_cmd(ticket_path)
    evolution_propose_from_incident_cmd(incident_path)
    logs_cmd(selector;limit)
    deploy_agent_cmd(selector;apply)
    verify_agent_cmd(selector;no_health)
    docker_cmd(uri;dry_run)
    replay_failure_cmd(source;create_test;json_out)
    main(argv)
  packages/resource-agent-hypervisor/hypervisor/cli_commands.py:
    e: echo_json,run_local_agent,deploy_agent,verify_agent,read_agent_logs,call_docker
    echo_json(payload)
    run_local_agent(selector)
    deploy_agent(selector)
    verify_agent(selector)
    read_agent_logs(selector)
    call_docker(uri)
  packages/resource-agent-hypervisor/hypervisor/compatibility/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/compatibility/checker.py:
    e: _load_policy,classify_registry_change
    _load_policy(root)
    classify_registry_change(old_root;new_root)
  packages/resource-agent-hypervisor/hypervisor/config/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/config/config_checks.py:
    e: validate_hypervisor,validate_llm,validate_uri3,validate_path_sections
    validate_hypervisor(cfg)
    validate_llm(cfg)
    validate_uri3(cfg)
    validate_path_sections(cfg)
  packages/resource-agent-hypervisor/hypervisor/config/defaults.py:
    e: load_yaml_file,embedded_defaults_raw,apply_builtin_defaults,get_default_config
    load_yaml_file(path)
    embedded_defaults_raw()
    apply_builtin_defaults(cfg)
    get_default_config()
  packages/resource-agent-hypervisor/hypervisor/config/env.py:
    e: _parse_bool,apply_legacy_env_overrides,apply_structured_env_overrides,apply_env_overrides
    _parse_bool(value)
    apply_legacy_env_overrides(cfg)
    apply_structured_env_overrides(cfg)
    apply_env_overrides(cfg)
  packages/resource-agent-hypervisor/hypervisor/config/loader.py:
    e: config_search_paths,resolve_config_path,load_config,get_config,load_hypervisor_config
    config_search_paths()
    resolve_config_path()
    load_config(path)
    get_config()
    load_hypervisor_config(path)
  packages/resource-agent-hypervisor/hypervisor/config/models.py:
    e: LLMConfig,Uri3Config,RegistryConfig,DomainPackConfig,AgentsConfig,DeploymentConfig,HypervisorSettings,HypervisorConfig
    LLMConfig: from_dict(2)
    Uri3Config: from_dict(2)
    RegistryConfig: from_dict(2)
    DomainPackConfig: from_dict(2)
    AgentsConfig: from_dict(2)
    DeploymentConfig: from_dict(2)
    HypervisorSettings: from_dict(2)
    HypervisorConfig: from_dict(2),to_dict(0)
  packages/resource-agent-hypervisor/hypervisor/config/uri_config.py:
    e: _repo_config_dir,apply_uri_yaml_configs
    _repo_config_dir(root)
    apply_uri_yaml_configs(cfg)
  packages/resource-agent-hypervisor/hypervisor/config/validators.py:
    e: merge_config,validate_config
    merge_config(base;overlay)
    validate_config(cfg)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cli.py:
    e: _parse_args,main
    _parse_args(argv)
    main(argv)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py:
    e: run_schema_command,run_cross_command,run_build_command,run_export_md_command,run_check_command
    run_schema_command(root)
    run_cross_command(root)
    run_build_command(root)
    run_export_md_command(root)
    run_check_command(root)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/capabilities.py:
    e: _validate_single_capability,validate_capability_cross_refs
    _validate_single_capability(capability)
    validate_capability_cross_refs(registry)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/proto_index.py:
    e: load_proto_text,schema_exists
    load_proto_text(root)
    schema_exists(proto_text;schema_ref)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/resources.py:
    e: validate_resource_cross_refs
    validate_resource_cross_refs(registry)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py:
    e: validate_cross_references,validate_root
    validate_cross_references(registry)
    validate_root(root)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py:
    e: _read_yaml,load_contract_registry
    _read_yaml(path)
    load_contract_registry(root)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/merge_helpers.py:
    e: merge_proto_contract,merge_resources_contract,merge_views_contract
    merge_proto_contract(contracts_dir;domain_id;proto_text)
    merge_resources_contract(contracts_dir;resources)
    merge_views_contract(contracts_dir;views)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/merger.py:
    e: merge_main_contracts
    merge_main_contracts(domain_id;resources;views;proto_text)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/models.py:
    e: ResourceContract,ViewContract,CapabilityContract,ContractRegistry
    ResourceContract:
    ViewContract:
    CapabilityContract:
    ContractRegistry: resource_by_uri(1),view_by_name(1),capability_by_name(2)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py:
    e: _hash_file,_contract_hash,build_registry_manifest,write_registry_manifest
    _hash_file(path)
    _contract_hash(root)
    build_registry_manifest(root)
    write_registry_manifest(root;output)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/capabilities.py:
    e: _resolves_as_external_uri,validate_resource_read_capability,validate_command_capability,validate_capabilities
    _resolves_as_external_uri(uri)
    validate_resource_read_capability(registry;cap)
    validate_command_capability(cap)
    validate_capabilities(registry)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/resources.py:
    e: validate_resources,validate_views
    validate_resources(registry)
    validate_views(registry)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_exporter.py:
    e: export_json,export_markdown
    export_json(root;output)
    export_markdown(root;output)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py:
    e: _read_yaml,_read_json,validate_file,validate_contract_files,SchemaValidationResult
    SchemaValidationResult:
    _read_yaml(path)
    _read_json(path)
    validate_file(data_path;schema_path)
    validate_contract_files(root)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py:
    e: _parse_bool,_parse_kinds,_schema_refs_from_contract,_find_proto_files,_artifact_entry,_read_yaml,_slug_to_snake,_contract_uri,_agent_contract_uri,resolve_contract_path,_format_schema_results,_validation_payload,fetch_agent_contract,validate_agent_contract,validate_contract_registry_uri,fetch_registry_manifest,generate_agent_contract,fetch_agent_artifacts,handle_contract_uri
    _parse_bool(value)
    _parse_kinds(value)
    _schema_refs_from_contract(contract)
    _find_proto_files(root;schema_refs)
    _artifact_entry()
    _read_yaml(path)
    _slug_to_snake(value)
    _contract_uri(path)
    _agent_contract_uri(agent_name)
    resolve_contract_path(name;root)
    _format_schema_results(results)
    _validation_payload()
    fetch_agent_contract(name;root)
    validate_agent_contract(name;root)
    validate_contract_registry_uri(root)
    fetch_registry_manifest(root)
    generate_agent_contract(name;root)
    fetch_agent_artifacts(name;root)
    handle_contract_uri(uri;root)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/validate.py:
    e: validate_registry
    validate_registry(registry)
  packages/resource-agent-hypervisor/hypervisor/core.py:
    e: Hypervisor
    Hypervisor: __post_init__(0),from_config(2),start(0),stop(0),register_agent(1),status(0),__repr__(0)  # Main Hypervisor controller.
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/aliases.py:
    e: _read_yaml,load_deployment_selector_aliases
    _read_yaml(path)
    load_deployment_selector_aliases(root)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/docker_runner.py:
    e: docker_uri_for_deployment,build_docker_deploy_plan,build_docker_control_plan,apply_docker_deploy,stop_docker_deployment,verify_docker_deployment
    docker_uri_for_deployment(deployment)
    build_docker_deploy_plan(deployment)
    build_docker_control_plan(deployment;action)
    apply_docker_deploy(deployment)
    stop_docker_deployment(deployment)
    verify_docker_deployment(deployment)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/env.py:
    e: build_deployment_env_map,resolve_deployment_env,default_log_uri
    build_deployment_env_map(deployment_id;agent_ref;deployment_env)
    resolve_deployment_env(deployment_id;agent_ref;deployment_env)
    default_log_uri(deployment_id;agent_ref)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_config.py:
    e: repo_config_dir,load_deployments_uri_config,load_runtime_uri_config
    repo_config_dir(root)
    load_deployments_uri_config(root)
    load_runtime_uri_config(root)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_merge.py:
    e: merge_runtime_defaults,materialize_env_values
    merge_runtime_defaults(merged)
    materialize_env_values(merged)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py:
    e: port_from_http_uri,port_from_command,health_uri_for_port,_runtime_command,_network_effective_port,resolve_effective_health_uri,command_port_from_runtime
    port_from_http_uri(uri)
    port_from_command(command)
    health_uri_for_port(port)
    _runtime_command(state;plan)
    _network_effective_port(state)
    resolve_effective_health_uri(state;plan)
    command_port_from_runtime(state;plan)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py:
    e: _port_from_http_uri,_port_conflict_incident,_foreign_service_incident,_runtime_incidents,_health_incidents,classify_incidents,blocking_incidents
    _port_from_http_uri(uri)
    _port_conflict_incident()
    _foreign_service_incident()
    _runtime_incidents()
    _health_incidents()
    classify_incidents()
    blocking_incidents(incidents)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/pipeline.py:
    e: _runtime_command_port,_derive_effective_card_uri,gather_inspection_context,_merge_log_results,probe_agent_endpoints,build_inspection_report,InspectionContext
    InspectionContext:
    _runtime_command_port(state;plan)
    _derive_effective_card_uri(effective_health_uri;state;run_plan;deployment)
    gather_inspection_context(deployment)
    _merge_log_results(primary;secondary)
    probe_agent_endpoints(context)
    build_inspection_report(context)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/probe.py:
    e: _probe_payload_ok,_host_probe_uri,_probe_response,probe_http,log_uri_with_filters,read_error_logs
    _probe_payload_ok(payload)
    _host_probe_uri(uri)
    _probe_response(uri;response)
    probe_http(uri)
    log_uri_with_filters(log_uri)
    read_error_logs(log_uri)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/readiness.py:
    e: readiness_summary,recommended_action_from_incidents,build_agent_readiness_report
    readiness_summary()
    recommended_action_from_incidents(incident_codes)
    build_agent_readiness_report()
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py:
    e: _lifecycle_payload,_repo_root,_validate_run_agent_options,_finalize_run_plan,_load_active_runtime_state,_sync_reused_runtime_state,_resolve_running_process,_run_non_local_target,_start_local_process,_is_process_start_failure,_resolve_initial_run_plan,_execute_run_agent_plan,_emit_run_agent_result,run_agent,restart_agent
    _lifecycle_payload(payload)
    _repo_root(root)
    _validate_run_agent_options()
    _finalize_run_plan(plan_dict)
    _load_active_runtime_state(selector;deployment)
    _sync_reused_runtime_state(deployment_id;existing;plan)
    _resolve_running_process(selector;deployment;existing;plan)
    _run_non_local_target(deployment)
    _start_local_process(deployment;plan)
    _is_process_start_failure(payload)
    _resolve_initial_run_plan(selector;deployment)
    _execute_run_agent_plan(deployment;plan;finalize)
    _emit_run_agent_result(deployment;result)
    run_agent(selector)
    restart_agent(selector)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle_status.py:
    e: _lifecycle_payload,_repo_root,agent_status,agent_logs_uri
    _lifecycle_payload(payload)
    _repo_root(root)
    agent_status(selector)
    agent_logs_uri(selector)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py:
    e: default_registry_path,_read_yaml,_port_from_uri,_parse_declared,_parse_runtime,_parse_deployment,load_deployment_registry
    default_registry_path(root)
    _read_yaml(path)
    _port_from_uri(uri)
    _parse_declared(item)
    _parse_runtime(item)
    _parse_deployment(item)
    load_deployment_registry(root)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py:
    e: _local_endpoint,_local_health_uri,_local_card_uri,local_target_to_relative_path,repo_python_executable,local_target_to_module,build_local_run_plan
    _local_endpoint(path)
    _local_health_uri(deployment)
    _local_card_uri(deployment)
    local_target_to_relative_path(target_uri)
    repo_python_executable(repo)
    local_target_to_module(target_uri)
    build_local_run_plan(deployment)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_verify.py:
    e: verify_local_deployment
    verify_local_deployment(deployment)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py:
    e: _port_from_uri,DeploymentDeclared,DeploymentRuntimeView,AgentDeployment,DeploymentRegistry
    DeploymentDeclared: to_dict(0)
    DeploymentRuntimeView: to_dict(0)
    AgentDeployment: declared_health_uri(0),effective_health_uri(0),to_dict(0)
    DeploymentRegistry: by_id(1),by_agent_ref(1)
    _port_from_uri(uri)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_conflict.py:
    e: classify_port_listeners,port_conflict_detail
    classify_port_listeners(port)
    port_conflict_detail()
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_utils.py:
    e: is_port_free,find_free_port,expected_agent_id,port_from_http_uri,health_matches_agent,foreign_service_detail
    is_port_free(port)
    find_free_port(preferred)
    expected_agent_id(agent_ref)
    port_from_http_uri(uri)
    health_matches_agent(probe)
    foreign_service_detail(probe)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/process.py:
    e: _safe_log_stem,process_log_path,process_log_uri,start_process
    _safe_log_stem(value)
    process_log_path(plan)
    process_log_uri(path)
    start_process(plan)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/process_discovery.py:
    e: _iter_proc_pids,_listening_socket_inodes,pids_listening_on_port,command_line,command_matches_plan,terminate_pid,_pid_alive
    _iter_proc_pids()
    _listening_socket_inodes(port)
    pids_listening_on_port(port)
    command_line(pid)
    command_matches_plan(pid;plan)
    terminate_pid(pid)
    _pid_alive(pid)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/registry_sync.py:
    e: card_uri_for_port,deployment_with_port,sync_deployment_port,sync_deployment_health_uri
    card_uri_for_port(port)
    deployment_with_port(deployment;port)
    sync_deployment_port(deployment_id;port)
    sync_deployment_health_uri(deployment_id;health_uri)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/remote_runner.py:
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py:
    e: load_or_clear_runtime_state,build_agent_run_plan,rebind_plan_port_if_busy,resolve_running_mode,reuse_existing_process_plan,sync_runtime_health_uri,_workspace_pythonpath,prepare_runtime_env,verify_process_alive,write_runtime_state_after_start,process_start_failure_payload,validate_run_dependencies,persist_rebound_port,attach_started_process
    load_or_clear_runtime_state(deployment_id;repo)
    build_agent_run_plan(deployment)
    rebind_plan_port_if_busy(deployment;plan)
    resolve_running_mode()
    reuse_existing_process_plan(existing;plan)
    sync_runtime_health_uri(state;health_uri)
    _workspace_pythonpath(repo)
    prepare_runtime_env(deployment)
    verify_process_alive(process_pid)
    write_runtime_state_after_start(deployment;plan)
    process_start_failure_payload(deployment_id)
    validate_run_dependencies(plan)
    persist_rebound_port(deployment;plan)
    attach_started_process(plan;process_pid)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_plans.py:
    e: build_run_plan
    build_run_plan(deployment)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/runner.py:
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py:
    e: runtime_root,state_path,_port_from_http_uri,_port_from_command,_process_status,_health_uri,_pid,_command,state_health_uri,_process_log_path,_process_log_uri,_build_uri_block,_build_process_block,_build_status_block,_build_network_block,_legacy_runtime_state,_apply_flat_accessors,normalize_runtime_state,load_runtime_state,save_runtime_state,clear_runtime_state,is_process_alive,runtime_status,now_iso
    runtime_root(root)
    state_path(deployment_id;root)
    _port_from_http_uri(uri)
    _port_from_command(command)
    _process_status(raw)
    _health_uri(raw)
    _pid(raw)
    _command(raw)
    state_health_uri(raw)
    _process_log_path(raw)
    _process_log_uri(raw)
    _build_uri_block(raw;dep_id)
    _build_process_block(raw;command)
    _build_status_block(raw)
    _build_network_block(command;health_uri;raw)
    _legacy_runtime_state(raw)
    _apply_flat_accessors(body)
    normalize_runtime_state(raw)
    load_runtime_state(deployment_id;root)
    save_runtime_state(deployment_id;state;root)
    clear_runtime_state(deployment_id;root)
    is_process_alive(pid)
    runtime_status(deployment_id;root)
    now_iso()
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/selector.py:
    e: parse_hypervisor_uri,_prefer_local_deployment,resolve_deployment
    parse_hypervisor_uri(uri)
    _prefer_local_deployment(matches)
    resolve_deployment(selector)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_deploy.py:
    e: build_ssh_deploy_plan,apply_ssh_deploy_plan
    build_ssh_deploy_plan(deployment)
    apply_ssh_deploy_plan(plan)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_helpers.py:
    e: generated_agent_dir,remote_module_for
    generated_agent_dir(agent_ref;root)
    remote_module_for(deployment)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_run.py:
    e: build_ssh_run_plan,apply_ssh_run_plan
    build_ssh_run_plan(deployment)
    apply_ssh_run_plan(plan)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_verify.py:
    e: verify_remote_deployment
    verify_remote_deployment(deployment)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py:
    e: infer_port,deployment_id_for_agent,infer_health_uri,infer_card_uri,deployment_from_uri_tree,_merge_uri_tree_deployment,sync_from_uri_tree,resolve_status,list_deployments,get_deployment_for_agent,registry_summary
    infer_port(deployment)
    deployment_id_for_agent(agent_id)
    infer_health_uri(target_uri;agent_id)
    infer_card_uri(agent;agent_id)
    deployment_from_uri_tree(tree)
    _merge_uri_tree_deployment(existing;incoming)
    sync_from_uri_tree(tree)
    resolve_status(deployment)
    list_deployments(registry)
    get_deployment_for_agent(agent_ref)
    registry_summary(registry)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py:
    e: _lifecycle_payload,_repo_root,_safe_stop_plan,_state_health_uri,_candidate_stop_ports,_terminate_matching_agent_processes,_emit_stop_result,_stop_docker_deployment,_stop_without_runtime_state,_stop_with_runtime_state,stop_agent
    _lifecycle_payload(payload)
    _repo_root(root)
    _safe_stop_plan(deployment)
    _state_health_uri(state)
    _candidate_stop_ports(state;plan)
    _terminate_matching_agent_processes(state;plan)
    _emit_stop_result(deployment;result_core)
    _stop_docker_deployment(deployment)
    _stop_without_runtime_state(deployment;plan)
    _stop_with_runtime_state(deployment;state;plan)
    stop_agent(selector)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py:
    e: _lifecycle_payload,_repo_root,inspect_agent,_runtime_command_port,_auto_repair_plan,_apply_repair,ensure_agent_healthy,supervise_agent
    _lifecycle_payload(payload)
    _repo_root(root)
    inspect_agent(selector)
    _runtime_command_port(inspection)
    _auto_repair_plan(inspection)
    _apply_repair(selector)
    ensure_agent_healthy(selector)
    supervise_agent(selector)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py:
    e: _repo_root,_safe_selector,watch_state_path,load_watch_state,save_watch_state,_inspection_from_result,_incident_codes,_service_status,_health_signature,_actions_from_result,_write_watch_log,_repair_allowed,_run_supervision,_learn_allowed_for_state,_emit_tick_events,_next_state,supervise_watch
    _repo_root(root)
    _safe_selector(selector)
    watch_state_path(selector;root)
    load_watch_state(selector;root)
    save_watch_state(selector;state;root)
    _inspection_from_result(result)
    _incident_codes(inspection)
    _service_status(result)
    _health_signature(result)
    _actions_from_result(result)
    _write_watch_log(root)
    _repair_allowed(state)
    _run_supervision(selector)
    _learn_allowed_for_state(state)
    _emit_tick_events(repo)
    _next_state(state)
    supervise_watch(selector)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py:
    e: save_deployment_registry,upsert_deployment,remove_deployment,write_deployment_registry
    save_deployment_registry(registry)
    upsert_deployment(registry;deployment)
    remove_deployment(registry;deployment_id)
    write_deployment_registry(deployments)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/agent_contract.py:
    e: generate_agent_contract
    generate_agent_contract(model)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/commands.py:
    e: generate_commands
    generate_commands(model)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/handlers.py:
    e: generate_handlers
    generate_handlers(model)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/proto.py:
    e: generate_proto
    generate_proto(model)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/renderers.py:
    e: generate_renderers
    generate_renderers(model)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/resources.py:
    e: generate_resources
    generate_resources(model)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/views.py:
    e: generate_views
    generate_views(resources)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py:
    e: generate_domain_pack_from_tree,generate_domain_pack
    generate_domain_pack_from_tree(tree;out_dir)
    generate_domain_pack(uri_tree_path;domain_dir)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/model.py:
    e: DomainModel
    DomainModel: from_uri_tree(3)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/pack_writer.py:
    e: write_domain_pack
    write_domain_pack(model)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/parser.py:
    e: parse_uri_tree,derive_domain_model
    parse_uri_tree(uri_tree_path)
    derive_domain_model(tree;out_dir)
  packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py:
    e: package_name,generic_proto,weather_proto,weather_handler,generic_handler
    package_name(domain_id)
    generic_proto(domain_id)
    weather_proto()
    weather_handler()
    generic_handler()
  packages/resource-agent-hypervisor/hypervisor/domain_pack/writer.py:
    e: write_file
    write_file(path;content)
  packages/resource-agent-hypervisor/hypervisor/events.py:
    e: _repo_root,emit_operation_event,emit_result_event
    _repo_root(root)
    emit_operation_event(code;message)
    emit_result_event(operation;selector;result)
  packages/resource-agent-hypervisor/hypervisor/evolution/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/evolution/cli.py:
    e: main
    main(argv)
  packages/resource-agent-hypervisor/hypervisor/evolution/models.py:
    e: load_proposal,EvolutionProposal
    EvolutionProposal:
    load_proposal(path)
  packages/resource-agent-hypervisor/hypervisor/evolution/proposal_from_source.py:
    e: build_evolution_proposal,build_repair_proposal_from_incident,build_evolution_proposal_from_ticket
    build_evolution_proposal(source)
    build_repair_proposal_from_incident(incident)
    build_evolution_proposal_from_ticket(ticket)
  packages/resource-agent-hypervisor/hypervisor/evolution/validator.py:
    e: validate_proposal_dict,validate_proposal
    validate_proposal_dict(payload;repo_root)
    validate_proposal(proposal)
  packages/resource-agent-hypervisor/hypervisor/integrations/planfile/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/integrations/planfile/ticket_mapper.py:
    e: _ticket_uri,planfile_task_to_ticket,load_planfile_strategy,import_tickets_from_planfile,propose_from_ticket_path
    _ticket_uri(ticket_type;ticket_id)
    planfile_task_to_ticket(task)
    load_planfile_strategy(path)
    import_tickets_from_planfile(strategy_path)
    propose_from_ticket_path(ticket_path)
  packages/resource-agent-hypervisor/hypervisor/paths.py:
    e: _is_hypervisor_root,_walk_hypervisor_root,find_repo_root,repo_root,_looks_like_www,resolve_www_dir
    _is_hypervisor_root(path)
    _walk_hypervisor_root(start)
    find_repo_root(start)
    repo_root()
    _looks_like_www(path)
    resolve_www_dir(start)
  packages/resource-agent-hypervisor/hypervisor/policy_gate/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py:
    e: evaluate_change,GateDecision
    GateDecision:
    evaluate_change(change_report;approved)
  packages/resource-agent-hypervisor/hypervisor/repair/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/repair/classifier.py:
    e: _incident_text,_warning_text,_log_text,_collect_text,classify_inspection,ErrorFamily
    ErrorFamily:
    _incident_text(inspection)
    _warning_text(inspection)
    _log_text(log_payload)
    _collect_text(inspection;log_payload)
    classify_inspection(inspection)
  packages/resource-agent-hypervisor/hypervisor/repair/healer.py:
    e: run_uri_healer
    run_uri_healer(selector)
  packages/resource-agent-hypervisor/hypervisor/repair/incident.py:
    e: _incident_id,incident_uri,incident_storage_path,_symptom_from_item,_symptoms_from_inspection,_incident_uri_block,_incident_status_block,_incident_evidence,build_incident_from_inspection,write_incident,load_incident
    _incident_id()
    incident_uri(agent_id;incident_id)
    incident_storage_path(repo_root;agent_id;incident_id)
    _symptom_from_item(item)
    _symptoms_from_inspection(inspection)
    _incident_uri_block(agent_id;metadata_id;inspection)
    _incident_status_block(inspection;readiness;health)
    _incident_evidence(inspection)
    build_incident_from_inspection(inspection)
    write_incident(incident)
    load_incident(path)
  packages/resource-agent-hypervisor/hypervisor/repair/models.py:
    e: Symptom,IncidentArtifact
    Symptom: to_dict(0)
    IncidentArtifact: to_dict(0),self_uri(0)
  packages/resource-agent-hypervisor/hypervisor/repair/plan_builder.py:
    e: _plan_id,_ordered_unique,_inspection_codes,_prioritized_playbooks,build_repair_plan_from_diagnosis,build_repair_plan_from_inspection
    _plan_id(agent_id)
    _ordered_unique(items)
    _inspection_codes(inspection)
    _prioritized_playbooks(inspection;playbooks)
    build_repair_plan_from_diagnosis(diagnosis)
    build_repair_plan_from_inspection(inspection)
  packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py:
    e: _repo_root,_playbook_sync_health_uri,_playbook_restart_agent,_playbook_clear_stale_runtime,_playbook_rebind_port,_playbook_inspect,_playbook_requires_approval,_playbook_not_implemented,apply_playbook,apply_playbook_sequence
    _repo_root(root)
    _playbook_sync_health_uri(selector;repo)
    _playbook_restart_agent(selector;repo)
    _playbook_clear_stale_runtime(selector;repo)
    _playbook_rebind_port(selector;repo)
    _playbook_inspect(selector;repo)
    _playbook_requires_approval(playbook)
    _playbook_not_implemented(playbook)
    apply_playbook(playbook)
    apply_playbook_sequence(playbooks)
  packages/resource-agent-hypervisor/hypervisor/repair/policy.py:
    e: policy_level_for_playbook,playbook_requires_approval,is_playbook_allowed
    policy_level_for_playbook(playbook)
    playbook_requires_approval(playbook)
    is_playbook_allowed(playbook)
  packages/resource-agent-hypervisor/hypervisor/repair/proposal_builder.py:
    e: build_repair_proposal,link_proposal_to_incident
    build_repair_proposal(incident)
    link_proposal_to_incident(incident_path;proposal)
  packages/resource-agent-hypervisor/hypervisor/repair/registry.py:
    e: repair_cases_dir,list_repair_cases,load_repair_case,_case_matches_symptoms,find_matching_case
    repair_cases_dir(repo_root)
    list_repair_cases(repo_root)
    load_repair_case(path)
    _case_matches_symptoms(case_doc;readiness)
    find_matching_case(classification;inspection)
  packages/resource-agent-hypervisor/hypervisor/repair/sandbox.py:
    e: simulate_playbook,test_repair_plan_in_sandbox
    simulate_playbook(playbook)
    test_repair_plan_in_sandbox(plan)
  packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py:
    e: _envelope,_repo_root,_sync_registry_if_drifted,diagnose_agent,_repair_playbook_candidates,_execute_repair_playbooks,_healthy_repair_apply_body,repair_apply,supervise_with_repair,learn_from_incident
    _envelope(payload)
    _repo_root(root)
    _sync_registry_if_drifted(inspection)
    diagnose_agent(selector)
    _repair_playbook_candidates(diagnosis;classification)
    _execute_repair_playbooks(candidates)
    _healthy_repair_apply_body(selector;diagnosis;inspection)
    repair_apply(selector)
    supervise_with_repair(selector)
    learn_from_incident(incident_path)
  packages/resource-agent-hypervisor/hypervisor/repair/validator.py:
    e: validate_incident_dict,validate_repair_plan_dict,validate_evolution_proposal_dict,validate_runtime_state_dict,validate_ticket_dict,read_yaml
    validate_incident_dict(data;repo_root)
    validate_repair_plan_dict(data;repo_root)
    validate_evolution_proposal_dict(data;repo_root)
    validate_runtime_state_dict(data;repo_root)
    validate_ticket_dict(data;repo_root)
    read_yaml(path)
  packages/resource-agent-hypervisor/hypervisor/routing/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/routing/dispatcher.py:
    e: call_uri
    call_uri(input_uri;payload)
  packages/resource-agent-hypervisor/hypervisor/routing/explain.py:
    e: explain_semantic_route,explain_executable_uri
    explain_semantic_route(uri)
    explain_executable_uri(uri)
  packages/resource-agent-hypervisor/hypervisor/routing/models.py:
    e: _public_context,RoutePolicyDecision,HypervisorRouteResolution
    RoutePolicyDecision: to_dict(0)
    HypervisorRouteResolution: to_dict(0)
    _public_context(context)
  packages/resource-agent-hypervisor/hypervisor/routing/policy.py:
    e: policy_options,_semantic_requires_approval,evaluate_route_policy,evaluate_route_policy_decision,PolicyRequest,PolicyEvaluation
    PolicyRequest:
    PolicyEvaluation: reason(0),to_route_decision(0)
    policy_options(request)
    _semantic_requires_approval(uri)
    evaluate_route_policy(uri)
    evaluate_route_policy_decision(uri)
  packages/resource-agent-hypervisor/hypervisor/routing/registry_bridge.py:
    e: load_runtime_registry,resolve_operator_by_scheme,resolve_operator_deployment
    load_runtime_registry(root)
    resolve_operator_by_scheme(scheme)
    resolve_operator_deployment(deployment_id)
  packages/resource-agent-hypervisor/hypervisor/routing/resolver.py:
    e: resolve_hypervisor_route,_select_environment_and_adapter,_payload_session,_normalize_environment,_canonical_operator_scheme,_operator_base_url
    resolve_hypervisor_route(input_uri)
    _select_environment_and_adapter()
    _payload_session(payload)
    _normalize_environment(value;registry)
    _canonical_operator_scheme(route)
    _operator_base_url(operator)
  packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py:
    e: supports_hypervisor_system_uri,_is_runtime_request,_is_health_request,_is_schema_request,_is_repair_request,_is_contract_request,_is_agent_factory_request,_is_hypervisor_agent_request,_runtime_request,_health_request,_schema_request,_repair_request,_agent_factory_request,_hypervisor_agent_request,_log_request,_file_request,_contract_request,_select_hypervisor_system_handler,call_hypervisor_system_uri
    supports_hypervisor_system_uri(uri)
    _is_runtime_request(request)
    _is_health_request(request)
    _is_schema_request(request)
    _is_repair_request(request)
    _is_contract_request(request)
    _is_agent_factory_request(request)
    _is_hypervisor_agent_request(request)
    _runtime_request(request)
    _health_request(request)
    _schema_request(request)
    _repair_request(request)
    _agent_factory_request(request)
    _hypervisor_agent_request(request)
    _log_request(request)
    _file_request(request)
    _contract_request(request)
    _select_hypervisor_system_handler(request)
    call_hypervisor_system_uri(uri)
  packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py:
    e: handle_runtime_uri,handle_health_uri,_contract_path_for_agent,_schema_refs_from_capabilities,_read_contract,_contract_uri_for_schema,handle_schema_uri,handle_repair_uri,handle_agent_factory_uri,handle_hypervisor_agent_uri,handle_log_uri,handle_file_uri,handle_contract_uri
    handle_runtime_uri(parts)
    handle_health_uri(parts)
    _contract_path_for_agent(agent_id)
    _schema_refs_from_capabilities(capabilities)
    _read_contract(path)
    _contract_uri_for_schema(agent_id;file_uri)
    handle_schema_uri(parts)
    handle_repair_uri(parts)
    handle_agent_factory_uri(request)
    handle_hypervisor_agent_uri(request)
    handle_log_uri(uri)
    handle_file_uri(uri)
    handle_contract_uri(uri;repo)
  packages/resource-agent-hypervisor/hypervisor/routing/system_request.py:
    e: uri_path_parts,query_params,bool_param,int_param,SystemUriRequest
    SystemUriRequest:
    uri_path_parts(uri)
    query_params(uri)
    bool_param(value)
    int_param(value)
  packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py:
    e: register_view_renderer,supports_view_uri,normalize_view_uri,resolve_view_envelope,handle_view_uri,ViewEnvelope
    ViewEnvelope: to_dict(0)
    register_view_renderer(renderer)
    supports_view_uri(uri)
    normalize_view_uri(uri)
    resolve_view_envelope(view_uri)
    handle_view_uri(uri)
  packages/resource-agent-hypervisor/hypervisor/routing/views/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/routing/views/process.py:
    e: _human_title,_related_uris,_process_actions,_process_status_fields,build_process_view_data
    _human_title(agent_ref;agent_id)
    _related_uris(agent_id;inspection)
    _process_actions(agent_id;related)
    _process_status_fields(inspection;readiness;summary)
    build_process_view_data(agent_id)
  packages/resource-agent-hypervisor/hypervisor/uri/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/uri/client.py:
    e: Uri3Client
    Uri3Client: __init__(0),resolve(1),call(2),explain(2),scan(1),logs(1),schema(1),graph(1),nl2uri(1)  # Thin hypervisor adapter over uri3 routing, scanning and grap
  packages/resource-agent-hypervisor/hypervisor/uri2llm/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/uri2llm/env_resolver.py:
  packages/resource-agent-hypervisor/hypervisor/uri2llm/function_resolver.py:
  packages/resource-agent-hypervisor/hypervisor/uri2llm/llm_resolver.py:
  packages/resource-agent-hypervisor/hypervisor/uri2llm/protocol_resolver.py:
  packages/resource-agent-hypervisor/hypervisor/uri2llm/pypi_resolver.py:
  packages/resource-agent-hypervisor/hypervisor/uri2llm/router.py:
  packages/resource-agent-hypervisor/hypervisor/verifier/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/verifier/capability_tests.py:
    e: build_capability_test_plan
    build_capability_test_plan(registry)
  packages/resource-agent-hypervisor/hypervisor/verifier/cli.py:
    e: main
    main(argv)
  packages/resource-agent-hypervisor/meta_agent/__init__.py:
  packages/resource-agent-hypervisor/meta_agent/api.py:
    e: health,proposal_from_prompt,validate,repair,generate,pipeline,verify,PromptRequest,SpecPathRequest
    PromptRequest:
    SpecPathRequest:
    health()
    proposal_from_prompt(req)
    validate(req)
    repair(req)
    generate(req)
    pipeline(req)
    verify()
  packages/resource-agent-hypervisor/meta_agent/cli.py:
    e: main
    main()
  packages/resource-agent-hypervisor/meta_agent/cli_commands.py:
    e: cmd_plan,cmd_validate,cmd_repair,cmd_generate,cmd_pipeline,cmd_verify
    cmd_plan(prompt;out)
    cmd_validate(spec)
    cmd_repair(spec)
    cmd_generate(spec)
    cmd_pipeline(prompt;out)
    cmd_verify()
  packages/resource-agent-hypervisor/meta_agent/domain_planner/__init__.py:
  packages/resource-agent-hypervisor/meta_agent/domain_planner/domain_pack_generator.py:
  packages/resource-agent-hypervisor/meta_agent/domain_planner/llm_planner.py:
  packages/resource-agent-hypervisor/meta_agent/models.py:
    e: dump_yaml,AgentCreationIntent,RepairResult,PipelineResult
    AgentCreationIntent:  # Normalized request to create an agent.
    RepairResult:
    PipelineResult:
    dump_yaml(data)
  packages/resource-agent-hypervisor/meta_agent/orchestrator.py:
    e: save_proposal_from_prompt,validate_repair_generate,pipeline_from_prompt,asdict_result
    save_proposal_from_prompt(prompt;output_path)
    validate_repair_generate(spec_path)
    pipeline_from_prompt(prompt)
    asdict_result(result)
  packages/resource-agent-hypervisor/meta_agent/planner.py:
    e: slugify,package_name,singularize,infer_intent,intent_to_agent_spec
    slugify(value)
    package_name(agent_name)
    singularize(word)
    infer_intent(prompt)
    intent_to_agent_spec(intent)
  packages/resource-agent-hypervisor/meta_agent/repair/__init__.py:
  packages/resource-agent-hypervisor/meta_agent/repair/loader.py:
    e: load_spec,write_spec
    load_spec(path)
    write_spec(path;data)
  packages/resource-agent-hypervisor/meta_agent/repair/pipeline.py:
    e: repair_agent_spec
    repair_agent_spec(path)
  packages/resource-agent-hypervisor/meta_agent/repair/rules.py:
    e: repair_agent_block,repair_duplicate_capability_names,repair_missing_capability_type,repair_resource_read_capability,repair_command_capability,repair_capabilities
    repair_agent_block(data;path_stem;warnings)
    repair_duplicate_capability_names(capabilities;warnings)
    repair_missing_capability_type(cap;warnings)
    repair_resource_read_capability(cap;warnings)
    repair_command_capability(cap;warnings)
    repair_capabilities(data;warnings)
  packages/resource-agent-hypervisor/runtime_client/__init__.py:
  packages/resource-agent-hypervisor/runtime_client/client.py:
    e: ResourceRuntimeClient
    ResourceRuntimeClient: __init__(2),read_resource(1),dispatch_command(2)  # Small HTTP client used by generated thin agents.
  packages/uri2flow/uri2flow/__init__.py:
  packages/uri2flow/uri2flow/cli.py:
    e: cmd_validate,cmd_expand,cmd_print,build_parser,main
    cmd_validate(args)
    cmd_expand(args)
    cmd_print(args)
    build_parser()
    main(argv)
  packages/uri2flow/uri2flow/expander.py:
    e: _node_from_step,_edges_from_depends,expand_flow,dump_yaml
    _node_from_step(step;previous_id;used)
    _edges_from_depends(nodes)
    expand_flow(flow)
    dump_yaml(data)
  packages/uri2flow/uri2flow/loaders/__init__.py:
  packages/uri2flow/uri2flow/loaders/markpact_loader.py:
  packages/uri2flow/uri2flow/models.py:
    e: FlowStep,FlowDocument
    FlowStep:
    FlowDocument: to_dict(0)
  packages/uri2flow/uri2flow/parser.py:
    e: _as_list,_parse_step,parse_flow,load_flow,FlowParseError
    FlowParseError:
    _as_list(value)
    _parse_step(raw)
    parse_flow(data)
    load_flow(path)
  packages/uri2flow/uri2flow/resolver.py:
    e: _find_repo_root,_pattern_to_regex,_match_pattern,_load_flow_defaults_config,_defaults_from_entry,_defaults_from_scheme,_defaults_from_patterns,_fallback_defaults,default_operation_for_uri,clear_defaults_cache,OperationDefaults
    OperationDefaults:
    _find_repo_root(start)
    _pattern_to_regex(pattern)
    _match_pattern(pattern;uri)
    _load_flow_defaults_config()
    _defaults_from_entry(entry)
    _defaults_from_scheme(scheme)
    _defaults_from_patterns(uri)
    _fallback_defaults()
    default_operation_for_uri(uri)
    clear_defaults_cache()
  packages/uri2flow/uri2flow/utils.py:
    e: slugify,scheme_of,path_parts,node_id_from_uri
    slugify(value)
    scheme_of(uri)
    path_parts(uri)
    node_id_from_uri(uri;used)
  packages/uri2flow/uri2flow/validator.py:
    e: validate_flow_document,validate_expanded_flow,validate_flow
    validate_flow_document(data)
    validate_expanded_flow(data)
    validate_flow(path)
  scripts/architecture_audit/__init__.py:
  scripts/architecture_audit/areas.py:
    e: normalize_path,area_for_path,domain_term_present
    normalize_path(path)
    area_for_path(path)
    domain_term_present(term;text)
  scripts/architecture_audit/audit.py:
    e: area_summary,build_backlog,_backlog_item,build_audit,_suggested_gates
    area_summary(modules)
    build_backlog(findings)
    _backlog_item(priority;title;why;finding_count)
    build_audit(root;map_path;dup_path)
    _suggested_gates()
  scripts/architecture_audit/checks_domain.py:
    e: read_text_if_small,audit_domain_vocabulary,_is_audit_tool_module,_domain_vocabulary_finding,audit_stale_map_entries,audit_domain_named_modules
    read_text_if_small(path)
    audit_domain_vocabulary(root;modules)
    _is_audit_tool_module(path)
    _domain_vocabulary_finding(module;hits)
    audit_stale_map_entries(root;modules)
    audit_domain_named_modules(root;modules)
  scripts/architecture_audit/checks_structure.py:
    e: is_generated_area,unique_ordered,sort_findings,audit_map_alerts,audit_large_modules,_hotspot_finding,_should_skip_hotspot,audit_duplication,_ignored_source_areas,_source_areas,_is_generated_source_mix,_is_cross_area,_is_runtime_operator_boundary,_classify_duplication,_live_duplication_group,_fragment_symbol_is_stale,_duplication_group_findings
    is_generated_area(area)
    unique_ordered(values)
    sort_findings(findings)
    audit_map_alerts(alerts;hotspots)
    audit_large_modules(modules)
    _hotspot_finding(hotspot)
    _should_skip_hotspot(hotspot)
    audit_duplication(groups;hotspots)
    _ignored_source_areas()
    _source_areas(areas)
    _is_generated_source_mix(areas)
    _is_cross_area(source_areas)
    _is_runtime_operator_boundary(source_areas)
    _classify_duplication(group;areas)
    _live_duplication_group(group;root)
    _fragment_symbol_is_stale(root;fragment)
    _duplication_group_findings(group)
  scripts/architecture_audit/cli.py:
    e: build_parser,resolve_input,write_output,fail_code,main
    build_parser()
    resolve_input(root;path)
    write_output(text;out)
    fail_code(findings;threshold)
    main(argv)
  scripts/architecture_audit/models.py:
    e: ModuleEntry,DupFragment,DupGroup,Finding,AuditResult
    ModuleEntry:
    DupFragment:
    DupGroup:
    Finding:
    AuditResult:
  scripts/architecture_audit/parsers.py:
    e: parse_inline_list,parse_map,parse_duplication
    parse_inline_list(line)
    parse_map(path)
    parse_duplication(path)
  scripts/architecture_audit/render.py:
    e: render_markdown,_area_lines,_finding_lines,_backlog_lines,_gate_lines
    render_markdown(result)
    _area_lines(result)
    _finding_lines(result)
    _backlog_lines(result)
    _gate_lines(result)
  scripts/architecture_responsibility_audit.py:
  scripts/examples/audit_agent_reports.py:
    e: _validate_example,_validate_contracts,_validate_deployments,_write_deployment_reports,_render_markdown,main,ExampleAuditSpec,Finding,AuditReport
    ExampleAuditSpec:
    Finding:
    AuditReport: errors(0),warnings(0)
    _validate_example(spec;repo;registry)
    _validate_contracts(repo)
    _validate_deployments(repo;registry)
    _write_deployment_reports(repo;out_dir)
    _render_markdown(report)
    main()
  scripts/examples/comprehensive_test.py:
    e: _resolve_argv,_missing_requirements,_tail,_run_command,run_suite,write_reports,_automation_summary,main,CommandResult,ComprehensiveReport
    CommandResult:
    ComprehensiveReport: passed(0),failed(0),skipped(0)
    _resolve_argv(spec;repo_root;env)
    _missing_requirements(caps;requires)
    _tail(text;limit)
    _run_command(spec;repo_root;env;caps)
    run_suite(repo_root)
    write_reports(repo_root;report)
    _automation_summary(report)
    main()
  scripts/examples/effective_weather_playwright.py:
    e: _run,_json_cmd,_health_ok,_extract_health_uri,_discover_local_agent_health,_inspect_agent,_is_agent_healthy,_try_repair_or_start,_ensure_weather_agent,_flow_text,_task_text,_artifact_to_path,_validate_workflow_result,_validate_png_artifact,_run_uri3_flow,_run_uri2ops_task,main
    _run(argv)
    _json_cmd(argv)
    _health_ok(url)
    _extract_health_uri(payload)
    _discover_local_agent_health()
    _inspect_agent(agent_id)
    _is_agent_healthy(inspected;health_uri)
    _try_repair_or_start(agent_id)
    _ensure_weather_agent(agent_id)
    _flow_text(flow_id;health_uri)
    _task_text(task_id;health_uri)
    _artifact_to_path(uri)
    _validate_workflow_result(payload;health_uri)
    _validate_png_artifact(payload)
    _run_uri3_flow(flow_path;graph_path;health_uri)
    _run_uri2ops_task(task_path)
    main(argv)
  scripts/examples/run_uri3_workflow.py:
    e: main
    main(argv)
  scripts/tellmesh/fix_and_publish.py:
    e: copy_assets,fix_uri2flow_pyproject,fix_uri2verify_pyproject,fix_nl2uri_urish_sources,update_goal_tests,goal_push,main
    copy_assets()
    fix_uri2flow_pyproject()
    fix_uri2verify_pyproject()
    fix_nl2uri_urish_sources()
    update_goal_tests()
    goal_push(name)
    main()
  scripts/tellmesh/move_tests.py:
    e: sync_tests,remove_hypervisor_tests,push_tellmesh,main
    sync_tests(name)
    remove_hypervisor_tests(name)
    push_tellmesh(name)
    main()
  scripts/tellmesh/split_packages.py:
    e: run,goal_yaml,copy_package,append_uv_sources,ensure_repo,publish_with_goal,main
    run(cmd)
    goal_yaml(name)
    copy_package(name)
    append_uv_sources(pyproject_path;name)
    ensure_repo(name;dst)
    publish_with_goal(name;dst)
    main()
  scripts/tellmesh/sync_www.py:
    e: sync_www,main
    sync_www()
    main()
  scripts/www/about_parser.py:
    e: split_frontmatter,load_about,iter_about_files
    split_frontmatter(text)
    load_about(path)
    iter_about_files(examples_root)
  scripts/www/build_examples_docs.py:
    e: _import_markdown,natural_key,slug_for_dir,slug_for_overview,rewrite_example_links,_resolve_target,_is_external_or_anchor,_rewrite_known_www_target,_rewrite_examples_target,_rewrite_url,md_to_html,extract_title,list_example_dirs,embeddable_files,render_file_block,render_example_section,build_toc,build_page,build_overview_section,main
    _import_markdown()
    natural_key(name)
    slug_for_dir(name)
    slug_for_overview()
    rewrite_example_links(text)
    _resolve_target(raw_path)
    _is_external_or_anchor(raw)
    _rewrite_known_www_target(label;target;fragment)
    _rewrite_examples_target(label;target;fragment)
    _rewrite_url(label;url)
    md_to_html(text)
    extract_title(md_text;fallback)
    list_example_dirs()
    embeddable_files(example_dir)
    render_file_block(path;example_dir)
    render_example_section(example_dir)
    build_toc(entries)
    build_page(entries;overview_html)
    build_overview_section()
    main()
  scripts/www/build_examples_manifest.py:
    e: natural_key,extract_title,category_for,_build_office_chain,load_office_chains,test_summary,build_manifest,main
    natural_key(name)
    extract_title(readme;fallback)
    category_for(name)
    _build_office_chain(chain)
    load_office_chains()
    test_summary()
    build_manifest()
    main()
  scripts/www/build_landing_integrations.py:
    e: _esc,_i18n_values,_cta_i18n_values,_spotlight_body_html,_render_cta_links,_render_i18n_spans,_render_i18n,_snippet_block,render_connector,render_card,_render_inline_i18n,render_spotlight,_card_body_html,collect_cards,build_sections,splice_index,write_i18n_js,main
    _esc(value)
    _i18n_values(card;field)
    _cta_i18n_values(card;field)
    _spotlight_body_html(card;source;fallback_html)
    _render_cta_links(href;values)
    _render_i18n_spans(values)
    _render_i18n(field;values)
    _snippet_block(card)
    render_connector(card)
    render_card(card;body_html)
    _render_inline_i18n(values)
    render_spotlight(card;body_html)
    _card_body_html(card;source;shared_html)
    collect_cards()
    build_sections(cards)
    splice_index(connectors_html;grid_html)
    write_i18n_js(i18n_export)
    main()
  scripts/www/check_examples_links.py:
    e: _iter_hrefs,_collect_anchor_ids,_extract_block,_check_href,check_examples_links,main
    _iter_hrefs(block)
    _collect_anchor_ids(html)
    _extract_block(html;pattern)
    _check_href(href)
    check_examples_links(page)
    main()
  scripts/www/md_html.py:
    e: _import_markdown,md_to_html,cache_key,cached_html
    _import_markdown()
    md_to_html(text)
    cache_key(source;body)
    cached_html(source;body;cache_dir)
  scripts/www/monitor_landing.py:
    e: fetch_html,extract_prices,load_baseline,save_baseline,main
    fetch_html(url;timeout)
    extract_prices(html)
    load_baseline(path)
    save_baseline(path;payload)
    main()
  scripts/www/monitor_notify.py:
    e: webhook_url,is_placeholder_webhook,is_supported_webhook,emit_alert,post_webhook
    webhook_url(explicit)
    is_placeholder_webhook(url)
    is_supported_webhook(url)
    emit_alert(event;message)
    post_webhook(url;payload)
  scripts/www/monitor_url.py:
    e: fetch,main
    fetch(url;timeout)
    main()
  scripts/www/site_nav.py:
    e: brand_logo_src,render_brand,render_topbar,render_footer
    brand_logo_src(prefix)
    render_brand()
    render_topbar()
    render_footer()
  scripts/www/www_root.py:
    e: www_dir
    www_dir()
  testenv/ssh_agent_host/mock_agent_server.py:
    e: Handler
    Handler: _json(2),do_GET(0),log_message(1)
  tests/__init__.py:
  tests/architecture/envelope_helpers.py:
    e: normalize_service_result,assert_service_result_shape,assert_workflow_result_shape
    normalize_service_result(payload)
    assert_service_result_shape(payload)
    assert_workflow_result_shape(payload)
  tests/architecture/import_scanner.py:
    e: repo_root_from_here
    repo_root_from_here()
  tests/architecture/test_doctor_contract.py:
    e: test_doctor_contract
    test_doctor_contract(repo_root)
  tests/architecture/test_doctor_gate.py:
    e: test_uri3_doctor_gate
    test_uri3_doctor_gate(repo_root)
  tests/architecture/test_explain_contract.py:
    e: _assert_explain_contract,test_explain_weather_contract,test_explain_browser_contract,test_explain_http_contract
    _assert_explain_contract(payload)
    test_explain_weather_contract(repo_root)
    test_explain_browser_contract(repo_root)
    test_explain_http_contract(repo_root)
  tests/architecture/test_import_boundaries.py:
    e: test_forbidden_imports
    test_forbidden_imports()
  tests/architecture/test_result_envelope_contract.py:
    e: test_touri_call_envelope,test_touri_data_quality_failure_envelope,test_uri3_workflow_dry_run_envelope
    test_touri_call_envelope(repo_root)
    test_touri_data_quality_failure_envelope(tmp_path)
    test_uri3_workflow_dry_run_envelope()
  tests/architecture/test_technical_ok_business_fail.py:
    e: _write_capability,test_technical_ok_business_fail_via_data_quality
    _write_capability(tmp_path;manifest)
    test_technical_ok_business_fail_via_data_quality(tmp_path)
  tests/architecture/test_uri2run_envelope.py:
    e: test_uri2run_python_envelope,test_uri2run_shell_envelope
    test_uri2run_python_envelope()
    test_uri2run_shell_envelope()
  tests/capabilities/weather_forecast/test_fixtures.py:
    e: test_weather_forecast_fixtures_exist,test_good_fixture_contains_expected_marker
    test_weather_forecast_fixtures_exist(repo_root)
    test_good_fixture_contains_expected_marker(repo_root)
  tests/conftest.py:
    e: repo_root,_hypervisor_repo_root_env,workspace_pythonpath,workspace_env,cli_argv,examples_env
    repo_root()
    _hypervisor_repo_root_env(repo_root)
    workspace_pythonpath(repo_root)
    workspace_env(repo_root)
    cli_argv(name)
    examples_env(repo_root)
  tests/domain_pack/__init__.py:
  tests/domain_pack/test_generator.py:
    e: _weather_tree,test_derive_domain_model,test_generate_proto_weather,test_generate_resources_and_views,test_generate_domain_pack_from_tree,test_generate_domain_pack_from_uri_tree_file,test_deprecated_meta_agent_reexport
    _weather_tree()
    test_derive_domain_model()
    test_generate_proto_weather()
    test_generate_resources_and_views()
    test_generate_domain_pack_from_tree(tmp_path)
    test_generate_domain_pack_from_uri_tree_file(tmp_path)
    test_deprecated_meta_agent_reexport()
  tests/examples/capabilities.py:
    e: _tcp_open,_http_ok,_adb_device,_uia_available,_cli_available,_weather_agent_health,probe_machine,write_capabilities_report,CapabilityProbe,MachineCapabilities
    CapabilityProbe:
    MachineCapabilities: available(1),to_dict(0)
    _tcp_open(host;port;timeout)
    _http_ok(url;timeout)
    _adb_device()
    _uia_available()
    _cli_available(name;repo_root)
    _weather_agent_health()
    probe_machine(repo_root)
    write_capabilities_report(repo_root;caps;path)
  tests/examples/catalog.py:
    e: ExampleSpec
    ExampleSpec:
  tests/examples/command_catalog.py:
    e: _run_sh_commands,CommandSpec
    CommandSpec:
    _run_sh_commands()
  tests/examples/conftest.py:
    e: repo_root,examples_env,run_shell,docker_available,_python_candidates,_python_runs_playwright,playwright_python,playwright_available,www_available,skip_if_markers
    repo_root()
    examples_env(repo_root)
    run_shell(repo_root;command)
    docker_available()
    _python_candidates(repo_root)
    _python_runs_playwright(python;env)
    playwright_python(repo_root)
    playwright_available(repo_root)
    www_available()
    skip_if_markers(spec;repo_root)
  tests/examples/shell_runner.py:
    e: _skip,_run_sh,_local_agent_url,_ex02,_ex03,_ex05,_ex06,_ex07,_ex08,_ex15pw,_ex16www,_ex22dash,_ex11,_should_skip,run_example,run_catalog,main
    _skip(_root;_env)
    _run_sh(spec;root;env)
    _local_agent_url(root;env)
    _ex02(root;env)
    _ex03(root;env)
    _ex05(root;env)
    _ex06(root;env)
    _ex07(root;env)
    _ex08(root;env)
    _ex15pw(root;env)
    _ex16www(root;env)
    _ex22dash(root;env)
    _ex11(root;env)
    _should_skip(spec;root)
    run_example(spec)
    run_catalog()
    main(argv)
  tests/examples/test_comprehensive.py:
    e: _missing,_resolve_argv,_run_spec,machine_caps,test_default_example_commands,test_real_example_commands,test_capabilities_report_written,test_command_catalog_covers_all_examples,test_compact_flow_real_command_is_self_contained
    _missing(caps;requires)
    _resolve_argv(spec;repo_root;env)
    _run_spec(spec;repo_root;examples_env)
    machine_caps(repo_root)
    test_default_example_commands(spec;repo_root;examples_env;machine_caps)
    test_real_example_commands(spec;repo_root;examples_env;machine_caps)
    test_capabilities_report_written(repo_root;machine_caps)
    test_command_catalog_covers_all_examples()
    test_compact_flow_real_command_is_self_contained()
  tests/examples/test_effective_weather_playwright.py:
    e: test_flow_text_with_screenshot_is_valid_compact_flow,test_artifact_uri_maps_to_workflow_output_path
    test_flow_text_with_screenshot_is_valid_compact_flow()
    test_artifact_uri_maps_to_workflow_output_path()
  tests/examples/test_examples_smoke.py:
    e: test_examples_readme_lists_known_directories,test_run_sh_script_exists,test_touri_capability_manifests_validate,test_workflow_graph_yaml_parseable,test_architecture_stack_imports,test_catalog_covers_all_run_sh
    test_examples_readme_lists_known_directories(repo_root)
    test_run_sh_script_exists(spec;repo_root)
    test_touri_capability_manifests_validate(repo_root;examples_env)
    test_workflow_graph_yaml_parseable(repo_root)
    test_architecture_stack_imports()
    test_catalog_covers_all_run_sh(repo_root)
  tests/examples/test_inline_examples.py:
    e: _local_agent_url,test_example_02_uri3_scan_http,test_example_03_ssh_docker_testenv,test_example_05_meta_repair,test_example_06_orders_agent,test_example_07_invoices_agent,test_example_08_evolution,test_example_15_playwright_mock_via_uri3,test_example_16www_landing_monitor,test_example_22_dashboard_agent
    _local_agent_url(repo_root;env)
    test_example_02_uri3_scan_http(repo_root;examples_env)
    test_example_03_ssh_docker_testenv(repo_root;examples_env)
    test_example_05_meta_repair(repo_root;examples_env)
    test_example_06_orders_agent(repo_root;examples_env)
    test_example_07_invoices_agent(repo_root;examples_env)
    test_example_08_evolution(repo_root;examples_env)
    test_example_15_playwright_mock_via_uri3(repo_root;examples_env)
    test_example_16www_landing_monitor(repo_root;examples_env)
    test_example_22_dashboard_agent(repo_root;examples_env)
  tests/examples/test_run_sh_examples.py:
    e: test_example_run_sh
    test_example_run_sh(spec;repo_root;examples_env)
  tests/generator/__init__.py:
  tests/generator/test_headers.py:
    e: test_generated_python_files_have_standard_header,test_contract_source_ref_is_repo_relative,test_verify_generated_ignores_pycache
    test_generated_python_files_have_standard_header(tmp_path;monkeypatch)
    test_contract_source_ref_is_repo_relative()
    test_verify_generated_ignores_pycache(tmp_path;monkeypatch)
  tests/hypervisor/__init__.py:
  tests/hypervisor/test_agent_describe.py:
    e: test_describe_weather_agent_markdown,test_describe_desktop_operator_contract,test_describe_invoices_agent_skill_examples,test_describe_dashboard_system_agent_architecture,test_describe_screenshot_analysis_custom_agent,test_describe_weather_agent_has_health_uri,test_describe_agent_writes_file
    test_describe_weather_agent_markdown()
    test_describe_desktop_operator_contract()
    test_describe_invoices_agent_skill_examples()
    test_describe_dashboard_system_agent_architecture()
    test_describe_screenshot_analysis_custom_agent()
    test_describe_weather_agent_has_health_uri()
    test_describe_agent_writes_file(tmp_path)
  tests/hypervisor/test_agent_factory_uri.py:
    e: test_agent_factory_generate_uri_dry_run,test_hypervisor_agent_run_uri_dry_run_waits_for_generated_deployment,test_hypervisor_local_alias_run_uri_dry_run,test_schema_uri_returns_agent_contract_and_capability_refs,test_file_uri_returns_small_text_content
    test_agent_factory_generate_uri_dry_run(tmp_path)
    test_hypervisor_agent_run_uri_dry_run_waits_for_generated_deployment(tmp_path)
    test_hypervisor_local_alias_run_uri_dry_run()
    test_schema_uri_returns_agent_contract_and_capability_refs(tmp_path)
    test_file_uri_returns_small_text_content(tmp_path)
  tests/hypervisor/test_agent_lifecycle.py:
    e: client,test_registry_lists_new_agents,test_api_agents_includes_new_deployments,test_build_run_plan_for_new_agents,test_uri_health_dry_run_for_new_agent,test_uri_repair_diagnose_for_new_agent,test_uri_repair_apply_dry_run,test_uri_repair_auto_dry_run,test_uri_repair_apply_requires_approval,test_hypervisor_repair_supervisor_auto,test_hypervisor_repair_forced_playbook_runs_when_healthy
    client()
    test_registry_lists_new_agents()
    test_api_agents_includes_new_deployments(client)
    test_build_run_plan_for_new_agents(agent_id;port;module)
    test_uri_health_dry_run_for_new_agent()
    test_uri_repair_diagnose_for_new_agent()
    test_uri_repair_apply_dry_run(client)
    test_uri_repair_auto_dry_run()
    test_uri_repair_apply_requires_approval(client)
    test_hypervisor_repair_supervisor_auto(monkeypatch)
    test_hypervisor_repair_forced_playbook_runs_when_healthy(monkeypatch)
  tests/hypervisor/test_agent_runner.py:
    e: _deployment_port,_mock_run_dependencies,test_local_target_to_module,test_build_run_plan_for_local_deployment,test_build_run_plan_with_port_override_updates_local_endpoints,test_run_agent_dry_run_emits_lifecycle_event,test_build_run_plan_missing_path,test_agent_status_without_health,test_ssh_run_plan_via_build_run_plan,test_ssh_target_starts_via_remote_runner,test_run_agent_detach_idempotent_when_already_running,test_run_agent_reuse_syncs_health_uri_from_command,test_run_agent_restarts_when_explicit_port_differs,test_run_agent_if_running_fail,test_run_agent_rebinds_when_preferred_port_busy,test_stop_agent_cleans_orphan_listener_from_stale_runtime,test_stop_agent_does_not_kill_foreign_listener_without_state,test_inspect_agent_separates_process_running_from_health,test_inspect_agent_detects_command_health_mismatch,test_inspect_agent_reads_process_log_uri,test_supervise_auto_syncs_health_uri,test_ensure_agent_healthy_waits_before_first_probe,test_verify_local_deployment
    _deployment_port(deployment_id)
    _mock_run_dependencies(monkeypatch)
    test_local_target_to_module()
    test_build_run_plan_for_local_deployment()
    test_build_run_plan_with_port_override_updates_local_endpoints()
    test_run_agent_dry_run_emits_lifecycle_event(monkeypatch)
    test_build_run_plan_missing_path(tmp_path;monkeypatch)
    test_agent_status_without_health()
    test_ssh_run_plan_via_build_run_plan()
    test_ssh_target_starts_via_remote_runner(monkeypatch)
    test_run_agent_detach_idempotent_when_already_running(monkeypatch)
    test_run_agent_reuse_syncs_health_uri_from_command(monkeypatch)
    test_run_agent_restarts_when_explicit_port_differs(monkeypatch)
    test_run_agent_if_running_fail(monkeypatch)
    test_run_agent_rebinds_when_preferred_port_busy(monkeypatch)
    test_stop_agent_cleans_orphan_listener_from_stale_runtime(monkeypatch)
    test_stop_agent_does_not_kill_foreign_listener_without_state(monkeypatch)
    test_inspect_agent_separates_process_running_from_health(monkeypatch)
    test_inspect_agent_detects_command_health_mismatch(monkeypatch)
    test_inspect_agent_reads_process_log_uri(monkeypatch)
    test_supervise_auto_syncs_health_uri(monkeypatch)
    test_ensure_agent_healthy_waits_before_first_probe(monkeypatch)
    test_verify_local_deployment(monkeypatch)
  tests/hypervisor/test_artifact_standards.py:
    e: test_runtime_state_schema_on_save,test_legacy_runtime_state_upgrades_on_load,test_log_event_envelope,test_deployment_registry_declared_runtime_views,test_planfile_ticket_import_and_proposal,test_evolution_source_normalization,test_artifact_lifecycle_coverage_reports_loose_files,test_repo_uri_configs_are_canonical_artifacts
    test_runtime_state_schema_on_save(tmp_path)
    test_legacy_runtime_state_upgrades_on_load(tmp_path)
    test_log_event_envelope(tmp_path)
    test_deployment_registry_declared_runtime_views()
    test_planfile_ticket_import_and_proposal(tmp_path)
    test_evolution_source_normalization()
    test_artifact_lifecycle_coverage_reports_loose_files(tmp_path)
    test_repo_uri_configs_are_canonical_artifacts()
  tests/hypervisor/test_autonomous_agents.py:
    e: test_describe_remote_deploy_custom_agent,test_describe_gnome_programmer_custom_agent,test_remote_deploy_plan_for_ssh_dev
    test_describe_remote_deploy_custom_agent()
    test_describe_gnome_programmer_custom_agent()
    test_remote_deploy_plan_for_ssh_dev()
  tests/hypervisor/test_browser_operator_separation.py:
    e: _load_browser_operator,test_browser_operator_contract_is_generic_capability_agent,test_browser_domain_registry_uses_operator_uris,test_browser_operator_is_registered_as_package_agent
    _load_browser_operator(repo_root)
    test_browser_operator_contract_is_generic_capability_agent(repo_root)
    test_browser_domain_registry_uses_operator_uris(repo_root)
    test_browser_operator_is_registered_as_package_agent(repo_root)
  tests/hypervisor/test_browser_ops_domain.py:
    e: _load_yaml,test_browser_ops_domain_declares_operator_boundary,test_browser_ops_operator_registry_matches_uri2ops_capabilities,test_browser_ops_scenario_registry_is_loaded_and_routable,test_browser_operator_points_to_browser_ops_without_owning_scenarios
    _load_yaml(repo_root;relpath)
    test_browser_ops_domain_declares_operator_boundary(repo_root)
    test_browser_ops_operator_registry_matches_uri2ops_capabilities(repo_root)
    test_browser_ops_scenario_registry_is_loaded_and_routable(repo_root)
    test_browser_operator_points_to_browser_ops_without_owning_scenarios(repo_root)
  tests/hypervisor/test_chat_flow_view.py:
    e: client,_planner_plans_from_ask,test_batch_ask_yields_three_flow_plans,test_workflow_dry_run_uri_call_returns_graph_steps
    client()
    _planner_plans_from_ask(result)
    test_batch_ask_yields_three_flow_plans()
    test_workflow_dry_run_uri_call_returns_graph_steps(client)
  tests/hypervisor/test_chat_www.py:
    e: client,test_format_ask_markdown_dashboard,test_format_uri_result_dry_run_preview,test_format_uri_result_diagnosis_markdown,test_format_uri_result_summary_omits_envelope_json,test_format_uri_result_markdown,test_format_uri_result_markdown_workflow_plan,test_format_uri_result_markdown_include_envelope_opt_in,test_format_uri_result_markdown_includes_runtime_and_logs,test_format_uri_result_markdown_reads_top_level_runtime,test_format_uri_result_markdown_shows_log_entries,test_api_ask_returns_markdown,test_api_ask_detects_agent_operational_prompts,test_api_ask_detects_screenshot_schedule_as_workflow,test_api_ask_detects_weather_forecast,test_api_ask_multiline_batch_plans_each_line,test_api_ask_accepts_chat_uri_field,test_api_ask_accepts_chat_uri_as_prompt,test_api_uri_call_chat_prompt,test_api_ask_requires_prompt_or_uri,test_api_ask_accepts_nl_uri,test_api_uri_call_nl_uri_plans,test_api_uri_call_dry_run_preview_markdown,test_api_uri_call_repair_dry_run_is_preview,test_api_uri_call_physical_operator_dry_run_is_preview,test_root_redirects_to_www,test_www_index_served,test_www_index_integrations_section,test_www_index_office_examples,test_www_examples_gallery,test_www_examples_docs_page,test_build_examples_docs_script,test_examples_docs_link_check,test_www_index_links_examples_gallery,test_api_ask_office_invoice_batch,test_readme_links_docs_todo_changelog,test_www_chat_served,test_www_flow_chat_served,test_www_chat_flow_view_module,test_www_chat_js_guards_stale_and_duplicate_actions,test_www_landing_has_tour_copy,test_www_landing_js_explains_repair_loop,test_www_compose_mounts_system_artifacts,test_www_dockerfile_includes_generated_agents_and_repair_cases,test_api_events_returns_typed_feed,test_api_events_stream_contract,test_api_plan_run_dry_run,test_api_plan_run_speak_summary,test_api_voice_speak_mock,test_api_voice_transcribe_mock
    client()
    test_format_ask_markdown_dashboard()
    test_format_uri_result_dry_run_preview()
    test_format_uri_result_diagnosis_markdown()
    test_format_uri_result_summary_omits_envelope_json()
    test_format_uri_result_markdown()
    test_format_uri_result_markdown_workflow_plan()
    test_format_uri_result_markdown_include_envelope_opt_in()
    test_format_uri_result_markdown_includes_runtime_and_logs()
    test_format_uri_result_markdown_reads_top_level_runtime()
    test_format_uri_result_markdown_shows_log_entries()
    test_api_ask_returns_markdown(client;monkeypatch)
    test_api_ask_detects_agent_operational_prompts(client;prompt;kind;subtype;expected_uri)
    test_api_ask_detects_screenshot_schedule_as_workflow(client)
    test_api_ask_detects_weather_forecast(client)
    test_api_ask_multiline_batch_plans_each_line(client)
    test_api_ask_accepts_chat_uri_field(client)
    test_api_ask_accepts_chat_uri_as_prompt(client)
    test_api_uri_call_chat_prompt(client)
    test_api_ask_requires_prompt_or_uri(client)
    test_api_ask_accepts_nl_uri(client)
    test_api_uri_call_nl_uri_plans(client)
    test_api_uri_call_dry_run_preview_markdown(client)
    test_api_uri_call_repair_dry_run_is_preview(client)
    test_api_uri_call_physical_operator_dry_run_is_preview(client)
    test_root_redirects_to_www(client)
    test_www_index_served(client)
    test_www_index_integrations_section(client)
    test_www_index_office_examples(client)
    test_www_examples_gallery(client)
    test_www_examples_docs_page(client)
    test_build_examples_docs_script(repo_root)
    test_examples_docs_link_check(repo_root)
    test_www_index_links_examples_gallery(client)
    test_api_ask_office_invoice_batch(client)
    test_readme_links_docs_todo_changelog(repo_root)
    test_www_chat_served(client)
    test_www_flow_chat_served(client)
    test_www_chat_flow_view_module(repo_root)
    test_www_chat_js_guards_stale_and_duplicate_actions(repo_root)
    test_www_landing_has_tour_copy(client)
    test_www_landing_js_explains_repair_loop(repo_root)
    test_www_compose_mounts_system_artifacts(repo_root)
    test_www_dockerfile_includes_generated_agents_and_repair_cases(repo_root)
    test_api_events_returns_typed_feed(client)
    test_api_events_stream_contract(monkeypatch)
    test_api_plan_run_dry_run(client)
    test_api_plan_run_speak_summary(client)
    test_api_voice_speak_mock(client)
    test_api_voice_transcribe_mock(client)
  tests/hypervisor/test_config.py:
    e: test_default_config_has_structured_sections,test_load_config_merges_user_file,test_env_overrides,test_validate_config_reports_invalid_profile,test_load_hypervisor_config_model,test_load_config_merges_llm_uri_yaml
    test_default_config_has_structured_sections()
    test_load_config_merges_user_file(tmp_path)
    test_env_overrides(monkeypatch)
    test_validate_config_reports_invalid_profile()
    test_load_hypervisor_config_model()
    test_load_config_merges_llm_uri_yaml()
  tests/hypervisor/test_contract_uri.py:
    e: _write_contract_fixture,test_contract_uri_fetch_by_agent_name,test_contract_uri_fetch_by_agents_slug,test_contract_uri_validate_agent,test_contract_uri_validate_registry,test_contract_uri_fetch_weather_agent,test_schema_uri_includes_contract_related_uri,test_contract_uri_generate_dry_run,test_contract_uri_generate_writes_package,test_contract_uri_artifacts_manifest,test_contract_uri_artifacts_includes_proto_for_user_agent
    _write_contract_fixture(tmp_path)
    test_contract_uri_fetch_by_agent_name(tmp_path)
    test_contract_uri_fetch_by_agents_slug(tmp_path)
    test_contract_uri_validate_agent(tmp_path)
    test_contract_uri_validate_registry(tmp_path)
    test_contract_uri_fetch_weather_agent(repo_root)
    test_schema_uri_includes_contract_related_uri(tmp_path)
    test_contract_uri_generate_dry_run(tmp_path)
    test_contract_uri_generate_writes_package(tmp_path)
    test_contract_uri_artifacts_manifest(tmp_path)
    test_contract_uri_artifacts_includes_proto_for_user_agent(repo_root)
  tests/hypervisor/test_dashboard_agent.py:
    e: client,test_health_and_agent_card,test_ui_agents_lists_deployments,test_api_process_view,test_uri_call_read_allowed,test_uri_call_repair_apply_requires_approval,test_uri_call_repair_apply_with_approval,test_uri_call_execution_error_returns_failed_envelope,test_policy_preview_repair,test_monitor_webhook_surfaces_in_events,test_local_target_supports_packages_path,test_local_target_supports_system_dashboard_path,test_resolve_view_uri_process,test_call_system_uri_marks_view_and_logs_as_success,test_uri_implies_dry_run_suffix,test_call_system_uri_workflow_portal_zus_dry_run,test_api_uri_call_workflow_without_dry_run_checkbox,test_call_system_uri_http_health,test_call_system_uri_browser_open_mock,test_call_system_uri_browser_open_dry_run_plan,test_call_system_uri_office_supplier_report_dry_run,test_call_system_uri_office_supplier_report_execute,test_api_uri_call_office_supplier_report,test_api_uri_call_browser_open,test_api_uri_call_browser_open_requires_approval,test_api_uri_call_desktop_operator_health
    client()
    test_health_and_agent_card(client)
    test_ui_agents_lists_deployments(client;monkeypatch)
    test_api_process_view(client;monkeypatch)
    test_uri_call_read_allowed(client;monkeypatch)
    test_uri_call_repair_apply_requires_approval(client)
    test_uri_call_repair_apply_with_approval(client;monkeypatch)
    test_uri_call_execution_error_returns_failed_envelope(client;monkeypatch)
    test_policy_preview_repair()
    test_monitor_webhook_surfaces_in_events(client;tmp_path;monkeypatch)
    test_local_target_supports_packages_path()
    test_local_target_supports_system_dashboard_path()
    test_resolve_view_uri_process(monkeypatch)
    test_call_system_uri_marks_view_and_logs_as_success(monkeypatch)
    test_uri_implies_dry_run_suffix()
    test_call_system_uri_workflow_portal_zus_dry_run()
    test_api_uri_call_workflow_without_dry_run_checkbox(client)
    test_call_system_uri_http_health(monkeypatch)
    test_call_system_uri_browser_open_mock()
    test_call_system_uri_browser_open_dry_run_plan()
    test_call_system_uri_office_supplier_report_dry_run()
    test_call_system_uri_office_supplier_report_execute(tmp_path)
    test_api_uri_call_office_supplier_report(client)
    test_api_uri_call_browser_open(client)
    test_api_uri_call_browser_open_requires_approval(client)
    test_api_uri_call_desktop_operator_health(client)
  tests/hypervisor/test_dashboard_policy.py:
    e: test_dashboard_blocks_repair_apply_without_approval,test_dashboard_allows_repair_apply_with_approval,test_dashboard_blocks_browser_mutation_without_approval,test_dashboard_preview_marks_repair_apply_as_requires_approval
    test_dashboard_blocks_repair_apply_without_approval()
    test_dashboard_allows_repair_apply_with_approval()
    test_dashboard_blocks_browser_mutation_without_approval()
    test_dashboard_preview_marks_repair_apply_as_requires_approval()
  tests/hypervisor/test_dashboard_routing_api.py:
    e: client,test_explain_system_uri_includes_hypervisor_resolution,test_api_uri_explain_operator_route,test_call_system_uri_operator_uses_hypervisor_dispatch
    client()
    test_explain_system_uri_includes_hypervisor_resolution(repo_root)
    test_api_uri_explain_operator_route(client)
    test_call_system_uri_operator_uses_hypervisor_dispatch(monkeypatch;repo_root)
  tests/hypervisor/test_deployment_aliases.py:
    e: test_load_weather_agent_alias_from_domain_fragment,test_resolve_local_weather_agent_alias,test_weather_map_fragment_declares_alias
    test_load_weather_agent_alias_from_domain_fragment(repo_root)
    test_resolve_local_weather_agent_alias(repo_root)
    test_weather_map_fragment_declares_alias(repo_root)
  tests/hypervisor/test_deployment_registry.py:
    e: test_load_default_deployments,test_deployment_from_weather_uri_tree,test_sync_from_uri_tree_writes_registry,test_sync_from_uri_tree_preserves_existing_http_endpoints,test_upsert_replaces_existing_deployment,test_resolve_status_without_health_check,test_registry_summary,test_ssh_target_uri_supported_in_model
    test_load_default_deployments()
    test_deployment_from_weather_uri_tree()
    test_sync_from_uri_tree_writes_registry(tmp_path)
    test_sync_from_uri_tree_preserves_existing_http_endpoints(tmp_path)
    test_upsert_replaces_existing_deployment(tmp_path)
    test_resolve_status_without_health_check()
    test_registry_summary()
    test_ssh_target_uri_supported_in_model(tmp_path)
  tests/hypervisor/test_deployment_selector.py:
    e: test_parse_hypervisor_local_uri,test_parse_hypervisor_deployment_uri,test_resolve_local_weather_agent_alias
    test_parse_hypervisor_local_uri()
    test_parse_hypervisor_deployment_uri()
    test_resolve_local_weather_agent_alias()
  tests/hypervisor/test_desktop_operator_separation.py:
    e: _load_desktop_operator,test_desktop_operator_contract_is_generic_capability_agent,test_desktop_operator_does_not_embed_domain_vocabulary,test_domain_registry_uses_operator_uris_without_owning_operator_contract,test_desktop_operator_is_registered_as_package_agent
    _load_desktop_operator(repo_root)
    test_desktop_operator_contract_is_generic_capability_agent(repo_root)
    test_desktop_operator_does_not_embed_domain_vocabulary(repo_root)
    test_domain_registry_uses_operator_uris_without_owning_operator_contract(repo_root)
    test_desktop_operator_is_registered_as_package_agent(repo_root)
  tests/hypervisor/test_desktop_ops_domain.py:
    e: _load_yaml,test_desktop_ops_domain_declares_operator_boundary,test_desktop_ops_operator_registry_matches_uri2ops_capabilities,test_desktop_ops_scenario_registry_is_loaded_and_routable,test_desktop_ops_does_not_embed_vertical_scenarios,test_desktop_operator_points_to_desktop_ops_without_owning_scenarios
    _load_yaml(repo_root;relpath)
    test_desktop_ops_domain_declares_operator_boundary(repo_root)
    test_desktop_ops_operator_registry_matches_uri2ops_capabilities(repo_root)
    test_desktop_ops_scenario_registry_is_loaded_and_routable(repo_root)
    test_desktop_ops_does_not_embed_vertical_scenarios(repo_root)
    test_desktop_operator_points_to_desktop_ops_without_owning_scenarios(repo_root)
  tests/hypervisor/test_docker_runner.py:
    e: test_build_docker_deploy_plan,test_build_docker_control_plan_up
    test_build_docker_deploy_plan()
    test_build_docker_control_plan_up()
  tests/hypervisor/test_events_service.py:
    e: test_collect_system_events_includes_log_event,test_collect_system_events_includes_hypervisor_operation_events,test_collect_system_events_prefers_latest_log_lines,test_collect_system_events_includes_supervise_watch_log_event,test_collect_system_events_includes_watch_log_with_agent_id,test_collect_system_events_includes_incident,test_collect_system_events_treats_http_healthy_unmanaged_agent_as_healthy
    test_collect_system_events_includes_log_event(tmp_path;monkeypatch)
    test_collect_system_events_includes_hypervisor_operation_events(tmp_path;monkeypatch)
    test_collect_system_events_prefers_latest_log_lines(tmp_path;monkeypatch)
    test_collect_system_events_includes_supervise_watch_log_event(tmp_path;monkeypatch)
    test_collect_system_events_includes_watch_log_with_agent_id(tmp_path;monkeypatch)
    test_collect_system_events_includes_incident(tmp_path;monkeypatch)
    test_collect_system_events_treats_http_healthy_unmanaged_agent_as_healthy(tmp_path;monkeypatch)
  tests/hypervisor/test_graph_hypervisor_routing.py:
    e: test_workflow_operator_uses_hypervisor_routing
    test_workflow_operator_uses_hypervisor_routing(monkeypatch;tmp_path)
  tests/hypervisor/test_health_uri.py:
    e: test_resolve_effective_health_uri_prefers_network_effective_uri,test_resolve_effective_health_uri_uses_process_command,test_command_port_from_runtime_uses_network_effective_port
    test_resolve_effective_health_uri_prefers_network_effective_uri()
    test_resolve_effective_health_uri_uses_process_command()
    test_command_port_from_runtime_uses_network_effective_port()
  tests/hypervisor/test_hypervisor_cli.py:
    e: test_cli_deployments_and_run_agent_dry_run,test_cli_ssh_run_agent_dry_run,test_cli_deploy_agent_dry_run,test_cli_agent_status_includes_runtime_fields,test_cli_run_agent_dry_run_accepts_if_running,test_cli_run_agent_dry_run_emits_operation_event,test_cli_run_agent_accepts_approve_compatibility_flag,test_cli_explain_operator_route,test_cli_call_operator_route_uses_hypervisor_dispatch,test_cli_inspect_agent,test_cli_supervise_watch_limited,test_cli_repair_heal
    test_cli_deployments_and_run_agent_dry_run(capsys)
    test_cli_ssh_run_agent_dry_run(capsys)
    test_cli_deploy_agent_dry_run(capsys)
    test_cli_agent_status_includes_runtime_fields(capsys)
    test_cli_run_agent_dry_run_accepts_if_running(capsys)
    test_cli_run_agent_dry_run_emits_operation_event(monkeypatch;capsys)
    test_cli_run_agent_accepts_approve_compatibility_flag(capsys)
    test_cli_explain_operator_route(capsys)
    test_cli_call_operator_route_uses_hypervisor_dispatch(monkeypatch;capsys)
    test_cli_inspect_agent(monkeypatch;capsys)
    test_cli_supervise_watch_limited(monkeypatch;capsys)
    test_cli_repair_heal(monkeypatch;capsys)
  tests/hypervisor/test_inspection_probe.py:
    e: test_probe_http_rewrites_localhost_when_probe_host_is_set,test_probe_http_keeps_non_localhost_targets,test_probe_http_accepts_expected_service_without_agent,test_probe_http_rejects_unexpected_service_without_agent
    test_probe_http_rewrites_localhost_when_probe_host_is_set(monkeypatch)
    test_probe_http_keeps_non_localhost_targets(monkeypatch)
    test_probe_http_accepts_expected_service_without_agent(monkeypatch)
    test_probe_http_rejects_unexpected_service_without_agent(monkeypatch)
  tests/hypervisor/test_local_run_plan.py:
    e: test_local_run_plan_ignores_a2a_card_uri,test_local_run_plan_prefers_declared_http_endpoints,test_local_target_to_module_custom_agent,test_local_run_plan_custom_agent
    test_local_run_plan_ignores_a2a_card_uri(repo_root)
    test_local_run_plan_prefers_declared_http_endpoints(repo_root)
    test_local_target_to_module_custom_agent()
    test_local_run_plan_custom_agent(repo_root)
  tests/hypervisor/test_markpact_deployments.py:
    e: test_deployments_readme_has_markpact_deploy_blocks
    test_deployments_readme_has_markpact_deploy_blocks(repo_root)
  tests/hypervisor/test_monitor_landing.py:
    e: _run_monitor,test_monitor_detects_unreachable_url,test_monitor_baseline_and_unchanged_prices,test_monitor_detects_price_change
    _run_monitor()
    test_monitor_detects_unreachable_url(repo_root)
    test_monitor_baseline_and_unchanged_prices(repo_root)
    test_monitor_detects_price_change(repo_root;tmp_path)
  tests/hypervisor/test_monitor_url.py:
    e: _run,test_monitor_url_ok,test_monitor_url_down,test_baseline_created_does_not_post_webhook,test_webhook_posts_on_price_change,test_placeholder_webhook_is_skipped,test_monitor_landing_notify_on_price_change
    _run(script)
    test_monitor_url_ok(repo_root)
    test_monitor_url_down(repo_root)
    test_baseline_created_does_not_post_webhook()
    test_webhook_posts_on_price_change()
    test_placeholder_webhook_is_skipped(capsys)
    test_monitor_landing_notify_on_price_change(repo_root;tmp_path)
  tests/hypervisor/test_operator_agent_packages.py:
    e: test_browser_operator_registry_is_browser_only,test_desktop_operator_registry_excludes_browser,test_device_robot_operator_registry_is_physical_only,test_browser_operator_app_loads,test_common_assertion_handler
    test_browser_operator_registry_is_browser_only(repo_root)
    test_desktop_operator_registry_excludes_browser(repo_root)
    test_device_robot_operator_registry_is_physical_only(repo_root)
    test_browser_operator_app_loads(repo_root)
    test_common_assertion_handler(repo_root)
  tests/hypervisor/test_physical_operator_separation.py:
    e: _load_operator,test_device_robot_operator_contract_is_generic_capability_agent,test_physical_domain_registry_uses_operator_uris,test_device_robot_operator_is_registered_as_package_agent
    _load_operator(repo_root)
    test_device_robot_operator_contract_is_generic_capability_agent(repo_root)
    test_physical_domain_registry_uses_operator_uris(repo_root)
    test_device_robot_operator_is_registered_as_package_agent(repo_root)
  tests/hypervisor/test_plan_runner.py:
    e: test_agent_id_from_uri,test_run_planned_uris_success,test_run_planned_uris_auto_repair_and_retry,test_run_planned_uris_skips_repair_for_non_agent_uri,test_format_plan_run_markdown_includes_repair_lines
    test_agent_id_from_uri(uri;agent_id)
    test_run_planned_uris_success(monkeypatch)
    test_run_planned_uris_auto_repair_and_retry(monkeypatch)
    test_run_planned_uris_skips_repair_for_non_agent_uri(monkeypatch)
    test_format_plan_run_markdown_includes_repair_lines()
  tests/hypervisor/test_port_conflict.py:
    e: test_classify_port_listeners_marks_foreign_process,test_port_conflict_detail_includes_probe_payload,test_port_conflict_detail_ignores_owned_listener
    test_classify_port_listeners_marks_foreign_process()
    test_port_conflict_detail_includes_probe_payload()
    test_port_conflict_detail_ignores_owned_listener()
  tests/hypervisor/test_presentation_uri.py:
    e: test_source_view_uri_from_html_shorthand,test_source_view_uri_from_html_explicit_view_prefix,test_resolve_html_presentation,test_resolve_markdown_presentation
    test_source_view_uri_from_html_shorthand()
    test_source_view_uri_from_html_explicit_view_prefix()
    test_resolve_html_presentation(monkeypatch)
    test_resolve_markdown_presentation(monkeypatch)
  tests/hypervisor/test_registry_sync.py:
    e: test_validate_run_dependencies_detects_missing_uvicorn,test_sync_deployment_port_updates_registry
    test_validate_run_dependencies_detects_missing_uvicorn()
    test_sync_deployment_port_updates_registry(tmp_path;monkeypatch)
  tests/hypervisor/test_remote_runner.py:
    e: test_build_ssh_deploy_plan,test_build_ssh_run_plan_dry_run,test_build_run_plan_ssh_delegates,test_verify_remote_deployment
    test_build_ssh_deploy_plan()
    test_build_ssh_run_plan_dry_run()
    test_build_run_plan_ssh_delegates()
    test_verify_remote_deployment(monkeypatch)
  tests/hypervisor/test_repair_supervisor.py:
    e: test_classify_port_and_health_timeout,test_incident_artifact_has_schema_and_uri,test_find_known_repair_case,test_repair_apply_syncs_registry_when_healthy_but_drifted,test_repair_apply_emits_operation_event_for_healthy_agent
    test_classify_port_and_health_timeout()
    test_incident_artifact_has_schema_and_uri(tmp_path;monkeypatch)
    test_find_known_repair_case()
    test_repair_apply_syncs_registry_when_healthy_but_drifted(tmp_path;monkeypatch)
    test_repair_apply_emits_operation_event_for_healthy_agent(tmp_path;monkeypatch)
  tests/hypervisor/test_routing_pipeline.py:
    e: test_hypervisor_resolves_canonical_route_to_operator_runtime,test_hypervisor_treats_playwright_as_adapter_not_environment,test_hypervisor_preserves_payload_session_reference,test_hypervisor_resolution_to_dict_summarizes_live_session,test_hypervisor_blocks_side_effecting_route_without_approval,test_hypervisor_dispatches_approved_route_through_uri2run,test_uri3_client_operator_call_uses_hypervisor_routing
    test_hypervisor_resolves_canonical_route_to_operator_runtime(repo_root)
    test_hypervisor_treats_playwright_as_adapter_not_environment(repo_root)
    test_hypervisor_preserves_payload_session_reference(monkeypatch;repo_root)
    test_hypervisor_resolution_to_dict_summarizes_live_session(repo_root)
    test_hypervisor_blocks_side_effecting_route_without_approval(repo_root)
    test_hypervisor_dispatches_approved_route_through_uri2run(monkeypatch;repo_root)
    test_uri3_client_operator_call_uses_hypervisor_routing(monkeypatch)
  tests/hypervisor/test_routing_policy.py:
    e: test_strict_approve_blocks_browser_without_approval,test_resolver_allows_browser_with_approval,test_strict_approve_blocks_shell_mutation_without_approval,test_health_read_allowed_without_approval
    test_strict_approve_blocks_browser_without_approval()
    test_resolver_allows_browser_with_approval(repo_root)
    test_strict_approve_blocks_shell_mutation_without_approval()
    test_health_read_allowed_without_approval()
  tests/hypervisor/test_runtime_state.py:
    e: test_build_run_plan_includes_env_and_runtime_paths,test_resolve_deployment_env_merges_uri_yaml,test_runtime_state_roundtrip,test_is_process_alive_treats_permission_error_as_alive,test_sync_runtime_health_uri_updates_network_fields,test_start_process_detach_writes_process_log
    test_build_run_plan_includes_env_and_runtime_paths()
    test_resolve_deployment_env_merges_uri_yaml(tmp_path;monkeypatch)
    test_runtime_state_roundtrip(tmp_path)
    test_is_process_alive_treats_permission_error_as_alive(monkeypatch)
    test_sync_runtime_health_uri_updates_network_fields()
    test_start_process_detach_writes_process_log(tmp_path)
  tests/hypervisor/test_schema_collab_contract.py:
    e: test_schema_collab_contract_cross_refs,test_operator_robot_state_proto_exists
    test_schema_collab_contract_cross_refs(repo_root)
    test_operator_robot_state_proto_exists(repo_root)
  tests/hypervisor/test_screenshot_analysis_agent.py:
    e: test_screenshot_analysis_agent_analyzes_operator_json_artifact,test_screenshot_analysis_agent_analyzes_png_and_detects_repeated_frame,test_screenshot_analysis_agent_prefers_screenshot_step_artifact
    test_screenshot_analysis_agent_analyzes_operator_json_artifact(tmp_path)
    test_screenshot_analysis_agent_analyzes_png_and_detects_repeated_frame(tmp_path)
    test_screenshot_analysis_agent_prefers_screenshot_step_artifact()
  tests/hypervisor/test_sprint1_autonomy.py:
    e: test_build_agent_readiness_report_separates_process_from_health,test_build_agent_readiness_report_rebind_on_port_conflict,test_build_agent_readiness_report_keeps_warnings_out_of_incidents,test_build_repair_plan_from_diagnosis,test_build_repair_plan_prioritizes_stale_runtime_before_uri_drift,test_repair_apply_verifies_after_each_playbook,test_diagnose_includes_repair_plan,test_diagnose_healthy_warning_only_has_no_repair_plan
    test_build_agent_readiness_report_separates_process_from_health()
    test_build_agent_readiness_report_rebind_on_port_conflict()
    test_build_agent_readiness_report_keeps_warnings_out_of_incidents()
    test_build_repair_plan_from_diagnosis()
    test_build_repair_plan_prioritizes_stale_runtime_before_uri_drift()
    test_repair_apply_verifies_after_each_playbook(monkeypatch)
    test_diagnose_includes_repair_plan(monkeypatch)
    test_diagnose_healthy_warning_only_has_no_repair_plan(monkeypatch)
  tests/hypervisor/test_supervise_watch.py:
    e: _read_watch_events,_healthy,_failed,test_supervise_watch_emits_health_change_only_on_signature_change,test_supervise_watch_applies_repair_backoff_for_repeated_failure,test_supervise_watch_creates_one_incident_during_backoff
    _read_watch_events(root)
    _healthy()
    _failed(code)
    test_supervise_watch_emits_health_change_only_on_signature_change(tmp_path;monkeypatch)
    test_supervise_watch_applies_repair_backoff_for_repeated_failure(tmp_path;monkeypatch)
    test_supervise_watch_creates_one_incident_during_backoff(tmp_path;monkeypatch)
  tests/hypervisor/test_system_agent_packages.py:
    e: test_hypervisor_dashboard_is_registered_as_system_agent,test_hypervisor_dashboard_contract_symlink,test_hypervisor_dashboard_app_loads,test_runtime_environments_lists_system_dashboard
    test_hypervisor_dashboard_is_registered_as_system_agent(repo_root)
    test_hypervisor_dashboard_contract_symlink(repo_root)
    test_hypervisor_dashboard_app_loads()
    test_runtime_environments_lists_system_dashboard(repo_root)
  tests/hypervisor/test_system_routing.py:
    e: test_supports_hypervisor_system_uri,test_supports_view_uri,test_call_hypervisor_system_uri_health_dry_run,test_call_system_uri_delegates_health_to_hypervisor_routing,test_call_system_uri_repair_diagnose_via_hypervisor,test_call_system_uri_view_uses_hypervisor_view_handlers
    test_supports_hypervisor_system_uri()
    test_supports_view_uri()
    test_call_hypervisor_system_uri_health_dry_run(repo_root)
    test_call_system_uri_delegates_health_to_hypervisor_routing(repo_root)
    test_call_system_uri_repair_diagnose_via_hypervisor(repo_root)
    test_call_system_uri_view_uses_hypervisor_view_handlers(monkeypatch;repo_root)
  tests/hypervisor/test_tutorial_three_agents_smoke.py:
    e: test_three_agents_tutorial_smoke_routes_core_commands,test_three_agents_tutorial_smoke_ask_batch,test_three_agents_tutorial_smoke_proof_dry_run
    test_three_agents_tutorial_smoke_routes_core_commands()
    test_three_agents_tutorial_smoke_ask_batch()
    test_three_agents_tutorial_smoke_proof_dry_run()
  tests/hypervisor/test_uri_exchange_schema.py:
    e: uri_exchange_schema,_validate,test_uri_exchange_schema_accepts_single_planner_executor,test_uri_exchange_schema_accepts_batch_planner,test_uri_exchange_schema_rejects_missing_session_id
    uri_exchange_schema()
    _validate(schema;payload)
    test_uri_exchange_schema_accepts_single_planner_executor(uri_exchange_schema)
    test_uri_exchange_schema_accepts_batch_planner(uri_exchange_schema)
    test_uri_exchange_schema_rejects_missing_session_id(uri_exchange_schema)
  tests/hypervisor/test_uri_healer.py:
    e: test_run_uri_healer_delegates_to_supervise_with_repair
    test_run_uri_healer_delegates_to_supervise_with_repair(monkeypatch)
  tests/hypervisor/test_view_routing.py:
    e: test_explain_executable_uri_operator_includes_resolution,test_resolve_view_envelope_process_without_renderer
    test_explain_executable_uri_operator_includes_resolution(repo_root)
    test_resolve_view_envelope_process_without_renderer(repo_root)
  tests/hypervisor/test_www_integrations_build.py:
    e: test_about_parser_loads_cards,test_build_landing_integrations_check,test_build_examples_manifest_check,test_examples_manifest_includes_office_chains,test_index_has_generated_integration_cards,test_spotlight_includes_full_i18n_cta_and_body,_load_integrations_module,test_all_about_cards_reused_on_website,test_index_integrations_match_fragment,test_ecommerce_cards_use_distinct_bodies
    test_about_parser_loads_cards(repo_root)
    test_build_landing_integrations_check(repo_root)
    test_build_examples_manifest_check(repo_root)
    test_examples_manifest_includes_office_chains(repo_root)
    test_index_has_generated_integration_cards(repo_root)
    test_spotlight_includes_full_i18n_cta_and_body(repo_root)
    _load_integrations_module(repo_root)
    test_all_about_cards_reused_on_website(repo_root)
    test_index_integrations_match_fragment(repo_root)
    test_ecommerce_cards_use_distinct_bodies(repo_root)
  tests/integration/__init__.py:
  tests/integration/test_flow_to_workflow_execution.py:
    e: test_compact_flow_to_dry_run,test_branching_flow_has_expected_edges,test_nl2uri_flow_expands_and_validates
    test_compact_flow_to_dry_run(repo_root)
    test_branching_flow_has_expected_edges(repo_root)
    test_nl2uri_flow_expands_and_validates()
  tests/integration/test_nl2a_e2e.py:
    e: isolated_project,test_nl2a_full_pipeline_weather_map,test_nl2a_cli_generate_no_llm
    isolated_project(tmp_path;monkeypatch)
    test_nl2a_full_pipeline_weather_map(isolated_project)
    test_nl2a_cli_generate_no_llm(isolated_project)
  tests/integration/test_uri3_uri2ops_delegation.py:
    e: test_default_operator_adapter_is_uri2ops,test_uri2ops_delegation_mock_browser_workflow
    test_default_operator_adapter_is_uri2ops()
    test_uri2ops_delegation_mock_browser_workflow(tmp_path)
  tests/meta_agent/__init__.py:
  tests/meta_agent/test_repair.py:
    e: test_repair_agent_block_fills_metadata,test_repair_resource_read_fills_renderer_and_schema,test_repair_command_fills_fields,test_repair_capabilities_deduplicates_names,test_repair_agent_spec_integration
    test_repair_agent_block_fills_metadata()
    test_repair_resource_read_fills_renderer_and_schema()
    test_repair_command_fills_fields()
    test_repair_capabilities_deduplicates_names()
    test_repair_agent_spec_integration(tmp_path)
  tests/nl2uri/test_domain_planner.py:
    e: test_normalize_bad_llm_weather_tree_uses_deterministic_template,test_plan_from_prompt_weather_no_llm_full_tree
    test_normalize_bad_llm_weather_tree_uses_deterministic_template()
    test_plan_from_prompt_weather_no_llm_full_tree()
  tests/nl2uri/test_flow_planner.py:
    e: test_classify_uri_flow_for_sequential_process,test_classify_task_prompt_as_uri_flow,test_classify_condition_stays_workflow_graph,test_plan_flow_weather_prompt,test_plan_auto_prefers_uri_flow_for_weather,test_flow_expands_to_valid_workflow_graph
    test_classify_uri_flow_for_sequential_process()
    test_classify_task_prompt_as_uri_flow()
    test_classify_condition_stays_workflow_graph()
    test_plan_flow_weather_prompt()
    test_plan_auto_prefers_uri_flow_for_weather()
    test_flow_expands_to_valid_workflow_graph()
  tests/nl2uri/test_flow_planner_llm.py:
    e: test_build_flow_planner_system_prompt_includes_compact_shape,test_plan_flow_with_llm_validates_compact_output,test_plan_flow_with_llm_converts_graph_nodes,test_plan_flow_with_llm_fallback_on_invalid,test_plan_flow_use_llm_flag
    test_build_flow_planner_system_prompt_includes_compact_shape()
    test_plan_flow_with_llm_validates_compact_output(mock_call)
    test_plan_flow_with_llm_converts_graph_nodes(mock_call)
    test_plan_flow_with_llm_fallback_on_invalid(mock_call)
    test_plan_flow_use_llm_flag(mock_plan)
  tests/nl2uri/test_flow_repair.py:
    e: test_extract_flow_payload_from_graph_nodes,test_sanitize_flow_step_drops_unknown_scheme,test_repair_flow_body_from_task_steps,test_validate_expanded_flow_accepts_weather_flow,test_repair_and_validate_flow_branching,test_repair_and_validate_flow_rejects_empty
    test_extract_flow_payload_from_graph_nodes()
    test_sanitize_flow_step_drops_unknown_scheme()
    test_repair_flow_body_from_task_steps()
    test_validate_expanded_flow_accepts_weather_flow()
    test_repair_and_validate_flow_branching()
    test_repair_and_validate_flow_rejects_empty()
  tests/nl2uri/test_graph_planner.py:
    e: test_classify_resource_tree,test_classify_task_graph,test_classify_workflow_graph,test_plan_single_status,test_plan_list_health_and_card,test_plan_tree_contains_domain_root,test_plan_screenshot_schedule_stable_id,test_plan_task_linear_steps,test_plan_workflow_generate_run_check,test_plan_auto_matches_classifier
    test_classify_resource_tree()
    test_classify_task_graph()
    test_classify_workflow_graph()
    test_plan_single_status()
    test_plan_list_health_and_card()
    test_plan_tree_contains_domain_root()
    test_plan_screenshot_schedule_stable_id()
    test_plan_task_linear_steps()
    test_plan_workflow_generate_run_check()
    test_plan_auto_matches_classifier()
  tests/nl2uri/test_graph_planner_llm.py:
    e: test_build_graph_planner_system_prompt_includes_registry,test_sanitize_node_drops_unknown_scheme,test_sanitize_node_coerces_operation,test_repair_graph_body_from_task_shape,test_extract_graph_payload_accepts_graph_nodes_top_level,test_plan_graph_with_llm_validates_output,test_plan_graph_with_llm_fallback_on_invalid,test_plan_task_use_llm_flag
    test_build_graph_planner_system_prompt_includes_registry()
    test_sanitize_node_drops_unknown_scheme()
    test_sanitize_node_coerces_operation()
    test_repair_graph_body_from_task_shape()
    test_extract_graph_payload_accepts_graph_nodes_top_level()
    test_plan_graph_with_llm_validates_output(mock_call)
    test_plan_graph_with_llm_fallback_on_invalid(mock_call)
    test_plan_task_use_llm_flag(mock_call)
  tests/nl2uri/test_weather_forecast.py:
    e: test_is_weather_forecast_prompt,test_weather_forecast_uri_from_polish_prompt,test_extract_weather_place_and_days,test_detect_weather_intent,test_ask_weather_forecast_plans_executable_uri,test_plan_weather_forecast_payload
    test_is_weather_forecast_prompt(prompt;expected)
    test_weather_forecast_uri_from_polish_prompt()
    test_extract_weather_place_and_days()
    test_detect_weather_intent()
    test_ask_weather_forecast_plans_executable_uri()
    test_plan_weather_forecast_payload()
  tests/resource_agent_factory/test_default_port.py:
    e: test_default_port_from_deployment_registry,test_default_port_falls_back_to_8101
    test_default_port_from_deployment_registry(repo_root)
    test_default_port_falls_back_to_8101(repo_root;tmp_path)
  tests/scripts/test_architecture_responsibility_audit.py:
    e: load_audit_module,write_fixture_files,test_audit_detects_cross_boundary_duplication,test_audit_ignores_stale_duplicate_symbol_when_file_changed,test_audit_flags_domain_named_generic_module_when_file_exists,test_audit_does_not_flag_domain_vocabulary_in_operator_agents,test_audit_ignores_its_own_domain_vocabulary,test_audit_cli_outputs_json
    load_audit_module(repo_root)
    write_fixture_files(tmp_path)
    test_audit_detects_cross_boundary_duplication(repo_root;tmp_path)
    test_audit_ignores_stale_duplicate_symbol_when_file_changed(repo_root;tmp_path)
    test_audit_flags_domain_named_generic_module_when_file_exists(repo_root;tmp_path)
    test_audit_does_not_flag_domain_vocabulary_in_operator_agents(repo_root;tmp_path)
    test_audit_ignores_its_own_domain_vocabulary(repo_root;tmp_path)
    test_audit_cli_outputs_json(repo_root;tmp_path)
  tests/test_capability_tests.py:
    e: test_capability_test_plan_is_built_from_registry
    test_capability_test_plan_is_built_from_registry()
  tests/test_contract_registry.py:
    e: test_contract_registry_loads_and_validates,test_user_read_capability_matches_resource_contract
    test_contract_registry_loads_and_validates()
    test_user_read_capability_matches_resource_contract()
  tests/test_cross_validation_v03.py:
    e: test_cross_validation_ok
    test_cross_validation_ok()
  tests/test_dependencies.py:
    e: test_typer_bundled_click_is_complete
    test_typer_bundled_click_is_complete()
  tests/test_evolution_proposal.py:
    e: test_evolution_proposal_validates
    test_evolution_proposal_validates()
  tests/test_generate.py:
    e: test_generate_user_agent
    test_generate_user_agent()
  tests/test_hypervisor.py:
    e: test_version_present,test_default_config_has_hypervisor_section,test_load_config_merges_user_file,test_hypervisor_object,test_hypervisor_from_config_and_limits,test_cli_status_runs,test_cli_config_path
    test_version_present()
    test_default_config_has_hypervisor_section()
    test_load_config_merges_user_file(tmp_path)
    test_hypervisor_object()
    test_hypervisor_from_config_and_limits()
    test_cli_status_runs(capsys)
    test_cli_config_path(capsys)
  tests/test_meta_agent.py:
    e: test_save_proposal_from_prompt,test_repair_broken_agent,test_pipeline_from_prompt_generates_agent
    test_save_proposal_from_prompt(tmp_path)
    test_repair_broken_agent(tmp_path)
    test_pipeline_from_prompt_generates_agent(tmp_path)
  tests/test_nl2uri.py:
    e: test_weather_prompt_generates_weather_uri_tree
    test_weather_prompt_generates_weather_uri_tree()
  tests/test_operator_task.py:
    e: test_task_validates,test_task_plan,test_task_runs_mock
    test_task_validates()
    test_task_plan()
    test_task_runs_mock()
  tests/test_policy_gate.py:
    e: test_policy_gate_allows_non_breaking_change,test_policy_gate_blocks_breaking_change_without_approval,test_policy_gate_allows_breaking_change_with_approval
    test_policy_gate_allows_non_breaking_change()
    test_policy_gate_blocks_breaking_change_without_approval()
    test_policy_gate_allows_breaking_change_with_approval()
  tests/test_registry_builder_v03.py:
    e: test_registry_manifest_contains_contract_hash,test_registry_exports
    test_registry_manifest_contains_contract_hash()
    test_registry_exports(tmp_path)
  tests/test_runtime_client.py:
    e: test_runtime_client_returns_error_when_runtime_unavailable
    test_runtime_client_returns_error_when_runtime_unavailable()
  tests/test_schema_validation_v03.py:
    e: test_schema_validation_ok
    test_schema_validation_ok()
  tests/test_uri2llm_v04.py:
    e: test_env_uri_resolution,test_llm_uri_resolution,test_pypi_uri_resolution
    test_env_uri_resolution(monkeypatch)
    test_llm_uri_resolution()
    test_pypi_uri_resolution()
  tests/test_uri3.py:
    e: test_validate_uri,test_graph_weather_tree
    test_validate_uri()
    test_graph_weather_tree()
  tests/test_uri_tree_validator.py:
    e: test_uri_tree_schema_ok
    test_uri_tree_schema_ok()
  tests/test_validate.py:
    e: test_user_agent_contract_is_valid
    test_user_agent_contract_is_valid()
  tests/uri2flow/conftest.py:
    e: repo_root
    repo_root()
  tests/uri2flow/test_cli.py:
    e: test_cli_expand
    test_cli_expand(repo_root;tmp_path)
  tests/uri2flow/test_expand_branching_flow.py:
    e: test_expand_branching_flow
    test_expand_branching_flow(repo_root)
  tests/uri2flow/test_expand_linear_flow.py:
    e: test_expand_linear_flow
    test_expand_linear_flow(repo_root)
  tests/uri2flow/test_flow_defaults.py:
    e: setup_function,test_pattern_match_hypervisor_run,test_pattern_match_hypervisor_restart,test_pattern_match_browser_open,test_pattern_match_dom_extract,test_pattern_match_screen_observe,test_pattern_match_input_type,test_scheme_default_for_http,test_fallback_for_unknown_scheme
    setup_function()
    test_pattern_match_hypervisor_run()
    test_pattern_match_hypervisor_restart()
    test_pattern_match_browser_open()
    test_pattern_match_dom_extract()
    test_pattern_match_screen_observe()
    test_pattern_match_input_type()
    test_scheme_default_for_http()
    test_fallback_for_unknown_scheme()
  tests/uri2flow/test_parser_forms.py:
    e: test_accepts_string_and_mapping_forms
    test_accepts_string_and_mapping_forms()
  tests/uri2flow/test_uri2flow_markpact_loader.py:
    e: _markpact_ref,test_is_markpact_registry,test_extract_markpact_flow_blocks,test_load_markpact_flow_dict,test_load_flow_markpact_ref,test_expand_flow_markpact_ref,test_markpact_flow_requires_fragment_when_ambiguous,test_markpact_flow_matches_yaml_flow,test_resolve_markpact_ref,test_uri2flow_expand_cli,test_missing_flow_fragment_raises,test_missing_markpact_readme_raises
    _markpact_ref(repo_root;fragment)
    test_is_markpact_registry()
    test_extract_markpact_flow_blocks()
    test_load_markpact_flow_dict(repo_root)
    test_load_flow_markpact_ref(repo_root)
    test_expand_flow_markpact_ref(repo_root)
    test_markpact_flow_requires_fragment_when_ambiguous(tmp_path)
    test_markpact_flow_matches_yaml_flow(repo_root)
    test_resolve_markpact_ref(repo_root)
    test_uri2flow_expand_cli(repo_root;tmp_path)
    test_missing_flow_fragment_raises(repo_root)
    test_missing_markpact_readme_raises(repo_root)
  tests/uri2pact/test_markpact_scenarios.py:
    e: test_load_office_markpact_scenarios,test_load_office_markpact_scenario_registry_includes_yaml
    test_load_office_markpact_scenarios(repo_root)
    test_load_office_markpact_scenario_registry_includes_yaml(repo_root)
  tests/uri2run/test_protocol_transports.py:
    e: test_docker_transport_dry_run,test_run_target_docker_scheme,test_ssh_transport_resolve_mode,test_ssh_transport_exec_mode,test_mcp_transport_list_tools,test_mcp_transport_call_tool,test_a2a_transport_agent_card,test_a2a_transport_tasks,test_run_target_mcp_scheme,test_mcp_transport_http_error
    test_docker_transport_dry_run()
    test_run_target_docker_scheme()
    test_ssh_transport_resolve_mode()
    test_ssh_transport_exec_mode(monkeypatch)
    test_mcp_transport_list_tools(monkeypatch)
    test_mcp_transport_call_tool(monkeypatch)
    test_a2a_transport_agent_card(monkeypatch)
    test_a2a_transport_tasks(monkeypatch)
    test_run_target_mcp_scheme(monkeypatch)
    test_mcp_transport_http_error(monkeypatch)
  tests/uri2run/test_stream_transports.py:
    e: test_stdio_transport_json_roundtrip,test_run_target_stdio_scheme,test_sse_transport_parses_events,test_ws_transport_without_dependency,test_uri3_workflow_python_runtime_adapter
    test_stdio_transport_json_roundtrip()
    test_run_target_stdio_scheme()
    test_sse_transport_parses_events(monkeypatch)
    test_ws_transport_without_dependency()
    test_uri3_workflow_python_runtime_adapter(tmp_path)
  tests/uri2run/test_transport_matrix.py:
    e: test_python_transport,test_shell_transport_success,test_shell_transport_failure,test_http_transport_success,test_http_transport_uses_backend_options_and_retries,test_shell_transport_supports_argv_without_shell,test_flow_transport_dry_run,test_touri_delegates_python_backend_to_uri2run,test_unsupported_transport
    test_python_transport()
    test_shell_transport_success()
    test_shell_transport_failure()
    test_http_transport_success(monkeypatch)
    test_http_transport_uses_backend_options_and_retries(monkeypatch)
    test_shell_transport_supports_argv_without_shell()
    test_flow_transport_dry_run(repo_root)
    test_touri_delegates_python_backend_to_uri2run(repo_root)
    test_unsupported_transport()
  tests/uri2run/test_uri2run.py:
    e: test_run_target_stt_mock_scheme,test_cli_call_stt_mock_scheme_outputs_json,test_run_target_python_returns_service_result,test_run_target_shell_scheme_with_args,test_run_backend_mock_returns_shared_envelope,test_cli_call_python_outputs_json,test_touri_python_backend_delegates_to_uri2run
    test_run_target_stt_mock_scheme()
    test_cli_call_stt_mock_scheme_outputs_json(capsys)
    test_run_target_python_returns_service_result()
    test_run_target_shell_scheme_with_args()
    test_run_backend_mock_returns_shared_envelope()
    test_cli_call_python_outputs_json(capsys)
    test_touri_python_backend_delegates_to_uri2run(monkeypatch)
  tests/uri2run/test_voice_resolver.py:
    e: test_resolve_stt_mock_to_python,test_resolve_stt_whisper_to_python,test_resolve_tts_mock_to_python,test_unknown_voice_uri_returns_touri_or_unresolved
    test_resolve_stt_mock_to_python()
    test_resolve_stt_whisper_to_python()
    test_resolve_tts_mock_to_python()
    test_unknown_voice_uri_returns_touri_or_unresolved()
  tests/uri2run/test_workflow_transport.py:
    e: test_flow_and_graph_transports_share_dry_run_path,test_workflow_transport_invalid_graph_uses_error_code
    test_flow_and_graph_transports_share_dry_run_path(repo_root)
    test_workflow_transport_invalid_graph_uses_error_code()
  tests/uri3/__init__.py:
  tests/uri3/test_browser_adapter.py:
    e: test_resolve_browser_mode_mock,test_mock_adapter_writes_artifact_files,test_playwright_browser_workflow
    test_resolve_browser_mode_mock()
    test_mock_adapter_writes_artifact_files(tmp_path)
    test_playwright_browser_workflow(tmp_path)
  tests/uri3/test_cli.py:
    e: runner,test_scan_shortcuts_load_defaults,test_resolve_scan_target_by_name,test_resolve_scan_target_full_uri,test_cli_list_command,test_cli_list_json,test_cli_no_args_shows_quick_reference,test_cli_scan_without_args_shows_help,test_cli_scan_shortcut_name,test_cli_scan_all,test_cli_call_docker_dry_run
    runner()
    test_scan_shortcuts_load_defaults()
    test_resolve_scan_target_by_name()
    test_resolve_scan_target_full_uri()
    test_cli_list_command(runner)
    test_cli_list_json(runner)
    test_cli_no_args_shows_quick_reference(runner)
    test_cli_scan_without_args_shows_help(runner;monkeypatch)
    test_cli_scan_shortcut_name(runner;monkeypatch)
    test_cli_scan_all(runner;monkeypatch)
    test_cli_call_docker_dry_run(runner)
  tests/uri3/test_dispatch.py:
    e: test_parse_instance_env,test_parse_instance_docker_stack,test_resolve_target_pypi
    test_parse_instance_env()
    test_parse_instance_docker_stack()
    test_resolve_target_pypi()
  tests/uri3/test_docker_control.py:
    e: test_parse_docker_stack_uri,test_resolve_docker_generate_plan,test_control_docker_up_dry_run,test_control_docker_generate_writes_file,test_control_docker_container_stop_dry_run,test_control_docker_up_recovers_from_name_conflict
    test_parse_docker_stack_uri()
    test_resolve_docker_generate_plan()
    test_control_docker_up_dry_run()
    test_control_docker_generate_writes_file(tmp_path;monkeypatch)
    test_control_docker_container_stop_dry_run()
    test_control_docker_up_recovers_from_name_conflict(monkeypatch)
  tests/uri3/test_doctor.py:
    e: test_doctor_passes_on_repo,test_doctor_build_registry_writes_indexes,test_build_registry_indexes_content
    test_doctor_passes_on_repo(repo_root)
    test_doctor_build_registry_writes_indexes(tmp_path;repo_root)
    test_build_registry_indexes_content(repo_root)
  tests/uri3/test_envelope_migrate.py:
    e: test_migrate_workflow_log_adds_status_fields
    test_migrate_workflow_log_adds_status_fields(tmp_path)
  tests/uri3/test_explain_extended.py:
    e: test_explain_includes_verification_hints,test_explain_includes_fallbacks_and_data_quality,test_explain_runtime_transport_for_stdio_backend
    test_explain_includes_verification_hints(repo_root)
    test_explain_includes_fallbacks_and_data_quality(tmp_path)
    test_explain_runtime_transport_for_stdio_backend(tmp_path)
  tests/uri3/test_explain_uri.py:
    e: test_explain_weather_uri_matches_touri,test_explain_http_uri_matches_uri3,test_explain_file_uri_matches_uri3,test_explain_browser_uri_matches_uri2ops,test_explain_unknown_scheme_denied
    test_explain_weather_uri_matches_touri(repo_root)
    test_explain_http_uri_matches_uri3(repo_root)
    test_explain_file_uri_matches_uri3(tmp_path;repo_root)
    test_explain_browser_uri_matches_uri2ops(repo_root)
    test_explain_unknown_scheme_denied(repo_root)
  tests/uri3/test_file_resolver.py:
    e: test_resolve_file_uri_returns_metadata,test_path_from_file_uri_unquotes_spaces
    test_resolve_file_uri_returns_metadata(tmp_path)
    test_path_from_file_uri_unquotes_spaces(tmp_path)
  tests/uri3/test_http_scanner.py:
    e: test_scan_http_health_uri_does_not_double_path,test_scan_http_404_health_is_error,test_health_scan_ok_requires_200
    test_scan_http_health_uri_does_not_double_path(monkeypatch)
    test_scan_http_404_health_is_error(monkeypatch)
    test_health_scan_ok_requires_200()
  tests/uri3/test_lifecycle_envelope.py:
    e: test_lifecycle_plan_payload_has_status_envelope,test_lifecycle_stopped_payload_has_status_envelope
    test_lifecycle_plan_payload_has_status_envelope()
    test_lifecycle_stopped_payload_has_status_envelope()
  tests/uri3/test_llm_profiles.py:
    e: test_load_llm_config_has_domain_planner,test_resolve_llm_profile_domain_planner,test_resolve_llm_profile_respects_default_env
    test_load_llm_config_has_domain_planner()
    test_resolve_llm_profile_domain_planner(monkeypatch)
    test_resolve_llm_profile_respects_default_env(monkeypatch)
  tests/uri3/test_log_reader_meta.py:
    e: test_read_logs_result_missing_file
    test_read_logs_result_missing_file(tmp_path;monkeypatch)
  tests/uri3/test_log_uri.py:
    e: _write_sample_log,test_resolve_log_uri,test_read_logs_with_filters,test_read_logs_from_explicit_file,test_call_log_uri_returns_entries,test_scan_log_uri,test_summarize_logs
    _write_sample_log(path)
    test_resolve_log_uri()
    test_read_logs_with_filters(tmp_path;monkeypatch)
    test_read_logs_from_explicit_file(tmp_path;monkeypatch)
    test_call_log_uri_returns_entries(tmp_path;monkeypatch)
    test_scan_log_uri(tmp_path;monkeypatch)
    test_summarize_logs(tmp_path;monkeypatch)
  tests/uri3/test_replay.py:
    e: test_replay_workflow_events_by_id,test_replay_workflow_events_by_path,test_build_task_payload_from_step_started_events,test_create_regression_test_writes_pytest
    test_replay_workflow_events_by_id(tmp_path)
    test_replay_workflow_events_by_path(tmp_path)
    test_build_task_payload_from_step_started_events(tmp_path)
    test_create_regression_test_writes_pytest(tmp_path)
  tests/uri3/test_resolvers.py:
    e: test_env_uri_resolution,test_llm_uri_resolution,test_pypi_uri_resolution,test_python_uri_resolution,test_http_uri_resolution,test_a2a_uri_resolution,test_mcp_uri_resolution,test_resource_uri_resolution,test_python_call,test_env_call_set_persists_to_dotenv,test_env_call_set_updates_existing_key,test_router_resolve_returns_uri_resolution,test_unsupported_scheme,test_deprecated_uri2llm_reexport
    test_env_uri_resolution(monkeypatch)
    test_llm_uri_resolution()
    test_pypi_uri_resolution()
    test_python_uri_resolution()
    test_http_uri_resolution()
    test_a2a_uri_resolution()
    test_mcp_uri_resolution()
    test_resource_uri_resolution()
    test_python_call()
    test_env_call_set_persists_to_dotenv(tmp_path;monkeypatch)
    test_env_call_set_updates_existing_key(tmp_path;monkeypatch)
    test_router_resolve_returns_uri_resolution()
    test_unsupported_scheme()
    test_deprecated_uri2llm_reexport()
  tests/uri3/test_result_envelope.py:
    e: test_uri3_workflow_result_includes_status_envelope,test_uri3_workflow_blocked_has_failed_service_status,test_uri2ops_task_result_includes_status_envelope
    test_uri3_workflow_result_includes_status_envelope(tmp_path)
    test_uri3_workflow_blocked_has_failed_service_status()
    test_uri2ops_task_result_includes_status_envelope(tmp_path)
  tests/uri3/test_router_call.py:
    e: test_resolve_docker_stack,test_call_docker_stack_dry_run
    test_resolve_docker_stack()
    test_call_docker_stack_dry_run()
  tests/uri3/test_schema.py:
    e: test_normalize_scheme,test_get_scheme_schema_log,test_get_scheme_schema_unknown,test_list_schemes_includes_log,test_analyze_concrete_log_uri,test_analyze_invalid_log_uri,test_describe_scheme_only,test_describe_concrete_uri,test_cli_schema_log_scheme,test_cli_schema_list,test_cli_schema_analyze
    test_normalize_scheme()
    test_get_scheme_schema_log()
    test_get_scheme_schema_unknown()
    test_list_schemes_includes_log()
    test_analyze_concrete_log_uri()
    test_analyze_invalid_log_uri()
    test_describe_scheme_only()
    test_describe_concrete_uri()
    test_cli_schema_log_scheme()
    test_cli_schema_list()
    test_cli_schema_analyze()
  tests/uri3/test_service_result.py:
    e: test_service_result_finalize_sets_three_status_levels,test_error_envelope_normalizes_legacy_detail,test_success_service_result
    test_service_result_finalize_sets_three_status_levels()
    test_error_envelope_normalizes_legacy_detail()
    test_success_service_result()
  tests/uri3/test_ssh_auth.py:
    e: test_resolve_ssh_password_from_env,test_resolve_ssh_password_from_profile,test_build_ssh_command_uses_sshpass_when_password_set,test_ssh_auth_hint_on_permission_denied
    test_resolve_ssh_password_from_env(monkeypatch)
    test_resolve_ssh_password_from_profile(tmp_path;monkeypatch)
    test_build_ssh_command_uses_sshpass_when_password_set(monkeypatch)
    test_ssh_auth_hint_on_permission_denied(monkeypatch)
  tests/uri3/test_ssh_scanner.py:
    e: test_parse_ssh_uri,test_parse_ssh_uri_requires_host,test_scan_ssh_invalid_uri,test_resolve_ssh_alias,test_scan_ssh_unreachable,test_scan_ssh_success
    test_parse_ssh_uri()
    test_parse_ssh_uri_requires_host()
    test_scan_ssh_invalid_uri()
    test_resolve_ssh_alias()
    test_scan_ssh_unreachable(monkeypatch)
    test_scan_ssh_success(monkeypatch)
  tests/uri3/test_uri_yaml.py:
    e: test_is_uri,test_load_llm_uri_yaml,test_load_uri_yaml_unwraps_artifact_envelope,test_resolve_uri_values_keeps_secrets_by_default
    test_is_uri()
    test_load_llm_uri_yaml()
    test_load_uri_yaml_unwraps_artifact_envelope()
    test_resolve_uri_values_keeps_secrets_by_default()
  tests/uri3/test_workflow_executor.py:
    e: test_run_workflow_dry_run_completes,test_run_workflow_blocks_command_without_approve,test_run_workflow_execute_mock_with_approve,test_run_workflow_accepts_workflow_graph_object,test_run_workflow_skips_conditional_branch,test_run_workflow_service_failure_uses_completed_with_service_error
    test_run_workflow_dry_run_completes()
    test_run_workflow_blocks_command_without_approve()
    test_run_workflow_execute_mock_with_approve(tmp_path)
    test_run_workflow_accepts_workflow_graph_object(tmp_path)
    test_run_workflow_skips_conditional_branch(tmp_path)
    test_run_workflow_service_failure_uses_completed_with_service_error(tmp_path)
  tests/uri3/test_workflow_graph.py:
    e: test_load_task_payload,test_validate_task_payload,test_execution_plan_order,test_detect_cycle
    test_load_task_payload()
    test_validate_task_payload()
    test_execution_plan_order()
    test_detect_cycle()
  tests/urigen/test_urigen_cycle.py:
    e: test_plan_generate_verify_explain_cycle,test_profile_aliases_are_canonicalized,test_apply_plan_and_transaction,_setup_apply_tmp,test_apply_plan_includes_diff,test_apply_idempotent_second_run,test_apply_failure_rolls_back_created_files,test_apply_manual_rollback_restores_files,test_proposal_and_ecosystem_have_envelope,test_plan_and_verify_do_not_touch_repo_roots,test_cli_plan_generate_verify,test_cli_profiles_lists_aliases
    test_plan_generate_verify_explain_cycle(tmp_path)
    test_profile_aliases_are_canonicalized()
    test_apply_plan_and_transaction(tmp_path;repo_root)
    _setup_apply_tmp(tmp_path;repo_root)
    test_apply_plan_includes_diff(tmp_path;repo_root)
    test_apply_idempotent_second_run(tmp_path;repo_root)
    test_apply_failure_rolls_back_created_files(tmp_path;repo_root;monkeypatch)
    test_apply_manual_rollback_restores_files(tmp_path;repo_root)
    test_proposal_and_ecosystem_have_envelope(tmp_path)
    test_plan_and_verify_do_not_touch_repo_roots(tmp_path;repo_root)
    test_cli_plan_generate_verify(tmp_path)
    test_cli_profiles_lists_aliases(capsys)
  tests/urish/test_agent_backend.py:
    e: test_agent_action_run_forwards_detach_once
    test_agent_action_run_forwards_detach_once()
  tests/urish/test_agent_factory.py:
    e: test_detect_agent_factory_intent,test_dashboard_prompt_still_uses_ecosystem_intent,test_build_agent_contract_from_uri_prompt,test_build_agent_contract_from_robot_uri_prompt,test_ask_agent_factory_returns_lifecycle_steps,test_generate_agent_dry_run_does_not_write,test_ssh_prompt_plans_remote_deployment,test_ssh_keyword_uses_default_target,test_ask_ssh_prompt_includes_deploy_steps
    test_detect_agent_factory_intent()
    test_dashboard_prompt_still_uses_ecosystem_intent()
    test_build_agent_contract_from_uri_prompt()
    test_build_agent_contract_from_robot_uri_prompt()
    test_ask_agent_factory_returns_lifecycle_steps()
    test_generate_agent_dry_run_does_not_write(tmp_path)
    test_ssh_prompt_plans_remote_deployment(tmp_path)
    test_ssh_keyword_uses_default_target(tmp_path)
    test_ask_ssh_prompt_includes_deploy_steps()
  tests/urish/test_ask_dashboard.py:
    e: test_detect_dashboard_agent_intent,test_detect_agent_process_view_intent,test_detect_agent_diagnose_intent,test_detect_agent_health_intent,test_ask_agent_process_view_plans_hypervisor_uri,test_ask_agent_diagnose_plans_repair_uri,test_screenshot_prompt_uses_workflow_not_domain,test_screenshot_prompt_plans_stable_workflow_uri,test_screenshot_polish_inflection_detects_workflow,test_weather_forecast_prompt_plans_weather_uri,test_detect_www_chat_dashboard_intent_without_agent_word,test_ask_dashboard_includes_generate_and_semantic_id,test_plan_ecosystem_dashboard_profile,test_dashboard_ecosystem_generate_verify,test_dashboard_create_plan_only
    test_detect_dashboard_agent_intent()
    test_detect_agent_process_view_intent()
    test_detect_agent_diagnose_intent()
    test_detect_agent_health_intent()
    test_ask_agent_process_view_plans_hypervisor_uri()
    test_ask_agent_diagnose_plans_repair_uri()
    test_screenshot_prompt_uses_workflow_not_domain()
    test_screenshot_prompt_plans_stable_workflow_uri()
    test_screenshot_polish_inflection_detects_workflow()
    test_weather_forecast_prompt_plans_weather_uri()
    test_detect_www_chat_dashboard_intent_without_agent_word()
    test_ask_dashboard_includes_generate_and_semantic_id()
    test_plan_ecosystem_dashboard_profile()
    test_dashboard_ecosystem_generate_verify(tmp_path)
    test_dashboard_create_plan_only()
  tests/urish/test_call_routing.py:
    e: test_dashboard_view_uris_are_system,test_weather_like_view_uris_are_not_system,test_misrouted_view_forecast_does_not_raise
    test_dashboard_view_uris_are_system()
    test_weather_like_view_uris_are_not_system()
    test_misrouted_view_forecast_does_not_raise(monkeypatch)
  tests/urish/test_desktop_policy.py:
    e: test_desktop_operator_policy_distinguishes_reads_and_mutations,test_desktop_mutations_default_to_real_in_dev_policy
    test_desktop_operator_policy_distinguishes_reads_and_mutations()
    test_desktop_mutations_default_to_real_in_dev_policy()
  tests/urish/test_office_intent.py:
    e: test_detect_office_invoice_batch,test_detect_office_portal_report,test_detect_office_bank_transfer,test_detect_office_invoice_status,test_agent_diagnose_still_wins_over_office,test_ask_office_invoice_batch,test_detect_office_ecommerce_sync,test_detect_office_allegro_erp_failure,test_ask_office_ecommerce_sync
    test_detect_office_invoice_batch()
    test_detect_office_portal_report()
    test_detect_office_bank_transfer()
    test_detect_office_invoice_status()
    test_agent_diagnose_still_wins_over_office()
    test_ask_office_invoice_batch()
    test_detect_office_ecommerce_sync()
    test_detect_office_allegro_erp_failure()
    test_ask_office_ecommerce_sync()
  tests/urish/test_office_scenarios.py:
    e: test_landing_quote_maps_to_scenario,test_ask_landing_quote_returns_card_uris,test_office_scenario_count_matches_landing
    test_landing_quote_maps_to_scenario(scenario_id;subtype;prompt;expected_uri)
    test_ask_landing_quote_returns_card_uris(scenario_id;_subtype;prompt;_expected_uri)
    test_office_scenario_count_matches_landing()
  tests/urish/test_physical_policy.py:
    e: test_physical_operator_policy_distinguishes_reads_and_mutations,test_physical_mutations_default_to_real_in_dev_policy
    test_physical_operator_policy_distinguishes_reads_and_mutations()
    test_physical_mutations_default_to_real_in_dev_policy()
  tests/urish/test_prompt_split.py:
    e: test_split_nl_commands_single_line,test_split_nl_commands_multiline,test_ask_prompt_batch
    test_split_nl_commands_single_line()
    test_split_nl_commands_multiline()
    test_ask_prompt_batch()
  tests/urish/test_render.py:
    e: test_render_view_fallback_helper,test_render_view_summary_in_text_mode
    test_render_view_fallback_helper()
    test_render_view_summary_in_text_mode()
  tests/urish/test_repl.py:
    e: test_parse_repl_line_bare_uri_real_mode_by_default,test_parse_repl_line_bare_uri_dry_run_mode,test_parse_repl_line_repair_apply_adds_approve_in_real_mode,test_parse_repl_line_dry_run_uri_skips_approve_in_real_mode,test_parse_repl_line_natural_language_uses_ask_without_dry_run_by_default,test_parse_repl_line_natural_language_ask_dry_run_when_enabled,test_parse_repl_line_explicit_command_passthrough,test_parse_repl_line_meta_help_returns_none,test_main_empty_argv_starts_repl,test_run_repl_executes_uri_line,test_execute_cli_argv_view_uri
    test_parse_repl_line_bare_uri_real_mode_by_default()
    test_parse_repl_line_bare_uri_dry_run_mode()
    test_parse_repl_line_repair_apply_adds_approve_in_real_mode()
    test_parse_repl_line_dry_run_uri_skips_approve_in_real_mode()
    test_parse_repl_line_natural_language_uses_ask_without_dry_run_by_default()
    test_parse_repl_line_natural_language_ask_dry_run_when_enabled()
    test_parse_repl_line_explicit_command_passthrough()
    test_parse_repl_line_meta_help_returns_none(capsys)
    test_main_empty_argv_starts_repl()
    test_run_repl_executes_uri_line()
    test_execute_cli_argv_view_uri(monkeypatch)
  tests/urish/test_scenario_registry_boundary.py:
    e: test_office_scenarios_are_loaded_from_domains_registry,test_urish_has_no_office_specific_compat_modules
    test_office_scenarios_are_loaded_from_domains_registry()
    test_urish_has_no_office_specific_compat_modules(repo_root)
  tests/urish/test_ticket_workflow.py:
    e: _write_ticket,test_detect_dashboard_intent_from_ticket,test_ticket_workflow_includes_ecosystem_steps,test_show_ticket_returns_next_steps,test_evolve_from_ticket_generates_proposal_and_steps,test_doctor_strict_adds_artifact_checks,test_cli_doctor_strict_flag
    _write_ticket(tmp_path)
    test_detect_dashboard_intent_from_ticket()
    test_ticket_workflow_includes_ecosystem_steps()
    test_show_ticket_returns_next_steps(tmp_path)
    test_evolve_from_ticket_generates_proposal_and_steps(tmp_path)
    test_doctor_strict_adds_artifact_checks()
    test_cli_doctor_strict_flag()
  tests/urish/test_urish_cli.py:
    e: test_load_payload_from_json,test_load_payload_from_file,test_load_payload_stdin_envelope,test_render_text_view_summary,test_render_text_envelope,test_shortcuts_load,test_shortcut_specs_preserve_payload,test_cli_call_python_mock,test_cli_default_uri_invokes_call,test_cli_plan_passes_plain_defaults_to_call_backend,test_cli_call_accepts_payload_at_file,test_cli_call_shortcut_uses_default_payload,test_cli_call_shortcut_explicit_payload_wins,test_resolve_target_uri_passthrough,test_policy_blocks_mutation_without_approval,test_policy_allows_read,test_policy_force_dry_run,test_classify_repair_uri,test_classify_repair_diagnose_uri_as_read,test_select_from_envelope,test_cli_ask_command,test_cli_select_command,test_cli_policy_blocked_exit_code,test_cli_ticket_list,test_cli_repair_diagnose,test_cli_watch_limited,test_cli_proof_summarizes_one_uri,test_cli_ecosystem_generate_command,test_cli_ecosystem_profiles_command,test_cli_dashboard_create_plan_only,test_cli_agent_run_passes_detach_once,test_cli_agent_create_dashboard_alias,test_cli_www_create_from_nl_prompt,test_cli_agent_describe_does_not_crash_on_typer_signature,test_cli_agent_describe_writes_output
    test_load_payload_from_json()
    test_load_payload_from_file(tmp_path)
    test_load_payload_stdin_envelope()
    test_render_text_view_summary()
    test_render_text_envelope()
    test_shortcuts_load()
    test_shortcut_specs_preserve_payload()
    test_cli_call_python_mock()
    test_cli_default_uri_invokes_call()
    test_cli_plan_passes_plain_defaults_to_call_backend()
    test_cli_call_accepts_payload_at_file(tmp_path)
    test_cli_call_shortcut_uses_default_payload()
    test_cli_call_shortcut_explicit_payload_wins()
    test_resolve_target_uri_passthrough()
    test_policy_blocks_mutation_without_approval()
    test_policy_allows_read()
    test_policy_force_dry_run()
    test_classify_repair_uri()
    test_classify_repair_diagnose_uri_as_read()
    test_select_from_envelope()
    test_cli_ask_command()
    test_cli_select_command()
    test_cli_policy_blocked_exit_code()
    test_cli_ticket_list()
    test_cli_repair_diagnose()
    test_cli_watch_limited()
    test_cli_proof_summarizes_one_uri(capsys)
    test_cli_ecosystem_generate_command(tmp_path)
    test_cli_ecosystem_profiles_command()
    test_cli_dashboard_create_plan_only()
    test_cli_agent_run_passes_detach_once()
    test_cli_agent_create_dashboard_alias()
    test_cli_www_create_from_nl_prompt()
    test_cli_agent_describe_does_not_crash_on_typer_signature()
    test_cli_agent_describe_writes_output(tmp_path)
  tests/urish/test_workflow_run.py:
    e: test_run_workflow_uri_dry_run,test_explain_workflow_order_resolves_touri,test_run_workflow_supplier_report,test_run_workflow_portal_zus_dry_run,test_run_workflow_bank_batch_dry_run,test_explain_cron_uri_resolves_touri,test_run_cron_www_monitor_dry_run,test_call_health_agent_system_uri,test_call_cron_uri_uses_touri_backend,test_call_device_uri_uses_hypervisor_operator_routing
    test_run_workflow_uri_dry_run()
    test_explain_workflow_order_resolves_touri()
    test_run_workflow_supplier_report()
    test_run_workflow_portal_zus_dry_run()
    test_run_workflow_bank_batch_dry_run()
    test_explain_cron_uri_resolves_touri()
    test_run_cron_www_monitor_dry_run()
    test_call_health_agent_system_uri()
    test_call_cron_uri_uses_touri_backend(monkeypatch)
    test_call_device_uri_uses_hypervisor_operator_routing(monkeypatch)
  www/api-bridge/bridge.py:
    e: envelope,run_cmd,health,call_uri,preview_uri,agents,events,ask,UriCall,AskCall
    UriCall:
    AskCall:
    envelope(ok;result_type;data)
    run_cmd(args;timeout)
    health()
    call_uri(body)
    preview_uri(body)
    agents()
    events(limit)
    ask(body)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('hypervisor', '0.5.28', 'python').

% ── Project Files ────────────────────────────────────────
project_file('agents/__init__.py', 2, 'python').
project_file('agents/custom/__init__.py', 1, 'python').
project_file('agents/custom/gnome_programmer_agent/__init__.py', 1, 'python').
project_file('agents/custom/gnome_programmer_agent/agent_card.py', 29, 'python').
project_file('agents/custom/gnome_programmer_agent/main.py', 13, 'python').
project_file('agents/custom/gnome_programmer_agent/programmer.py', 185, 'python').
project_file('agents/custom/gnome_programmer_agent/routes.py', 74, 'python').
project_file('agents/custom/remote_deploy_agent/__init__.py', 1, 'python').
project_file('agents/custom/remote_deploy_agent/agent_card.py', 41, 'python').
project_file('agents/custom/remote_deploy_agent/deploy.py', 91, 'python').
project_file('agents/custom/remote_deploy_agent/main.py', 13, 'python').
project_file('agents/custom/remote_deploy_agent/routes.py', 70, 'python').
project_file('agents/custom/screenshot_analysis_agent/__init__.py', 3, 'python').
project_file('agents/custom/screenshot_analysis_agent/agent_card.py', 56, 'python').
project_file('agents/custom/screenshot_analysis_agent/analysis.py', 266, 'python').
project_file('agents/custom/screenshot_analysis_agent/main.py', 13, 'python').
project_file('agents/custom/screenshot_analysis_agent/routes.py', 81, 'python').
project_file('agents/generated/__init__.py', 1, 'python').
project_file('agents/generated/codex_nl_plan_agent/__init__.py', 5, 'python').
project_file('agents/generated/codex_nl_plan_agent/agent_card.py', 42, 'python').
project_file('agents/generated/codex_nl_plan_agent/main.py', 21, 'python').
project_file('agents/generated/codex_nl_plan_agent/routes.py', 147, 'python').
project_file('agents/generated/codex_nl_plan_agent/tests/test_contract.py', 21, 'python').
project_file('agents/generated/codex_nl_smoke_agent/__init__.py', 5, 'python').
project_file('agents/generated/codex_nl_smoke_agent/agent_card.py', 42, 'python').
project_file('agents/generated/codex_nl_smoke_agent/main.py', 21, 'python').
project_file('agents/generated/codex_nl_smoke_agent/routes.py', 147, 'python').
project_file('agents/generated/codex_nl_smoke_agent/tests/test_contract.py', 21, 'python').
project_file('agents/generated/codex_uri_smoke_agent/__init__.py', 5, 'python').
project_file('agents/generated/codex_uri_smoke_agent/agent_card.py', 39, 'python').
project_file('agents/generated/codex_uri_smoke_agent/main.py', 20, 'python').
project_file('agents/generated/codex_uri_smoke_agent/routes.py', 147, 'python').
project_file('agents/generated/codex_uri_smoke_agent/tests/test_contract.py', 21, 'python').
project_file('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/__init__.py', 5, 'python').
project_file('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/agent_card.py', 21, 'python').
project_file('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/main.py', 20, 'python').
project_file('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', 139, 'python').
project_file('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/tests/test_contract.py', 21, 'python').
project_file('agents/generated/gnome_programmer_agent/__init__.py', 5, 'python').
project_file('agents/generated/gnome_programmer_agent/agent_card.py', 43, 'python').
project_file('agents/generated/gnome_programmer_agent/main.py', 20, 'python').
project_file('agents/generated/gnome_programmer_agent/routes.py', 153, 'python').
project_file('agents/generated/gnome_programmer_agent/tests/test_contract.py', 21, 'python').
project_file('agents/generated/hypervisor_dashboard_agent/__init__.py', 5, 'python').
project_file('agents/generated/hypervisor_dashboard_agent/agent_card.py', 68, 'python').
project_file('agents/generated/hypervisor_dashboard_agent/main.py', 20, 'python').
project_file('agents/generated/hypervisor_dashboard_agent/routes.py', 166, 'python').
project_file('agents/generated/hypervisor_dashboard_agent/tests/test_contract.py', 21, 'python').
project_file('agents/generated/invoices_agent/__init__.py', 5, 'python').
project_file('agents/generated/invoices_agent/agent_card.py', 42, 'python').
project_file('agents/generated/invoices_agent/main.py', 20, 'python').
project_file('agents/generated/invoices_agent/routes.py', 149, 'python').
project_file('agents/generated/invoices_agent/tests/test_contract.py', 21, 'python').
project_file('agents/generated/remote_deploy_agent/__init__.py', 5, 'python').
project_file('agents/generated/remote_deploy_agent/agent_card.py', 62, 'python').
project_file('agents/generated/remote_deploy_agent/main.py', 20, 'python').
project_file('agents/generated/remote_deploy_agent/routes.py', 167, 'python').
project_file('agents/generated/remote_deploy_agent/tests/test_contract.py', 21, 'python').
project_file('agents/generated/schema_collab_agent/__init__.py', 5, 'python').
project_file('agents/generated/schema_collab_agent/agent_card.py', 51, 'python').
project_file('agents/generated/schema_collab_agent/main.py', 22, 'python').
project_file('agents/generated/schema_collab_agent/routes.py', 151, 'python').
project_file('agents/generated/schema_collab_agent/tests/test_contract.py', 21, 'python').
project_file('agents/generated/screenshot_analysis_agent/__init__.py', 5, 'python').
project_file('agents/generated/screenshot_analysis_agent/agent_card.py', 43, 'python').
project_file('agents/generated/screenshot_analysis_agent/main.py', 20, 'python').
project_file('agents/generated/screenshot_analysis_agent/routes.py', 153, 'python').
project_file('agents/generated/screenshot_analysis_agent/tests/test_contract.py', 21, 'python').
project_file('agents/generated/user_agent/__init__.py', 5, 'python').
project_file('agents/generated/user_agent/agent_card.py', 48, 'python').
project_file('agents/generated/user_agent/main.py', 20, 'python').
project_file('agents/generated/user_agent/routes.py', 156, 'python').
project_file('agents/generated/user_agent/tests/test_contract.py', 21, 'python').
project_file('agents/generated/weather_map_agent/__init__.py', 5, 'python').
project_file('agents/generated/weather_map_agent/agent_card.py', 32, 'python').
project_file('agents/generated/weather_map_agent/main.py', 20, 'python').
project_file('agents/generated/weather_map_agent/routes.py', 145, 'python').
project_file('agents/generated/weather_map_agent/tests/test_contract.py', 21, 'python').
project_file('agents/operators/__init__.py', 2, 'python').
project_file('agents/operators/browser_operator/__init__.py', 1, 'python').
project_file('agents/operators/browser_operator/adapters/__init__.py', 1, 'python').
project_file('agents/operators/browser_operator/adapters/browser_mock.py', 78, 'python').
project_file('agents/operators/browser_operator/adapters/browser_playwright.py', 322, 'python').
project_file('agents/operators/browser_operator/adapters/browser_playwright_worker.py', 86, 'python').
project_file('agents/operators/browser_operator/adapters/browser_router.py', 89, 'python').
project_file('agents/operators/browser_operator/main.py', 12, 'python').
project_file('agents/operators/common/__init__.py', 2, 'python').
project_file('agents/operators/common/assertion.py', 13, 'python').
project_file('agents/operators/desktop_operator/__init__.py', 1, 'python').
project_file('agents/operators/desktop_operator/adapters/__init__.py', 1, 'python').
project_file('agents/operators/desktop_operator/adapters/android_adb.py', 144, 'python').
project_file('agents/operators/desktop_operator/adapters/android_mock.py', 57, 'python').
project_file('agents/operators/desktop_operator/adapters/android_router.py', 55, 'python').
project_file('agents/operators/desktop_operator/adapters/android_uri.py', 27, 'python').
project_file('agents/operators/desktop_operator/adapters/input_gnome.py', 52, 'python').
project_file('agents/operators/desktop_operator/adapters/input_mock.py', 13, 'python').
project_file('agents/operators/desktop_operator/adapters/input_router.py', 37, 'python').
project_file('agents/operators/desktop_operator/adapters/pcwin_mock.py', 39, 'python').
project_file('agents/operators/desktop_operator/adapters/pcwin_router.py', 50, 'python').
project_file('agents/operators/desktop_operator/adapters/pcwin_uia.py', 94, 'python').
project_file('agents/operators/desktop_operator/adapters/pcwin_uri.py', 48, 'python').
project_file('agents/operators/desktop_operator/adapters/screen_gnome.py', 140, 'python').
project_file('agents/operators/desktop_operator/adapters/screen_mock.py', 11, 'python').
project_file('agents/operators/desktop_operator/adapters/screen_router.py', 37, 'python').
project_file('agents/operators/desktop_operator/main.py', 12, 'python').
project_file('agents/operators/device_robot_operator/__init__.py', 1, 'python').
project_file('agents/operators/device_robot_operator/adapters/__init__.py', 1, 'python').
project_file('agents/operators/device_robot_operator/adapters/physical_mock.py', 134, 'python').
project_file('agents/operators/device_robot_operator/main.py', 12, 'python').
project_file('agents/operators/operator_runtime.py', 34, 'python').
project_file('agents/system/__init__.py', 2, 'python').
project_file('agents/system/hypervisor_dashboard/__init__.py', 2, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/__init__.py', 1, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/agent_card.py', 75, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', 388, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', 286, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/main.py', 25, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/models.py', 83, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/monitor_webhook.py', 128, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/paths.py', 14, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/plan_runner.py', 174, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/policy.py', 55, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/presentation.py', 83, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 417, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/static/dashboard.css', 63, 'css').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/static/dashboard.js', 62, 'javascript').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', 335, 'python').
project_file('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/view_builder.py', 71, 'python').
project_file('agents/system/hypervisor_dashboard/main.py', 8, 'python').
project_file('app.doql.less', 431, 'less').
project_file('domains/__init__.py', 1, 'python').
project_file('domains/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html/__init__.py', 1, 'python').
project_file('domains/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html/handlers/__init__.py', 1, 'python').
project_file('domains/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html/handlers/run.py', 6, 'python').
project_file('domains/weather_map/__init__.py', 1, 'python').
project_file('domains/weather_map/handlers/__init__.py', 1, 'python').
project_file('domains/weather_map/handlers/generate_weather_map.py', 31, 'python').
project_file('domains/weather_map/planner.py', 62, 'python').
project_file('examples/01_quickstart_local/run.sh', 9, 'shell').
project_file('examples/04_nl2a_weather_map/run.sh', 8, 'shell').
project_file('examples/09_run_agent_hypervisor/run.sh', 8, 'shell').
project_file('examples/10_browser_operator/run.sh', 6, 'shell').
project_file('examples/11_playwright_browser/run.sh', 86, 'shell').
project_file('examples/12_android_operator/run.sh', 9, 'shell').
project_file('examples/13_nl2uri_multi_uri_graph/run.sh', 46, 'shell').
project_file('examples/13_pcwin_operator/run.sh', 9, 'shell').
project_file('examples/14_uri2ops_serve/run.sh', 21, 'shell').
project_file('examples/14_workflow_executor_mock/run.sh', 40, 'shell').
project_file('examples/15_compact_uri_flow/run.sh', 8, 'shell').
project_file('examples/16_llm_graph_planner/run.sh', 20, 'shell').
project_file('examples/17_flow_vs_graph/run.sh', 20, 'shell').
project_file('examples/18_llm_flow_planner/run.sh', 35, 'shell').
project_file('examples/20_touri_capabilities/run.sh', 11, 'shell').
project_file('examples/21_touri_voice/run.sh', 77, 'shell').
project_file('examples/21_touri_voice/touri_examples_voice/__init__.py', 1, 'python').
project_file('examples/21_touri_voice/touri_examples_voice/stt.py', 8, 'python').
project_file('examples/21_touri_voice/touri_examples_voice/tts.py', 6, 'python').
project_file('examples/21_touri_voice/touri_examples_voice/voice_command.py', 6, 'python').
project_file('examples/22_markpact_weather/run.sh', 27, 'shell').
project_file('examples/23_nl_to_agent_tutorial/run.sh', 205, 'shell').
project_file('examples/30_golden_path/run.sh', 26, 'shell').
project_file('examples/31_office_day/run.sh', 55, 'shell').
project_file('examples/32_ecommerce_integrations/run.sh', 18, 'shell').
project_file('examples/33_office_workflows/run.sh', 42, 'shell').
project_file('examples/34_cron_uri/run.sh', 35, 'shell').
project_file('examples/35_website_screenshot_schedule/run.sh', 38, 'shell').
project_file('examples/36_physical_ops/run.sh', 15, 'shell').
project_file('examples/37_agent_screenshot_analysis/run.sh', 87, 'shell').
project_file('examples/38_autonomous_agents/run.sh', 94, 'shell').
project_file('packages/resource-agent-factory/agents/generated/orders_agent/__init__.py', 5, 'python').
project_file('packages/resource-agent-factory/agents/generated/orders_agent/agent_card.py', 37, 'python').
project_file('packages/resource-agent-factory/agents/generated/orders_agent/main.py', 16, 'python').
project_file('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', 90, 'python').
project_file('packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py', 18, 'python').
project_file('packages/resource-agent-factory/agents/generated/user_agent/__init__.py', 5, 'python').
project_file('packages/resource-agent-factory/agents/generated/user_agent/agent_card.py', 63, 'python').
project_file('packages/resource-agent-factory/agents/generated/user_agent/main.py', 16, 'python').
project_file('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 96, 'python').
project_file('packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py', 18, 'python').
project_file('packages/resource-agent-factory/generator/__init__.py', 1, 'python').
project_file('packages/resource-agent-factory/generator/agent_generator.py', 133, 'python').
project_file('packages/resource-agent-factory/generator/hashutil.py', 10, 'python').
project_file('packages/resource-agent-factory/generator/header.py', 57, 'python').
project_file('packages/resource-agent-factory/generator/model.py', 95, 'python').
project_file('packages/resource-agent-factory/generator/paths.py', 13, 'python').
project_file('packages/resource-agent-factory/generator/validate.py', 70, 'python').
project_file('packages/resource-agent-factory/generator/verify.py', 84, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/__init__.py', 14, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/_version.py', 21, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', 678, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/artifacts/__init__.py', 4, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', 309, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/cli.py', 564, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 160, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/compatibility/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/compatibility/checker.py', 44, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/__init__.py', 25, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/config_checks.py', 51, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/defaults.py', 64, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/env.py', 55, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/loader.py', 97, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/models.py', 159, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/uri_config.py', 41, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/validators.py', 34, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cli.py', 42, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py', 66, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/__init__.py', 10, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/capabilities.py', 69, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/proto_index.py', 17, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/resources.py', 23, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py', 43, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py', 81, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/merge_helpers.py', 62, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/merger.py', 27, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/models.py', 57, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py', 61, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/__init__.py', 5, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/capabilities.py', 60, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/resources.py', 27, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_exporter.py', 30, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', 55, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', 563, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/validate.py', 14, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/core.py', 85, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/__init__.py', 66, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/aliases.py', 35, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/docker_runner.py', 77, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env.py', 51, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_config.py', 29, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_merge.py', 32, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py', 67, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/__init__.py', 14, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py', 185, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/pipeline.py', 232, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/probe.py', 149, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/readiness.py', 93, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', 424, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle_status.py', 68, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', 88, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', 121, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_verify.py', 40, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', 125, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_conflict.py', 78, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_utils.py', 63, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process.py', 58, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process_discovery.py', 125, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/registry_sync.py', 69, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/remote_runner.py', 17, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 305, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_plans.py', 34, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runner.py', 38, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 296, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/selector.py', 77, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_deploy.py', 96, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_helpers.py', 15, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_run.py', 119, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_verify.py', 39, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 189, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', 240, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py', 200, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', 409, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py', 46, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/__init__.py', 32, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/agent_contract.py', 49, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/commands.py', 19, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/handlers.py', 11, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/proto.py', 9, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/renderers.py', 15, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/resources.py', 25, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/views.py', 17, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 76, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/model.py', 26, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/pack_writer.py', 94, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/parser.py', 18, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 122, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/writer.py', 12, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/events.py', 87, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/cli.py', 34, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/models.py', 33, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/proposal_from_source.py', 128, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/validator.py', 46, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/integrations/planfile/__init__.py', 14, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/integrations/planfile/ticket_mapper.py', 96, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/paths.py', 77, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/policy_gate/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py', 27, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/__init__.py', 18, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/classifier.py', 139, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/healer.py', 36, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', 182, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/models.py', 64, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/plan_builder.py', 109, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py', 135, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/policy.py', 72, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/proposal_builder.py', 36, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/registry.py', 59, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/sandbox.py', 50, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py', 382, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/repair/validator.py', 52, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/__init__.py', 40, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/dispatcher.py', 74, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/explain.py', 75, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/models.py', 64, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/policy.py', 138, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/registry_bridge.py', 60, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/resolver.py', 148, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', 176, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', 306, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/system_request.py', 51, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py', 139, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/views/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/routing/views/process.py', 105, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri/client.py', 74, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/__init__.py', 16, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/env_resolver.py', 6, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/function_resolver.py', 6, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/llm_resolver.py', 6, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/protocol_resolver.py', 11, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/pypi_resolver.py', 6, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/router.py', 6, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/verifier/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/verifier/capability_tests.py', 9, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/verifier/cli.py', 29, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/__init__.py', 2, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/api.py', 84, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/cli.py', 52, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/cli_commands.py', 70, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/domain_planner/__init__.py', 2, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/domain_planner/domain_pack_generator.py', 17, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/domain_planner/llm_planner.py', 16, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/models.py', 44, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/orchestrator.py', 74, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/planner.py', 160, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/repair/__init__.py', 4, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/repair/loader.py', 18, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/repair/pipeline.py', 40, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/repair/rules.py', 83, 'python').
project_file('packages/resource-agent-hypervisor/runtime_client/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/runtime_client/client.py', 48, 'python').
project_file('packages/uri2flow/uri2flow/__init__.py', 17, 'python').
project_file('packages/uri2flow/uri2flow/cli.py', 76, 'python').
project_file('packages/uri2flow/uri2flow/expander.py', 82, 'python').
project_file('packages/uri2flow/uri2flow/loaders/__init__.py', 20, 'python').
project_file('packages/uri2flow/uri2flow/loaders/markpact_loader.py', 24, 'python').
project_file('packages/uri2flow/uri2flow/models.py', 48, 'python').
project_file('packages/uri2flow/uri2flow/parser.py', 100, 'python').
project_file('packages/uri2flow/uri2flow/resolver.py', 111, 'python').
project_file('packages/uri2flow/uri2flow/utils.py', 39, 'python').
project_file('packages/uri2flow/uri2flow/validator.py', 65, 'python').
project_file('project.sh', 59, 'shell').
project_file('scripts/architecture_audit/__init__.py', 21, 'python').
project_file('scripts/architecture_audit/areas.py', 157, 'python').
project_file('scripts/architecture_audit/audit.py', 145, 'python').
project_file('scripts/architecture_audit/checks_domain.py', 143, 'python').
project_file('scripts/architecture_audit/checks_structure.py', 279, 'python').
project_file('scripts/architecture_audit/cli.py', 93, 'python').
project_file('scripts/architecture_audit/models.py', 54, 'python').
project_file('scripts/architecture_audit/parsers.py', 171, 'python').
project_file('scripts/architecture_audit/render.py', 84, 'python').
project_file('scripts/architecture_responsibility_audit.py', 29, 'python').
project_file('scripts/ci/architecture_gate.sh', 57, 'shell').
project_file('scripts/ci/ensure_editable_install.sh', 20, 'shell').
project_file('scripts/examples/audit_agent_reports.py', 428, 'python').
project_file('scripts/examples/cli_fallback.sh', 66, 'shell').
project_file('scripts/examples/comprehensive_test.py', 391, 'python').
project_file('scripts/examples/doql_host_preview.sh', 75, 'shell').
project_file('scripts/examples/effective_weather_playwright.py', 467, 'python').
project_file('scripts/examples/run_uri3_workflow.py', 59, 'python').
project_file('scripts/fix-generated-ownership.sh', 19, 'shell').
project_file('scripts/tellmesh/fix_and_publish.py', 130, 'python').
project_file('scripts/tellmesh/move_tests.py', 138, 'python').
project_file('scripts/tellmesh/split_packages.py', 280, 'python').
project_file('scripts/tellmesh/sync_www.py', 86, 'python').
project_file('scripts/test-all-examples.sh', 6, 'shell').
project_file('scripts/www/about_parser.py', 54, 'python').
project_file('scripts/www/build_examples_docs.py', 327, 'python').
project_file('scripts/www/build_examples_manifest.py', 171, 'python').
project_file('scripts/www/build_landing_integrations.py', 320, 'python').
project_file('scripts/www/check_examples_links.py', 112, 'python').
project_file('scripts/www/install-cron.sh', 151, 'shell').
project_file('scripts/www/md_html.py', 49, 'python').
project_file('scripts/www/monitor_landing.py', 134, 'python').
project_file('scripts/www/monitor_notify.py', 90, 'python').
project_file('scripts/www/monitor_url.py', 84, 'python').
project_file('scripts/www/run_monitors.sh', 48, 'shell').
project_file('scripts/www/site_nav.py', 78, 'python').
project_file('scripts/www/smoke.sh', 29, 'shell').
project_file('scripts/www/test_monitors.sh', 180, 'shell').
project_file('scripts/www/verify_agents.sh', 35, 'shell').
project_file('scripts/www/www_root.py', 19, 'python').
project_file('testenv/ssh_agent_host/entrypoint.sh', 8, 'shell').
project_file('testenv/ssh_agent_host/mock_agent_server.py', 58, 'python').
project_file('tests/__init__.py', 1, 'python').
project_file('tests/architecture/envelope_helpers.py', 41, 'python').
project_file('tests/architecture/import_scanner.py', 17, 'python').
project_file('tests/architecture/test_doctor_contract.py', 33, 'python').
project_file('tests/architecture/test_doctor_gate.py', 14, 'python').
project_file('tests/architecture/test_explain_contract.py', 43, 'python').
project_file('tests/architecture/test_import_boundaries.py', 11, 'python').
project_file('tests/architecture/test_result_envelope_contract.py', 65, 'python').
project_file('tests/architecture/test_technical_ok_business_fail.py', 54, 'python').
project_file('tests/architecture/test_uri2run_envelope.py', 28, 'python').
project_file('tests/capabilities/weather_forecast/test_fixtures.py', 23, 'python').
project_file('tests/conftest.py', 122, 'python').
project_file('tests/domain_pack/__init__.py', 2, 'python').
project_file('tests/domain_pack/test_generator.py', 84, 'python').
project_file('tests/examples/capabilities.py', 220, 'python').
project_file('tests/examples/catalog.py', 135, 'python').
project_file('tests/examples/command_catalog.py', 381, 'python').
project_file('tests/examples/conftest.py', 133, 'python').
project_file('tests/examples/shell_runner.py', 341, 'python').
project_file('tests/examples/test_comprehensive.py', 118, 'python').
project_file('tests/examples/test_effective_weather_playwright.py', 42, 'python').
project_file('tests/examples/test_examples_smoke.py', 71, 'python').
project_file('tests/examples/test_inline_examples.py', 204, 'python').
project_file('tests/examples/test_run_sh_examples.py', 32, 'python').
project_file('tests/generator/__init__.py', 2, 'python').
project_file('tests/generator/test_headers.py', 78, 'python').
project_file('tests/hypervisor/__init__.py', 2, 'python').
project_file('tests/hypervisor/test_agent_describe.py', 106, 'python').
project_file('tests/hypervisor/test_agent_factory_uri.py', 101, 'python').
project_file('tests/hypervisor/test_agent_lifecycle.py', 164, 'python').
project_file('tests/hypervisor/test_agent_runner.py', 662, 'python').
project_file('tests/hypervisor/test_artifact_standards.py', 163, 'python').
project_file('tests/hypervisor/test_autonomous_agents.py', 29, 'python').
project_file('tests/hypervisor/test_browser_operator_separation.py', 66, 'python').
project_file('tests/hypervisor/test_browser_ops_domain.py', 55, 'python').
project_file('tests/hypervisor/test_chat_flow_view.py', 82, 'python').
project_file('tests/hypervisor/test_chat_www.py', 819, 'python').
project_file('tests/hypervisor/test_config.py', 82, 'python').
project_file('tests/hypervisor/test_contract_uri.py', 159, 'python').
project_file('tests/hypervisor/test_dashboard_agent.py', 390, 'python').
project_file('tests/hypervisor/test_dashboard_policy.py', 33, 'python').
project_file('tests/hypervisor/test_dashboard_routing_api.py', 72, 'python').
project_file('tests/hypervisor/test_deployment_aliases.py', 24, 'python').
project_file('tests/hypervisor/test_deployment_registry.py', 132, 'python').
project_file('tests/hypervisor/test_deployment_selector.py', 21, 'python').
project_file('tests/hypervisor/test_desktop_operator_separation.py', 87, 'python').
project_file('tests/hypervisor/test_desktop_ops_domain.py', 112, 'python').
project_file('tests/hypervisor/test_docker_runner.py', 22, 'python').
project_file('tests/hypervisor/test_events_service.py', 195, 'python').
project_file('tests/hypervisor/test_graph_hypervisor_routing.py', 44, 'python').
project_file('tests/hypervisor/test_health_uri.py', 41, 'python').
project_file('tests/hypervisor/test_hypervisor_cli.py', 197, 'python').
project_file('tests/hypervisor/test_inspection_probe.py', 80, 'python').
project_file('tests/hypervisor/test_local_run_plan.py', 59, 'python').
project_file('tests/hypervisor/test_markpact_deployments.py', 22, 'python').
project_file('tests/hypervisor/test_monitor_landing.py', 71, 'python').
project_file('tests/hypervisor/test_monitor_url.py', 139, 'python').
project_file('tests/hypervisor/test_operator_agent_packages.py', 49, 'python').
project_file('tests/hypervisor/test_physical_operator_separation.py', 70, 'python').
project_file('tests/hypervisor/test_plan_runner.py', 129, 'python').
project_file('tests/hypervisor/test_port_conflict.py', 83, 'python').
project_file('tests/hypervisor/test_presentation_uri.py', 86, 'python').
project_file('tests/hypervisor/test_registry_sync.py', 77, 'python').
project_file('tests/hypervisor/test_remote_runner.py', 64, 'python').
project_file('tests/hypervisor/test_repair_supervisor.py', 167, 'python').
project_file('tests/hypervisor/test_routing_pipeline.py', 147, 'python').
project_file('tests/hypervisor/test_routing_policy.py', 47, 'python').
project_file('tests/hypervisor/test_runtime_state.py', 102, 'python').
project_file('tests/hypervisor/test_schema_collab_contract.py', 16, 'python').
project_file('tests/hypervisor/test_screenshot_analysis_agent.py', 72, 'python').
project_file('tests/hypervisor/test_sprint1_autonomy.py', 246, 'python').
project_file('tests/hypervisor/test_supervise_watch.py', 140, 'python').
project_file('tests/hypervisor/test_system_agent_packages.py', 46, 'python').
project_file('tests/hypervisor/test_system_routing.py', 72, 'python').
project_file('tests/hypervisor/test_tutorial_three_agents_smoke.py', 45, 'python').
project_file('tests/hypervisor/test_uri_exchange_schema.py', 77, 'python').
project_file('tests/hypervisor/test_uri_healer.py', 23, 'python').
project_file('tests/hypervisor/test_view_routing.py', 32, 'python').
project_file('tests/hypervisor/test_www_integrations_build.py', 202, 'python').
project_file('tests/integration/__init__.py', 2, 'python').
project_file('tests/integration/test_flow_to_workflow_execution.py', 39, 'python').
project_file('tests/integration/test_nl2a_e2e.py', 93, 'python').
project_file('tests/integration/test_uri3_uri2ops_delegation.py', 43, 'python').
project_file('tests/meta_agent/__init__.py', 2, 'python').
project_file('tests/meta_agent/test_repair.py', 80, 'python').
project_file('tests/nl2uri/test_domain_planner.py', 32, 'python').
project_file('tests/nl2uri/test_flow_planner.py', 50, 'python').
project_file('tests/nl2uri/test_flow_planner_llm.py', 70, 'python').
project_file('tests/nl2uri/test_flow_repair.py', 97, 'python').
project_file('tests/nl2uri/test_graph_planner.py', 75, 'python').
project_file('tests/nl2uri/test_graph_planner_llm.py', 119, 'python').
project_file('tests/nl2uri/test_weather_forecast.py', 60, 'python').
project_file('tests/resource_agent_factory/test_default_port.py', 15, 'python').
project_file('tests/scripts/test_architecture_responsibility_audit.py', 260, 'python').
project_file('tests/test_capability_tests.py', 11, 'python').
project_file('tests/test_contract_registry.py', 21, 'python').
project_file('tests/test_cross_validation_v03.py', 6, 'python').
project_file('tests/test_dependencies.py', 15, 'python').
project_file('tests/test_evolution_proposal.py', 9, 'python').
project_file('tests/test_generate.py', 11, 'python').
project_file('tests/test_hypervisor.py', 87, 'python').
project_file('tests/test_meta_agent.py', 63, 'python').
project_file('tests/test_nl2uri.py', 10, 'python').
project_file('tests/test_operator_task.py', 23, 'python').
project_file('tests/test_policy_gate.py', 19, 'python').
project_file('tests/test_registry_builder_v03.py', 21, 'python').
project_file('tests/test_runtime_client.py', 9, 'python').
project_file('tests/test_schema_validation_v03.py', 8, 'python').
project_file('tests/test_uri2llm_v04.py', 22, 'python').
project_file('tests/test_uri3.py', 12, 'python').
project_file('tests/test_uri_tree_validator.py', 5, 'python').
project_file('tests/test_validate.py', 9, 'python').
project_file('tests/uri2flow/conftest.py', 15, 'python').
project_file('tests/uri2flow/test_cli.py', 13, 'python').
project_file('tests/uri2flow/test_expand_branching_flow.py', 14, 'python').
project_file('tests/uri2flow/test_expand_linear_flow.py', 15, 'python').
project_file('tests/uri2flow/test_flow_defaults.py', 58, 'python').
project_file('tests/uri2flow/test_parser_forms.py', 16, 'python').
project_file('tests/uri2flow/test_uri2flow_markpact_loader.py', 125, 'python').
project_file('tests/uri2pact/test_markpact_scenarios.py', 35, 'python').
project_file('tests/uri2run/test_protocol_transports.py', 201, 'python').
project_file('tests/uri2run/test_stream_transports.py', 83, 'python').
project_file('tests/uri2run/test_transport_matrix.py', 145, 'python').
project_file('tests/uri2run/test_uri2run.py', 115, 'python').
project_file('tests/uri2run/test_voice_resolver.py', 32, 'python').
project_file('tests/uri2run/test_workflow_transport.py', 44, 'python').
project_file('tests/uri3/__init__.py', 2, 'python').
project_file('tests/uri3/test_browser_adapter.py', 109, 'python').
project_file('tests/uri3/test_cli.py', 88, 'python').
project_file('tests/uri3/test_dispatch.py', 23, 'python').
project_file('tests/uri3/test_docker_control.py', 115, 'python').
project_file('tests/uri3/test_doctor.py', 43, 'python').
project_file('tests/uri3/test_envelope_migrate.py', 30, 'python').
project_file('tests/uri3/test_explain_extended.py', 72, 'python').
project_file('tests/uri3/test_explain_uri.py', 42, 'python').
project_file('tests/uri3/test_file_resolver.py', 29, 'python').
project_file('tests/uri3/test_http_scanner.py', 43, 'python').
project_file('tests/uri3/test_lifecycle_envelope.py', 33, 'python').
project_file('tests/uri3/test_llm_profiles.py', 34, 'python').
project_file('tests/uri3/test_log_reader_meta.py', 20, 'python').
project_file('tests/uri3/test_log_uri.py', 87, 'python').
project_file('tests/uri3/test_replay.py', 60, 'python').
project_file('tests/uri3/test_resolvers.py', 107, 'python').
project_file('tests/uri3/test_result_envelope.py', 58, 'python').
project_file('tests/uri3/test_router_call.py', 20, 'python').
project_file('tests/uri3/test_schema.py', 99, 'python').
project_file('tests/uri3/test_service_result.py', 32, 'python').
project_file('tests/uri3/test_ssh_auth.py', 55, 'python').
project_file('tests/uri3/test_ssh_scanner.py', 65, 'python').
project_file('tests/uri3/test_uri_yaml.py', 39, 'python').
project_file('tests/uri3/test_workflow_executor.py', 148, 'python').
project_file('tests/uri3/test_workflow_graph.py', 53, 'python').
project_file('tests/urigen/test_urigen_cycle.py', 217, 'python').
project_file('tests/urish/test_agent_backend.py', 27, 'python').
project_file('tests/urish/test_agent_factory.py', 106, 'python').
project_file('tests/urish/test_ask_dashboard.py', 183, 'python').
project_file('tests/urish/test_call_routing.py', 27, 'python').
project_file('tests/urish/test_desktop_policy.py', 53, 'python').
project_file('tests/urish/test_office_intent.py', 76, 'python').
project_file('tests/urish/test_office_scenarios.py', 80, 'python').
project_file('tests/urish/test_physical_policy.py', 40, 'python').
project_file('tests/urish/test_prompt_split.py', 34, 'python').
project_file('tests/urish/test_render.py', 51, 'python').
project_file('tests/urish/test_repl.py', 130, 'python').
project_file('tests/urish/test_scenario_registry_boundary.py', 21, 'python').
project_file('tests/urish/test_ticket_workflow.py', 139, 'python').
project_file('tests/urish/test_urish_cli.py', 466, 'python').
project_file('tests/urish/test_workflow_run.py', 126, 'python').
project_file('tree.sh', 2, 'shell').
project_file('www/api-bridge/bridge.py', 200, 'python').
project_file('www/app.js', 732, 'javascript').
project_file('www/assets/api-client.js', 216, 'javascript').
project_file('www/assets/app.js', 261, 'javascript').
project_file('www/assets/config.js', 14, 'javascript').
project_file('www/assets/styles.css', 148, 'css').
project_file('www/chat-flow-view.js', 274, 'javascript').
project_file('www/chat-markdown.js', 81, 'javascript').
project_file('www/chat-uri.js', 183, 'javascript').
project_file('www/chat-voice.js', 158, 'javascript').
project_file('www/docs-examples.js', 60, 'javascript').
project_file('www/examples-gallery.js', 145, 'javascript').
project_file('www/flow-chat.css', 551, 'css').
project_file('www/flow-chat.js', 226, 'javascript').
project_file('www/generated/examples-manifest.js', 478, 'javascript').
project_file('www/generated/integrations-i18n.js', 1144, 'javascript').
project_file('www/landing-i18n.js', 720, 'javascript').
project_file('www/landing.css', 2998, 'css').
project_file('www/landing.js', 837, 'javascript').
project_file('www/office-cards-i18n.js', 307, 'javascript').
project_file('www/site-shell.css', 168, 'css').
project_file('www/styles.css', 490, 'css').

% ── Python Functions ─────────────────────────────────────
python_function('agents/custom/gnome_programmer_agent/programmer.py', 'repo_root', 0, 1, 1).
python_function('agents/custom/gnome_programmer_agent/programmer.py', '_post_json', 2, 3, 9).
python_function('agents/custom/gnome_programmer_agent/programmer.py', '_operator_task', 0, 1, 2).
python_function('agents/custom/gnome_programmer_agent/programmer.py', 'observe_desktop', 0, 2, 8).
python_function('agents/custom/gnome_programmer_agent/programmer.py', 'type_on_desktop', 0, 1, 3).
python_function('agents/custom/gnome_programmer_agent/programmer.py', 'programmer_session', 0, 5, 10).
python_function('agents/custom/gnome_programmer_agent/programmer.py', '_extract_artifact', 1, 14, 3).
python_function('agents/custom/gnome_programmer_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/custom/gnome_programmer_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/custom/gnome_programmer_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/custom/gnome_programmer_agent/routes.py', 'skill_observe_desktop', 1, 1, 3).
python_function('agents/custom/gnome_programmer_agent/routes.py', 'skill_type_on_desktop', 1, 1, 2).
python_function('agents/custom/gnome_programmer_agent/routes.py', 'skill_run_programmer_session', 1, 1, 3).
python_function('agents/custom/remote_deploy_agent/deploy.py', 'repo_root', 0, 1, 1).
python_function('agents/custom/remote_deploy_agent/deploy.py', '_resolve_deployment', 1, 2, 2).
python_function('agents/custom/remote_deploy_agent/deploy.py', 'plan_remote_deploy', 1, 3, 6).
python_function('agents/custom/remote_deploy_agent/deploy.py', 'apply_remote_deploy', 1, 2, 6).
python_function('agents/custom/remote_deploy_agent/deploy.py', 'verify_remote_agent', 1, 2, 5).
python_function('agents/custom/remote_deploy_agent/deploy.py', 'start_remote_agent', 1, 2, 6).
python_function('agents/custom/remote_deploy_agent/deploy.py', 'deploy_verify_start', 1, 4, 10).
python_function('agents/custom/remote_deploy_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/custom/remote_deploy_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/custom/remote_deploy_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/custom/remote_deploy_agent/routes.py', 'skill_plan_remote_deploy', 1, 1, 3).
python_function('agents/custom/remote_deploy_agent/routes.py', 'skill_apply_remote_deploy', 1, 1, 3).
python_function('agents/custom/remote_deploy_agent/routes.py', 'skill_verify_remote_agent', 1, 1, 3).
python_function('agents/custom/remote_deploy_agent/routes.py', 'skill_start_remote_agent', 1, 1, 3).
python_function('agents/custom/remote_deploy_agent/routes.py', 'skill_deploy_verify_start', 1, 1, 3).
python_function('agents/custom/screenshot_analysis_agent/analysis.py', 'repo_root', 0, 1, 1).
python_function('agents/custom/screenshot_analysis_agent/analysis.py', '_path_from_file_uri', 1, 5, 3).
python_function('agents/custom/screenshot_analysis_agent/analysis.py', 'resolve_observation_path', 1, 6, 6).
python_function('agents/custom/screenshot_analysis_agent/analysis.py', '_png_size', 1, 4, 3).
python_function('agents/custom/screenshot_analysis_agent/analysis.py', '_json_summary', 1, 7, 9).
python_function('agents/custom/screenshot_analysis_agent/analysis.py', '_read_previous', 1, 7, 6).
python_function('agents/custom/screenshot_analysis_agent/analysis.py', '_append_markdown', 2, 3, 4).
python_function('agents/custom/screenshot_analysis_agent/analysis.py', 'analyze_artifact', 1, 7, 22).
python_function('agents/custom/screenshot_analysis_agent/analysis.py', '_post_json', 2, 3, 9).
python_function('agents/custom/screenshot_analysis_agent/analysis.py', '_extract_screenshot_artifact', 1, 14, 4).
python_function('agents/custom/screenshot_analysis_agent/analysis.py', 'capture_with_operator', 0, 3, 6).
python_function('agents/custom/screenshot_analysis_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/custom/screenshot_analysis_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/custom/screenshot_analysis_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/custom/screenshot_analysis_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/custom/screenshot_analysis_agent/routes.py', 'skill_analyze_screenshot', 1, 1, 3).
python_function('agents/custom/screenshot_analysis_agent/routes.py', 'skill_capture_and_analyze', 1, 1, 3).
python_function('agents/custom/screenshot_analysis_agent/routes.py', 'skill_run_scheduled_capture_analysis', 1, 1, 2).
python_function('agents/generated/codex_nl_plan_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/codex_nl_plan_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/codex_nl_plan_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/codex_nl_plan_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/codex_nl_plan_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/codex_nl_plan_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/codex_nl_plan_agent/routes.py', 'skill_read_markpact_source', 0, 1, 2).
python_function('agents/generated/codex_nl_plan_agent/routes.py', 'skill_read_device_status', 0, 1, 2).
python_function('agents/generated/codex_nl_plan_agent/routes.py', 'skill_run_cron_monitor', 1, 1, 2).
python_function('agents/generated/codex_nl_plan_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/codex_nl_plan_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/codex_nl_plan_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/codex_nl_plan_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/codex_nl_plan_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/codex_nl_plan_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/codex_nl_plan_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', 'skill_read_markpact_source', 0, 1, 2).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', 'skill_read_device_status', 0, 1, 2).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', 'skill_run_cron_monitor', 1, 1, 2).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/codex_nl_smoke_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/codex_nl_smoke_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/codex_nl_smoke_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/codex_nl_smoke_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', 'skill_read_markpact_source', 0, 1, 2).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', 'skill_read_device_status', 0, 1, 2).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', 'skill_run_cron_monitor', 1, 1, 2).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/codex_uri_smoke_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/codex_uri_smoke_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/codex_uri_smoke_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/codex_uri_smoke_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', 'skill_run', 1, 1, 2).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/gnome_programmer_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/gnome_programmer_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/gnome_programmer_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/gnome_programmer_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/gnome_programmer_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/gnome_programmer_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/gnome_programmer_agent/routes.py', 'skill_observe_desktop', 1, 1, 2).
python_function('agents/generated/gnome_programmer_agent/routes.py', 'skill_type_on_desktop', 1, 1, 2).
python_function('agents/generated/gnome_programmer_agent/routes.py', 'skill_programmer_session', 1, 1, 2).
python_function('agents/generated/gnome_programmer_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/gnome_programmer_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/gnome_programmer_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/gnome_programmer_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/gnome_programmer_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/gnome_programmer_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/gnome_programmer_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'skill_process_view', 1, 1, 3).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'skill_workflow_timeline', 1, 1, 3).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'skill_incident_explain', 1, 1, 3).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'skill_repair_diagnose', 1, 1, 3).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'skill_repair_action', 1, 1, 2).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', 'skill_uri_call', 1, 1, 2).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/hypervisor_dashboard_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/hypervisor_dashboard_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/hypervisor_dashboard_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/hypervisor_dashboard_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/invoices_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/invoices_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/invoices_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/invoices_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/invoices_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/invoices_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/invoices_agent/routes.py', 'skill_read_invoice', 1, 1, 3).
python_function('agents/generated/invoices_agent/routes.py', 'skill_read_invoice_events', 1, 1, 3).
python_function('agents/generated/invoices_agent/routes.py', 'skill_create_invoice', 1, 1, 2).
python_function('agents/generated/invoices_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/invoices_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/invoices_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/invoices_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/invoices_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/invoices_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/invoices_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/remote_deploy_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/remote_deploy_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/remote_deploy_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/remote_deploy_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/remote_deploy_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/remote_deploy_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/remote_deploy_agent/routes.py', 'skill_plan_remote_deploy', 1, 1, 2).
python_function('agents/generated/remote_deploy_agent/routes.py', 'skill_apply_remote_deploy', 1, 1, 2).
python_function('agents/generated/remote_deploy_agent/routes.py', 'skill_verify_remote_agent', 1, 1, 2).
python_function('agents/generated/remote_deploy_agent/routes.py', 'skill_start_remote_agent', 1, 1, 2).
python_function('agents/generated/remote_deploy_agent/routes.py', 'skill_deploy_verify_start', 1, 1, 2).
python_function('agents/generated/remote_deploy_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/remote_deploy_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/remote_deploy_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/remote_deploy_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/remote_deploy_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/remote_deploy_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/remote_deploy_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/schema_collab_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/schema_collab_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/schema_collab_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/schema_collab_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/schema_collab_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/schema_collab_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/schema_collab_agent/routes.py', 'skill_read_markpact_source', 0, 1, 2).
python_function('agents/generated/schema_collab_agent/routes.py', 'skill_read_device_status', 0, 1, 2).
python_function('agents/generated/schema_collab_agent/routes.py', 'skill_read_robot_state', 0, 1, 2).
python_function('agents/generated/schema_collab_agent/routes.py', 'skill_run_cron_monitor', 1, 1, 2).
python_function('agents/generated/schema_collab_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/schema_collab_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/schema_collab_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/schema_collab_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/schema_collab_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/schema_collab_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/schema_collab_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/screenshot_analysis_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/screenshot_analysis_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/screenshot_analysis_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/screenshot_analysis_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/screenshot_analysis_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/screenshot_analysis_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/screenshot_analysis_agent/routes.py', 'skill_analyze_screenshot', 1, 1, 2).
python_function('agents/generated/screenshot_analysis_agent/routes.py', 'skill_capture_and_analyze', 1, 1, 2).
python_function('agents/generated/screenshot_analysis_agent/routes.py', 'skill_scheduled_capture_analysis', 1, 1, 2).
python_function('agents/generated/screenshot_analysis_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/screenshot_analysis_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/screenshot_analysis_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/screenshot_analysis_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/screenshot_analysis_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/screenshot_analysis_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/screenshot_analysis_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/user_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/user_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/user_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/user_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/user_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/user_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/user_agent/routes.py', 'skill_read_user', 1, 1, 3).
python_function('agents/generated/user_agent/routes.py', 'skill_read_user_roles', 1, 1, 3).
python_function('agents/generated/user_agent/routes.py', 'skill_create_user', 1, 1, 2).
python_function('agents/generated/user_agent/routes.py', 'skill_assign_user_role', 1, 1, 2).
python_function('agents/generated/user_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/user_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/user_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/user_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/weather_map_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/generated/weather_map_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/generated/weather_map_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/generated/weather_map_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/generated/weather_map_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('agents/generated/weather_map_agent/routes.py', 'dispatch_command', 1, 4, 5).
python_function('agents/generated/weather_map_agent/routes.py', 'skill_read_weather_map', 2, 1, 3).
python_function('agents/generated/weather_map_agent/routes.py', 'skill_generate_weather_map', 1, 1, 2).
python_function('agents/generated/weather_map_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('agents/generated/weather_map_agent/routes.py', '_read_uri', 1, 3, 4).
python_function('agents/generated/weather_map_agent/routes.py', '_command_uri', 1, 5, 2).
python_function('agents/generated/weather_map_agent/routes.py', '_dispatch_command', 2, 2, 4).
python_function('agents/generated/weather_map_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/weather_map_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/weather_map_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/operators/browser_operator/adapters/browser_mock.py', '_artifact_root', 1, 2, 1).
python_function('agents/operators/browser_operator/adapters/browser_mock.py', '_session', 1, 3, 2).
python_function('agents/operators/browser_operator/adapters/browser_mock.py', '_mock_page_text', 1, 3, 1).
python_function('agents/operators/browser_operator/adapters/browser_mock.py', 'open_page', 2, 2, 5).
python_function('agents/operators/browser_operator/adapters/browser_mock.py', 'extract_dom', 2, 3, 5).
python_function('agents/operators/browser_operator/adapters/browser_mock.py', 'screenshot', 2, 1, 3).
python_function('agents/operators/browser_operator/adapters/browser_mock.py', 'capture_page', 2, 2, 3).
python_function('agents/operators/browser_operator/adapters/browser_mock.py', 'click', 2, 1, 3).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'playwright_install_hint', 0, 1, 0).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'playwright_browsers_hint', 0, 1, 0).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'playwright_import_error', 1, 2, 1).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'playwright_browsers_error', 1, 2, 1).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'playwright_available', 0, 2, 0).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'json_dumps', 1, 1, 1).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', '_playwright_worker', 0, 2, 1).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', '_run_sync', 1, 1, 2).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'probe_playwright_ready', 0, 1, 6).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', '_session', 1, 2, 2).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', '_task_context', 1, 4, 2).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'close_playwright_session', 1, 3, 9).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'open_page', 2, 1, 22).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'extract_dom', 2, 1, 9).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'screenshot', 2, 1, 7).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'click', 2, 1, 9).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'capture_page', 2, 10, 7).
python_function('agents/operators/browser_operator/adapters/browser_playwright.py', 'execute', 2, 12, 8).
python_function('agents/operators/browser_operator/adapters/browser_playwright_worker.py', 'capture_page', 2, 11, 15).
python_function('agents/operators/browser_operator/adapters/browser_playwright_worker.py', 'main', 0, 7, 8).
python_function('agents/operators/browser_operator/adapters/browser_router.py', '_playwright_ready', 0, 2, 1).
python_function('agents/operators/browser_operator/adapters/browser_router.py', 'playwright_ready', 0, 1, 1).
python_function('agents/operators/browser_operator/adapters/browser_router.py', 'resolve_adapter_mode', 2, 9, 5).
python_function('agents/operators/browser_operator/adapters/browser_router.py', '_dispatch', 3, 3, 9).
python_function('agents/operators/browser_operator/adapters/browser_router.py', 'open_page', 2, 1, 1).
python_function('agents/operators/browser_operator/adapters/browser_router.py', 'extract_dom', 2, 1, 1).
python_function('agents/operators/browser_operator/adapters/browser_router.py', 'screenshot', 2, 1, 1).
python_function('agents/operators/browser_operator/adapters/browser_router.py', 'capture_page', 2, 1, 1).
python_function('agents/operators/browser_operator/adapters/browser_router.py', 'click', 2, 1, 1).
python_function('agents/operators/browser_operator/adapters/browser_router.py', 'cleanup_browser_session', 1, 1, 1).
python_function('agents/operators/common/assertion.py', 'check', 2, 2, 2).
python_function('agents/operators/desktop_operator/adapters/android_adb.py', '_task_context', 1, 4, 2).
python_function('agents/operators/desktop_operator/adapters/android_adb.py', '_run_adb', 1, 1, 1).
python_function('agents/operators/desktop_operator/adapters/android_adb.py', 'adb_available', 0, 2, 1).
python_function('agents/operators/desktop_operator/adapters/android_adb.py', 'device_ready', 1, 3, 3).
python_function('agents/operators/desktop_operator/adapters/android_adb.py', 'list_devices', 0, 6, 6).
python_function('agents/operators/desktop_operator/adapters/android_adb.py', 'screenshot', 2, 6, 9).
python_function('agents/operators/desktop_operator/adapters/android_adb.py', 'dump_ui', 2, 7, 13).
python_function('agents/operators/desktop_operator/adapters/android_adb.py', 'tap', 2, 11, 12).
python_function('agents/operators/desktop_operator/adapters/android_adb.py', '_find_selector_bounds', 2, 4, 5).
python_function('agents/operators/desktop_operator/adapters/android_mock.py', '_task_context', 1, 4, 2).
python_function('agents/operators/desktop_operator/adapters/android_mock.py', 'screenshot', 2, 2, 6).
python_function('agents/operators/desktop_operator/adapters/android_mock.py', 'dump_ui', 2, 2, 5).
python_function('agents/operators/desktop_operator/adapters/android_mock.py', 'tap', 2, 2, 6).
python_function('agents/operators/desktop_operator/adapters/android_router.py', '_adb_ready', 0, 3, 3).
python_function('agents/operators/desktop_operator/adapters/android_router.py', 'resolve_adapter_mode', 2, 8, 5).
python_function('agents/operators/desktop_operator/adapters/android_router.py', '_dispatch', 3, 5, 3).
python_function('agents/operators/desktop_operator/adapters/android_router.py', 'screenshot', 2, 1, 1).
python_function('agents/operators/desktop_operator/adapters/android_router.py', 'dump_ui', 2, 1, 1).
python_function('agents/operators/desktop_operator/adapters/android_router.py', 'tap', 2, 1, 1).
python_function('agents/operators/desktop_operator/adapters/android_uri.py', 'parse_android_uri', 1, 10, 4).
python_function('agents/operators/desktop_operator/adapters/android_uri.py', 'device_id_from_payload', 1, 4, 4).
python_function('agents/operators/desktop_operator/adapters/input_gnome.py', 'gnome_input_available', 0, 4, 3).
python_function('agents/operators/desktop_operator/adapters/input_gnome.py', 'type_text', 2, 10, 8).
python_function('agents/operators/desktop_operator/adapters/input_mock.py', 'type_text', 2, 2, 3).
python_function('agents/operators/desktop_operator/adapters/input_router.py', '_gnome_ready', 0, 2, 1).
python_function('agents/operators/desktop_operator/adapters/input_router.py', 'resolve_adapter_mode', 2, 8, 5).
python_function('agents/operators/desktop_operator/adapters/input_router.py', 'type_text', 2, 2, 2).
python_function('agents/operators/desktop_operator/adapters/pcwin_mock.py', '_task_context', 1, 4, 2).
python_function('agents/operators/desktop_operator/adapters/pcwin_mock.py', 'focus', 2, 3, 6).
python_function('agents/operators/desktop_operator/adapters/pcwin_mock.py', 'click', 2, 2, 7).
python_function('agents/operators/desktop_operator/adapters/pcwin_router.py', '_uia_ready', 0, 2, 1).
python_function('agents/operators/desktop_operator/adapters/pcwin_router.py', 'resolve_adapter_mode', 2, 8, 5).
python_function('agents/operators/desktop_operator/adapters/pcwin_router.py', '_dispatch', 3, 4, 3).
python_function('agents/operators/desktop_operator/adapters/pcwin_router.py', 'focus', 2, 1, 1).
python_function('agents/operators/desktop_operator/adapters/pcwin_router.py', 'click', 2, 1, 1).
python_function('agents/operators/desktop_operator/adapters/pcwin_uia.py', '_task_context', 1, 4, 2).
python_function('agents/operators/desktop_operator/adapters/pcwin_uia.py', 'uia_available', 0, 3, 0).
python_function('agents/operators/desktop_operator/adapters/pcwin_uia.py', '_session', 1, 2, 1).
python_function('agents/operators/desktop_operator/adapters/pcwin_uia.py', '_focused_window', 1, 2, 3).
python_function('agents/operators/desktop_operator/adapters/pcwin_uia.py', 'focus', 2, 11, 14).
python_function('agents/operators/desktop_operator/adapters/pcwin_uia.py', 'click', 2, 9, 12).
python_function('agents/operators/desktop_operator/adapters/pcwin_uri.py', '_pcwin_segments', 1, 7, 4).
python_function('agents/operators/desktop_operator/adapters/pcwin_uri.py', 'parse_pcwin_uri', 1, 4, 3).
python_function('agents/operators/desktop_operator/adapters/pcwin_uri.py', 'window_id_from_payload', 1, 6, 4).
python_function('agents/operators/desktop_operator/adapters/pcwin_uri.py', 'automation_id_from_payload', 1, 6, 4).
python_function('agents/operators/desktop_operator/adapters/screen_gnome.py', 'gnome_available', 0, 5, 3).
python_function('agents/operators/desktop_operator/adapters/screen_gnome.py', '_task_context', 1, 4, 2).
python_function('agents/operators/desktop_operator/adapters/screen_gnome.py', 'observe', 2, 10, 12).
python_function('agents/operators/desktop_operator/adapters/screen_gnome.py', '_desktop_env', 0, 4, 4).
python_function('agents/operators/desktop_operator/adapters/screen_gnome.py', '_capture_screenshot', 1, 26, 7).
python_function('agents/operators/desktop_operator/adapters/screen_gnome.py', '_list_windows', 0, 5, 6).
python_function('agents/operators/desktop_operator/adapters/screen_mock.py', 'observe', 2, 1, 2).
python_function('agents/operators/desktop_operator/adapters/screen_router.py', '_gnome_ready', 0, 2, 1).
python_function('agents/operators/desktop_operator/adapters/screen_router.py', 'resolve_adapter_mode', 2, 8, 5).
python_function('agents/operators/desktop_operator/adapters/screen_router.py', 'observe', 2, 2, 2).
python_function('agents/operators/device_robot_operator/adapters/physical_mock.py', '_path_parts', 1, 4, 3).
python_function('agents/operators/device_robot_operator/adapters/physical_mock.py', '_target_id', 2, 6, 4).
python_function('agents/operators/device_robot_operator/adapters/physical_mock.py', 'robot_state', 2, 2, 4).
python_function('agents/operators/device_robot_operator/adapters/physical_mock.py', 'robot_move', 2, 3, 4).
python_function('agents/operators/device_robot_operator/adapters/physical_mock.py', 'robot_stop', 2, 2, 4).
python_function('agents/operators/device_robot_operator/adapters/physical_mock.py', 'robot_mission_start', 2, 5, 6).
python_function('agents/operators/device_robot_operator/adapters/physical_mock.py', 'device_status', 2, 3, 4).
python_function('agents/operators/device_robot_operator/adapters/physical_mock.py', 'device_read', 2, 4, 4).
python_function('agents/operators/device_robot_operator/adapters/physical_mock.py', 'device_write', 2, 4, 4).
python_function('agents/operators/operator_runtime.py', 'operator_package_root', 1, 1, 2).
python_function('agents/operators/operator_runtime.py', 'repo_root_from_operator', 1, 1, 1).
python_function('agents/operators/operator_runtime.py', 'create_operator_app', 1, 1, 4).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_header_lines', 1, 3, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_identity_lines', 1, 7, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_planned_lines', 1, 5, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_next_step_lines', 1, 4, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_format_action_block', 2, 12, 4).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', 'format_ask_markdown', 1, 5, 12).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_uri_result_status_label', 1, 7, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_uri_result_header_lines', 1, 4, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_diagnosis_detail_lines', 1, 7, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_workflow_plan_lines', 1, 11, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_uri_result_body_lines', 1, 4, 7).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_envelope_json_block', 1, 1, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', 'format_uri_result_markdown', 1, 9, 9).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', 'format_uri_result_summary', 1, 1, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_next_step_hint', 1, 14, 6).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_display_planned', 2, 4, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_runtime_result_lines', 1, 5, 9).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_first_dict', 0, 3, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_status_lines', 2, 10, 4).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_action_lines', 1, 14, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_incident_lines', 2, 13, 6).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_log_lines', 2, 5, 6).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_log_entry_preview_lines', 1, 12, 6).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/chat_format.py', '_shorten_log_message', 1, 2, 4).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_parse_ts', 1, 5, 7).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_extract_agent_id', 2, 2, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_extract_incident_id', 2, 2, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_extract_summary', 1, 6, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_build_incident_event', 3, 8, 9).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_incident_events', 1, 5, 9).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_monitor_events', 1, 11, 14).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_derive_service_status', 2, 5, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_health_summary', 2, 5, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_agent_health_event', 2, 8, 8).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_agent_health_events', 1, 5, 8).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_should_include_log_event', 1, 4, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_agent_id_from_log_subject', 1, 4, 4).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_log_event_from_payload', 1, 13, 8).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_recent_jsonl_lines', 1, 2, 6).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_events_from_jsonl_path', 1, 7, 9).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', '_log_jsonl_events', 1, 4, 7).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', 'collect_system_events', 0, 3, 10).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/events_service.py', 'filter_events_since', 2, 5, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/monitor_webhook.py', '_safe_slug', 2, 3, 4).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/monitor_webhook.py', '_event_name', 1, 5, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/monitor_webhook.py', '_summary', 2, 4, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/monitor_webhook.py', '_monitor_path', 2, 1, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/monitor_webhook.py', '_write_log_event', 1, 4, 9).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/monitor_webhook.py', 'write_monitor_webhook', 1, 9, 12).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/paths.py', 'repo_www_dir', 0, 2, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/plan_runner.py', 'agent_id_from_uri', 1, 3, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/plan_runner.py', '_execute_uri', 1, 7, 6).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/plan_runner.py', '_attempt_auto_repair', 1, 2, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/plan_runner.py', 'run_planned_uris', 1, 12, 8).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/plan_runner.py', 'format_plan_run_markdown', 1, 9, 7).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/policy.py', 'decision_for_uri', 1, 1, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/policy.py', 'preview_action', 1, 3, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/presentation.py', '_uri_path_parts', 1, 4, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/presentation.py', 'source_view_uri', 1, 7, 5).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/presentation.py', 'resolve_html_presentation', 1, 1, 4).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/presentation.py', 'resolve_markdown_presentation', 1, 1, 5).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'root', 0, 2, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'chat_page_redirect', 0, 2, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'health', 0, 1, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'ui_root', 0, 1, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'ui_agents', 1, 1, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'ui_agent_detail', 2, 3, 5).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_process_view', 1, 2, 5).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_ask', 1, 13, 10).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_uri_preview', 1, 1, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_uri_explain', 1, 2, 5).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_uri_call', 1, 11, 13).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_plan_run', 1, 2, 4).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', '_speak_plan_summary', 1, 5, 5).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_voice_transcribe', 1, 7, 5).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_voice_speak', 1, 4, 4).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_agents', 0, 1, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_events', 2, 1, 6).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_monitor_webhook', 1, 3, 6).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'api_events_stream', 2, 1, 9).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_repo_root', 1, 2, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', 'uri_implies_dry_run', 1, 2, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', 'list_agent_deployments', 0, 2, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', 'resolve_view_uri', 1, 1, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_is_presentation_request', 1, 1, 0).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_html_request', 1, 1, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_markdown_request', 1, 1, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_is_touri_run_request', 1, 1, 0).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_touri_run_request', 1, 4, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_is_http_request', 1, 1, 0).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_infer_operator_operation', 1, 6, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_is_operator_request', 1, 1, 0).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', 'explain_system_uri', 1, 1, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_operator_request', 1, 7, 8).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_is_chat_request', 1, 3, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_chat_request', 1, 1, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_is_nl_request', 1, 1, 0).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_nl_request', 1, 1, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_http_request', 1, 4, 4).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_presentation_request', 1, 2, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_select_dashboard_uri_handler', 1, 3, 1).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', 'call_system_uri', 1, 6, 11).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/view_builder.py', '_process_model_from_data', 1, 12, 8).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/view_builder.py', 'build_process_view', 1, 1, 2).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/view_builder.py', 'render_process_html', 1, 1, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/view_builder.py', '_dashboard_view_renderer', 2, 2, 3).
python_function('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/view_builder.py', 'register_dashboard_view_renderer', 0, 1, 1).
python_function('domains/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html/handlers/run.py', 'handler', 1, 1, 0).
python_function('domains/weather_map/handlers/generate_weather_map.py', 'handler', 1, 3, 7).
python_function('domains/weather_map/planner.py', 'is_weather_prompt', 1, 1, 2).
python_function('domains/weather_map/planner.py', 'deterministic_weather_plan', 1, 2, 1).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', 'health', 0, 1, 1).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', 'dispatch_command', 1, 4, 4).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', 'skill_read_order', 1, 1, 3).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', 'skill_read_order_events', 1, 1, 3).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 'health', 0, 1, 1).
python_function('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 'capabilities', 0, 1, 1).
python_function('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 'well_known_agent_json', 0, 1, 1).
python_function('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 'well_known_agent_card_json', 0, 1, 1).
python_function('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 'read_resource', 1, 4, 5).
python_function('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 'dispatch_command', 1, 4, 4).
python_function('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 'skill_read_user', 1, 1, 3).
python_function('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 'skill_read_user_roles', 1, 1, 3).
python_function('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 'skill_create_user', 1, 1, 2).
python_function('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 'skill_assign_user_role', 1, 1, 2).
python_function('packages/resource-agent-factory/agents/generated/user_agent/routes.py', '_uri_allowed', 2, 4, 2).
python_function('packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('packages/resource-agent-factory/generator/agent_generator.py', '_default_port_for_agent', 2, 3, 3).
python_function('packages/resource-agent-factory/generator/agent_generator.py', 'render_template', 4, 3, 5).
python_function('packages/resource-agent-factory/generator/agent_generator.py', 'generate_agent', 1, 5, 21).
python_function('packages/resource-agent-factory/generator/agent_generator.py', 'expand_paths', 1, 4, 6).
python_function('packages/resource-agent-factory/generator/agent_generator.py', 'main', 1, 5, 3).
python_function('packages/resource-agent-factory/generator/hashutil.py', 'file_sha256', 1, 1, 4).
python_function('packages/resource-agent-factory/generator/header.py', 'contract_source_ref', 2, 3, 5).
python_function('packages/resource-agent-factory/generator/header.py', 'python_file_header', 2, 1, 0).
python_function('packages/resource-agent-factory/generator/header.py', 'dockerfile_header', 2, 1, 0).
python_function('packages/resource-agent-factory/generator/header.py', 'markdown_generated_banner', 2, 1, 0).
python_function('packages/resource-agent-factory/generator/header.py', 'generated_marker_payload', 2, 1, 0).
python_function('packages/resource-agent-factory/generator/model.py', 'load_agent_spec', 1, 7, 11).
python_function('packages/resource-agent-factory/generator/model.py', 'spec_to_plain_dict', 2, 3, 1).
python_function('packages/resource-agent-factory/generator/paths.py', 'project_root', 0, 1, 1).
python_function('packages/resource-agent-factory/generator/validate.py', 'validate_agent', 1, 11, 4).
python_function('packages/resource-agent-factory/generator/validate.py', 'iter_agent_specs', 1, 3, 4).
python_function('packages/resource-agent-factory/generator/validate.py', 'main', 1, 7, 6).
python_function('packages/resource-agent-factory/generator/verify.py', 'verify_generated_agent', 1, 7, 7).
python_function('packages/resource-agent-factory/generator/verify.py', '_agent_dirs', 1, 6, 4).
python_function('packages/resource-agent-factory/generator/verify.py', 'verify_generated', 1, 3, 3).
python_function('packages/resource-agent-factory/generator/verify.py', 'main', 1, 6, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', 'describe_agent', 1, 17, 21).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_deployment_health_label', 1, 6, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_safe_run_plan', 2, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_find_contract_path', 3, 13, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_find_domain_pack', 4, 11, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_package_relative_path', 2, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_list_package_files', 1, 6, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_agent_kind', 1, 6, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_capability_backing_note', 0, 4, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_skill_invoke_example', 1, 12, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_file_role', 1, 4, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_extract_markpact_blocks', 1, 4, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_read_yaml', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_rel', 2, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', '_render_markdown', 0, 70, 17).
python_function('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', 'validate_config_dict', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', 'validate_runtime_environments_dict', 2, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', '_validate_path', 4, 4, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', 'check_artifacts', 1, 11, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', '_read_structured_mapping', 1, 3, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', '_artifact_lifecycle_result', 3, 14, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', '_collect_lifecycle_results', 1, 6, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', '_lifecycle_summary', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', '_lifecycle_samples', 1, 2, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', 'check_lifecycle_coverage', 1, 10, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', 'check_schemas', 1, 5, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', '_load_json_payload', 2, 4, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'call', 5, 2, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'explain', 3, 1, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'scan', 1, 3, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'resolve', 1, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'status', 0, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'config_cmd', 1, 2, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'deployments_list', 0, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'run_agent_cmd', 10, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'stop_agent_cmd', 1, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'restart_agent_cmd', 5, 1, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'agent_status_cmd', 2, 1, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'inspect_agent_cmd', 3, 1, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'describe_agent_cmd', 3, 4, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'supervise_cmd', 10, 8, 12).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'repair_diagnose_cmd', 3, 1, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'repair_apply_cmd', 4, 2, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'repair_heal_cmd', 6, 2, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'repair_learn_cmd', 2, 2, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'artifacts_check_cmd', 1, 2, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'artifacts_schemas_cmd', 0, 2, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'artifacts_lifecycle_cmd', 2, 3, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'ticket_import_cmd', 2, 3, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'evolution_propose_from_ticket_cmd', 1, 2, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'evolution_propose_from_incident_cmd', 1, 1, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'logs_cmd', 2, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'deploy_agent_cmd', 2, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'verify_agent_cmd', 2, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'docker_cmd', 2, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'replay_failure_cmd', 3, 5, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'main', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 'echo_json', 1, 2, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 'run_local_agent', 1, 7, 13).
python_function('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 'deploy_agent', 1, 7, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 'verify_agent', 1, 5, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 'read_agent_logs', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 'call_docker', 1, 5, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/compatibility/checker.py', '_load_policy', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/compatibility/checker.py', 'classify_registry_change', 2, 8, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/config/config_checks.py', 'validate_hypervisor', 1, 7, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/config/config_checks.py', 'validate_llm', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/config/config_checks.py', 'validate_uri3', 1, 4, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/config/config_checks.py', 'validate_path_sections', 1, 5, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/config/defaults.py', 'load_yaml_file', 1, 4, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/config/defaults.py', 'embedded_defaults_raw', 0, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/config/defaults.py', 'apply_builtin_defaults', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/config/defaults.py', 'get_default_config', 0, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/config/env.py', '_parse_bool', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/config/env.py', 'apply_legacy_env_overrides', 1, 6, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/config/env.py', 'apply_structured_env_overrides', 1, 9, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/config/env.py', 'apply_env_overrides', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/config/loader.py', 'config_search_paths', 0, 6, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/config/loader.py', 'resolve_config_path', 0, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/config/loader.py', 'load_config', 1, 3, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/config/loader.py', 'get_config', 0, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/config/loader.py', 'load_hypervisor_config', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/config/uri_config.py', '_repo_config_dir', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/config/uri_config.py', 'apply_uri_yaml_configs', 1, 10, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/config/validators.py', 'merge_config', 2, 5, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/config/validators.py', 'validate_config', 1, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cli.py', '_parse_args', 1, 5, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cli.py', 'main', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py', 'run_schema_command', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py', 'run_cross_command', 1, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py', 'run_build_command', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py', 'run_export_md_command', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py', 'run_check_command', 1, 5, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/capabilities.py', '_validate_single_capability', 1, 14, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/capabilities.py', 'validate_capability_cross_refs', 1, 4, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/proto_index.py', 'load_proto_text', 1, 2, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/proto_index.py', 'schema_exists', 2, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/resources.py', 'validate_resource_cross_refs', 1, 6, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py', 'validate_cross_references', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py', 'validate_root', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py', '_read_yaml', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py', 'load_contract_registry', 1, 9, 11).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/merge_helpers.py', 'merge_proto_contract', 3, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/merge_helpers.py', 'merge_resources_contract', 2, 5, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/merge_helpers.py', 'merge_views_contract', 2, 6, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/merger.py', 'merge_main_contracts', 4, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py', '_hash_file', 1, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py', '_contract_hash', 1, 3, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py', 'build_registry_manifest', 1, 5, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py', 'write_registry_manifest', 2, 2, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/capabilities.py', '_resolves_as_external_uri', 1, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/capabilities.py', 'validate_resource_read_capability', 2, 8, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/capabilities.py', 'validate_command_capability', 1, 3, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/capabilities.py', 'validate_capabilities', 1, 4, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/resources.py', 'validate_resources', 1, 7, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/resources.py', 'validate_views', 1, 3, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_exporter.py', 'export_json', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_exporter.py', 'export_markdown', 2, 6, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', '_read_yaml', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', '_read_json', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', 'validate_file', 2, 3, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', 'validate_contract_files', 1, 6, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', '_parse_bool', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', '_parse_kinds', 1, 5, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', '_schema_refs_from_contract', 1, 7, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', '_find_proto_files', 2, 8, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', '_artifact_entry', 0, 3, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', '_read_yaml', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', '_slug_to_snake', 1, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', '_contract_uri', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', '_agent_contract_uri', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', 'resolve_contract_path', 2, 22, 13).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', '_format_schema_results', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', '_validation_payload', 0, 2, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', 'fetch_agent_contract', 2, 8, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', 'validate_agent_contract', 2, 14, 12).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', 'validate_contract_registry_uri', 1, 6, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', 'fetch_registry_manifest', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', 'generate_agent_contract', 2, 12, 13).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', 'fetch_agent_artifacts', 2, 21, 17).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py', 'handle_contract_uri', 2, 21, 17).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/validate.py', 'validate_registry', 1, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/aliases.py', '_read_yaml', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/aliases.py', 'load_deployment_selector_aliases', 1, 8, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/docker_runner.py', 'docker_uri_for_deployment', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/docker_runner.py', 'build_docker_deploy_plan', 1, 4, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/docker_runner.py', 'build_docker_control_plan', 2, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/docker_runner.py', 'apply_docker_deploy', 1, 3, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/docker_runner.py', 'stop_docker_deployment', 1, 4, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/docker_runner.py', 'verify_docker_deployment', 1, 9, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env.py', 'build_deployment_env_map', 3, 9, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env.py', 'resolve_deployment_env', 3, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env.py', 'default_log_uri', 2, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_config.py', 'repo_config_dir', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_config.py', 'load_deployments_uri_config', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_config.py', 'load_runtime_uri_config', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_merge.py', 'merge_runtime_defaults', 1, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_merge.py', 'materialize_env_values', 1, 6, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py', 'port_from_http_uri', 1, 5, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py', 'port_from_command', 1, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py', 'health_uri_for_port', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py', '_runtime_command', 2, 6, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py', '_network_effective_port', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py', 'resolve_effective_health_uri', 2, 8, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py', 'command_port_from_runtime', 2, 5, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py', '_port_from_http_uri', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py', '_port_conflict_incident', 0, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py', '_foreign_service_incident', 0, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py', '_runtime_incidents', 0, 4, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py', '_health_incidents', 0, 5, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py', 'classify_incidents', 0, 13, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py', 'blocking_incidents', 1, 3, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/pipeline.py', '_runtime_command_port', 2, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/pipeline.py', '_derive_effective_card_uri', 4, 7, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/pipeline.py', 'gather_inspection_context', 1, 12, 14).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/pipeline.py', '_merge_log_results', 2, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/pipeline.py', 'probe_agent_endpoints', 1, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/pipeline.py', 'build_inspection_report', 1, 13, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/probe.py', '_probe_payload_ok', 1, 13, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/probe.py', '_host_probe_uri', 1, 5, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/probe.py', '_probe_response', 2, 10, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/probe.py', 'probe_http', 1, 5, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/probe.py', 'log_uri_with_filters', 1, 1, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/probe.py', 'read_error_logs', 1, 4, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/readiness.py', 'readiness_summary', 0, 6, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/readiness.py', 'recommended_action_from_incidents', 1, 6, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/readiness.py', 'build_agent_readiness_report', 0, 9, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_lifecycle_payload', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_repo_root', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_validate_run_agent_options', 0, 4, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_finalize_run_plan', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_load_active_runtime_state', 2, 3, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_sync_reused_runtime_state', 3, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_resolve_running_process', 4, 6, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_run_non_local_target', 1, 4, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_start_local_process', 2, 7, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_is_process_start_failure', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_resolve_initial_run_plan', 2, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_execute_run_agent_plan', 3, 3, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_emit_run_agent_result', 2, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', 'run_agent', 1, 3, 11).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', 'restart_agent', 1, 1, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle_status.py', '_lifecycle_payload', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle_status.py', '_repo_root', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle_status.py', 'agent_status', 1, 5, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle_status.py', 'agent_logs_uri', 1, 3, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', 'default_registry_path', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', '_read_yaml', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', '_port_from_uri', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', '_parse_declared', 1, 7, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', '_parse_runtime', 1, 6, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', '_parse_deployment', 1, 5, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', 'load_deployment_registry', 1, 5, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', '_local_endpoint', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', '_local_health_uri', 1, 6, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', '_local_card_uri', 1, 6, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', 'local_target_to_relative_path', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', 'repo_python_executable', 1, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', 'local_target_to_module', 1, 6, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', 'build_local_run_plan', 1, 4, 13).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_verify.py', 'verify_local_deployment', 1, 8, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', '_port_from_uri', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_conflict.py', 'classify_port_listeners', 1, 6, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_conflict.py', 'port_conflict_detail', 0, 7, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_utils.py', 'is_port_free', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_utils.py', 'find_free_port', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_utils.py', 'expected_agent_id', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_utils.py', 'port_from_http_uri', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_utils.py', 'health_matches_agent', 1, 4, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_utils.py', 'foreign_service_detail', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process.py', '_safe_log_stem', 1, 5, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process.py', 'process_log_path', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process.py', 'process_log_uri', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process.py', 'start_process', 1, 4, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process_discovery.py', '_iter_proc_pids', 0, 4, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process_discovery.py', '_listening_socket_inodes', 1, 9, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process_discovery.py', 'pids_listening_on_port', 1, 8, 12).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process_discovery.py', 'command_line', 1, 6, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process_discovery.py', 'command_matches_plan', 2, 7, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process_discovery.py', 'terminate_pid', 1, 9, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process_discovery.py', '_pid_alive', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/registry_sync.py', 'card_uri_for_port', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/registry_sync.py', 'deployment_with_port', 2, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/registry_sync.py', 'sync_deployment_port', 2, 2, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/registry_sync.py', 'sync_deployment_health_uri', 2, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'load_or_clear_runtime_state', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'build_agent_run_plan', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'rebind_plan_port_if_busy', 2, 3, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'resolve_running_mode', 0, 10, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'reuse_existing_process_plan', 2, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'sync_runtime_health_uri', 2, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', '_workspace_pythonpath', 1, 7, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'prepare_runtime_env', 1, 8, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'verify_process_alive', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'write_runtime_state_after_start', 2, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'process_start_failure_payload', 1, 5, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'validate_run_dependencies', 1, 8, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'persist_rebound_port', 2, 7, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_executor.py', 'attach_started_process', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_plans.py', 'build_run_plan', 1, 5, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'runtime_root', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'state_path', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_port_from_http_uri', 1, 5, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_port_from_command', 1, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_process_status', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_health_uri', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_pid', 1, 4, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_command', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'state_health_uri', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_process_log_path', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_process_log_uri', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_build_uri_block', 2, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_build_process_block', 2, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_build_status_block', 1, 7, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_build_network_block', 3, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_legacy_runtime_state', 1, 5, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', '_apply_flat_accessors', 1, 3, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'normalize_runtime_state', 1, 3, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'load_runtime_state', 2, 3, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'save_runtime_state', 3, 12, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'clear_runtime_state', 2, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'is_process_alive', 1, 5, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'runtime_status', 2, 6, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'now_iso', 0, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/selector.py', 'parse_hypervisor_uri', 1, 14, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/selector.py', '_prefer_local_deployment', 1, 9, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/selector.py', 'resolve_deployment', 1, 12, 13).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_deploy.py', 'build_ssh_deploy_plan', 1, 3, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_deploy.py', 'apply_ssh_deploy_plan', 1, 7, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_helpers.py', 'generated_agent_dir', 2, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_helpers.py', 'remote_module_for', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_run.py', 'build_ssh_run_plan', 1, 7, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_run.py', 'apply_ssh_run_plan', 1, 10, 12).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_verify.py', 'verify_remote_deployment', 1, 12, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'infer_port', 1, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'deployment_id_for_agent', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'infer_health_uri', 2, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'infer_card_uri', 2, 7, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'deployment_from_uri_tree', 1, 12, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', '_merge_uri_tree_deployment', 2, 13, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'sync_from_uri_tree', 1, 3, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'resolve_status', 1, 11, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'list_deployments', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'get_deployment_for_agent', 1, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'registry_summary', 1, 4, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', '_lifecycle_payload', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', '_repo_root', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', '_safe_stop_plan', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', '_state_health_uri', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', '_candidate_stop_ports', 2, 4, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', '_terminate_matching_agent_processes', 2, 11, 11).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', '_emit_stop_result', 2, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', '_stop_docker_deployment', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', '_stop_without_runtime_state', 2, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', '_stop_with_runtime_state', 3, 5, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py', 'stop_agent', 1, 3, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py', '_lifecycle_payload', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py', '_repo_root', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py', 'inspect_agent', 1, 1, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py', '_runtime_command_port', 1, 4, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py', '_auto_repair_plan', 1, 8, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py', '_apply_repair', 1, 4, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py', 'ensure_agent_healthy', 1, 10, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py', 'supervise_agent', 1, 4, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_repo_root', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_safe_selector', 1, 4, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', 'watch_state_path', 2, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', 'load_watch_state', 2, 4, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', 'save_watch_state', 3, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_inspection_from_result', 1, 5, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_incident_codes', 1, 5, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_service_status', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_health_signature', 1, 4, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_actions_from_result', 1, 10, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_write_watch_log', 1, 2, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_repair_allowed', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_run_supervision', 1, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_learn_allowed_for_state', 1, 4, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_emit_tick_events', 1, 11, 11).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', '_next_state', 1, 6, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/watch.py', 'supervise_watch', 1, 14, 20).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py', 'save_deployment_registry', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py', 'upsert_deployment', 2, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py', 'remove_deployment', 2, 3, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py', 'write_deployment_registry', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/agent_contract.py', 'generate_agent_contract', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/commands.py', 'generate_commands', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/handlers.py', 'generate_handlers', 1, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/proto.py', 'generate_proto', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/renderers.py', 'generate_renderers', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/resources.py', 'generate_resources', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/artifact_generators/views.py', 'generate_views', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'generate_domain_pack_from_tree', 2, 2, 11).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'generate_domain_pack', 2, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/pack_writer.py', 'write_domain_pack', 1, 8, 13).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/parser.py', 'parse_uri_tree', 1, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/parser.py', 'derive_domain_model', 2, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'package_name', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'generic_proto', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'weather_proto', 0, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'weather_handler', 0, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'generic_handler', 0, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/writer.py', 'write_file', 2, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/events.py', '_repo_root', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/events.py', 'emit_operation_event', 2, 6, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/events.py', 'emit_result_event', 3, 5, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/cli.py', 'main', 1, 10, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/models.py', 'load_proposal', 1, 5, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/proposal_from_source.py', 'build_evolution_proposal', 1, 3, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/proposal_from_source.py', 'build_repair_proposal_from_incident', 1, 8, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/proposal_from_source.py', 'build_evolution_proposal_from_ticket', 1, 11, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/validator.py', 'validate_proposal_dict', 2, 14, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/validator.py', 'validate_proposal', 1, 3, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/integrations/planfile/ticket_mapper.py', '_ticket_uri', 2, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/integrations/planfile/ticket_mapper.py', 'planfile_task_to_ticket', 1, 10, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/integrations/planfile/ticket_mapper.py', 'load_planfile_strategy', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/integrations/planfile/ticket_mapper.py', 'import_tickets_from_planfile', 1, 10, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/integrations/planfile/ticket_mapper.py', 'propose_from_ticket_path', 1, 3, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/paths.py', '_is_hypervisor_root', 1, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/paths.py', '_walk_hypervisor_root', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/paths.py', 'find_repo_root', 1, 6, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/paths.py', 'repo_root', 0, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/paths.py', '_looks_like_www', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/paths.py', 'resolve_www_dir', 1, 6, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py', 'evaluate_change', 2, 5, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/classifier.py', '_incident_text', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/classifier.py', '_warning_text', 1, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/classifier.py', '_log_text', 1, 7, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/classifier.py', '_collect_text', 2, 4, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/classifier.py', 'classify_inspection', 1, 5, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/healer.py', 'run_uri_healer', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', '_incident_id', 0, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', 'incident_uri', 2, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', 'incident_storage_path', 3, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', '_symptom_from_item', 1, 4, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', '_symptoms_from_inspection', 1, 6, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', '_incident_uri_block', 3, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', '_incident_status_block', 3, 6, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', '_incident_evidence', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', 'build_incident_from_inspection', 1, 8, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', 'write_incident', 1, 3, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/incident.py', 'load_incident', 1, 4, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/plan_builder.py', '_plan_id', 1, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/plan_builder.py', '_ordered_unique', 1, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/plan_builder.py', '_inspection_codes', 1, 10, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/plan_builder.py', '_prioritized_playbooks', 2, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/plan_builder.py', 'build_repair_plan_from_diagnosis', 1, 11, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/plan_builder.py', 'build_repair_plan_from_inspection', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py', '_repo_root', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py', '_playbook_sync_health_uri', 2, 4, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py', '_playbook_restart_agent', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py', '_playbook_clear_stale_runtime', 2, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py', '_playbook_rebind_port', 2, 8, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py', '_playbook_inspect', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py', '_playbook_requires_approval', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py', '_playbook_not_implemented', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py', 'apply_playbook', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/playbooks.py', 'apply_playbook_sequence', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/policy.py', 'policy_level_for_playbook', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/policy.py', 'playbook_requires_approval', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/policy.py', 'is_playbook_allowed', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/proposal_builder.py', 'build_repair_proposal', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/proposal_builder.py', 'link_proposal_to_incident', 2, 2, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/registry.py', 'repair_cases_dir', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/registry.py', 'list_repair_cases', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/registry.py', 'load_repair_case', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/registry.py', '_case_matches_symptoms', 2, 10, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/registry.py', 'find_matching_case', 2, 8, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/sandbox.py', 'simulate_playbook', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/sandbox.py', 'test_repair_plan_in_sandbox', 1, 6, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py', '_envelope', 1, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py', '_repo_root', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py', '_sync_registry_if_drifted', 1, 10, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py', 'diagnose_agent', 1, 4, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py', '_repair_playbook_candidates', 2, 9, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py', '_execute_repair_playbooks', 1, 7, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py', '_healthy_repair_apply_body', 3, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py', 'repair_apply', 1, 8, 12).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py', 'supervise_with_repair', 1, 9, 15).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/supervisor.py', 'learn_from_incident', 1, 11, 12).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/validator.py', 'validate_incident_dict', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/validator.py', 'validate_repair_plan_dict', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/validator.py', 'validate_evolution_proposal_dict', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/validator.py', 'validate_runtime_state_dict', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/validator.py', 'validate_ticket_dict', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/repair/validator.py', 'read_yaml', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/dispatcher.py', 'call_uri', 2, 6, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/explain.py', 'explain_semantic_route', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/explain.py', 'explain_executable_uri', 1, 6, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/models.py', '_public_context', 1, 3, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/policy.py', 'policy_options', 1, 3, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/policy.py', '_semantic_requires_approval', 1, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/policy.py', 'evaluate_route_policy', 1, 13, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/policy.py', 'evaluate_route_policy_decision', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/registry_bridge.py', 'load_runtime_registry', 1, 4, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/registry_bridge.py', 'resolve_operator_by_scheme', 1, 7, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/registry_bridge.py', 'resolve_operator_deployment', 1, 5, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/resolver.py', 'resolve_hypervisor_route', 1, 14, 14).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/resolver.py', '_select_environment_and_adapter', 0, 11, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/resolver.py', '_payload_session', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/resolver.py', '_normalize_environment', 2, 8, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/resolver.py', '_canonical_operator_scheme', 1, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/resolver.py', '_operator_base_url', 1, 7, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', 'supports_hypervisor_system_uri', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_is_runtime_request', 1, 4, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_is_health_request', 1, 3, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_is_schema_request', 1, 3, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_is_repair_request', 1, 3, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_is_contract_request', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_is_agent_factory_request', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_is_hypervisor_agent_request', 1, 5, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_runtime_request', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_health_request', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_schema_request', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_repair_request', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_agent_factory_request', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_hypervisor_agent_request', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_log_request', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_file_request', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_contract_request', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', '_select_hypervisor_system_handler', 1, 3, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py', 'call_hypervisor_system_uri', 1, 3, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', 'handle_runtime_uri', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', 'handle_health_uri', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', '_contract_path_for_agent', 1, 4, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', '_schema_refs_from_capabilities', 1, 4, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', '_read_contract', 1, 5, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', '_contract_uri_for_schema', 2, 7, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', 'handle_schema_uri', 1, 20, 12).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', 'handle_repair_uri', 1, 6, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', 'handle_agent_factory_uri', 1, 6, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', 'handle_hypervisor_agent_uri', 1, 6, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', 'handle_log_uri', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', 'handle_file_uri', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_handlers.py', 'handle_contract_uri', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_request.py', 'uri_path_parts', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_request.py', 'query_params', 1, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_request.py', 'bool_param', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/system_request.py', 'int_param', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py', 'register_view_renderer', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py', 'supports_view_uri', 1, 4, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py', 'normalize_view_uri', 1, 8, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py', 'resolve_view_envelope', 1, 13, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py', 'handle_view_uri', 1, 5, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/views/process.py', '_human_title', 2, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/views/process.py', '_related_uris', 2, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/views/process.py', '_process_actions', 2, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/views/process.py', '_process_status_fields', 3, 8, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/routing/views/process.py', 'build_process_view_data', 1, 8, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/verifier/capability_tests.py', 'build_capability_test_plan', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/verifier/cli.py', 'main', 1, 5, 6).
python_function('packages/resource-agent-hypervisor/meta_agent/api.py', 'health', 0, 1, 1).
python_function('packages/resource-agent-hypervisor/meta_agent/api.py', 'proposal_from_prompt', 1, 2, 6).
python_function('packages/resource-agent-hypervisor/meta_agent/api.py', 'validate', 1, 2, 5).
python_function('packages/resource-agent-hypervisor/meta_agent/api.py', 'repair', 1, 2, 5).
python_function('packages/resource-agent-hypervisor/meta_agent/api.py', 'generate', 1, 2, 6).
python_function('packages/resource-agent-hypervisor/meta_agent/api.py', 'pipeline', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/meta_agent/api.py', 'verify', 0, 1, 2).
python_function('packages/resource-agent-hypervisor/meta_agent/cli.py', 'main', 0, 7, 11).
python_function('packages/resource-agent-hypervisor/meta_agent/cli_commands.py', 'cmd_plan', 2, 2, 4).
python_function('packages/resource-agent-hypervisor/meta_agent/cli_commands.py', 'cmd_validate', 1, 3, 3).
python_function('packages/resource-agent-hypervisor/meta_agent/cli_commands.py', 'cmd_repair', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/meta_agent/cli_commands.py', 'cmd_generate', 1, 2, 5).
python_function('packages/resource-agent-hypervisor/meta_agent/cli_commands.py', 'cmd_pipeline', 2, 3, 5).
python_function('packages/resource-agent-hypervisor/meta_agent/cli_commands.py', 'cmd_verify', 0, 3, 2).
python_function('packages/resource-agent-hypervisor/meta_agent/models.py', 'dump_yaml', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/meta_agent/orchestrator.py', 'save_proposal_from_prompt', 2, 2, 6).
python_function('packages/resource-agent-hypervisor/meta_agent/orchestrator.py', 'validate_repair_generate', 1, 7, 7).
python_function('packages/resource-agent-hypervisor/meta_agent/orchestrator.py', 'pipeline_from_prompt', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/meta_agent/orchestrator.py', 'asdict_result', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/meta_agent/planner.py', 'slugify', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/meta_agent/planner.py', 'package_name', 1, 3, 5).
python_function('packages/resource-agent-hypervisor/meta_agent/planner.py', 'singularize', 1, 4, 2).
python_function('packages/resource-agent-hypervisor/meta_agent/planner.py', 'infer_intent', 1, 9, 14).
python_function('packages/resource-agent-hypervisor/meta_agent/planner.py', 'intent_to_agent_spec', 1, 8, 9).
python_function('packages/resource-agent-hypervisor/meta_agent/repair/loader.py', 'load_spec', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/meta_agent/repair/loader.py', 'write_spec', 2, 1, 2).
python_function('packages/resource-agent-hypervisor/meta_agent/repair/pipeline.py', 'repair_agent_spec', 1, 2, 9).
python_function('packages/resource-agent-hypervisor/meta_agent/repair/rules.py', 'repair_agent_block', 3, 6, 6).
python_function('packages/resource-agent-hypervisor/meta_agent/repair/rules.py', 'repair_duplicate_capability_names', 2, 5, 4).
python_function('packages/resource-agent-hypervisor/meta_agent/repair/rules.py', 'repair_missing_capability_type', 2, 3, 2).
python_function('packages/resource-agent-hypervisor/meta_agent/repair/rules.py', 'repair_resource_read_capability', 2, 8, 6).
python_function('packages/resource-agent-hypervisor/meta_agent/repair/rules.py', 'repair_command_capability', 2, 4, 5).
python_function('packages/resource-agent-hypervisor/meta_agent/repair/rules.py', 'repair_capabilities', 2, 6, 7).
python_function('packages/uri2flow/uri2flow/cli.py', 'cmd_validate', 1, 2, 4).
python_function('packages/uri2flow/uri2flow/cli.py', 'cmd_expand', 1, 3, 7).
python_function('packages/uri2flow/uri2flow/cli.py', 'cmd_print', 1, 1, 4).
python_function('packages/uri2flow/uri2flow/cli.py', 'build_parser', 0, 1, 5).
python_function('packages/uri2flow/uri2flow/cli.py', 'main', 1, 1, 3).
python_function('packages/uri2flow/uri2flow/expander.py', '_node_from_step', 3, 11, 3).
python_function('packages/uri2flow/uri2flow/expander.py', '_edges_from_depends', 1, 4, 2).
python_function('packages/uri2flow/uri2flow/expander.py', 'expand_flow', 1, 6, 7).
python_function('packages/uri2flow/uri2flow/expander.py', 'dump_yaml', 1, 1, 1).
python_function('packages/uri2flow/uri2flow/parser.py', '_as_list', 1, 5, 4).
python_function('packages/uri2flow/uri2flow/parser.py', '_parse_step', 1, 10, 11).
python_function('packages/uri2flow/uri2flow/parser.py', 'parse_flow', 1, 12, 7).
python_function('packages/uri2flow/uri2flow/parser.py', 'load_flow', 1, 4, 8).
python_function('packages/uri2flow/uri2flow/resolver.py', '_find_repo_root', 1, 7, 6).
python_function('packages/uri2flow/uri2flow/resolver.py', '_pattern_to_regex', 1, 4, 7).
python_function('packages/uri2flow/uri2flow/resolver.py', '_match_pattern', 2, 2, 3).
python_function('packages/uri2flow/uri2flow/resolver.py', '_load_flow_defaults_config', 0, 4, 7).
python_function('packages/uri2flow/uri2flow/resolver.py', '_defaults_from_entry', 1, 3, 4).
python_function('packages/uri2flow/uri2flow/resolver.py', '_defaults_from_scheme', 1, 3, 4).
python_function('packages/uri2flow/uri2flow/resolver.py', '_defaults_from_patterns', 1, 7, 6).
python_function('packages/uri2flow/uri2flow/resolver.py', '_fallback_defaults', 0, 4, 5).
python_function('packages/uri2flow/uri2flow/resolver.py', 'default_operation_for_uri', 1, 3, 4).
python_function('packages/uri2flow/uri2flow/resolver.py', 'clear_defaults_cache', 0, 1, 1).
python_function('packages/uri2flow/uri2flow/utils.py', 'slugify', 1, 2, 3).
python_function('packages/uri2flow/uri2flow/utils.py', 'scheme_of', 1, 1, 1).
python_function('packages/uri2flow/uri2flow/utils.py', 'path_parts', 1, 4, 4).
python_function('packages/uri2flow/uri2flow/utils.py', 'node_id_from_uri', 2, 5, 7).
python_function('packages/uri2flow/uri2flow/validator.py', 'validate_flow_document', 1, 10, 7).
python_function('packages/uri2flow/uri2flow/validator.py', 'validate_expanded_flow', 1, 2, 5).
python_function('packages/uri2flow/uri2flow/validator.py', 'validate_flow', 1, 11, 4).
python_function('scripts/architecture_audit/areas.py', 'normalize_path', 1, 1, 3).
python_function('scripts/architecture_audit/areas.py', 'area_for_path', 1, 13, 3).
python_function('scripts/architecture_audit/areas.py', 'domain_term_present', 2, 2, 2).
python_function('scripts/architecture_audit/audit.py', 'area_summary', 1, 3, 3).
python_function('scripts/architecture_audit/audit.py', 'build_backlog', 1, 14, 5).
python_function('scripts/architecture_audit/audit.py', '_backlog_item', 4, 1, 0).
python_function('scripts/architecture_audit/audit.py', 'build_audit', 3, 2, 18).
python_function('scripts/architecture_audit/audit.py', '_suggested_gates', 0, 1, 0).
python_function('scripts/architecture_audit/checks_domain.py', 'read_text_if_small', 1, 5, 3).
python_function('scripts/architecture_audit/checks_domain.py', 'audit_domain_vocabulary', 2, 9, 8).
python_function('scripts/architecture_audit/checks_domain.py', '_is_audit_tool_module', 1, 2, 1).
python_function('scripts/architecture_audit/checks_domain.py', '_domain_vocabulary_finding', 2, 4, 2).
python_function('scripts/architecture_audit/checks_domain.py', 'audit_stale_map_entries', 2, 5, 3).
python_function('scripts/architecture_audit/checks_domain.py', 'audit_domain_named_modules', 2, 7, 8).
python_function('scripts/architecture_audit/checks_structure.py', 'is_generated_area', 1, 1, 0).
python_function('scripts/architecture_audit/checks_structure.py', 'unique_ordered', 1, 3, 3).
python_function('scripts/architecture_audit/checks_structure.py', 'sort_findings', 1, 1, 1).
python_function('scripts/architecture_audit/checks_structure.py', 'audit_map_alerts', 2, 5, 3).
python_function('scripts/architecture_audit/checks_structure.py', 'audit_large_modules', 1, 11, 2).
python_function('scripts/architecture_audit/checks_structure.py', '_hotspot_finding', 1, 1, 2).
python_function('scripts/architecture_audit/checks_structure.py', '_should_skip_hotspot', 1, 1, 1).
python_function('scripts/architecture_audit/checks_structure.py', 'audit_duplication', 2, 5, 6).
python_function('scripts/architecture_audit/checks_structure.py', '_ignored_source_areas', 0, 1, 0).
python_function('scripts/architecture_audit/checks_structure.py', '_source_areas', 1, 3, 1).
python_function('scripts/architecture_audit/checks_structure.py', '_is_generated_source_mix', 1, 5, 3).
python_function('scripts/architecture_audit/checks_structure.py', '_is_cross_area', 1, 1, 2).
python_function('scripts/architecture_audit/checks_structure.py', '_is_runtime_operator_boundary', 1, 2, 1).
python_function('scripts/architecture_audit/checks_structure.py', '_classify_duplication', 2, 6, 4).
python_function('scripts/architecture_audit/checks_structure.py', '_live_duplication_group', 2, 5, 4).
python_function('scripts/architecture_audit/checks_structure.py', '_fragment_symbol_is_stale', 2, 5, 5).
python_function('scripts/architecture_audit/checks_structure.py', '_duplication_group_findings', 1, 6, 5).
python_function('scripts/architecture_audit/cli.py', 'build_parser', 0, 1, 4).
python_function('scripts/architecture_audit/cli.py', 'resolve_input', 2, 2, 1).
python_function('scripts/architecture_audit/cli.py', 'write_output', 2, 2, 3).
python_function('scripts/architecture_audit/cli.py', 'fail_code', 2, 4, 1).
python_function('scripts/architecture_audit/cli.py', 'main', 1, 5, 12).
python_function('scripts/architecture_audit/parsers.py', 'parse_inline_list', 1, 4, 2).
python_function('scripts/architecture_audit/parsers.py', 'parse_map', 1, 12, 18).
python_function('scripts/architecture_audit/parsers.py', 'parse_duplication', 1, 11, 18).
python_function('scripts/architecture_audit/render.py', 'render_markdown', 1, 1, 8).
python_function('scripts/architecture_audit/render.py', '_area_lines', 1, 2, 1).
python_function('scripts/architecture_audit/render.py', '_finding_lines', 1, 3, 3).
python_function('scripts/architecture_audit/render.py', '_backlog_lines', 1, 3, 1).
python_function('scripts/architecture_audit/render.py', '_gate_lines', 1, 2, 1).
python_function('scripts/examples/audit_agent_reports.py', '_validate_example', 3, 25, 10).
python_function('scripts/examples/audit_agent_reports.py', '_validate_contracts', 1, 6, 4).
python_function('scripts/examples/audit_agent_reports.py', '_validate_deployments', 2, 26, 19).
python_function('scripts/examples/audit_agent_reports.py', '_write_deployment_reports', 2, 2, 5).
python_function('scripts/examples/audit_agent_reports.py', '_render_markdown', 1, 12, 5).
python_function('scripts/examples/audit_agent_reports.py', 'main', 0, 7, 20).
python_function('scripts/examples/comprehensive_test.py', '_resolve_argv', 3, 8, 5).
python_function('scripts/examples/comprehensive_test.py', '_missing_requirements', 2, 3, 1).
python_function('scripts/examples/comprehensive_test.py', '_tail', 2, 2, 0).
python_function('scripts/examples/comprehensive_test.py', '_run_command', 4, 10, 8).
python_function('scripts/examples/comprehensive_test.py', 'run_suite', 1, 11, 15).
python_function('scripts/examples/comprehensive_test.py', 'write_reports', 2, 12, 14).
python_function('scripts/examples/comprehensive_test.py', '_automation_summary', 1, 9, 5).
python_function('scripts/examples/comprehensive_test.py', 'main', 0, 7, 8).
python_function('scripts/examples/effective_weather_playwright.py', '_run', 1, 3, 3).
python_function('scripts/examples/effective_weather_playwright.py', '_json_cmd', 1, 2, 4).
python_function('scripts/examples/effective_weather_playwright.py', '_health_ok', 1, 2, 1).
python_function('scripts/examples/effective_weather_playwright.py', '_extract_health_uri', 1, 4, 3).
python_function('scripts/examples/effective_weather_playwright.py', '_discover_local_agent_health', 0, 5, 4).
python_function('scripts/examples/effective_weather_playwright.py', '_inspect_agent', 1, 3, 3).
python_function('scripts/examples/effective_weather_playwright.py', '_is_agent_healthy', 2, 4, 3).
python_function('scripts/examples/effective_weather_playwright.py', '_try_repair_or_start', 1, 2, 2).
python_function('scripts/examples/effective_weather_playwright.py', '_ensure_weather_agent', 1, 11, 7).
python_function('scripts/examples/effective_weather_playwright.py', '_flow_text', 2, 2, 2).
python_function('scripts/examples/effective_weather_playwright.py', '_task_text', 2, 1, 1).
python_function('scripts/examples/effective_weather_playwright.py', '_artifact_to_path', 1, 3, 4).
python_function('scripts/examples/effective_weather_playwright.py', '_validate_workflow_result', 2, 14, 4).
python_function('scripts/examples/effective_weather_playwright.py', '_validate_png_artifact', 1, 10, 8).
python_function('scripts/examples/effective_weather_playwright.py', '_run_uri3_flow', 3, 5, 16).
python_function('scripts/examples/effective_weather_playwright.py', '_run_uri2ops_task', 1, 7, 10).
python_function('scripts/examples/effective_weather_playwright.py', 'main', 1, 4, 16).
python_function('scripts/examples/run_uri3_workflow.py', 'main', 1, 4, 11).
python_function('scripts/tellmesh/fix_and_publish.py', 'copy_assets', 0, 5, 8).
python_function('scripts/tellmesh/fix_and_publish.py', 'fix_uri2flow_pyproject', 0, 2, 2).
python_function('scripts/tellmesh/fix_and_publish.py', 'fix_uri2verify_pyproject', 0, 3, 2).
python_function('scripts/tellmesh/fix_and_publish.py', 'fix_nl2uri_urish_sources', 0, 6, 8).
python_function('scripts/tellmesh/fix_and_publish.py', 'update_goal_tests', 0, 3, 5).
python_function('scripts/tellmesh/fix_and_publish.py', 'goal_push', 1, 1, 3).
python_function('scripts/tellmesh/fix_and_publish.py', 'main', 0, 2, 7).
python_function('scripts/tellmesh/move_tests.py', 'sync_tests', 1, 11, 13).
python_function('scripts/tellmesh/move_tests.py', 'remove_hypervisor_tests', 1, 4, 6).
python_function('scripts/tellmesh/move_tests.py', 'push_tellmesh', 1, 2, 2).
python_function('scripts/tellmesh/move_tests.py', 'main', 0, 5, 7).
python_function('scripts/tellmesh/split_packages.py', 'run', 1, 1, 3).
python_function('scripts/tellmesh/split_packages.py', 'goal_yaml', 1, 1, 1).
python_function('scripts/tellmesh/split_packages.py', 'copy_package', 1, 10, 14).
python_function('scripts/tellmesh/split_packages.py', 'append_uv_sources', 2, 5, 7).
python_function('scripts/tellmesh/split_packages.py', 'ensure_repo', 2, 7, 6).
python_function('scripts/tellmesh/split_packages.py', 'publish_with_goal', 2, 3, 2).
python_function('scripts/tellmesh/split_packages.py', 'main', 0, 2, 8).
python_function('scripts/tellmesh/sync_www.py', 'sync_www', 0, 8, 10).
python_function('scripts/tellmesh/sync_www.py', 'main', 0, 5, 12).
python_function('scripts/www/about_parser.py', 'split_frontmatter', 1, 4, 6).
python_function('scripts/www/about_parser.py', 'load_about', 1, 7, 10).
python_function('scripts/www/about_parser.py', 'iter_about_files', 1, 3, 3).
python_function('scripts/www/build_examples_docs.py', '_import_markdown', 0, 2, 1).
python_function('scripts/www/build_examples_docs.py', 'natural_key', 1, 3, 4).
python_function('scripts/www/build_examples_docs.py', 'slug_for_dir', 1, 1, 0).
python_function('scripts/www/build_examples_docs.py', 'slug_for_overview', 0, 1, 0).
python_function('scripts/www/build_examples_docs.py', 'rewrite_example_links', 1, 1, 3).
python_function('scripts/www/build_examples_docs.py', '_resolve_target', 1, 3, 3).
python_function('scripts/www/build_examples_docs.py', '_is_external_or_anchor', 1, 3, 1).
python_function('scripts/www/build_examples_docs.py', '_rewrite_known_www_target', 3, 4, 3).
python_function('scripts/www/build_examples_docs.py', '_rewrite_examples_target', 3, 8, 5).
python_function('scripts/www/build_examples_docs.py', '_rewrite_url', 2, 7, 8).
python_function('scripts/www/build_examples_docs.py', 'md_to_html', 1, 1, 2).
python_function('scripts/www/build_examples_docs.py', 'extract_title', 2, 3, 3).
python_function('scripts/www/build_examples_docs.py', 'list_example_dirs', 0, 8, 9).
python_function('scripts/www/build_examples_docs.py', 'embeddable_files', 1, 7, 8).
python_function('scripts/www/build_examples_docs.py', 'render_file_block', 2, 3, 7).
python_function('scripts/www/build_examples_docs.py', 'render_example_section', 1, 4, 11).
python_function('scripts/www/build_examples_docs.py', 'build_toc', 1, 3, 5).
python_function('scripts/www/build_examples_docs.py', 'build_page', 2, 2, 4).
python_function('scripts/www/build_examples_docs.py', 'build_overview_section', 0, 1, 4).
python_function('scripts/www/build_examples_docs.py', 'main', 0, 7, 14).
python_function('scripts/www/build_examples_manifest.py', 'natural_key', 1, 3, 4).
python_function('scripts/www/build_examples_manifest.py', 'extract_title', 2, 4, 6).
python_function('scripts/www/build_examples_manifest.py', 'category_for', 1, 3, 1).
python_function('scripts/www/build_examples_manifest.py', '_build_office_chain', 1, 11, 5).
python_function('scripts/www/build_examples_manifest.py', 'load_office_chains', 0, 6, 7).
python_function('scripts/www/build_examples_manifest.py', 'test_summary', 0, 1, 1).
python_function('scripts/www/build_examples_manifest.py', 'build_manifest', 0, 11, 13).
python_function('scripts/www/build_examples_manifest.py', 'main', 0, 5, 11).
python_function('scripts/www/build_landing_integrations.py', '_esc', 1, 1, 1).
python_function('scripts/www/build_landing_integrations.py', '_i18n_values', 2, 7, 3).
python_function('scripts/www/build_landing_integrations.py', '_cta_i18n_values', 2, 4, 3).
python_function('scripts/www/build_landing_integrations.py', '_spotlight_body_html', 3, 11, 10).
python_function('scripts/www/build_landing_integrations.py', '_render_cta_links', 2, 5, 6).
python_function('scripts/www/build_landing_integrations.py', '_render_i18n_spans', 1, 5, 7).
python_function('scripts/www/build_landing_integrations.py', '_render_i18n', 2, 6, 6).
python_function('scripts/www/build_landing_integrations.py', '_snippet_block', 1, 3, 4).
python_function('scripts/www/build_landing_integrations.py', 'render_connector', 1, 4, 7).
python_function('scripts/www/build_landing_integrations.py', 'render_card', 2, 2, 7).
python_function('scripts/www/build_landing_integrations.py', '_render_inline_i18n', 1, 5, 6).
python_function('scripts/www/build_landing_integrations.py', 'render_spotlight', 2, 4, 8).
python_function('scripts/www/build_landing_integrations.py', '_card_body_html', 3, 3, 4).
python_function('scripts/www/build_landing_integrations.py', 'collect_cards', 0, 10, 12).
python_function('scripts/www/build_landing_integrations.py', 'build_sections', 1, 12, 5).
python_function('scripts/www/build_landing_integrations.py', 'splice_index', 2, 4, 5).
python_function('scripts/www/build_landing_integrations.py', 'write_i18n_js', 1, 1, 3).
python_function('scripts/www/build_landing_integrations.py', 'main', 0, 12, 14).
python_function('scripts/www/check_examples_links.py', '_iter_hrefs', 1, 2, 2).
python_function('scripts/www/check_examples_links.py', '_collect_anchor_ids', 1, 1, 2).
python_function('scripts/www/check_examples_links.py', '_extract_block', 2, 2, 2).
python_function('scripts/www/check_examples_links.py', '_check_href', 1, 12, 7).
python_function('scripts/www/check_examples_links.py', 'check_examples_links', 1, 9, 8).
python_function('scripts/www/check_examples_links.py', 'main', 0, 3, 6).
python_function('scripts/www/md_html.py', '_import_markdown', 0, 2, 1).
python_function('scripts/www/md_html.py', 'md_to_html', 1, 2, 3).
python_function('scripts/www/md_html.py', 'cache_key', 2, 1, 4).
python_function('scripts/www/md_html.py', 'cached_html', 3, 3, 8).
python_function('scripts/www/monitor_landing.py', 'fetch_html', 2, 2, 5).
python_function('scripts/www/monitor_landing.py', 'extract_prices', 1, 3, 4).
python_function('scripts/www/monitor_landing.py', 'load_baseline', 1, 2, 3).
python_function('scripts/www/monitor_landing.py', 'save_baseline', 2, 1, 3).
python_function('scripts/www/monitor_landing.py', 'main', 0, 7, 13).
python_function('scripts/www/monitor_notify.py', 'webhook_url', 1, 3, 1).
python_function('scripts/www/monitor_notify.py', 'is_placeholder_webhook', 1, 2, 2).
python_function('scripts/www/monitor_notify.py', 'is_supported_webhook', 1, 1, 1).
python_function('scripts/www/monitor_notify.py', 'emit_alert', 2, 7, 7).
python_function('scripts/www/monitor_notify.py', 'post_webhook', 2, 3, 6).
python_function('scripts/www/monitor_url.py', 'fetch', 2, 1, 4).
python_function('scripts/www/monitor_url.py', 'main', 0, 5, 6).
python_function('scripts/www/site_nav.py', 'brand_logo_src', 1, 1, 0).
python_function('scripts/www/site_nav.py', 'render_brand', 0, 2, 1).
python_function('scripts/www/site_nav.py', 'render_topbar', 0, 5, 2).
python_function('scripts/www/site_nav.py', 'render_footer', 0, 1, 0).
python_function('scripts/www/www_root.py', 'www_dir', 0, 2, 1).
python_function('tests/architecture/envelope_helpers.py', 'normalize_service_result', 1, 2, 2).
python_function('tests/architecture/envelope_helpers.py', 'assert_service_result_shape', 1, 5, 4).
python_function('tests/architecture/envelope_helpers.py', 'assert_workflow_result_shape', 1, 2, 2).
python_function('tests/architecture/import_scanner.py', 'repo_root_from_here', 0, 1, 1).
python_function('tests/architecture/test_doctor_contract.py', 'test_doctor_contract', 1, 4, 2).
python_function('tests/architecture/test_doctor_gate.py', 'test_uri3_doctor_gate', 1, 5, 2).
python_function('tests/architecture/test_explain_contract.py', '_assert_explain_contract', 1, 5, 3).
python_function('tests/architecture/test_explain_contract.py', 'test_explain_weather_contract', 1, 2, 2).
python_function('tests/architecture/test_explain_contract.py', 'test_explain_browser_contract', 1, 2, 2).
python_function('tests/architecture/test_explain_contract.py', 'test_explain_http_contract', 1, 2, 2).
python_function('tests/architecture/test_import_boundaries.py', 'test_forbidden_imports', 0, 2, 2).
python_function('tests/architecture/test_result_envelope_contract.py', 'test_touri_call_envelope', 1, 1, 3).
python_function('tests/architecture/test_result_envelope_contract.py', 'test_touri_data_quality_failure_envelope', 1, 4, 5).
python_function('tests/architecture/test_result_envelope_contract.py', 'test_uri3_workflow_dry_run_envelope', 0, 1, 3).
python_function('tests/architecture/test_technical_ok_business_fail.py', '_write_capability', 2, 1, 2).
python_function('tests/architecture/test_technical_ok_business_fail.py', 'test_technical_ok_business_fail_via_data_quality', 1, 11, 5).
python_function('tests/architecture/test_uri2run_envelope.py', 'test_uri2run_python_envelope', 0, 3, 3).
python_function('tests/architecture/test_uri2run_envelope.py', 'test_uri2run_shell_envelope', 0, 2, 3).
python_function('tests/capabilities/weather_forecast/test_fixtures.py', 'test_weather_forecast_fixtures_exist', 1, 3, 2).
python_function('tests/capabilities/weather_forecast/test_fixtures.py', 'test_good_fixture_contains_expected_marker', 1, 3, 1).
python_function('tests/conftest.py', 'repo_root', 0, 4, 6).
python_function('tests/conftest.py', '_hypervisor_repo_root_env', 1, 2, 5).
python_function('tests/conftest.py', 'workspace_pythonpath', 1, 4, 4).
python_function('tests/conftest.py', 'workspace_env', 1, 4, 9).
python_function('tests/conftest.py', 'cli_argv', 1, 11, 7).
python_function('tests/conftest.py', 'examples_env', 1, 1, 2).
python_function('tests/domain_pack/test_generator.py', '_weather_tree', 0, 1, 0).
python_function('tests/domain_pack/test_generator.py', 'test_derive_domain_model', 0, 3, 3).
python_function('tests/domain_pack/test_generator.py', 'test_generate_proto_weather', 0, 2, 4).
python_function('tests/domain_pack/test_generator.py', 'test_generate_resources_and_views', 0, 3, 5).
python_function('tests/domain_pack/test_generator.py', 'test_generate_domain_pack_from_tree', 1, 3, 4).
python_function('tests/domain_pack/test_generator.py', 'test_generate_domain_pack_from_uri_tree_file', 1, 3, 5).
python_function('tests/domain_pack/test_generator.py', 'test_deprecated_meta_agent_reexport', 0, 3, 4).
python_function('tests/examples/capabilities.py', '_tcp_open', 3, 2, 1).
python_function('tests/examples/capabilities.py', '_http_ok', 2, 2, 4).
python_function('tests/examples/capabilities.py', '_adb_device', 0, 6, 5).
python_function('tests/examples/capabilities.py', '_uia_available', 0, 3, 2).
python_function('tests/examples/capabilities.py', '_cli_available', 2, 5, 4).
python_function('tests/examples/capabilities.py', '_weather_agent_health', 0, 6, 4).
python_function('tests/examples/capabilities.py', 'probe_machine', 1, 6, 14).
python_function('tests/examples/capabilities.py', 'write_capabilities_report', 3, 1, 4).
python_function('tests/examples/command_catalog.py', '_run_sh_commands', 0, 6, 3).
python_function('tests/examples/conftest.py', 'repo_root', 0, 3, 5).
python_function('tests/examples/conftest.py', 'examples_env', 1, 2, 3).
python_function('tests/examples/conftest.py', 'run_shell', 2, 1, 1).
python_function('tests/examples/conftest.py', 'docker_available', 0, 2, 2).
python_function('tests/examples/conftest.py', '_python_candidates', 1, 6, 5).
python_function('tests/examples/conftest.py', '_python_runs_playwright', 2, 1, 1).
python_function('tests/examples/conftest.py', 'playwright_python', 1, 3, 2).
python_function('tests/examples/conftest.py', 'playwright_available', 1, 2, 1).
python_function('tests/examples/conftest.py', 'www_available', 0, 2, 2).
python_function('tests/examples/conftest.py', 'skip_if_markers', 2, 7, 4).
python_function('tests/examples/shell_runner.py', '_skip', 2, 1, 0).
python_function('tests/examples/shell_runner.py', '_run_sh', 3, 1, 2).
python_function('tests/examples/shell_runner.py', '_local_agent_url', 2, 3, 3).
python_function('tests/examples/shell_runner.py', '_ex02', 2, 2, 3).
python_function('tests/examples/shell_runner.py', '_ex03', 2, 3, 4).
python_function('tests/examples/shell_runner.py', '_ex05', 2, 3, 1).
python_function('tests/examples/shell_runner.py', '_ex06', 2, 3, 1).
python_function('tests/examples/shell_runner.py', '_ex07', 2, 3, 3).
python_function('tests/examples/shell_runner.py', '_ex08', 2, 1, 1).
python_function('tests/examples/shell_runner.py', '_ex15pw', 2, 2, 3).
python_function('tests/examples/shell_runner.py', '_ex16www', 2, 4, 4).
python_function('tests/examples/shell_runner.py', '_ex22dash', 2, 2, 3).
python_function('tests/examples/shell_runner.py', '_ex11', 2, 2, 2).
python_function('tests/examples/shell_runner.py', '_should_skip', 2, 7, 3).
python_function('tests/examples/shell_runner.py', 'run_example', 1, 4, 5).
python_function('tests/examples/shell_runner.py', 'run_catalog', 0, 9, 9).
python_function('tests/examples/shell_runner.py', 'main', 1, 1, 4).
python_function('tests/examples/test_comprehensive.py', '_missing', 2, 3, 1).
python_function('tests/examples/test_comprehensive.py', '_resolve_argv', 3, 8, 5).
python_function('tests/examples/test_comprehensive.py', '_run_spec', 3, 8, 7).
python_function('tests/examples/test_comprehensive.py', 'machine_caps', 1, 1, 2).
python_function('tests/examples/test_comprehensive.py', 'test_default_example_commands', 4, 2, 5).
python_function('tests/examples/test_comprehensive.py', 'test_real_example_commands', 4, 2, 5).
python_function('tests/examples/test_comprehensive.py', 'test_capabilities_report_written', 2, 3, 2).
python_function('tests/examples/test_comprehensive.py', 'test_command_catalog_covers_all_examples', 0, 4, 1).
python_function('tests/examples/test_comprehensive.py', 'test_compact_flow_real_command_is_self_contained', 0, 5, 1).
python_function('tests/examples/test_effective_weather_playwright.py', 'test_flow_text_with_screenshot_is_valid_compact_flow', 0, 5, 2).
python_function('tests/examples/test_effective_weather_playwright.py', 'test_artifact_uri_maps_to_workflow_output_path', 0, 2, 1).
python_function('tests/examples/test_examples_smoke.py', 'test_examples_readme_lists_known_directories', 1, 3, 2).
python_function('tests/examples/test_examples_smoke.py', 'test_run_sh_script_exists', 2, 2, 3).
python_function('tests/examples/test_examples_smoke.py', 'test_touri_capability_manifests_validate', 2, 3, 5).
python_function('tests/examples/test_examples_smoke.py', 'test_workflow_graph_yaml_parseable', 1, 3, 3).
python_function('tests/examples/test_examples_smoke.py', 'test_architecture_stack_imports', 0, 4, 1).
python_function('tests/examples/test_examples_smoke.py', 'test_catalog_covers_all_run_sh', 1, 6, 3).
python_function('tests/examples/test_inline_examples.py', '_local_agent_url', 2, 3, 3).
python_function('tests/examples/test_inline_examples.py', 'test_example_02_uri3_scan_http', 2, 3, 4).
python_function('tests/examples/test_inline_examples.py', 'test_example_03_ssh_docker_testenv', 2, 5, 5).
python_function('tests/examples/test_inline_examples.py', 'test_example_05_meta_repair', 2, 3, 1).
python_function('tests/examples/test_inline_examples.py', 'test_example_06_orders_agent', 2, 3, 1).
python_function('tests/examples/test_inline_examples.py', 'test_example_07_invoices_agent', 2, 3, 3).
python_function('tests/examples/test_inline_examples.py', 'test_example_08_evolution', 2, 2, 1).
python_function('tests/examples/test_inline_examples.py', 'test_example_15_playwright_mock_via_uri3', 2, 3, 3).
python_function('tests/examples/test_inline_examples.py', 'test_example_16www_landing_monitor', 2, 4, 5).
python_function('tests/examples/test_inline_examples.py', 'test_example_22_dashboard_agent', 2, 3, 3).
python_function('tests/examples/test_run_sh_examples.py', 'test_example_run_sh', 3, 3, 5).
python_function('tests/generator/test_headers.py', 'test_generated_python_files_have_standard_header', 2, 9, 9).
python_function('tests/generator/test_headers.py', 'test_contract_source_ref_is_repo_relative', 0, 2, 3).
python_function('tests/generator/test_headers.py', 'test_verify_generated_ignores_pycache', 2, 2, 6).
python_function('tests/hypervisor/test_agent_describe.py', 'test_describe_weather_agent_markdown', 0, 11, 1).
python_function('tests/hypervisor/test_agent_describe.py', 'test_describe_desktop_operator_contract', 0, 8, 1).
python_function('tests/hypervisor/test_agent_describe.py', 'test_describe_invoices_agent_skill_examples', 0, 3, 1).
python_function('tests/hypervisor/test_agent_describe.py', 'test_describe_dashboard_system_agent_architecture', 0, 6, 1).
python_function('tests/hypervisor/test_agent_describe.py', 'test_describe_screenshot_analysis_custom_agent', 0, 15, 1).
python_function('tests/hypervisor/test_agent_describe.py', 'test_describe_weather_agent_has_health_uri', 0, 15, 4).
python_function('tests/hypervisor/test_agent_describe.py', 'test_describe_agent_writes_file', 1, 4, 4).
python_function('tests/hypervisor/test_agent_factory_uri.py', 'test_agent_factory_generate_uri_dry_run', 1, 5, 3).
python_function('tests/hypervisor/test_agent_factory_uri.py', 'test_hypervisor_agent_run_uri_dry_run_waits_for_generated_deployment', 1, 5, 1).
python_function('tests/hypervisor/test_agent_factory_uri.py', 'test_hypervisor_local_alias_run_uri_dry_run', 0, 4, 2).
python_function('tests/hypervisor/test_agent_factory_uri.py', 'test_schema_uri_returns_agent_contract_and_capability_refs', 1, 7, 4).
python_function('tests/hypervisor/test_agent_factory_uri.py', 'test_file_uri_returns_small_text_content', 1, 5, 3).
python_function('tests/hypervisor/test_agent_lifecycle.py', 'client', 0, 1, 1).
python_function('tests/hypervisor/test_agent_lifecycle.py', 'test_registry_lists_new_agents', 0, 4, 1).
python_function('tests/hypervisor/test_agent_lifecycle.py', 'test_api_agents_includes_new_deployments', 1, 5, 2).
python_function('tests/hypervisor/test_agent_lifecycle.py', 'test_build_run_plan_for_new_agents', 3, 4, 3).
python_function('tests/hypervisor/test_agent_lifecycle.py', 'test_uri_health_dry_run_for_new_agent', 0, 3, 1).
python_function('tests/hypervisor/test_agent_lifecycle.py', 'test_uri_repair_diagnose_for_new_agent', 0, 6, 1).
python_function('tests/hypervisor/test_agent_lifecycle.py', 'test_uri_repair_apply_dry_run', 1, 3, 3).
python_function('tests/hypervisor/test_agent_lifecycle.py', 'test_uri_repair_auto_dry_run', 0, 5, 2).
python_function('tests/hypervisor/test_agent_lifecycle.py', 'test_uri_repair_apply_requires_approval', 1, 3, 2).
python_function('tests/hypervisor/test_agent_lifecycle.py', 'test_hypervisor_repair_supervisor_auto', 1, 3, 4).
python_function('tests/hypervisor/test_agent_lifecycle.py', 'test_hypervisor_repair_forced_playbook_runs_when_healthy', 1, 5, 3).
python_function('tests/hypervisor/test_agent_runner.py', '_deployment_port', 1, 3, 3).
python_function('tests/hypervisor/test_agent_runner.py', '_mock_run_dependencies', 1, 1, 1).
python_function('tests/hypervisor/test_agent_runner.py', 'test_local_target_to_module', 0, 2, 1).
python_function('tests/hypervisor/test_agent_runner.py', 'test_build_run_plan_for_local_deployment', 0, 6, 3).
python_function('tests/hypervisor/test_agent_runner.py', 'test_build_run_plan_with_port_override_updates_local_endpoints', 0, 4, 2).
python_function('tests/hypervisor/test_agent_runner.py', 'test_run_agent_dry_run_emits_lifecycle_event', 1, 5, 3).
python_function('tests/hypervisor/test_agent_runner.py', 'test_build_run_plan_missing_path', 2, 1, 4).
python_function('tests/hypervisor/test_agent_runner.py', 'test_agent_status_without_health', 0, 3, 1).
python_function('tests/hypervisor/test_agent_runner.py', 'test_ssh_run_plan_via_build_run_plan', 0, 3, 2).
python_function('tests/hypervisor/test_agent_runner.py', 'test_ssh_target_starts_via_remote_runner', 1, 3, 3).
python_function('tests/hypervisor/test_agent_runner.py', 'test_run_agent_detach_idempotent_when_already_running', 1, 4, 4).
python_function('tests/hypervisor/test_agent_runner.py', 'test_run_agent_reuse_syncs_health_uri_from_command', 1, 4, 4).
python_function('tests/hypervisor/test_agent_runner.py', 'test_run_agent_restarts_when_explicit_port_differs', 1, 8, 6).
python_function('tests/hypervisor/test_agent_runner.py', 'test_run_agent_if_running_fail', 1, 1, 3).
python_function('tests/hypervisor/test_agent_runner.py', 'test_run_agent_rebinds_when_preferred_port_busy', 1, 8, 6).
python_function('tests/hypervisor/test_agent_runner.py', 'test_stop_agent_cleans_orphan_listener_from_stale_runtime', 1, 8, 4).
python_function('tests/hypervisor/test_agent_runner.py', 'test_stop_agent_does_not_kill_foreign_listener_without_state', 1, 6, 4).
python_function('tests/hypervisor/test_agent_runner.py', 'test_inspect_agent_separates_process_running_from_health', 1, 10, 3).
python_function('tests/hypervisor/test_agent_runner.py', 'test_inspect_agent_detects_command_health_mismatch', 1, 6, 4).
python_function('tests/hypervisor/test_agent_runner.py', 'test_inspect_agent_reads_process_log_uri', 1, 4, 4).
python_function('tests/hypervisor/test_agent_runner.py', 'test_supervise_auto_syncs_health_uri', 1, 5, 5).
python_function('tests/hypervisor/test_agent_runner.py', 'test_ensure_agent_healthy_waits_before_first_probe', 1, 4, 3).
python_function('tests/hypervisor/test_agent_runner.py', 'test_verify_local_deployment', 1, 5, 3).
python_function('tests/hypervisor/test_artifact_standards.py', 'test_runtime_state_schema_on_save', 1, 7, 5).
python_function('tests/hypervisor/test_artifact_standards.py', 'test_legacy_runtime_state_upgrades_on_load', 1, 3, 3).
python_function('tests/hypervisor/test_artifact_standards.py', 'test_log_event_envelope', 1, 4, 4).
python_function('tests/hypervisor/test_artifact_standards.py', 'test_deployment_registry_declared_runtime_views', 0, 6, 7).
python_function('tests/hypervisor/test_artifact_standards.py', 'test_planfile_ticket_import_and_proposal', 1, 5, 8).
python_function('tests/hypervisor/test_artifact_standards.py', 'test_evolution_source_normalization', 0, 3, 1).
python_function('tests/hypervisor/test_artifact_standards.py', 'test_artifact_lifecycle_coverage_reports_loose_files', 1, 6, 3).
python_function('tests/hypervisor/test_artifact_standards.py', 'test_repo_uri_configs_are_canonical_artifacts', 0, 8, 8).
python_function('tests/hypervisor/test_autonomous_agents.py', 'test_describe_remote_deploy_custom_agent', 0, 5, 1).
python_function('tests/hypervisor/test_autonomous_agents.py', 'test_describe_gnome_programmer_custom_agent', 0, 4, 1).
python_function('tests/hypervisor/test_autonomous_agents.py', 'test_remote_deploy_plan_for_ssh_dev', 0, 3, 1).
python_function('tests/hypervisor/test_browser_operator_separation.py', '_load_browser_operator', 1, 1, 2).
python_function('tests/hypervisor/test_browser_operator_separation.py', 'test_browser_operator_contract_is_generic_capability_agent', 1, 13, 2).
python_function('tests/hypervisor/test_browser_operator_separation.py', 'test_browser_domain_registry_uses_operator_uris', 1, 9, 6).
python_function('tests/hypervisor/test_browser_operator_separation.py', 'test_browser_operator_is_registered_as_package_agent', 1, 10, 3).
python_function('tests/hypervisor/test_browser_ops_domain.py', '_load_yaml', 2, 1, 2).
python_function('tests/hypervisor/test_browser_ops_domain.py', 'test_browser_ops_domain_declares_operator_boundary', 1, 7, 1).
python_function('tests/hypervisor/test_browser_ops_domain.py', 'test_browser_ops_operator_registry_matches_uri2ops_capabilities', 1, 6, 2).
python_function('tests/hypervisor/test_browser_ops_domain.py', 'test_browser_ops_scenario_registry_is_loaded_and_routable', 1, 6, 3).
python_function('tests/hypervisor/test_browser_ops_domain.py', 'test_browser_operator_points_to_browser_ops_without_owning_scenarios', 1, 4, 1).
python_function('tests/hypervisor/test_chat_flow_view.py', 'client', 0, 1, 1).
python_function('tests/hypervisor/test_chat_flow_view.py', '_planner_plans_from_ask', 1, 13, 1).
python_function('tests/hypervisor/test_chat_flow_view.py', 'test_batch_ask_yields_three_flow_plans', 0, 9, 3).
python_function('tests/hypervisor/test_chat_flow_view.py', 'test_workflow_dry_run_uri_call_returns_graph_steps', 1, 12, 4).
python_function('tests/hypervisor/test_chat_www.py', 'client', 0, 1, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_format_ask_markdown_dashboard', 0, 5, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_format_uri_result_dry_run_preview', 0, 3, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_format_uri_result_diagnosis_markdown', 0, 4, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_format_uri_result_summary_omits_envelope_json', 0, 5, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_format_uri_result_markdown', 0, 4, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_format_uri_result_markdown_workflow_plan', 0, 7, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_format_uri_result_markdown_include_envelope_opt_in', 0, 2, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_format_uri_result_markdown_includes_runtime_and_logs', 0, 7, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_format_uri_result_markdown_reads_top_level_runtime', 0, 6, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_format_uri_result_markdown_shows_log_entries', 0, 4, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_ask_returns_markdown', 2, 5, 3).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_ask_detects_agent_operational_prompts', 5, 8, 3).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_ask_detects_screenshot_schedule_as_workflow', 1, 6, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_ask_detects_weather_forecast', 1, 7, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_ask_multiline_batch_plans_each_line', 1, 13, 3).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_ask_accepts_chat_uri_field', 1, 8, 5).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_ask_accepts_chat_uri_as_prompt', 1, 4, 3).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_uri_call_chat_prompt', 1, 5, 3).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_ask_requires_prompt_or_uri', 1, 3, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_ask_accepts_nl_uri', 1, 6, 5).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_uri_call_nl_uri_plans', 1, 5, 3).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_uri_call_dry_run_preview_markdown', 1, 5, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_uri_call_repair_dry_run_is_preview', 1, 8, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_uri_call_physical_operator_dry_run_is_preview', 1, 7, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_root_redirects_to_www', 1, 3, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_index_served', 1, 9, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_index_integrations_section', 1, 5, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_index_office_examples', 1, 8, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_examples_gallery', 1, 7, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_examples_docs_page', 1, 8, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_build_examples_docs_script', 1, 3, 3).
python_function('tests/hypervisor/test_chat_www.py', 'test_examples_docs_link_check', 1, 2, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_index_links_examples_gallery', 1, 4, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_ask_office_invoice_batch', 1, 5, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_readme_links_docs_todo_changelog', 1, 7, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_chat_served', 1, 18, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_flow_chat_served', 1, 7, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_chat_flow_view_module', 1, 5, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_chat_js_guards_stale_and_duplicate_actions', 1, 20, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_landing_has_tour_copy', 1, 5, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_landing_js_explains_repair_loop', 1, 11, 3).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_compose_mounts_system_artifacts', 1, 8, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_www_dockerfile_includes_generated_agents_and_repair_cases', 1, 5, 1).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_events_returns_typed_feed', 1, 4, 3).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_events_stream_contract', 1, 6, 8).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_plan_run_dry_run', 1, 7, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_plan_run_speak_summary', 1, 4, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_voice_speak_mock', 1, 4, 2).
python_function('tests/hypervisor/test_chat_www.py', 'test_api_voice_transcribe_mock', 1, 3, 2).
python_function('tests/hypervisor/test_config.py', 'test_default_config_has_structured_sections', 0, 8, 2).
python_function('tests/hypervisor/test_config.py', 'test_load_config_merges_user_file', 1, 7, 2).
python_function('tests/hypervisor/test_config.py', 'test_env_overrides', 1, 4, 2).
python_function('tests/hypervisor/test_config.py', 'test_validate_config_reports_invalid_profile', 0, 3, 2).
python_function('tests/hypervisor/test_config.py', 'test_load_hypervisor_config_model', 0, 5, 4).
python_function('tests/hypervisor/test_config.py', 'test_load_config_merges_llm_uri_yaml', 0, 5, 5).
python_function('tests/hypervisor/test_contract_uri.py', '_write_contract_fixture', 1, 1, 2).
python_function('tests/hypervisor/test_contract_uri.py', 'test_contract_uri_fetch_by_agent_name', 1, 9, 2).
python_function('tests/hypervisor/test_contract_uri.py', 'test_contract_uri_fetch_by_agents_slug', 1, 3, 2).
python_function('tests/hypervisor/test_contract_uri.py', 'test_contract_uri_validate_agent', 1, 5, 2).
python_function('tests/hypervisor/test_contract_uri.py', 'test_contract_uri_validate_registry', 1, 3, 2).
python_function('tests/hypervisor/test_contract_uri.py', 'test_contract_uri_fetch_weather_agent', 1, 4, 1).
python_function('tests/hypervisor/test_contract_uri.py', 'test_schema_uri_includes_contract_related_uri', 1, 3, 2).
python_function('tests/hypervisor/test_contract_uri.py', 'test_contract_uri_generate_dry_run', 1, 6, 3).
python_function('tests/hypervisor/test_contract_uri.py', 'test_contract_uri_generate_writes_package', 1, 6, 3).
python_function('tests/hypervisor/test_contract_uri.py', 'test_contract_uri_artifacts_manifest', 1, 6, 4).
python_function('tests/hypervisor/test_contract_uri.py', 'test_contract_uri_artifacts_includes_proto_for_user_agent', 1, 5, 1).
python_function('tests/hypervisor/test_dashboard_agent.py', 'client', 0, 1, 1).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_health_and_agent_card', 1, 6, 3).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_ui_agents_lists_deployments', 2, 3, 2).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_api_process_view', 2, 3, 4).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_uri_call_read_allowed', 2, 3, 3).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_uri_call_repair_apply_requires_approval', 1, 3, 2).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_uri_call_repair_apply_with_approval', 2, 2, 2).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_uri_call_execution_error_returns_failed_envelope', 2, 6, 4).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_policy_preview_repair', 0, 3, 1).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_monitor_webhook_surfaces_in_events', 3, 8, 5).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_local_target_supports_packages_path', 0, 2, 1).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_local_target_supports_system_dashboard_path', 0, 2, 1).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_resolve_view_uri_process', 1, 3, 4).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_call_system_uri_marks_view_and_logs_as_success', 1, 5, 3).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_uri_implies_dry_run_suffix', 0, 3, 1).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_call_system_uri_workflow_portal_zus_dry_run', 0, 3, 2).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_api_uri_call_workflow_without_dry_run_checkbox', 1, 5, 3).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_call_system_uri_http_health', 1, 3, 4).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_call_system_uri_browser_open_mock', 0, 3, 2).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_call_system_uri_browser_open_dry_run_plan', 0, 4, 2).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_call_system_uri_office_supplier_report_dry_run', 0, 3, 2).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_call_system_uri_office_supplier_report_execute', 1, 3, 2).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_api_uri_call_office_supplier_report', 1, 4, 3).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_api_uri_call_browser_open', 1, 4, 3).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_api_uri_call_browser_open_requires_approval', 1, 4, 2).
python_function('tests/hypervisor/test_dashboard_agent.py', 'test_api_uri_call_desktop_operator_health', 1, 4, 3).
python_function('tests/hypervisor/test_dashboard_policy.py', 'test_dashboard_blocks_repair_apply_without_approval', 0, 3, 1).
python_function('tests/hypervisor/test_dashboard_policy.py', 'test_dashboard_allows_repair_apply_with_approval', 0, 2, 1).
python_function('tests/hypervisor/test_dashboard_policy.py', 'test_dashboard_blocks_browser_mutation_without_approval', 0, 3, 1).
python_function('tests/hypervisor/test_dashboard_policy.py', 'test_dashboard_preview_marks_repair_apply_as_requires_approval', 0, 3, 1).
python_function('tests/hypervisor/test_dashboard_routing_api.py', 'client', 0, 1, 1).
python_function('tests/hypervisor/test_dashboard_routing_api.py', 'test_explain_system_uri_includes_hypervisor_resolution', 1, 6, 1).
python_function('tests/hypervisor/test_dashboard_routing_api.py', 'test_api_uri_explain_operator_route', 1, 6, 2).
python_function('tests/hypervisor/test_dashboard_routing_api.py', 'test_call_system_uri_operator_uses_hypervisor_dispatch', 2, 5, 3).
python_function('tests/hypervisor/test_deployment_aliases.py', 'test_load_weather_agent_alias_from_domain_fragment', 1, 2, 2).
python_function('tests/hypervisor/test_deployment_aliases.py', 'test_resolve_local_weather_agent_alias', 1, 2, 1).
python_function('tests/hypervisor/test_deployment_aliases.py', 'test_weather_map_fragment_declares_alias', 1, 3, 1).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_load_default_deployments', 0, 7, 5).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_deployment_from_weather_uri_tree', 0, 5, 2).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_sync_from_uri_tree_writes_registry', 1, 4, 5).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_sync_from_uri_tree_preserves_existing_http_endpoints', 1, 5, 6).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_upsert_replaces_existing_deployment', 1, 2, 6).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_resolve_status_without_health_check', 0, 2, 2).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_registry_summary', 0, 3, 4).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_ssh_target_uri_supported_in_model', 1, 2, 9).
python_function('tests/hypervisor/test_deployment_selector.py', 'test_parse_hypervisor_local_uri', 0, 3, 1).
python_function('tests/hypervisor/test_deployment_selector.py', 'test_parse_hypervisor_deployment_uri', 0, 3, 1).
python_function('tests/hypervisor/test_deployment_selector.py', 'test_resolve_local_weather_agent_alias', 0, 2, 1).
python_function('tests/hypervisor/test_desktop_operator_separation.py', '_load_desktop_operator', 1, 1, 2).
python_function('tests/hypervisor/test_desktop_operator_separation.py', 'test_desktop_operator_contract_is_generic_capability_agent', 1, 14, 2).
python_function('tests/hypervisor/test_desktop_operator_separation.py', 'test_desktop_operator_does_not_embed_domain_vocabulary', 1, 3, 2).
python_function('tests/hypervisor/test_desktop_operator_separation.py', 'test_domain_registry_uses_operator_uris_without_owning_operator_contract', 1, 8, 6).
python_function('tests/hypervisor/test_desktop_operator_separation.py', 'test_desktop_operator_is_registered_as_package_agent', 1, 10, 3).
python_function('tests/hypervisor/test_desktop_ops_domain.py', '_load_yaml', 2, 1, 2).
python_function('tests/hypervisor/test_desktop_ops_domain.py', 'test_desktop_ops_domain_declares_operator_boundary', 1, 18, 2).
python_function('tests/hypervisor/test_desktop_ops_domain.py', 'test_desktop_ops_operator_registry_matches_uri2ops_capabilities', 1, 15, 4).
python_function('tests/hypervisor/test_desktop_ops_domain.py', 'test_desktop_ops_scenario_registry_is_loaded_and_routable', 1, 8, 3).
python_function('tests/hypervisor/test_desktop_ops_domain.py', 'test_desktop_ops_does_not_embed_vertical_scenarios', 1, 4, 2).
python_function('tests/hypervisor/test_desktop_ops_domain.py', 'test_desktop_operator_points_to_desktop_ops_without_owning_scenarios', 1, 7, 1).
python_function('tests/hypervisor/test_docker_runner.py', 'test_build_docker_deploy_plan', 0, 4, 3).
python_function('tests/hypervisor/test_docker_runner.py', 'test_build_docker_control_plan_up', 0, 3, 2).
python_function('tests/hypervisor/test_events_service.py', 'test_collect_system_events_includes_log_event', 2, 6, 4).
python_function('tests/hypervisor/test_events_service.py', 'test_collect_system_events_includes_hypervisor_operation_events', 2, 6, 3).
python_function('tests/hypervisor/test_events_service.py', 'test_collect_system_events_prefers_latest_log_lines', 2, 4, 8).
python_function('tests/hypervisor/test_events_service.py', 'test_collect_system_events_includes_supervise_watch_log_event', 2, 6, 4).
python_function('tests/hypervisor/test_events_service.py', 'test_collect_system_events_includes_watch_log_with_agent_id', 2, 6, 4).
python_function('tests/hypervisor/test_events_service.py', 'test_collect_system_events_includes_incident', 2, 3, 5).
python_function('tests/hypervisor/test_events_service.py', 'test_collect_system_events_treats_http_healthy_unmanaged_agent_as_healthy', 2, 4, 2).
python_function('tests/hypervisor/test_graph_hypervisor_routing.py', 'test_workflow_operator_uses_hypervisor_routing', 2, 5, 3).
python_function('tests/hypervisor/test_health_uri.py', 'test_resolve_effective_health_uri_prefers_network_effective_uri', 0, 2, 1).
python_function('tests/hypervisor/test_health_uri.py', 'test_resolve_effective_health_uri_uses_process_command', 0, 2, 1).
python_function('tests/hypervisor/test_health_uri.py', 'test_command_port_from_runtime_uses_network_effective_port', 0, 2, 1).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_deployments_and_run_agent_dry_run', 1, 9, 5).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_ssh_run_agent_dry_run', 1, 4, 3).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_deploy_agent_dry_run', 1, 3, 3).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_agent_status_includes_runtime_fields', 1, 4, 3).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_run_agent_dry_run_accepts_if_running', 1, 3, 3).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_run_agent_dry_run_emits_operation_event', 2, 5, 5).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_run_agent_accepts_approve_compatibility_flag', 1, 4, 3).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_explain_operator_route', 1, 5, 3).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_call_operator_route_uses_hypervisor_dispatch', 2, 5, 5).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_inspect_agent', 2, 3, 4).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_supervise_watch_limited', 2, 6, 13).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_repair_heal', 2, 3, 4).
python_function('tests/hypervisor/test_inspection_probe.py', 'test_probe_http_rewrites_localhost_when_probe_host_is_set', 1, 5, 4).
python_function('tests/hypervisor/test_inspection_probe.py', 'test_probe_http_keeps_non_localhost_targets', 1, 4, 4).
python_function('tests/hypervisor/test_inspection_probe.py', 'test_probe_http_accepts_expected_service_without_agent', 1, 4, 3).
python_function('tests/hypervisor/test_inspection_probe.py', 'test_probe_http_rejects_unexpected_service_without_agent', 1, 3, 3).
python_function('tests/hypervisor/test_local_run_plan.py', 'test_local_run_plan_ignores_a2a_card_uri', 1, 3, 2).
python_function('tests/hypervisor/test_local_run_plan.py', 'test_local_run_plan_prefers_declared_http_endpoints', 1, 3, 3).
python_function('tests/hypervisor/test_local_run_plan.py', 'test_local_target_to_module_custom_agent', 0, 2, 1).
python_function('tests/hypervisor/test_local_run_plan.py', 'test_local_run_plan_custom_agent', 1, 3, 2).
python_function('tests/hypervisor/test_markpact_deployments.py', 'test_deployments_readme_has_markpact_deploy_blocks', 1, 6, 5).
python_function('tests/hypervisor/test_monitor_landing.py', '_run_monitor', 0, 1, 2).
python_function('tests/hypervisor/test_monitor_landing.py', 'test_monitor_detects_unreachable_url', 1, 3, 1).
python_function('tests/hypervisor/test_monitor_landing.py', 'test_monitor_baseline_and_unchanged_prices', 1, 6, 4).
python_function('tests/hypervisor/test_monitor_landing.py', 'test_monitor_detects_price_change', 2, 3, 4).
python_function('tests/hypervisor/test_monitor_url.py', '_run', 1, 2, 2).
python_function('tests/hypervisor/test_monitor_url.py', 'test_monitor_url_ok', 1, 3, 1).
python_function('tests/hypervisor/test_monitor_url.py', 'test_monitor_url_down', 1, 4, 1).
python_function('tests/hypervisor/test_monitor_url.py', 'test_baseline_created_does_not_post_webhook', 0, 2, 8).
python_function('tests/hypervisor/test_monitor_url.py', 'test_webhook_posts_on_price_change', 0, 4, 8).
python_function('tests/hypervisor/test_monitor_url.py', 'test_placeholder_webhook_is_skipped', 1, 3, 6).
python_function('tests/hypervisor/test_monitor_url.py', 'test_monitor_landing_notify_on_price_change', 2, 4, 4).
python_function('tests/hypervisor/test_operator_agent_packages.py', 'test_browser_operator_registry_is_browser_only', 1, 3, 2).
python_function('tests/hypervisor/test_operator_agent_packages.py', 'test_desktop_operator_registry_excludes_browser', 1, 4, 2).
python_function('tests/hypervisor/test_operator_agent_packages.py', 'test_device_robot_operator_registry_is_physical_only', 1, 3, 2).
python_function('tests/hypervisor/test_operator_agent_packages.py', 'test_browser_operator_app_loads', 1, 2, 0).
python_function('tests/hypervisor/test_operator_agent_packages.py', 'test_common_assertion_handler', 1, 3, 1).
python_function('tests/hypervisor/test_physical_operator_separation.py', '_load_operator', 1, 1, 2).
python_function('tests/hypervisor/test_physical_operator_separation.py', 'test_device_robot_operator_contract_is_generic_capability_agent', 1, 13, 2).
python_function('tests/hypervisor/test_physical_operator_separation.py', 'test_physical_domain_registry_uses_operator_uris', 1, 9, 6).
python_function('tests/hypervisor/test_physical_operator_separation.py', 'test_device_robot_operator_is_registered_as_package_agent', 1, 10, 3).
python_function('tests/hypervisor/test_plan_runner.py', 'test_agent_id_from_uri', 2, 2, 2).
python_function('tests/hypervisor/test_plan_runner.py', 'test_run_planned_uris_success', 1, 5, 4).
python_function('tests/hypervisor/test_plan_runner.py', 'test_run_planned_uris_auto_repair_and_retry', 1, 7, 7).
python_function('tests/hypervisor/test_plan_runner.py', 'test_run_planned_uris_skips_repair_for_non_agent_uri', 1, 4, 3).
python_function('tests/hypervisor/test_plan_runner.py', 'test_format_plan_run_markdown_includes_repair_lines', 0, 4, 1).
python_function('tests/hypervisor/test_port_conflict.py', 'test_classify_port_listeners_marks_foreign_process', 0, 5, 3).
python_function('tests/hypervisor/test_port_conflict.py', 'test_port_conflict_detail_includes_probe_payload', 0, 4, 2).
python_function('tests/hypervisor/test_port_conflict.py', 'test_port_conflict_detail_ignores_owned_listener', 0, 2, 2).
python_function('tests/hypervisor/test_presentation_uri.py', 'test_source_view_uri_from_html_shorthand', 0, 2, 1).
python_function('tests/hypervisor/test_presentation_uri.py', 'test_source_view_uri_from_html_explicit_view_prefix', 0, 2, 1).
python_function('tests/hypervisor/test_presentation_uri.py', 'test_resolve_html_presentation', 1, 5, 4).
python_function('tests/hypervisor/test_presentation_uri.py', 'test_resolve_markdown_presentation', 1, 5, 4).
python_function('tests/hypervisor/test_registry_sync.py', 'test_validate_run_dependencies_detects_missing_uvicorn', 0, 3, 3).
python_function('tests/hypervisor/test_registry_sync.py', 'test_sync_deployment_port_updates_registry', 2, 8, 10).
python_function('tests/hypervisor/test_remote_runner.py', 'test_build_ssh_deploy_plan', 0, 4, 3).
python_function('tests/hypervisor/test_remote_runner.py', 'test_build_ssh_run_plan_dry_run', 0, 5, 2).
python_function('tests/hypervisor/test_remote_runner.py', 'test_build_run_plan_ssh_delegates', 0, 2, 2).
python_function('tests/hypervisor/test_remote_runner.py', 'test_verify_remote_deployment', 1, 4, 4).
python_function('tests/hypervisor/test_repair_supervisor.py', 'test_classify_port_and_health_timeout', 0, 4, 1).
python_function('tests/hypervisor/test_repair_supervisor.py', 'test_incident_artifact_has_schema_and_uri', 2, 5, 11).
python_function('tests/hypervisor/test_repair_supervisor.py', 'test_find_known_repair_case', 0, 3, 2).
python_function('tests/hypervisor/test_repair_supervisor.py', 'test_repair_apply_syncs_registry_when_healthy_but_drifted', 2, 6, 8).
python_function('tests/hypervisor/test_repair_supervisor.py', 'test_repair_apply_emits_operation_event_for_healthy_agent', 2, 3, 4).
python_function('tests/hypervisor/test_routing_pipeline.py', 'test_hypervisor_resolves_canonical_route_to_operator_runtime', 1, 9, 1).
python_function('tests/hypervisor/test_routing_pipeline.py', 'test_hypervisor_treats_playwright_as_adapter_not_environment', 1, 5, 1).
python_function('tests/hypervisor/test_routing_pipeline.py', 'test_hypervisor_preserves_payload_session_reference', 2, 5, 4).
python_function('tests/hypervisor/test_routing_pipeline.py', 'test_hypervisor_resolution_to_dict_summarizes_live_session', 1, 2, 4).
python_function('tests/hypervisor/test_routing_pipeline.py', 'test_hypervisor_blocks_side_effecting_route_without_approval', 1, 5, 2).
python_function('tests/hypervisor/test_routing_pipeline.py', 'test_hypervisor_dispatches_approved_route_through_uri2run', 2, 5, 4).
python_function('tests/hypervisor/test_routing_pipeline.py', 'test_uri3_client_operator_call_uses_hypervisor_routing', 1, 4, 4).
python_function('tests/hypervisor/test_routing_policy.py', 'test_strict_approve_blocks_browser_without_approval', 0, 3, 2).
python_function('tests/hypervisor/test_routing_policy.py', 'test_resolver_allows_browser_with_approval', 1, 3, 2).
python_function('tests/hypervisor/test_routing_policy.py', 'test_strict_approve_blocks_shell_mutation_without_approval', 0, 3, 2).
python_function('tests/hypervisor/test_routing_policy.py', 'test_health_read_allowed_without_approval', 0, 3, 2).
python_function('tests/hypervisor/test_runtime_state.py', 'test_build_run_plan_includes_env_and_runtime_paths', 0, 5, 3).
python_function('tests/hypervisor/test_runtime_state.py', 'test_resolve_deployment_env_merges_uri_yaml', 2, 3, 4).
python_function('tests/hypervisor/test_runtime_state.py', 'test_runtime_state_roundtrip', 1, 4, 4).
python_function('tests/hypervisor/test_runtime_state.py', 'test_is_process_alive_treats_permission_error_as_alive', 1, 2, 3).
python_function('tests/hypervisor/test_runtime_state.py', 'test_sync_runtime_health_uri_updates_network_fields', 0, 4, 1).
python_function('tests/hypervisor/test_runtime_state.py', 'test_start_process_detach_writes_process_log', 1, 5, 4).
python_function('tests/hypervisor/test_schema_collab_contract.py', 'test_schema_collab_contract_cross_refs', 1, 2, 1).
python_function('tests/hypervisor/test_schema_collab_contract.py', 'test_operator_robot_state_proto_exists', 1, 2, 1).
python_function('tests/hypervisor/test_screenshot_analysis_agent.py', 'test_screenshot_analysis_agent_analyzes_operator_json_artifact', 1, 5, 5).
python_function('tests/hypervisor/test_screenshot_analysis_agent.py', 'test_screenshot_analysis_agent_analyzes_png_and_detects_repeated_frame', 1, 7, 4).
python_function('tests/hypervisor/test_screenshot_analysis_agent.py', 'test_screenshot_analysis_agent_prefers_screenshot_step_artifact', 0, 2, 1).
python_function('tests/hypervisor/test_sprint1_autonomy.py', 'test_build_agent_readiness_report_separates_process_from_health', 0, 7, 1).
python_function('tests/hypervisor/test_sprint1_autonomy.py', 'test_build_agent_readiness_report_rebind_on_port_conflict', 0, 2, 1).
python_function('tests/hypervisor/test_sprint1_autonomy.py', 'test_build_agent_readiness_report_keeps_warnings_out_of_incidents', 0, 5, 1).
python_function('tests/hypervisor/test_sprint1_autonomy.py', 'test_build_repair_plan_from_diagnosis', 0, 5, 2).
python_function('tests/hypervisor/test_sprint1_autonomy.py', 'test_build_repair_plan_prioritizes_stale_runtime_before_uri_drift', 0, 4, 1).
python_function('tests/hypervisor/test_sprint1_autonomy.py', 'test_repair_apply_verifies_after_each_playbook', 1, 4, 3).
python_function('tests/hypervisor/test_sprint1_autonomy.py', 'test_diagnose_includes_repair_plan', 1, 5, 2).
python_function('tests/hypervisor/test_sprint1_autonomy.py', 'test_diagnose_healthy_warning_only_has_no_repair_plan', 1, 5, 2).
python_function('tests/hypervisor/test_supervise_watch.py', '_read_watch_events', 1, 3, 4).
python_function('tests/hypervisor/test_supervise_watch.py', '_healthy', 0, 1, 0).
python_function('tests/hypervisor/test_supervise_watch.py', '_failed', 1, 1, 0).
python_function('tests/hypervisor/test_supervise_watch.py', 'test_supervise_watch_emits_health_change_only_on_signature_change', 2, 5, 6).
python_function('tests/hypervisor/test_supervise_watch.py', 'test_supervise_watch_applies_repair_backoff_for_repeated_failure', 2, 2, 4).
python_function('tests/hypervisor/test_supervise_watch.py', 'test_supervise_watch_creates_one_incident_during_backoff', 2, 7, 7).
python_function('tests/hypervisor/test_system_agent_packages.py', 'test_hypervisor_dashboard_is_registered_as_system_agent', 1, 8, 4).
python_function('tests/hypervisor/test_system_agent_packages.py', 'test_hypervisor_dashboard_contract_symlink', 1, 3, 3).
python_function('tests/hypervisor/test_system_agent_packages.py', 'test_hypervisor_dashboard_app_loads', 0, 2, 0).
python_function('tests/hypervisor/test_system_agent_packages.py', 'test_runtime_environments_lists_system_dashboard', 1, 3, 2).
python_function('tests/hypervisor/test_system_routing.py', 'test_supports_hypervisor_system_uri', 0, 5, 1).
python_function('tests/hypervisor/test_system_routing.py', 'test_supports_view_uri', 0, 4, 1).
python_function('tests/hypervisor/test_system_routing.py', 'test_call_hypervisor_system_uri_health_dry_run', 1, 3, 1).
python_function('tests/hypervisor/test_system_routing.py', 'test_call_system_uri_delegates_health_to_hypervisor_routing', 1, 3, 2).
python_function('tests/hypervisor/test_system_routing.py', 'test_call_system_uri_repair_diagnose_via_hypervisor', 1, 2, 1).
python_function('tests/hypervisor/test_system_routing.py', 'test_call_system_uri_view_uses_hypervisor_view_handlers', 2, 3, 3).
python_function('tests/hypervisor/test_tutorial_three_agents_smoke.py', 'test_three_agents_tutorial_smoke_routes_core_commands', 0, 7, 1).
python_function('tests/hypervisor/test_tutorial_three_agents_smoke.py', 'test_three_agents_tutorial_smoke_ask_batch', 0, 7, 2).
python_function('tests/hypervisor/test_tutorial_three_agents_smoke.py', 'test_three_agents_tutorial_smoke_proof_dry_run', 0, 6, 1).
python_function('tests/hypervisor/test_uri_exchange_schema.py', 'uri_exchange_schema', 0, 1, 3).
python_function('tests/hypervisor/test_uri_exchange_schema.py', '_validate', 2, 3, 5).
python_function('tests/hypervisor/test_uri_exchange_schema.py', 'test_uri_exchange_schema_accepts_single_planner_executor', 1, 2, 1).
python_function('tests/hypervisor/test_uri_exchange_schema.py', 'test_uri_exchange_schema_accepts_batch_planner', 1, 2, 1).
python_function('tests/hypervisor/test_uri_exchange_schema.py', 'test_uri_exchange_schema_rejects_missing_session_id', 1, 2, 1).
python_function('tests/hypervisor/test_uri_healer.py', 'test_run_uri_healer_delegates_to_supervise_with_repair', 1, 5, 3).
python_function('tests/hypervisor/test_view_routing.py', 'test_explain_executable_uri_operator_includes_resolution', 1, 4, 2).
python_function('tests/hypervisor/test_view_routing.py', 'test_resolve_view_envelope_process_without_renderer', 1, 4, 2).
python_function('tests/hypervisor/test_www_integrations_build.py', 'test_about_parser_loads_cards', 1, 5, 7).
python_function('tests/hypervisor/test_www_integrations_build.py', 'test_build_landing_integrations_check', 1, 2, 2).
python_function('tests/hypervisor/test_www_integrations_build.py', 'test_build_examples_manifest_check', 1, 2, 2).
python_function('tests/hypervisor/test_www_integrations_build.py', 'test_examples_manifest_includes_office_chains', 1, 6, 7).
python_function('tests/hypervisor/test_www_integrations_build.py', 'test_index_has_generated_integration_cards', 1, 4, 2).
python_function('tests/hypervisor/test_www_integrations_build.py', 'test_spotlight_includes_full_i18n_cta_and_body', 1, 11, 7).
python_function('tests/hypervisor/test_www_integrations_build.py', '_load_integrations_module', 1, 2, 3).
python_function('tests/hypervisor/test_www_integrations_build.py', 'test_all_about_cards_reused_on_website', 1, 27, 18).
python_function('tests/hypervisor/test_www_integrations_build.py', 'test_index_integrations_match_fragment', 1, 4, 8).
python_function('tests/hypervisor/test_www_integrations_build.py', 'test_ecommerce_cards_use_distinct_bodies', 1, 6, 2).
python_function('tests/integration/test_flow_to_workflow_execution.py', 'test_compact_flow_to_dry_run', 1, 4, 5).
python_function('tests/integration/test_flow_to_workflow_execution.py', 'test_branching_flow_has_expected_edges', 1, 5, 1).
python_function('tests/integration/test_flow_to_workflow_execution.py', 'test_nl2uri_flow_expands_and_validates', 0, 3, 4).
python_function('tests/integration/test_nl2a_e2e.py', 'isolated_project', 2, 3, 7).
python_function('tests/integration/test_nl2a_e2e.py', 'test_nl2a_full_pipeline_weather_map', 1, 20, 9).
python_function('tests/integration/test_nl2a_e2e.py', 'test_nl2a_cli_generate_no_llm', 1, 8, 4).
python_function('tests/integration/test_uri3_uri2ops_delegation.py', 'test_default_operator_adapter_is_uri2ops', 0, 2, 2).
python_function('tests/integration/test_uri3_uri2ops_delegation.py', 'test_uri2ops_delegation_mock_browser_workflow', 1, 5, 4).
python_function('tests/meta_agent/test_repair.py', 'test_repair_agent_block_fills_metadata', 0, 5, 1).
python_function('tests/meta_agent/test_repair.py', 'test_repair_resource_read_fills_renderer_and_schema', 0, 3, 1).
python_function('tests/meta_agent/test_repair.py', 'test_repair_command_fills_fields', 0, 3, 1).
python_function('tests/meta_agent/test_repair.py', 'test_repair_capabilities_deduplicates_names', 0, 3, 3).
python_function('tests/meta_agent/test_repair.py', 'test_repair_agent_spec_integration', 1, 4, 6).
python_function('tests/nl2uri/test_domain_planner.py', 'test_normalize_bad_llm_weather_tree_uses_deterministic_template', 0, 6, 2).
python_function('tests/nl2uri/test_domain_planner.py', 'test_plan_from_prompt_weather_no_llm_full_tree', 0, 6, 1).
python_function('tests/nl2uri/test_flow_planner.py', 'test_classify_uri_flow_for_sequential_process', 0, 2, 1).
python_function('tests/nl2uri/test_flow_planner.py', 'test_classify_task_prompt_as_uri_flow', 0, 2, 1).
python_function('tests/nl2uri/test_flow_planner.py', 'test_classify_condition_stays_workflow_graph', 0, 2, 1).
python_function('tests/nl2uri/test_flow_planner.py', 'test_plan_flow_weather_prompt', 0, 8, 2).
python_function('tests/nl2uri/test_flow_planner.py', 'test_plan_auto_prefers_uri_flow_for_weather', 0, 2, 1).
python_function('tests/nl2uri/test_flow_planner.py', 'test_flow_expands_to_valid_workflow_graph', 0, 4, 2).
python_function('tests/nl2uri/test_flow_planner_llm.py', 'test_build_flow_planner_system_prompt_includes_compact_shape', 0, 5, 1).
python_function('tests/nl2uri/test_flow_planner_llm.py', 'test_plan_flow_with_llm_validates_compact_output', 1, 4, 2).
python_function('tests/nl2uri/test_flow_planner_llm.py', 'test_plan_flow_with_llm_converts_graph_nodes', 1, 3, 3).
python_function('tests/nl2uri/test_flow_planner_llm.py', 'test_plan_flow_with_llm_fallback_on_invalid', 1, 4, 2).
python_function('tests/nl2uri/test_flow_planner_llm.py', 'test_plan_flow_use_llm_flag', 1, 2, 3).
python_function('tests/nl2uri/test_flow_repair.py', 'test_extract_flow_payload_from_graph_nodes', 0, 4, 3).
python_function('tests/nl2uri/test_flow_repair.py', 'test_sanitize_flow_step_drops_unknown_scheme', 0, 3, 1).
python_function('tests/nl2uri/test_flow_repair.py', 'test_repair_flow_body_from_task_steps', 0, 4, 2).
python_function('tests/nl2uri/test_flow_repair.py', 'test_validate_expanded_flow_accepts_weather_flow', 0, 2, 2).
python_function('tests/nl2uri/test_flow_repair.py', 'test_repair_and_validate_flow_branching', 0, 4, 2).
python_function('tests/nl2uri/test_flow_repair.py', 'test_repair_and_validate_flow_rejects_empty', 0, 1, 2).
python_function('tests/nl2uri/test_graph_planner.py', 'test_classify_resource_tree', 0, 2, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_classify_task_graph', 0, 2, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_classify_workflow_graph', 0, 2, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_plan_single_status', 0, 3, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_plan_list_health_and_card', 0, 3, 2).
python_function('tests/nl2uri/test_graph_planner.py', 'test_plan_tree_contains_domain_root', 0, 3, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_plan_screenshot_schedule_stable_id', 0, 6, 2).
python_function('tests/nl2uri/test_graph_planner.py', 'test_plan_task_linear_steps', 0, 4, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_plan_workflow_generate_run_check', 0, 5, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_plan_auto_matches_classifier', 0, 2, 2).
python_function('tests/nl2uri/test_graph_planner_llm.py', 'test_build_graph_planner_system_prompt_includes_registry', 0, 5, 1).
python_function('tests/nl2uri/test_graph_planner_llm.py', 'test_sanitize_node_drops_unknown_scheme', 0, 3, 2).
python_function('tests/nl2uri/test_graph_planner_llm.py', 'test_sanitize_node_coerces_operation', 0, 3, 1).
python_function('tests/nl2uri/test_graph_planner_llm.py', 'test_repair_graph_body_from_task_shape', 0, 4, 2).
python_function('tests/nl2uri/test_graph_planner_llm.py', 'test_extract_graph_payload_accepts_graph_nodes_top_level', 0, 2, 1).
python_function('tests/nl2uri/test_graph_planner_llm.py', 'test_plan_graph_with_llm_validates_output', 1, 4, 3).
python_function('tests/nl2uri/test_graph_planner_llm.py', 'test_plan_graph_with_llm_fallback_on_invalid', 1, 4, 2).
python_function('tests/nl2uri/test_graph_planner_llm.py', 'test_plan_task_use_llm_flag', 1, 2, 4).
python_function('tests/nl2uri/test_weather_forecast.py', 'test_is_weather_forecast_prompt', 2, 2, 2).
python_function('tests/nl2uri/test_weather_forecast.py', 'test_weather_forecast_uri_from_polish_prompt', 0, 2, 1).
python_function('tests/nl2uri/test_weather_forecast.py', 'test_extract_weather_place_and_days', 0, 4, 2).
python_function('tests/nl2uri/test_weather_forecast.py', 'test_detect_weather_intent', 0, 4, 1).
python_function('tests/nl2uri/test_weather_forecast.py', 'test_ask_weather_forecast_plans_executable_uri', 0, 4, 1).
python_function('tests/nl2uri/test_weather_forecast.py', 'test_plan_weather_forecast_payload', 0, 4, 1).
python_function('tests/resource_agent_factory/test_default_port.py', 'test_default_port_from_deployment_registry', 1, 2, 2).
python_function('tests/resource_agent_factory/test_default_port.py', 'test_default_port_falls_back_to_8101', 2, 2, 2).
python_function('tests/scripts/test_architecture_responsibility_audit.py', 'load_audit_module', 1, 2, 3).
python_function('tests/scripts/test_architecture_responsibility_audit.py', 'write_fixture_files', 1, 1, 2).
python_function('tests/scripts/test_architecture_responsibility_audit.py', 'test_audit_detects_cross_boundary_duplication', 2, 7, 4).
python_function('tests/scripts/test_architecture_responsibility_audit.py', 'test_audit_ignores_stale_duplicate_symbol_when_file_changed', 2, 2, 7).
python_function('tests/scripts/test_architecture_responsibility_audit.py', 'test_audit_flags_domain_named_generic_module_when_file_exists', 2, 2, 6).
python_function('tests/scripts/test_architecture_responsibility_audit.py', 'test_audit_does_not_flag_domain_vocabulary_in_operator_agents', 2, 2, 6).
python_function('tests/scripts/test_architecture_responsibility_audit.py', 'test_audit_ignores_its_own_domain_vocabulary', 2, 2, 7).
python_function('tests/scripts/test_architecture_responsibility_audit.py', 'test_audit_cli_outputs_json', 2, 5, 4).
python_function('tests/test_capability_tests.py', 'test_capability_test_plan_is_built_from_registry', 0, 4, 2).
python_function('tests/test_contract_registry.py', 'test_contract_registry_loads_and_validates', 0, 5, 3).
python_function('tests/test_contract_registry.py', 'test_user_read_capability_matches_resource_contract', 0, 5, 3).
python_function('tests/test_cross_validation_v03.py', 'test_cross_validation_ok', 0, 2, 1).
python_function('tests/test_dependencies.py', 'test_typer_bundled_click_is_complete', 0, 3, 3).
python_function('tests/test_evolution_proposal.py', 'test_evolution_proposal_validates', 0, 3, 2).
python_function('tests/test_generate.py', 'test_generate_user_agent', 0, 4, 3).
python_function('tests/test_hypervisor.py', 'test_version_present', 0, 3, 1).
python_function('tests/test_hypervisor.py', 'test_default_config_has_hypervisor_section', 0, 3, 2).
python_function('tests/test_hypervisor.py', 'test_load_config_merges_user_file', 1, 5, 2).
python_function('tests/test_hypervisor.py', 'test_hypervisor_object', 0, 7, 3).
python_function('tests/test_hypervisor.py', 'test_hypervisor_from_config_and_limits', 0, 1, 3).
python_function('tests/test_hypervisor.py', 'test_cli_status_runs', 1, 4, 3).
python_function('tests/test_hypervisor.py', 'test_cli_config_path', 1, 3, 3).
python_function('tests/test_meta_agent.py', 'test_save_proposal_from_prompt', 1, 4, 5).
python_function('tests/test_meta_agent.py', 'test_repair_broken_agent', 1, 6, 8).
python_function('tests/test_meta_agent.py', 'test_pipeline_from_prompt_generates_agent', 1, 5, 5).
python_function('tests/test_nl2uri.py', 'test_weather_prompt_generates_weather_uri_tree', 0, 5, 1).
python_function('tests/test_operator_task.py', 'test_task_validates', 0, 2, 1).
python_function('tests/test_operator_task.py', 'test_task_plan', 0, 2, 2).
python_function('tests/test_operator_task.py', 'test_task_runs_mock', 0, 3, 2).
python_function('tests/test_policy_gate.py', 'test_policy_gate_allows_non_breaking_change', 0, 3, 1).
python_function('tests/test_policy_gate.py', 'test_policy_gate_blocks_breaking_change_without_approval', 0, 3, 1).
python_function('tests/test_policy_gate.py', 'test_policy_gate_allows_breaking_change_with_approval', 0, 2, 1).
python_function('tests/test_registry_builder_v03.py', 'test_registry_manifest_contains_contract_hash', 0, 4, 2).
python_function('tests/test_registry_builder_v03.py', 'test_registry_exports', 1, 3, 5).
python_function('tests/test_runtime_client.py', 'test_runtime_client_returns_error_when_runtime_unavailable', 0, 3, 2).
python_function('tests/test_schema_validation_v03.py', 'test_schema_validation_ok', 0, 3, 2).
python_function('tests/test_uri2llm_v04.py', 'test_env_uri_resolution', 1, 3, 2).
python_function('tests/test_uri2llm_v04.py', 'test_llm_uri_resolution', 0, 3, 1).
python_function('tests/test_uri2llm_v04.py', 'test_pypi_uri_resolution', 0, 2, 1).
python_function('tests/test_uri3.py', 'test_validate_uri', 0, 3, 1).
python_function('tests/test_uri3.py', 'test_graph_weather_tree', 0, 3, 3).
python_function('tests/test_uri_tree_validator.py', 'test_uri_tree_schema_ok', 0, 2, 1).
python_function('tests/test_validate.py', 'test_user_agent_contract_is_valid', 0, 2, 2).
python_function('tests/uri2flow/conftest.py', 'repo_root', 0, 4, 6).
python_function('tests/uri2flow/test_cli.py', 'test_cli_expand', 2, 4, 3).
python_function('tests/uri2flow/test_expand_branching_flow.py', 'test_expand_branching_flow', 1, 6, 1).
python_function('tests/uri2flow/test_expand_linear_flow.py', 'test_expand_linear_flow', 1, 7, 1).
python_function('tests/uri2flow/test_flow_defaults.py', 'setup_function', 0, 1, 1).
python_function('tests/uri2flow/test_flow_defaults.py', 'test_pattern_match_hypervisor_run', 0, 4, 1).
python_function('tests/uri2flow/test_flow_defaults.py', 'test_pattern_match_hypervisor_restart', 0, 3, 1).
python_function('tests/uri2flow/test_flow_defaults.py', 'test_pattern_match_browser_open', 0, 3, 1).
python_function('tests/uri2flow/test_flow_defaults.py', 'test_pattern_match_dom_extract', 0, 3, 1).
python_function('tests/uri2flow/test_flow_defaults.py', 'test_pattern_match_screen_observe', 0, 3, 1).
python_function('tests/uri2flow/test_flow_defaults.py', 'test_pattern_match_input_type', 0, 4, 1).
python_function('tests/uri2flow/test_flow_defaults.py', 'test_scheme_default_for_http', 0, 3, 1).
python_function('tests/uri2flow/test_flow_defaults.py', 'test_fallback_for_unknown_scheme', 0, 3, 1).
python_function('tests/uri2flow/test_parser_forms.py', 'test_accepts_string_and_mapping_forms', 0, 4, 2).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', '_markpact_ref', 2, 2, 0).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', 'test_is_markpact_registry', 0, 3, 1).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', 'test_extract_markpact_flow_blocks', 0, 4, 2).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', 'test_load_markpact_flow_dict', 1, 3, 3).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', 'test_load_flow_markpact_ref', 1, 4, 2).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', 'test_expand_flow_markpact_ref', 1, 5, 3).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', 'test_markpact_flow_requires_fragment_when_ambiguous', 1, 1, 3).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', 'test_markpact_flow_matches_yaml_flow', 1, 2, 2).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', 'test_resolve_markpact_ref', 1, 3, 3).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', 'test_uri2flow_expand_cli', 2, 4, 4).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', 'test_missing_flow_fragment_raises', 1, 1, 3).
python_function('tests/uri2flow/test_uri2flow_markpact_loader.py', 'test_missing_markpact_readme_raises', 1, 1, 2).
python_function('tests/uri2pact/test_markpact_scenarios.py', 'test_load_office_markpact_scenarios', 1, 3, 1).
python_function('tests/uri2pact/test_markpact_scenarios.py', 'test_load_office_markpact_scenario_registry_includes_yaml', 1, 5, 3).
python_function('tests/uri2run/test_protocol_transports.py', 'test_docker_transport_dry_run', 0, 6, 2).
python_function('tests/uri2run/test_protocol_transports.py', 'test_run_target_docker_scheme', 0, 3, 2).
python_function('tests/uri2run/test_protocol_transports.py', 'test_ssh_transport_resolve_mode', 0, 5, 2).
python_function('tests/uri2run/test_protocol_transports.py', 'test_ssh_transport_exec_mode', 1, 4, 4).
python_function('tests/uri2run/test_protocol_transports.py', 'test_mcp_transport_list_tools', 1, 4, 4).
python_function('tests/uri2run/test_protocol_transports.py', 'test_mcp_transport_call_tool', 1, 5, 6).
python_function('tests/uri2run/test_protocol_transports.py', 'test_a2a_transport_agent_card', 1, 3, 4).
python_function('tests/uri2run/test_protocol_transports.py', 'test_a2a_transport_tasks', 1, 4, 6).
python_function('tests/uri2run/test_protocol_transports.py', 'test_run_target_mcp_scheme', 1, 2, 3).
python_function('tests/uri2run/test_protocol_transports.py', 'test_mcp_transport_http_error', 1, 3, 4).
python_function('tests/uri2run/test_stream_transports.py', 'test_stdio_transport_json_roundtrip', 0, 5, 2).
python_function('tests/uri2run/test_stream_transports.py', 'test_run_target_stdio_scheme', 0, 2, 1).
python_function('tests/uri2run/test_stream_transports.py', 'test_sse_transport_parses_events', 1, 3, 4).
python_function('tests/uri2run/test_stream_transports.py', 'test_ws_transport_without_dependency', 0, 3, 2).
python_function('tests/uri2run/test_stream_transports.py', 'test_uri3_workflow_python_runtime_adapter', 1, 5, 2).
python_function('tests/uri2run/test_transport_matrix.py', 'test_python_transport', 0, 4, 3).
python_function('tests/uri2run/test_transport_matrix.py', 'test_shell_transport_success', 0, 5, 3).
python_function('tests/uri2run/test_transport_matrix.py', 'test_shell_transport_failure', 0, 3, 2).
python_function('tests/uri2run/test_transport_matrix.py', 'test_http_transport_success', 1, 6, 4).
python_function('tests/uri2run/test_transport_matrix.py', 'test_http_transport_uses_backend_options_and_retries', 1, 7, 7).
python_function('tests/uri2run/test_transport_matrix.py', 'test_shell_transport_supports_argv_without_shell', 0, 4, 2).
python_function('tests/uri2run/test_transport_matrix.py', 'test_flow_transport_dry_run', 1, 4, 3).
python_function('tests/uri2run/test_transport_matrix.py', 'test_touri_delegates_python_backend_to_uri2run', 1, 4, 2).
python_function('tests/uri2run/test_transport_matrix.py', 'test_unsupported_transport', 0, 5, 1).
python_function('tests/uri2run/test_uri2run.py', 'test_run_target_stt_mock_scheme', 0, 5, 2).
python_function('tests/uri2run/test_uri2run.py', 'test_cli_call_stt_mock_scheme_outputs_json', 1, 4, 3).
python_function('tests/uri2run/test_uri2run.py', 'test_run_target_python_returns_service_result', 0, 5, 2).
python_function('tests/uri2run/test_uri2run.py', 'test_run_target_shell_scheme_with_args', 0, 5, 2).
python_function('tests/uri2run/test_uri2run.py', 'test_run_backend_mock_returns_shared_envelope', 0, 5, 2).
python_function('tests/uri2run/test_uri2run.py', 'test_cli_call_python_outputs_json', 1, 4, 3).
python_function('tests/uri2run/test_uri2run.py', 'test_touri_python_backend_delegates_to_uri2run', 1, 5, 3).
python_function('tests/uri2run/test_voice_resolver.py', 'test_resolve_stt_mock_to_python', 0, 4, 1).
python_function('tests/uri2run/test_voice_resolver.py', 'test_resolve_stt_whisper_to_python', 0, 4, 1).
python_function('tests/uri2run/test_voice_resolver.py', 'test_resolve_tts_mock_to_python', 0, 3, 1).
python_function('tests/uri2run/test_voice_resolver.py', 'test_unknown_voice_uri_returns_touri_or_unresolved', 0, 3, 1).
python_function('tests/uri2run/test_workflow_transport.py', 'test_flow_and_graph_transports_share_dry_run_path', 1, 9, 4).
python_function('tests/uri2run/test_workflow_transport.py', 'test_workflow_transport_invalid_graph_uses_error_code', 0, 3, 3).
python_function('tests/uri3/test_browser_adapter.py', 'test_resolve_browser_mode_mock', 0, 2, 2).
python_function('tests/uri3/test_browser_adapter.py', 'test_mock_adapter_writes_artifact_files', 1, 5, 4).
python_function('tests/uri3/test_browser_adapter.py', 'test_playwright_browser_workflow', 1, 4, 18).
python_function('tests/uri3/test_cli.py', 'runner', 0, 1, 1).
python_function('tests/uri3/test_cli.py', 'test_scan_shortcuts_load_defaults', 0, 3, 2).
python_function('tests/uri3/test_cli.py', 'test_resolve_scan_target_by_name', 0, 2, 2).
python_function('tests/uri3/test_cli.py', 'test_resolve_scan_target_full_uri', 0, 2, 2).
python_function('tests/uri3/test_cli.py', 'test_cli_list_command', 1, 4, 1).
python_function('tests/uri3/test_cli.py', 'test_cli_list_json', 1, 4, 2).
python_function('tests/uri3/test_cli.py', 'test_cli_no_args_shows_quick_reference', 1, 3, 1).
python_function('tests/uri3/test_cli.py', 'test_cli_scan_without_args_shows_help', 2, 3, 2).
python_function('tests/uri3/test_cli.py', 'test_cli_scan_shortcut_name', 2, 3, 5).
python_function('tests/uri3/test_cli.py', 'test_cli_scan_all', 2, 3, 4).
python_function('tests/uri3/test_cli.py', 'test_cli_call_docker_dry_run', 1, 4, 2).
python_function('tests/uri3/test_dispatch.py', 'test_parse_instance_env', 0, 2, 1).
python_function('tests/uri3/test_dispatch.py', 'test_parse_instance_docker_stack', 0, 3, 1).
python_function('tests/uri3/test_dispatch.py', 'test_resolve_target_pypi', 0, 2, 1).
python_function('tests/uri3/test_docker_control.py', 'test_parse_docker_stack_uri', 0, 6, 2).
python_function('tests/uri3/test_docker_control.py', 'test_resolve_docker_generate_plan', 0, 4, 1).
python_function('tests/uri3/test_docker_control.py', 'test_control_docker_up_dry_run', 0, 4, 1).
python_function('tests/uri3/test_docker_control.py', 'test_control_docker_generate_writes_file', 2, 5, 8).
python_function('tests/uri3/test_docker_control.py', 'test_control_docker_container_stop_dry_run', 0, 2, 1).
python_function('tests/uri3/test_docker_control.py', 'test_control_docker_up_recovers_from_name_conflict', 1, 5, 6).
python_function('tests/uri3/test_doctor.py', 'test_doctor_passes_on_repo', 1, 9, 1).
python_function('tests/uri3/test_doctor.py', 'test_doctor_build_registry_writes_indexes', 2, 5, 3).
python_function('tests/uri3/test_doctor.py', 'test_build_registry_indexes_content', 1, 4, 1).
python_function('tests/uri3/test_envelope_migrate.py', 'test_migrate_workflow_log_adds_status_fields', 1, 6, 6).
python_function('tests/uri3/test_explain_extended.py', 'test_explain_includes_verification_hints', 1, 5, 1).
python_function('tests/uri3/test_explain_extended.py', 'test_explain_includes_fallbacks_and_data_quality', 1, 5, 3).
python_function('tests/uri3/test_explain_extended.py', 'test_explain_runtime_transport_for_stdio_backend', 1, 3, 3).
python_function('tests/uri3/test_explain_uri.py', 'test_explain_weather_uri_matches_touri', 1, 5, 1).
python_function('tests/uri3/test_explain_uri.py', 'test_explain_http_uri_matches_uri3', 1, 3, 1).
python_function('tests/uri3/test_explain_uri.py', 'test_explain_file_uri_matches_uri3', 2, 3, 3).
python_function('tests/uri3/test_explain_uri.py', 'test_explain_browser_uri_matches_uri2ops', 1, 3, 1).
python_function('tests/uri3/test_explain_uri.py', 'test_explain_unknown_scheme_denied', 1, 3, 1).
python_function('tests/uri3/test_file_resolver.py', 'test_resolve_file_uri_returns_metadata', 1, 8, 5).
python_function('tests/uri3/test_file_resolver.py', 'test_path_from_file_uri_unquotes_spaces', 1, 2, 3).
python_function('tests/uri3/test_http_scanner.py', 'test_scan_http_health_uri_does_not_double_path', 1, 6, 7).
python_function('tests/uri3/test_http_scanner.py', 'test_scan_http_404_health_is_error', 1, 5, 5).
python_function('tests/uri3/test_http_scanner.py', 'test_health_scan_ok_requires_200', 0, 2, 2).
python_function('tests/uri3/test_lifecycle_envelope.py', 'test_lifecycle_plan_payload_has_status_envelope', 0, 6, 1).
python_function('tests/uri3/test_lifecycle_envelope.py', 'test_lifecycle_stopped_payload_has_status_envelope', 0, 3, 1).
python_function('tests/uri3/test_llm_profiles.py', 'test_load_llm_config_has_domain_planner', 0, 3, 2).
python_function('tests/uri3/test_llm_profiles.py', 'test_resolve_llm_profile_domain_planner', 1, 6, 3).
python_function('tests/uri3/test_llm_profiles.py', 'test_resolve_llm_profile_respects_default_env', 1, 3, 2).
python_function('tests/uri3/test_log_reader_meta.py', 'test_read_logs_result_missing_file', 2, 6, 5).
python_function('tests/uri3/test_log_uri.py', '_write_sample_log', 1, 2, 4).
python_function('tests/uri3/test_log_uri.py', 'test_resolve_log_uri', 0, 7, 1).
python_function('tests/uri3/test_log_uri.py', 'test_read_logs_with_filters', 2, 5, 4).
python_function('tests/uri3/test_log_uri.py', 'test_read_logs_from_explicit_file', 2, 2, 4).
python_function('tests/uri3/test_log_uri.py', 'test_call_log_uri_returns_entries', 2, 3, 3).
python_function('tests/uri3/test_log_uri.py', 'test_scan_log_uri', 2, 5, 4).
python_function('tests/uri3/test_log_uri.py', 'test_summarize_logs', 2, 4, 3).
python_function('tests/uri3/test_replay.py', 'test_replay_workflow_events_by_id', 1, 5, 2).
python_function('tests/uri3/test_replay.py', 'test_replay_workflow_events_by_path', 1, 3, 3).
python_function('tests/uri3/test_replay.py', 'test_build_task_payload_from_step_started_events', 1, 4, 3).
python_function('tests/uri3/test_replay.py', 'test_create_regression_test_writes_pytest', 1, 5, 4).
python_function('tests/uri3/test_resolvers.py', 'test_env_uri_resolution', 1, 4, 2).
python_function('tests/uri3/test_resolvers.py', 'test_llm_uri_resolution', 0, 4, 1).
python_function('tests/uri3/test_resolvers.py', 'test_pypi_uri_resolution', 0, 2, 1).
python_function('tests/uri3/test_resolvers.py', 'test_python_uri_resolution', 0, 3, 1).
python_function('tests/uri3/test_resolvers.py', 'test_http_uri_resolution', 0, 2, 1).
python_function('tests/uri3/test_resolvers.py', 'test_a2a_uri_resolution', 0, 3, 1).
python_function('tests/uri3/test_resolvers.py', 'test_mcp_uri_resolution', 0, 2, 1).
python_function('tests/uri3/test_resolvers.py', 'test_resource_uri_resolution', 0, 3, 1).
python_function('tests/uri3/test_resolvers.py', 'test_python_call', 0, 2, 1).
python_function('tests/uri3/test_resolvers.py', 'test_env_call_set_persists_to_dotenv', 2, 5, 4).
python_function('tests/uri3/test_resolvers.py', 'test_env_call_set_updates_existing_key', 2, 5, 4).
python_function('tests/uri3/test_resolvers.py', 'test_router_resolve_returns_uri_resolution', 0, 2, 4).
python_function('tests/uri3/test_resolvers.py', 'test_unsupported_scheme', 0, 1, 2).
python_function('tests/uri3/test_resolvers.py', 'test_deprecated_uri2llm_reexport', 0, 3, 5).
python_function('tests/uri3/test_result_envelope.py', 'test_uri3_workflow_result_includes_status_envelope', 1, 6, 2).
python_function('tests/uri3/test_result_envelope.py', 'test_uri3_workflow_blocked_has_failed_service_status', 0, 4, 2).
python_function('tests/uri3/test_result_envelope.py', 'test_uri2ops_task_result_includes_status_envelope', 1, 3, 3).
python_function('tests/uri3/test_router_call.py', 'test_resolve_docker_stack', 0, 4, 1).
python_function('tests/uri3/test_router_call.py', 'test_call_docker_stack_dry_run', 0, 4, 1).
python_function('tests/uri3/test_schema.py', 'test_normalize_scheme', 0, 4, 1).
python_function('tests/uri3/test_schema.py', 'test_get_scheme_schema_log', 0, 7, 1).
python_function('tests/uri3/test_schema.py', 'test_get_scheme_schema_unknown', 0, 1, 2).
python_function('tests/uri3/test_schema.py', 'test_list_schemes_includes_log', 0, 3, 2).
python_function('tests/uri3/test_schema.py', 'test_analyze_concrete_log_uri', 0, 7, 1).
python_function('tests/uri3/test_schema.py', 'test_analyze_invalid_log_uri', 0, 3, 1).
python_function('tests/uri3/test_schema.py', 'test_describe_scheme_only', 0, 3, 1).
python_function('tests/uri3/test_schema.py', 'test_describe_concrete_uri', 0, 3, 1).
python_function('tests/uri3/test_schema.py', 'test_cli_schema_log_scheme', 0, 4, 3).
python_function('tests/uri3/test_schema.py', 'test_cli_schema_list', 0, 3, 3).
python_function('tests/uri3/test_schema.py', 'test_cli_schema_analyze', 0, 4, 3).
python_function('tests/uri3/test_service_result.py', 'test_service_result_finalize_sets_three_status_levels', 0, 6, 2).
python_function('tests/uri3/test_service_result.py', 'test_error_envelope_normalizes_legacy_detail', 0, 3, 3).
python_function('tests/uri3/test_service_result.py', 'test_success_service_result', 0, 3, 2).
python_function('tests/uri3/test_ssh_auth.py', 'test_resolve_ssh_password_from_env', 1, 2, 3).
python_function('tests/uri3/test_ssh_auth.py', 'test_resolve_ssh_password_from_profile', 2, 2, 5).
python_function('tests/uri3/test_ssh_auth.py', 'test_build_ssh_command_uses_sshpass_when_password_set', 1, 3, 3).
python_function('tests/uri3/test_ssh_auth.py', 'test_ssh_auth_hint_on_permission_denied', 1, 3, 3).
python_function('tests/uri3/test_ssh_scanner.py', 'test_parse_ssh_uri', 0, 6, 1).
python_function('tests/uri3/test_ssh_scanner.py', 'test_parse_ssh_uri_requires_host', 0, 1, 2).
python_function('tests/uri3/test_ssh_scanner.py', 'test_scan_ssh_invalid_uri', 0, 4, 2).
python_function('tests/uri3/test_ssh_scanner.py', 'test_resolve_ssh_alias', 0, 2, 1).
python_function('tests/uri3/test_ssh_scanner.py', 'test_scan_ssh_unreachable', 1, 4, 4).
python_function('tests/uri3/test_ssh_scanner.py', 'test_scan_ssh_success', 1, 2, 5).
python_function('tests/uri3/test_uri_yaml.py', 'test_is_uri', 0, 5, 1).
python_function('tests/uri3/test_uri_yaml.py', 'test_load_llm_uri_yaml', 0, 5, 2).
python_function('tests/uri3/test_uri_yaml.py', 'test_load_uri_yaml_unwraps_artifact_envelope', 0, 7, 1).
python_function('tests/uri3/test_uri_yaml.py', 'test_resolve_uri_values_keeps_secrets_by_default', 0, 2, 2).
python_function('tests/uri3/test_workflow_executor.py', 'test_run_workflow_dry_run_completes', 0, 9, 4).
python_function('tests/uri3/test_workflow_executor.py', 'test_run_workflow_blocks_command_without_approve', 0, 9, 2).
python_function('tests/uri3/test_workflow_executor.py', 'test_run_workflow_execute_mock_with_approve', 1, 12, 7).
python_function('tests/uri3/test_workflow_executor.py', 'test_run_workflow_accepts_workflow_graph_object', 1, 3, 2).
python_function('tests/uri3/test_workflow_executor.py', 'test_run_workflow_skips_conditional_branch', 1, 5, 1).
python_function('tests/uri3/test_workflow_executor.py', 'test_run_workflow_service_failure_uses_completed_with_service_error', 1, 7, 2).
python_function('tests/uri3/test_workflow_graph.py', 'test_load_task_payload', 0, 4, 2).
python_function('tests/uri3/test_workflow_graph.py', 'test_validate_task_payload', 0, 2, 1).
python_function('tests/uri3/test_workflow_graph.py', 'test_execution_plan_order', 0, 2, 1).
python_function('tests/uri3/test_workflow_graph.py', 'test_detect_cycle', 0, 4, 6).
python_function('tests/urigen/test_urigen_cycle.py', 'test_plan_generate_verify_explain_cycle', 1, 17, 9).
python_function('tests/urigen/test_urigen_cycle.py', 'test_profile_aliases_are_canonicalized', 0, 8, 3).
python_function('tests/urigen/test_urigen_cycle.py', 'test_apply_plan_and_transaction', 2, 9, 8).
python_function('tests/urigen/test_urigen_cycle.py', '_setup_apply_tmp', 2, 1, 5).
python_function('tests/urigen/test_urigen_cycle.py', 'test_apply_plan_includes_diff', 2, 4, 4).
python_function('tests/urigen/test_urigen_cycle.py', 'test_apply_idempotent_second_run', 2, 6, 6).
python_function('tests/urigen/test_urigen_cycle.py', 'test_apply_failure_rolls_back_created_files', 3, 5, 6).
python_function('tests/urigen/test_urigen_cycle.py', 'test_apply_manual_rollback_restores_files', 2, 4, 4).
python_function('tests/urigen/test_urigen_cycle.py', 'test_proposal_and_ecosystem_have_envelope', 1, 9, 6).
python_function('tests/urigen/test_urigen_cycle.py', 'test_plan_and_verify_do_not_touch_repo_roots', 2, 7, 6).
python_function('tests/urigen/test_urigen_cycle.py', 'test_cli_plan_generate_verify', 1, 5, 3).
python_function('tests/urigen/test_urigen_cycle.py', 'test_cli_profiles_lists_aliases', 1, 4, 2).
python_function('tests/urish/test_agent_backend.py', 'test_agent_action_run_forwards_detach_once', 0, 2, 3).
python_function('tests/urish/test_agent_factory.py', 'test_detect_agent_factory_intent', 0, 5, 1).
python_function('tests/urish/test_agent_factory.py', 'test_dashboard_prompt_still_uses_ecosystem_intent', 0, 3, 1).
python_function('tests/urish/test_agent_factory.py', 'test_build_agent_contract_from_uri_prompt', 0, 7, 2).
python_function('tests/urish/test_agent_factory.py', 'test_build_agent_contract_from_robot_uri_prompt', 0, 5, 1).
python_function('tests/urish/test_agent_factory.py', 'test_ask_agent_factory_returns_lifecycle_steps', 0, 8, 3).
python_function('tests/urish/test_agent_factory.py', 'test_generate_agent_dry_run_does_not_write', 1, 5, 2).
python_function('tests/urish/test_agent_factory.py', 'test_ssh_prompt_plans_remote_deployment', 1, 5, 2).
python_function('tests/urish/test_agent_factory.py', 'test_ssh_keyword_uses_default_target', 1, 3, 1).
python_function('tests/urish/test_agent_factory.py', 'test_ask_ssh_prompt_includes_deploy_steps', 0, 3, 2).
python_function('tests/urish/test_ask_dashboard.py', 'test_detect_dashboard_agent_intent', 0, 5, 1).
python_function('tests/urish/test_ask_dashboard.py', 'test_detect_agent_process_view_intent', 0, 5, 1).
python_function('tests/urish/test_ask_dashboard.py', 'test_detect_agent_diagnose_intent', 0, 5, 1).
python_function('tests/urish/test_ask_dashboard.py', 'test_detect_agent_health_intent', 0, 4, 1).
python_function('tests/urish/test_ask_dashboard.py', 'test_ask_agent_process_view_plans_hypervisor_uri', 0, 5, 2).
python_function('tests/urish/test_ask_dashboard.py', 'test_ask_agent_diagnose_plans_repair_uri', 0, 4, 1).
python_function('tests/urish/test_ask_dashboard.py', 'test_screenshot_prompt_uses_workflow_not_domain', 0, 2, 1).
python_function('tests/urish/test_ask_dashboard.py', 'test_screenshot_prompt_plans_stable_workflow_uri', 0, 7, 1).
python_function('tests/urish/test_ask_dashboard.py', 'test_screenshot_polish_inflection_detects_workflow', 0, 3, 2).
python_function('tests/urish/test_ask_dashboard.py', 'test_weather_forecast_prompt_plans_weather_uri', 0, 6, 2).
python_function('tests/urish/test_ask_dashboard.py', 'test_detect_www_chat_dashboard_intent_without_agent_word', 0, 4, 1).
python_function('tests/urish/test_ask_dashboard.py', 'test_ask_dashboard_includes_generate_and_semantic_id', 0, 10, 3).
python_function('tests/urish/test_ask_dashboard.py', 'test_plan_ecosystem_dashboard_profile', 0, 4, 1).
python_function('tests/urish/test_ask_dashboard.py', 'test_dashboard_ecosystem_generate_verify', 1, 11, 8).
python_function('tests/urish/test_ask_dashboard.py', 'test_dashboard_create_plan_only', 0, 5, 2).
python_function('tests/urish/test_call_routing.py', 'test_dashboard_view_uris_are_system', 0, 3, 2).
python_function('tests/urish/test_call_routing.py', 'test_weather_like_view_uris_are_not_system', 0, 3, 2).
python_function('tests/urish/test_call_routing.py', 'test_misrouted_view_forecast_does_not_raise', 1, 4, 4).
python_function('tests/urish/test_desktop_policy.py', 'test_desktop_operator_policy_distinguishes_reads_and_mutations', 0, 12, 1).
python_function('tests/urish/test_desktop_policy.py', 'test_desktop_mutations_default_to_real_in_dev_policy', 0, 13, 3).
python_function('tests/urish/test_office_intent.py', 'test_detect_office_invoice_batch', 0, 4, 1).
python_function('tests/urish/test_office_intent.py', 'test_detect_office_portal_report', 0, 4, 1).
python_function('tests/urish/test_office_intent.py', 'test_detect_office_bank_transfer', 0, 4, 1).
python_function('tests/urish/test_office_intent.py', 'test_detect_office_invoice_status', 0, 3, 1).
python_function('tests/urish/test_office_intent.py', 'test_agent_diagnose_still_wins_over_office', 0, 3, 1).
python_function('tests/urish/test_office_intent.py', 'test_ask_office_invoice_batch', 0, 5, 2).
python_function('tests/urish/test_office_intent.py', 'test_detect_office_ecommerce_sync', 0, 4, 1).
python_function('tests/urish/test_office_intent.py', 'test_detect_office_allegro_erp_failure', 0, 4, 1).
python_function('tests/urish/test_office_intent.py', 'test_ask_office_ecommerce_sync', 0, 4, 2).
python_function('tests/urish/test_office_scenarios.py', 'test_landing_quote_maps_to_scenario', 4, 8, 4).
python_function('tests/urish/test_office_scenarios.py', 'test_ask_landing_quote_returns_card_uris', 4, 4, 3).
python_function('tests/urish/test_office_scenarios.py', 'test_office_scenario_count_matches_landing', 0, 2, 2).
python_function('tests/urish/test_physical_policy.py', 'test_physical_operator_policy_distinguishes_reads_and_mutations', 0, 7, 1).
python_function('tests/urish/test_physical_policy.py', 'test_physical_mutations_default_to_real_in_dev_policy', 0, 10, 3).
python_function('tests/urish/test_prompt_split.py', 'test_split_nl_commands_single_line', 0, 2, 1).
python_function('tests/urish/test_prompt_split.py', 'test_split_nl_commands_multiline', 0, 2, 1).
python_function('tests/urish/test_prompt_split.py', 'test_ask_prompt_batch', 0, 5, 2).
python_function('tests/urish/test_render.py', 'test_render_view_fallback_helper', 0, 5, 1).
python_function('tests/urish/test_render.py', 'test_render_view_summary_in_text_mode', 0, 3, 1).
python_function('tests/urish/test_repl.py', 'test_parse_repl_line_bare_uri_real_mode_by_default', 0, 2, 2).
python_function('tests/urish/test_repl.py', 'test_parse_repl_line_bare_uri_dry_run_mode', 0, 2, 2).
python_function('tests/urish/test_repl.py', 'test_parse_repl_line_repair_apply_adds_approve_in_real_mode', 0, 2, 2).
python_function('tests/urish/test_repl.py', 'test_parse_repl_line_dry_run_uri_skips_approve_in_real_mode', 0, 3, 2).
python_function('tests/urish/test_repl.py', 'test_parse_repl_line_natural_language_uses_ask_without_dry_run_by_default', 0, 2, 2).
python_function('tests/urish/test_repl.py', 'test_parse_repl_line_natural_language_ask_dry_run_when_enabled', 0, 2, 2).
python_function('tests/urish/test_repl.py', 'test_parse_repl_line_explicit_command_passthrough', 0, 2, 2).
python_function('tests/urish/test_repl.py', 'test_parse_repl_line_meta_help_returns_none', 1, 4, 3).
python_function('tests/urish/test_repl.py', 'test_main_empty_argv_starts_repl', 0, 2, 3).
python_function('tests/urish/test_repl.py', 'test_run_repl_executes_uri_line', 0, 6, 3).
python_function('tests/urish/test_repl.py', 'test_execute_cli_argv_view_uri', 1, 2, 3).
python_function('tests/urish/test_scenario_registry_boundary.py', 'test_office_scenarios_are_loaded_from_domains_registry', 0, 6, 2).
python_function('tests/urish/test_scenario_registry_boundary.py', 'test_urish_has_no_office_specific_compat_modules', 1, 3, 1).
python_function('tests/urish/test_ticket_workflow.py', '_write_ticket', 1, 1, 3).
python_function('tests/urish/test_ticket_workflow.py', 'test_detect_dashboard_intent_from_ticket', 0, 3, 1).
python_function('tests/urish/test_ticket_workflow.py', 'test_ticket_workflow_includes_ecosystem_steps', 0, 4, 2).
python_function('tests/urish/test_ticket_workflow.py', 'test_show_ticket_returns_next_steps', 1, 4, 3).
python_function('tests/urish/test_ticket_workflow.py', 'test_evolve_from_ticket_generates_proposal_and_steps', 1, 6, 11).
python_function('tests/urish/test_ticket_workflow.py', 'test_doctor_strict_adds_artifact_checks', 0, 6, 3).
python_function('tests/urish/test_ticket_workflow.py', 'test_cli_doctor_strict_flag', 0, 2, 3).
python_function('tests/urish/test_urish_cli.py', 'test_load_payload_from_json', 0, 2, 1).
python_function('tests/urish/test_urish_cli.py', 'test_load_payload_from_file', 1, 2, 3).
python_function('tests/urish/test_urish_cli.py', 'test_load_payload_stdin_envelope', 0, 2, 4).
python_function('tests/urish/test_urish_cli.py', 'test_render_text_view_summary', 0, 5, 1).
python_function('tests/urish/test_urish_cli.py', 'test_render_text_envelope', 0, 3, 1).
python_function('tests/urish/test_urish_cli.py', 'test_shortcuts_load', 0, 2, 1).
python_function('tests/urish/test_urish_cli.py', 'test_shortcut_specs_preserve_payload', 0, 4, 1).
python_function('tests/urish/test_urish_cli.py', 'test_cli_call_python_mock', 0, 2, 3).
python_function('tests/urish/test_urish_cli.py', 'test_cli_default_uri_invokes_call', 0, 2, 3).
python_function('tests/urish/test_urish_cli.py', 'test_cli_plan_passes_plain_defaults_to_call_backend', 0, 5, 2).
python_function('tests/urish/test_urish_cli.py', 'test_cli_call_accepts_payload_at_file', 1, 3, 3).
python_function('tests/urish/test_urish_cli.py', 'test_cli_call_shortcut_uses_default_payload', 0, 4, 2).
python_function('tests/urish/test_urish_cli.py', 'test_cli_call_shortcut_explicit_payload_wins', 0, 3, 2).
python_function('tests/urish/test_urish_cli.py', 'test_resolve_target_uri_passthrough', 0, 2, 1).
python_function('tests/urish/test_urish_cli.py', 'test_policy_blocks_mutation_without_approval', 0, 4, 2).
python_function('tests/urish/test_urish_cli.py', 'test_policy_allows_read', 0, 3, 2).
python_function('tests/urish/test_urish_cli.py', 'test_policy_force_dry_run', 0, 3, 2).
python_function('tests/urish/test_urish_cli.py', 'test_classify_repair_uri', 0, 2, 1).
python_function('tests/urish/test_urish_cli.py', 'test_classify_repair_diagnose_uri_as_read', 0, 2, 1).
python_function('tests/urish/test_urish_cli.py', 'test_select_from_envelope', 0, 2, 1).
python_function('tests/urish/test_urish_cli.py', 'test_cli_ask_command', 0, 2, 3).
python_function('tests/urish/test_urish_cli.py', 'test_cli_select_command', 0, 2, 5).
python_function('tests/urish/test_urish_cli.py', 'test_cli_policy_blocked_exit_code', 0, 2, 1).
python_function('tests/urish/test_urish_cli.py', 'test_cli_ticket_list', 0, 2, 2).
python_function('tests/urish/test_urish_cli.py', 'test_cli_repair_diagnose', 0, 2, 3).
python_function('tests/urish/test_urish_cli.py', 'test_cli_watch_limited', 0, 2, 3).
python_function('tests/urish/test_urish_cli.py', 'test_cli_proof_summarizes_one_uri', 1, 9, 4).
python_function('tests/urish/test_urish_cli.py', 'test_cli_ecosystem_generate_command', 1, 2, 5).
python_function('tests/urish/test_urish_cli.py', 'test_cli_ecosystem_profiles_command', 0, 2, 1).
python_function('tests/urish/test_urish_cli.py', 'test_cli_dashboard_create_plan_only', 0, 4, 3).
python_function('tests/urish/test_urish_cli.py', 'test_cli_agent_run_passes_detach_once', 0, 2, 3).
python_function('tests/urish/test_urish_cli.py', 'test_cli_agent_create_dashboard_alias', 0, 4, 3).
python_function('tests/urish/test_urish_cli.py', 'test_cli_www_create_from_nl_prompt', 0, 5, 3).
python_function('tests/urish/test_urish_cli.py', 'test_cli_agent_describe_does_not_crash_on_typer_signature', 0, 2, 1).
python_function('tests/urish/test_urish_cli.py', 'test_cli_agent_describe_writes_output', 1, 4, 4).
python_function('tests/urish/test_workflow_run.py', 'test_run_workflow_uri_dry_run', 0, 3, 2).
python_function('tests/urish/test_workflow_run.py', 'test_explain_workflow_order_resolves_touri', 0, 3, 2).
python_function('tests/urish/test_workflow_run.py', 'test_run_workflow_supplier_report', 0, 2, 2).
python_function('tests/urish/test_workflow_run.py', 'test_run_workflow_portal_zus_dry_run', 0, 2, 2).
python_function('tests/urish/test_workflow_run.py', 'test_run_workflow_bank_batch_dry_run', 0, 2, 2).
python_function('tests/urish/test_workflow_run.py', 'test_explain_cron_uri_resolves_touri', 0, 3, 2).
python_function('tests/urish/test_workflow_run.py', 'test_run_cron_www_monitor_dry_run', 0, 2, 2).
python_function('tests/urish/test_workflow_run.py', 'test_call_health_agent_system_uri', 0, 3, 3).
python_function('tests/urish/test_workflow_run.py', 'test_call_cron_uri_uses_touri_backend', 1, 5, 3).
python_function('tests/urish/test_workflow_run.py', 'test_call_device_uri_uses_hypervisor_operator_routing', 1, 6, 3).
python_function('www/api-bridge/bridge.py', 'envelope', 3, 3, 0).
python_function('www/api-bridge/bridge.py', 'run_cmd', 2, 3, 3).
python_function('www/api-bridge/bridge.py', 'health', 0, 1, 2).
python_function('www/api-bridge/bridge.py', 'call_uri', 1, 11, 8).
python_function('www/api-bridge/bridge.py', 'preview_uri', 1, 2, 2).
python_function('www/api-bridge/bridge.py', 'agents', 0, 1, 1).
python_function('www/api-bridge/bridge.py', 'events', 1, 1, 1).
python_function('www/api-bridge/bridge.py', 'ask', 1, 2, 4).

% ── Python Classes ───────────────────────────────────────
python_class('agents/custom/gnome_programmer_agent/routes.py', 'OperatorRequest').
python_class('agents/custom/gnome_programmer_agent/routes.py', 'TypeRequest').
python_class('agents/custom/gnome_programmer_agent/routes.py', 'SessionRequest').
python_class('agents/custom/remote_deploy_agent/routes.py', 'DeploymentRequest').
python_class('agents/custom/screenshot_analysis_agent/routes.py', 'AnalyzeScreenshotRequest').
python_class('agents/custom/screenshot_analysis_agent/routes.py', 'CaptureAndAnalyzeRequest').
python_class('agents/generated/codex_nl_plan_agent/routes.py', 'CommandRequest').
python_class('agents/generated/codex_nl_smoke_agent/routes.py', 'CommandRequest').
python_class('agents/generated/codex_uri_smoke_agent/routes.py', 'CommandRequest').
python_class('agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py', 'CommandRequest').
python_class('agents/generated/gnome_programmer_agent/routes.py', 'CommandRequest').
python_class('agents/generated/hypervisor_dashboard_agent/routes.py', 'CommandRequest').
python_class('agents/generated/invoices_agent/routes.py', 'CommandRequest').
python_class('agents/generated/remote_deploy_agent/routes.py', 'CommandRequest').
python_class('agents/generated/schema_collab_agent/routes.py', 'CommandRequest').
python_class('agents/generated/screenshot_analysis_agent/routes.py', 'CommandRequest').
python_class('agents/generated/user_agent/routes.py', 'CommandRequest').
python_class('agents/generated/weather_map_agent/routes.py', 'CommandRequest').
python_class('agents/operators/browser_operator/adapters/browser_playwright.py', '_PlaywrightWorker').
python_method('_PlaywrightWorker', '__init__', 0, 1, 3).
python_method('_PlaywrightWorker', '_loop', 0, 4, 3).
python_method('_PlaywrightWorker', 'run', 1, 2, 4).
python_class('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/models.py', 'UriAction').
python_method('UriAction', 'to_dict', 0, 2, 0).
python_class('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/models.py', 'ProcessViewModel').
python_method('ProcessViewModel', 'to_dict', 0, 2, 1).
python_class('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/models.py', 'ViewEnvelope').
python_method('ViewEnvelope', 'to_dict', 0, 2, 0).
python_class('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/plan_runner.py', 'PlanRunOptions').
python_class('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/policy.py', 'ApprovalDecision').
python_class('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'PlanRunRequest').
python_class('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'VoiceSpeakRequest').
python_class('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'VoiceTranscribeRequest').
python_class('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'UriCallRequest').
python_class('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py', 'AskRequest').
python_class('agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py', '_SystemUriRequest').
python_class('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', 'CommandRequest').
python_class('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 'CommandRequest').
python_class('packages/resource-agent-factory/generator/model.py', 'Capability').
python_class('packages/resource-agent-factory/generator/model.py', 'AgentSpec').
python_method('AgentSpec', 'output_dir_name', 0, 1, 0).
python_class('packages/resource-agent-hypervisor/hypervisor/agent_describe.py', 'AgentDescribeReport').
python_method('AgentDescribeReport', 'write', 1, 1, 2).
python_class('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', 'ArtifactCheckResult').
python_class('packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py', 'ArtifactLifecycleResult').
python_class('packages/resource-agent-hypervisor/hypervisor/config/models.py', 'LLMConfig').
python_method('LLMConfig', 'from_dict', 2, 1, 3).
python_class('packages/resource-agent-hypervisor/hypervisor/config/models.py', 'Uri3Config').
python_method('Uri3Config', 'from_dict', 2, 1, 3).
python_class('packages/resource-agent-hypervisor/hypervisor/config/models.py', 'RegistryConfig').
python_method('RegistryConfig', 'from_dict', 2, 1, 3).
python_class('packages/resource-agent-hypervisor/hypervisor/config/models.py', 'DomainPackConfig').
python_method('DomainPackConfig', 'from_dict', 2, 1, 3).
python_class('packages/resource-agent-hypervisor/hypervisor/config/models.py', 'AgentsConfig').
python_method('AgentsConfig', 'from_dict', 2, 1, 3).
python_class('packages/resource-agent-hypervisor/hypervisor/config/models.py', 'DeploymentConfig').
python_method('DeploymentConfig', 'from_dict', 2, 1, 3).
python_class('packages/resource-agent-hypervisor/hypervisor/config/models.py', 'HypervisorSettings').
python_method('HypervisorSettings', 'from_dict', 2, 1, 5).
python_class('packages/resource-agent-hypervisor/hypervisor/config/models.py', 'HypervisorConfig').
python_method('HypervisorConfig', 'from_dict', 2, 1, 5).
python_method('HypervisorConfig', 'to_dict', 0, 1, 1).
python_class('packages/resource-agent-hypervisor/hypervisor/contract_registry/models.py', 'ResourceContract').
python_class('packages/resource-agent-hypervisor/hypervisor/contract_registry/models.py', 'ViewContract').
python_class('packages/resource-agent-hypervisor/hypervisor/contract_registry/models.py', 'CapabilityContract').
python_class('packages/resource-agent-hypervisor/hypervisor/contract_registry/models.py', 'ContractRegistry').
python_method('ContractRegistry', 'resource_by_uri', 1, 3, 1).
python_method('ContractRegistry', 'view_by_name', 1, 3, 1).
python_method('ContractRegistry', 'capability_by_name', 2, 4, 1).
python_class('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', 'SchemaValidationResult').
python_class('packages/resource-agent-hypervisor/hypervisor/core.py', 'Hypervisor').
python_method('Hypervisor', '__post_init__', 0, 1, 3).
python_method('Hypervisor', 'from_config', 2, 1, 2).
python_method('Hypervisor', 'start', 0, 2, 0).
python_method('Hypervisor', 'stop', 0, 2, 0).
python_method('Hypervisor', 'register_agent', 1, 3, 3).
python_method('Hypervisor', 'status', 0, 1, 2).
python_method('Hypervisor', '__repr__', 0, 1, 1).
python_class('packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/pipeline.py', 'InspectionContext').
python_class('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', 'DeploymentDeclared').
python_method('DeploymentDeclared', 'to_dict', 0, 7, 0).
python_class('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', 'DeploymentRuntimeView').
python_method('DeploymentRuntimeView', 'to_dict', 0, 7, 0).
python_class('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', 'AgentDeployment').
python_method('AgentDeployment', 'declared_health_uri', 0, 3, 0).
python_method('AgentDeployment', 'effective_health_uri', 0, 3, 0).
python_method('AgentDeployment', 'to_dict', 0, 7, 3).
python_class('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', 'DeploymentRegistry').
python_method('DeploymentRegistry', 'by_id', 1, 3, 1).
python_method('DeploymentRegistry', 'by_agent_ref', 1, 3, 0).
python_class('packages/resource-agent-hypervisor/hypervisor/domain_pack/model.py', 'DomainModel').
python_method('DomainModel', 'from_uri_tree', 3, 1, 1).
python_class('packages/resource-agent-hypervisor/hypervisor/evolution/models.py', 'EvolutionProposal').
python_class('packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py', 'GateDecision').
python_class('packages/resource-agent-hypervisor/hypervisor/repair/classifier.py', 'ErrorFamily').
python_class('packages/resource-agent-hypervisor/hypervisor/repair/models.py', 'Symptom').
python_method('Symptom', 'to_dict', 0, 2, 0).
python_class('packages/resource-agent-hypervisor/hypervisor/repair/models.py', 'IncidentArtifact').
python_method('IncidentArtifact', 'to_dict', 0, 2, 1).
python_method('IncidentArtifact', 'self_uri', 0, 1, 0).
python_class('packages/resource-agent-hypervisor/hypervisor/routing/models.py', 'RoutePolicyDecision').
python_method('RoutePolicyDecision', 'to_dict', 0, 1, 1).
python_class('packages/resource-agent-hypervisor/hypervisor/routing/models.py', 'HypervisorRouteResolution').
python_method('HypervisorRouteResolution', 'to_dict', 0, 1, 3).
python_class('packages/resource-agent-hypervisor/hypervisor/routing/policy.py', 'PolicyRequest').
python_class('packages/resource-agent-hypervisor/hypervisor/routing/policy.py', 'PolicyEvaluation').
python_method('PolicyEvaluation', 'reason', 0, 2, 0).
python_method('PolicyEvaluation', 'to_route_decision', 0, 1, 1).
python_class('packages/resource-agent-hypervisor/hypervisor/routing/system_request.py', 'SystemUriRequest').
python_class('packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py', 'ViewEnvelope').
python_method('ViewEnvelope', 'to_dict', 0, 2, 0).
python_class('packages/resource-agent-hypervisor/hypervisor/uri/client.py', 'Uri3Client').
python_method('Uri3Client', '__init__', 0, 1, 1).
python_method('Uri3Client', 'resolve', 1, 1, 1).
python_method('Uri3Client', 'call', 2, 3, 4).
python_method('Uri3Client', 'explain', 2, 3, 4).
python_method('Uri3Client', 'scan', 1, 1, 1).
python_method('Uri3Client', 'logs', 1, 2, 2).
python_method('Uri3Client', 'schema', 1, 1, 1).
python_method('Uri3Client', 'graph', 1, 1, 1).
python_method('Uri3Client', 'nl2uri', 1, 1, 1).
python_class('packages/resource-agent-hypervisor/meta_agent/api.py', 'PromptRequest').
python_class('packages/resource-agent-hypervisor/meta_agent/api.py', 'SpecPathRequest').
python_class('packages/resource-agent-hypervisor/meta_agent/models.py', 'AgentCreationIntent').
python_class('packages/resource-agent-hypervisor/meta_agent/models.py', 'RepairResult').
python_class('packages/resource-agent-hypervisor/meta_agent/models.py', 'PipelineResult').
python_class('packages/resource-agent-hypervisor/runtime_client/client.py', 'ResourceRuntimeClient').
python_method('ResourceRuntimeClient', '__init__', 2, 1, 1).
python_method('ResourceRuntimeClient', 'read_resource', 1, 2, 4).
python_method('ResourceRuntimeClient', 'dispatch_command', 2, 2, 4).
python_class('packages/uri2flow/uri2flow/models.py', 'FlowStep').
python_class('packages/uri2flow/uri2flow/models.py', 'FlowDocument').
python_method('FlowDocument', 'to_dict', 0, 11, 2).
python_class('packages/uri2flow/uri2flow/parser.py', 'FlowParseError').
python_class('packages/uri2flow/uri2flow/resolver.py', 'OperationDefaults').
python_class('scripts/architecture_audit/models.py', 'ModuleEntry').
python_class('scripts/architecture_audit/models.py', 'DupFragment').
python_class('scripts/architecture_audit/models.py', 'DupGroup').
python_class('scripts/architecture_audit/models.py', 'Finding').
python_class('scripts/architecture_audit/models.py', 'AuditResult').
python_class('scripts/examples/audit_agent_reports.py', 'ExampleAuditSpec').
python_class('scripts/examples/audit_agent_reports.py', 'Finding').
python_class('scripts/examples/audit_agent_reports.py', 'AuditReport').
python_method('AuditReport', 'errors', 0, 3, 1).
python_method('AuditReport', 'warnings', 0, 3, 1).
python_class('scripts/examples/comprehensive_test.py', 'CommandResult').
python_class('scripts/examples/comprehensive_test.py', 'ComprehensiveReport').
python_method('ComprehensiveReport', 'passed', 0, 3, 1).
python_method('ComprehensiveReport', 'failed', 0, 3, 1).
python_method('ComprehensiveReport', 'skipped', 0, 3, 1).
python_class('testenv/ssh_agent_host/mock_agent_server.py', 'Handler').
python_method('Handler', '_json', 2, 1, 8).
python_method('Handler', 'do_GET', 0, 5, 4).
python_method('Handler', 'log_message', 1, 1, 1).
python_class('tests/examples/capabilities.py', 'CapabilityProbe').
python_class('tests/examples/capabilities.py', 'MachineCapabilities').
python_method('MachineCapabilities', 'available', 1, 3, 0).
python_method('MachineCapabilities', 'to_dict', 0, 6, 1).
python_class('tests/examples/catalog.py', 'ExampleSpec').
python_class('tests/examples/command_catalog.py', 'CommandSpec').
python_class('www/api-bridge/bridge.py', 'UriCall').
python_class('www/api-bridge/bridge.py', 'AskCall').

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────
makefile_target('PYTHON', 'Prefer repo .venv so start-agents works outside an activated shell (conda base often lacks uvicorn).').
makefile_target('HYPERVISOR', '').
makefile_target('validate', '').
makefile_target('generate', '').
makefile_target('verify', '').
makefile_target('test', '').
makefile_target('architecture-test', '').
makefile_target('architecture-responsibility-audit', '').
makefile_target('doctor', '').
makefile_target('architecture-gate', '').
makefile_target('ci-gate', '').
makefile_target('examples-test', '').
makefile_target('examples-comprehensive', '').
makefile_target('examples-real-report', '').
makefile_target('doql-registry', '').
makefile_target('examples-comprehensive-mock', '').
makefile_target('examples-playwright-proof', '').
makefile_target('uri2flow-test', '').
makefile_target('uri2flow-validate', '').
makefile_target('uri2flow-expand', '').
makefile_target('uri3-flow-dry-run', '').
makefile_target('nl2uri-flow-validate', '').
makefile_target('example-18', '').
makefile_target('touri-test', '').
makefile_target('touri-demo', '').
makefile_target('voice-test', '').
makefile_target('voice-demo', '').
makefile_target('uri-tree', '').
makefile_target('graph', '').
makefile_target('nl2a-weather', '').
makefile_target('run-user-agent', '').
makefile_target('run-meta-agent', '').
makefile_target('meta-plan', '').
makefile_target('meta-pipeline', '').
makefile_target('meta-repair', '').
makefile_target('docker-ssh-up', '').
makefile_target('docker-ssh-down', '').
makefile_target('docker-testenv-up', '').
makefile_target('docker-testenv-down', '').
makefile_target('scan-http', '').
makefile_target('scan-ssh', '').
makefile_target('scan-all', '').
makefile_target('evolution-check', '').
makefile_target('examples', '').
makefile_target('run-weather-agent', '').
makefile_target('clean', '').
makefile_target('ensure-dev', '').
makefile_target('agent-health', '').
makefile_target('start', '').
makefile_target('start-agents', '').
makefile_target('start-full', '').
makefile_target('uri-shell', '').
makefile_target('stop', '').
makefile_target('www-test', '').
makefile_target('www-docs', '').
makefile_target('www-docs-check', '').
makefile_target('examples-shell', '').
makefile_target('www-smoke', '').
makefile_target('www-monitor', '').
makefile_target('www-monitor-reset', '').
makefile_target('www-monitor-test', '').
makefile_target('www-logs', '').

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', 'sk-or-v1-...', '').
env_variable('LLM_MODEL', 'llm://openrouter/qwen/qwen3-coder-next', '').
env_variable('LLM_BASE_URL', 'https://openrouter.ai/api/v1', '').
env_variable('LLM_TEMPERATURE', '0.1', '').
env_variable('LLM_MAX_TOKENS', '8000', '').
env_variable('RESOURCE_RUNTIME_URL', 'http://localhost:8000', '').
env_variable('HYPERVISOR_SSH_PASSWORD', 'deploy', '').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-api-smoke.testql.toon.yaml', 'api').
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-api-smoke.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('api', '').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_interface('cli', '').
sumd_workflow('validate', 'manual').
sumd_workflow_step('validate', 1, 'python -m generator.validate contracts').
sumd_workflow('generate', 'manual').
sumd_workflow_step('generate', 1, 'python -m generator.agent_generator contracts/agents/*.yaml').
sumd_workflow('verify', 'manual').
sumd_workflow_step('verify', 1, 'python -m generator.verify agents/generated').
sumd_workflow('test', 'manual').
sumd_workflow_step('test', 1, 'pytest -q').
sumd_workflow('architecture-test', 'manual').
sumd_workflow_step('architecture-test', 1, 'pytest tests/architecture -q').
sumd_workflow('architecture-responsibility-audit', 'manual').
sumd_workflow_step('architecture-responsibility-audit', 1, 'python3 scripts/architecture_responsibility_audit.py --top 30').
sumd_workflow('doctor', 'manual').
sumd_workflow_step('doctor', 1, 'uri3 doctor --json').
sumd_workflow('architecture-gate', 'manual').
sumd_workflow_step('architecture-gate', 1, 'bash scripts/ci/architecture_gate.sh').
sumd_workflow('ci-gate', 'manual').
sumd_workflow('examples-test', 'manual').
sumd_workflow_step('examples-test', 1, 'pytest tests/examples -q').
sumd_workflow('examples-comprehensive', 'manual').
sumd_workflow_step('examples-comprehensive', 1, 'python3 scripts/examples/comprehensive_test.py').
sumd_workflow('examples-real-report', 'manual').
sumd_workflow_step('examples-real-report', 1, 'python3 scripts/examples/comprehensive_test.py --real-only').
sumd_workflow('doql-registry', 'manual').
sumd_workflow_step('doql-registry', 1, 'bash scripts/examples/doql_host_preview.sh').
sumd_workflow('examples-comprehensive-mock', 'manual').
sumd_workflow_step('examples-comprehensive-mock', 1, 'python3 scripts/examples/comprehensive_test.py --mock-only').
sumd_workflow('examples-playwright-proof', 'manual').
sumd_workflow_step('examples-playwright-proof', 1, 'python3 scripts/examples/effective_weather_playwright.py').
sumd_workflow_step('examples-playwright-proof', 2, 'python3 scripts/examples/effective_weather_playwright.py --legacy-screenshot').
sumd_workflow('uri2flow-test', 'manual').
sumd_workflow_step('uri2flow-test', 1, 'pytest tests/uri2flow -q').
sumd_workflow('uri2flow-validate', 'manual').
sumd_workflow_step('uri2flow-validate', 1, 'uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml').
sumd_workflow('uri2flow-expand', 'manual').
sumd_workflow_step('uri2flow-expand', 1, 'mkdir -p output').
sumd_workflow_step('uri2flow-expand', 2, 'uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml').
sumd_workflow('uri3-flow-dry-run', 'manual').
sumd_workflow_step('uri3-flow-dry-run', 1, 'uri3 run-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --dry-run').
sumd_workflow('nl2uri-flow-validate', 'manual').
sumd_workflow_step('nl2uri-flow-validate', 1, 'nl2uri flow -p "wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome" --validate').
sumd_workflow('example-18', 'manual').
sumd_workflow_step('example-18', 1, 'bash examples/18_llm_flow_planner/run.sh').
sumd_workflow('touri-test', 'manual').
sumd_workflow_step('touri-test', 1, 'pytest tests/touri -q').
sumd_workflow('touri-demo', 'manual').
sumd_workflow_step('touri-demo', 1, 'touri validate examples/20_touri_capabilities/weather_forecast.uri.capability.yaml').
sumd_workflow_step('touri-demo', 2, 'touri list examples/20_touri_capabilities').
sumd_workflow_step('touri-demo', 3, 'touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities').
sumd_workflow_step('touri-demo', 4, 'touri call echo://Adam --registry examples/20_touri_capabilities').
sumd_workflow('voice-test', 'manual').
sumd_workflow_step('voice-test', 1, 'pytest tests/touri/test_voice_capabilities.py -q').
sumd_workflow('voice-demo', 'manual').
sumd_workflow_step('voice-demo', 1, 'touri validate examples/21_touri_voice/stt_mock.uri.capability.yaml').
sumd_workflow_step('voice-demo', 2, 'touri list examples/21_touri_voice').
sumd_workflow('uri-tree', 'manual').
sumd_workflow_step('uri-tree', 1, 'python -m nl2uri.cli tree --no-llm -p "$(WEATHER_PROMPT)" --out domains/weather_map/uri_tree.yaml').
sumd_workflow('graph', 'manual').
sumd_workflow_step('graph', 1, 'uri3 graph domains/weather_map/uri_tree.yaml').
sumd_workflow('nl2a-weather', 'manual').
sumd_workflow_step('nl2a-weather', 1, 'python -m nl2a.cli --no-llm -p "$(WEATHER_PROMPT)"').
sumd_workflow('run-user-agent', 'manual').
sumd_workflow_step('run-user-agent', 1, 'uvicorn agents.generated.user_agent.main:app --reload --port 8101').
sumd_workflow('run-meta-agent', 'manual').
sumd_workflow_step('run-meta-agent', 1, 'uvicorn meta_agent.api:app --reload --port 8200').
sumd_workflow('meta-plan', 'manual').
sumd_workflow_step('meta-plan', 1, 'python -m meta_agent.cli plan "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia"').
sumd_workflow('meta-pipeline', 'manual').
sumd_workflow_step('meta-pipeline', 1, 'python -m meta_agent.cli pipeline "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia"').
sumd_workflow('meta-repair', 'manual').
sumd_workflow_step('meta-repair', 1, 'python -m meta_agent.cli repair examples/05_meta_repair/broken_agent.yaml --write').
sumd_workflow('docker-ssh-up', 'manual').
sumd_workflow_step('docker-ssh-up', 1, 'python -m hypervisor.cli call \'docker://stack/ssh-testenv?action=up&build=1\'').
sumd_workflow('docker-ssh-down', 'manual').
sumd_workflow_step('docker-ssh-down', 1, 'python -m hypervisor.cli call \'docker://stack/ssh-testenv?action=down&remove_volumes=1\'').
sumd_workflow('docker-testenv-up', 'manual').
sumd_workflow('docker-testenv-down', 'manual').
sumd_workflow('scan-http', 'manual').
sumd_workflow_step('scan-http', 1, 'python -m uri3.cli scan http').
sumd_workflow('scan-ssh', 'manual').
sumd_workflow('scan-all', 'manual').
sumd_workflow('evolution-check', 'manual').
sumd_workflow_step('evolution-check', 1, 'python -m hypervisor.evolution.cli examples/08_evolution/proposals/add_orders_agent.yaml examples/08_evolution/proposals/add_invoices_agent.yaml').
sumd_workflow('examples', 'manual').
sumd_workflow_step('examples', 1, 'echo "See examples/README.md for the full catalog (01–09)."').
sumd_workflow('run-weather-agent', 'manual').
sumd_workflow_step('run-weather-agent', 1, 'python -m hypervisor.cli run-agent weather-map-agent.local').
sumd_workflow('clean', 'manual').
sumd_workflow_step('clean', 1, 'rm -rf agents/generated/* output/* .pytest_cache').
sumd_workflow('ensure-dev', 'manual').
sumd_workflow_step('ensure-dev', 1, '$(PYTHON) -c "import uvicorn" 2>/dev/null || { \').
sumd_workflow_step('ensure-dev', 2, 'echo "Installing dev deps into project Python…"').
sumd_workflow_step('ensure-dev', 3, '$(PYTHON) -m pip install -q -e ".[dev]"').
sumd_workflow('agent-health', 'manual').
sumd_workflow_step('agent-health', 1, 'echo "Agents:"').
sumd_workflow_step('agent-health', 2, 'for id in weather-map-agent.local invoices-agent.local user-agent.local').
sumd_workflow_step('agent-health', 3, 'uri=$$($(HYPERVISOR) inspect-agent $$id 2>/dev/null | $(PYTHON) -c "import json,sys').
sumd_workflow_step('agent-health', 4, 'if [ -n "$$uri" ]').
sumd_workflow_step('agent-health', 5, 'echo "  $$id -> $$uri"').
sumd_workflow_step('agent-health', 6, 'curl -fsS "$$uri" 2>/dev/null | $(PYTHON) -m json.tool || echo "    (unreachable)"').
sumd_workflow_step('agent-health', 7, 'fi').
sumd_workflow_step('agent-health', 8, 'done').
sumd_workflow('start', 'manual').
sumd_workflow_step('start', 1, '$(WWW_COMPOSE) up -d --build').
sumd_workflow_step('start', 2, 'echo "Waiting for www chat health on $(WWW_BASE)…"').
sumd_workflow_step('start', 3, 'for i in $$(seq 1 30)').
sumd_workflow_step('start', 4, 'if curl -fsS "$(WWW_BASE)/health" >/dev/null 2>&1').
sumd_workflow_step('start', 5, 'if [ "$$i" -eq 30 ]').
sumd_workflow_step('start', 6, 'sleep 1').
sumd_workflow_step('start', 7, 'done').
sumd_workflow_step('start', 8, 'curl -fsS "$(WWW_BASE)/health" | python3 -m json.tool').
sumd_workflow_step('start', 9, 'echo "Chat UI: $(WWW_BASE)/www/"').
sumd_workflow_step('start', 10, 'echo "Tip: run local agents with: make start-agents"').
sumd_workflow('start-agents', 'manual').
sumd_workflow_step('start-agents', 1, '$(HYPERVISOR) run-agent weather-map-agent.local --detach --if-running reuse --wait-healthy').
sumd_workflow_step('start-agents', 2, '$(HYPERVISOR) run-agent invoices-agent.local --detach --if-running reuse --wait-healthy').
sumd_workflow_step('start-agents', 3, '$(HYPERVISOR) run-agent user-agent.local --detach --if-running reuse --wait-healthy').
sumd_workflow_step('start-agents', 4, '$(MAKE) agent-health').
sumd_workflow('start-full', 'manual').
sumd_workflow('uri-shell', 'manual').
sumd_workflow_step('uri-shell', 1, 'urish').
sumd_workflow('stop', 'manual').
sumd_workflow_step('stop', 1, '$(WWW_COMPOSE) down').
sumd_workflow('www-test', 'manual').
sumd_workflow_step('www-test', 1, 'pytest tests/hypervisor/test_chat_www.py -q').
sumd_workflow('www-docs', 'manual').
sumd_workflow_step('www-docs', 1, 'python3 scripts/www/build_examples_docs.py').
sumd_workflow_step('www-docs', 2, 'python3 scripts/www/build_landing_integrations.py').
sumd_workflow_step('www-docs', 3, 'python3 scripts/www/build_examples_manifest.py').
sumd_workflow('www-docs-check', 'manual').
sumd_workflow_step('www-docs-check', 1, 'python3 scripts/www/build_examples_docs.py --check').
sumd_workflow_step('www-docs-check', 2, 'python3 scripts/www/build_landing_integrations.py --check').
sumd_workflow_step('www-docs-check', 3, 'python3 scripts/www/build_examples_manifest.py --check').
sumd_workflow_step('www-docs-check', 4, 'python3 scripts/www/check_examples_links.py').
sumd_workflow('examples-shell', 'manual').
sumd_workflow_step('examples-shell', 1, 'python3 tests/examples/shell_runner.py').
sumd_workflow('www-smoke', 'manual').
sumd_workflow_step('www-smoke', 1, 'bash scripts/www/smoke.sh "$(WWW_BASE)"').
sumd_workflow('www-monitor', 'manual').
sumd_workflow_step('www-monitor', 1, 'bash scripts/www/run_monitors.sh').
sumd_workflow('www-monitor-reset', 'manual').
sumd_workflow_step('www-monitor-reset', 1, 'python3 scripts/www/monitor_landing.py --url "$(WWW_BASE)/www/" --reset-baseline').
sumd_workflow('www-monitor-test', 'manual').
sumd_workflow_step('www-monitor-test', 1, 'bash scripts/www/test_monitors.sh').
sumd_workflow('www-logs', 'manual').
sumd_workflow_step('www-logs', 1, '$(WWW_COMPOSE) logs -f --tail=100').
sumd_deploy_target('docker_compose').
sumd_deploy_compose_file('docker-compose.yml').
```

## Call Graph

*397 nodes · 500 edges · 114 modules · CC̄=3.6*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_render_markdown` *(in packages.resource-agent-hypervisor.hypervisor.agent_describe)* | 70 ⚠ | 1 | 119 | **120** |
| `print` *(in examples.38_autonomous_agents.run)* | 0 | 85 | 0 | **85** |
| `find_repo_root` *(in packages.resource-agent-hypervisor.hypervisor.paths)* | 6 | 47 | 9 | **56** |
| `fetch_agent_artifacts` *(in packages.resource-agent-hypervisor.hypervisor.contract_registry.uri_resolver)* | 21 ⚠ | 1 | 42 | **43** |
| `load_contract_registry` *(in hypervisor.contract_registry.loader)* | 9 | 9 | 33 | **42** |
| `call_uri` *(in packages.resource-agent-hypervisor.hypervisor.routing.dispatcher)* | 6 | 25 | 16 | **41** |
| `echo_json` *(in packages.resource-agent-hypervisor.hypervisor.cli_commands)* | 2 | 33 | 5 | **38** |
| `write_domain_pack` *(in packages.resource-agent-hypervisor.hypervisor.domain_pack.pack_writer)* | 8 | 1 | 34 | **35** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/hypervisor
# generated in 0.23s
# nodes: 397 | edges: 500 | modules: 114
# CC̄=3.6

HUBS[20]:
  packages.resource-agent-hypervisor.hypervisor.agent_describe._render_markdown
    CC=70  in:1  out:119  total:120
  examples.38_autonomous_agents.run.print
    CC=0  in:85  out:0  total:85
  packages.resource-agent-hypervisor.hypervisor.paths.find_repo_root
    CC=6  in:47  out:9  total:56
  packages.resource-agent-hypervisor.hypervisor.contract_registry.uri_resolver.fetch_agent_artifacts
    CC=21  in:1  out:42  total:43
  hypervisor.contract_registry.loader.load_contract_registry
    CC=9  in:9  out:33  total:42
  packages.resource-agent-hypervisor.hypervisor.routing.dispatcher.call_uri
    CC=6  in:25  out:16  total:41
  packages.resource-agent-hypervisor.hypervisor.cli_commands.echo_json
    CC=2  in:33  out:5  total:38
  packages.resource-agent-hypervisor.hypervisor.domain_pack.pack_writer.write_domain_pack
    CC=8  in:1  out:34  total:35
  packages.resource-agent-hypervisor.hypervisor.contract_registry.uri_resolver.resolve_contract_path
    CC=22  in:5  out:29  total:34
  meta_agent.planner.infer_intent
    CC=9  in:1  out:30  total:31
  packages.resource-agent-hypervisor.hypervisor.agent_describe.describe_agent
    CC=17  in:4  out:26  total:30
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.selector.resolve_deployment
    CC=12  in:13  out:17  total:30
  packages.resource-agent-hypervisor.hypervisor.contract_registry.uri_resolver.handle_contract_uri
    CC=21  in:1  out:29  total:30
  packages.resource-agent-hypervisor.hypervisor.contract_registry.uri_resolver.generate_agent_contract
    CC=12  in:1  out:26  total:27
  generator.model.load_agent_spec
    CC=7  in:3  out:24  total:27
  packages.resource-agent-hypervisor.hypervisor.repair.supervisor.supervise_with_repair
    CC=9  in:4  out:23  total:27
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.loader.load_deployment_registry
    CC=5  in:18  out:8  total:26
  packages.resource-agent-hypervisor.hypervisor.agent_describe._find_domain_pack
    CC=11  in:1  out:24  total:25
  packages.resource-agent-factory.generator.agent_generator.generate_agent
    CC=5  in:3  out:22  total:25
  packages.resource-agent-hypervisor.hypervisor.repair.supervisor.diagnose_agent
    CC=4  in:5  out:19  total:24

MODULES:
  agents.custom.remote_deploy_agent.deploy  [1 funcs]
    repo_root  CC=1  out:1
  examples.38_autonomous_agents.run  [1 funcs]
    print  CC=0  out:0
  generator.hashutil  [1 funcs]
    file_sha256  CC=1  out:4
  generator.model  [2 funcs]
    load_agent_spec  CC=7  out:24
    spec_to_plain_dict  CC=3  out:1
  generator.validate  [3 funcs]
    iter_agent_specs  CC=3  out:6
    main  CC=7  out:9
    validate_agent  CC=11  out:10
  hypervisor.config.env  [4 funcs]
    _parse_bool  CC=1  out:1
    apply_env_overrides  CC=1  out:2
    apply_legacy_env_overrides  CC=6  out:4
    apply_structured_env_overrides  CC=9  out:17
  hypervisor.contract_registry.loader  [2 funcs]
    _read_yaml  CC=3  out:4
    load_contract_registry  CC=9  out:33
  hypervisor.contract_registry.registry_exporter  [2 funcs]
    export_json  CC=1  out:1
    export_markdown  CC=6  out:13
  hypervisor.contract_registry.schema_validator  [4 funcs]
    _read_json  CC=1  out:2
    _read_yaml  CC=2  out:2
    validate_contract_files  CC=6  out:13
    validate_file  CC=3  out:8
  hypervisor.evolution.models  [1 funcs]
    load_proposal  CC=5  out:11
  hypervisor.verifier.cli  [1 funcs]
    main  CC=5  out:8
  meta_agent.api  [6 funcs]
    generate  CC=2  out:6
    pipeline  CC=2  out:4
    proposal_from_prompt  CC=2  out:6
    repair  CC=2  out:5
    validate  CC=2  out:5
    verify  CC=1  out:2
  meta_agent.planner  [4 funcs]
    infer_intent  CC=9  out:30
    intent_to_agent_spec  CC=8  out:11
    package_name  CC=3  out:6
    singularize  CC=4  out:3
  meta_agent.repair.loader  [2 funcs]
    load_spec  CC=2  out:3
    write_spec  CC=1  out:2
  meta_agent.repair.pipeline  [1 funcs]
    repair_agent_spec  CC=2  out:12
  meta_agent.repair.rules  [6 funcs]
    repair_agent_block  CC=6  out:12
    repair_capabilities  CC=6  out:8
    repair_command_capability  CC=4  out:10
    repair_duplicate_capability_names  CC=5  out:5
    repair_missing_capability_type  CC=3  out:4
    repair_resource_read_capability  CC=8  out:14
  packages.resource-agent-factory.agents.generated.orders_agent.routes  [2 funcs]
    _uri_allowed  CC=4  out:2
    read_resource  CC=4  out:7
  packages.resource-agent-factory.agents.generated.user_agent.routes  [2 funcs]
    _uri_allowed  CC=4  out:2
    read_resource  CC=4  out:7
  packages.resource-agent-factory.generator.agent_generator  [4 funcs]
    _default_port_for_agent  CC=3  out:3
    expand_paths  CC=4  out:7
    generate_agent  CC=5  out:22
    main  CC=5  out:4
  packages.resource-agent-factory.generator.header  [2 funcs]
    contract_source_ref  CC=3  out:7
    generated_marker_payload  CC=1  out:0
  packages.resource-agent-factory.generator.paths  [1 funcs]
    project_root  CC=1  out:1
  packages.resource-agent-factory.generator.verify  [4 funcs]
    _agent_dirs  CC=6  out:4
    main  CC=6  out:8
    verify_generated  CC=3  out:3
    verify_generated_agent  CC=7  out:10
  packages.resource-agent-hypervisor.hypervisor.agent_describe  [13 funcs]
    _agent_kind  CC=6  out:5
    _capability_backing_note  CC=4  out:0
    _deployment_health_label  CC=6  out:4
    _file_role  CC=4  out:2
    _find_contract_path  CC=13  out:15
    _find_domain_pack  CC=11  out:24
    _list_package_files  CC=6  out:9
    _package_relative_path  CC=3  out:3
    _read_yaml  CC=3  out:4
    _rel  CC=3  out:3
  packages.resource-agent-hypervisor.hypervisor.artifacts.gate  [9 funcs]
    _artifact_lifecycle_result  CC=14  out:16
    _collect_lifecycle_results  CC=6  out:7
    _lifecycle_samples  CC=2  out:0
    _lifecycle_summary  CC=2  out:2
    _read_structured_mapping  CC=3  out:5
    _validate_path  CC=4  out:12
    check_artifacts  CC=11  out:7
    check_lifecycle_coverage  CC=10  out:8
    check_schemas  CC=5  out:12
  packages.resource-agent-hypervisor.hypervisor.cli  [27 funcs]
    _load_json_payload  CC=4  out:6
    agent_status_cmd  CC=1  out:5
    artifacts_check_cmd  CC=2  out:7
    artifacts_lifecycle_cmd  CC=3  out:8
    artifacts_schemas_cmd  CC=2  out:6
    call  CC=2  out:9
    config_cmd  CC=2  out:7
    deploy_agent_cmd  CC=1  out:4
    deployments_list  CC=1  out:4
    describe_agent_cmd  CC=4  out:11
  packages.resource-agent-hypervisor.hypervisor.cli_commands  [6 funcs]
    call_docker  CC=5  out:6
    deploy_agent  CC=7  out:16
    echo_json  CC=2  out:5
    read_agent_logs  CC=3  out:4
    run_local_agent  CC=7  out:17
    verify_agent  CC=5  out:11
  packages.resource-agent-hypervisor.hypervisor.config.config_checks  [4 funcs]
    validate_hypervisor  CC=7  out:7
    validate_llm  CC=4  out:4
    validate_path_sections  CC=5  out:5
    validate_uri3  CC=4  out:3
  packages.resource-agent-hypervisor.hypervisor.config.defaults  [4 funcs]
    apply_builtin_defaults  CC=1  out:17
    embedded_defaults_raw  CC=1  out:1
    get_default_config  CC=1  out:3
    load_yaml_file  CC=4  out:4
  packages.resource-agent-hypervisor.hypervisor.config.loader  [5 funcs]
    config_search_paths  CC=6  out:11
    get_config  CC=1  out:1
    load_config  CC=3  out:9
    load_hypervisor_config  CC=1  out:2
    resolve_config_path  CC=3  out:2
  packages.resource-agent-hypervisor.hypervisor.config.uri_config  [2 funcs]
    _repo_config_dir  CC=2  out:2
    apply_uri_yaml_configs  CC=10  out:14
  packages.resource-agent-hypervisor.hypervisor.config.validators  [2 funcs]
    merge_config  CC=5  out:5
    validate_config  CC=1  out:4
  packages.resource-agent-hypervisor.hypervisor.contract_registry.cli  [2 funcs]
    _parse_args  CC=5  out:2
    main  CC=2  out:1
  packages.resource-agent-hypervisor.hypervisor.contract_registry.cli_commands  [5 funcs]
    run_build_command  CC=1  out:2
    run_check_command  CC=5  out:13
    run_cross_command  CC=3  out:4
    run_export_md_command  CC=1  out:2
    run_schema_command  CC=5  out:3
  packages.resource-agent-hypervisor.hypervisor.contract_registry.cross_checks.capabilities  [2 funcs]
    _validate_single_capability  CC=14  out:6
    validate_capability_cross_refs  CC=4  out:4
  packages.resource-agent-hypervisor.hypervisor.contract_registry.cross_checks.proto_index  [2 funcs]
    load_proto_text  CC=2  out:5
    schema_exists  CC=1  out:3
  packages.resource-agent-hypervisor.hypervisor.contract_registry.cross_checks.resources  [1 funcs]
    validate_resource_cross_refs  CC=6  out:4
  packages.resource-agent-hypervisor.hypervisor.contract_registry.cross_validator  [2 funcs]
    validate_cross_references  CC=5  out:3
    validate_root  CC=1  out:2
  packages.resource-agent-hypervisor.hypervisor.contract_registry.merge_helpers  [3 funcs]
    merge_proto_contract  CC=2  out:1
    merge_resources_contract  CC=5  out:14
    merge_views_contract  CC=6  out:15
  packages.resource-agent-hypervisor.hypervisor.contract_registry.merger  [1 funcs]
    merge_main_contracts  CC=2  out:4
  packages.resource-agent-hypervisor.hypervisor.contract_registry.registry_builder  [3 funcs]
    _contract_hash  CC=3  out:13
    build_registry_manifest  CC=5  out:9
    write_registry_manifest  CC=2  out:6
  packages.resource-agent-hypervisor.hypervisor.contract_registry.registry_checks.capabilities  [4 funcs]
    _resolves_as_external_uri  CC=3  out:3
    validate_capabilities  CC=4  out:5
    validate_command_capability  CC=3  out:2
    validate_resource_read_capability  CC=8  out:4
  packages.resource-agent-hypervisor.hypervisor.contract_registry.registry_checks.resources  [2 funcs]
    validate_resources  CC=7  out:9
    validate_views  CC=3  out:2
  packages.resource-agent-hypervisor.hypervisor.contract_registry.uri_resolver  [15 funcs]
    _agent_contract_uri  CC=1  out:0
    _artifact_entry  CC=3  out:7
    _format_schema_results  CC=2  out:1
    _parse_bool  CC=2  out:2
    _parse_kinds  CC=5  out:3
    _read_yaml  CC=3  out:4
    _validation_payload  CC=2  out:0
    fetch_agent_artifacts  CC=21  out:42
    fetch_agent_contract  CC=8  out:15
    fetch_registry_manifest  CC=1  out:1
  packages.resource-agent-hypervisor.hypervisor.contract_registry.validate  [1 funcs]
    validate_registry  CC=1  out:3
  packages.resource-agent-hypervisor.hypervisor.core  [1 funcs]
    from_config  CC=1  out:2
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.docker_runner  [3 funcs]
    apply_docker_deploy  CC=3  out:6
    build_docker_deploy_plan  CC=4  out:6
    verify_docker_deployment  CC=9  out:5
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.env_config  [3 funcs]
    load_deployments_uri_config  CC=2  out:3
    load_runtime_uri_config  CC=2  out:3
    repo_config_dir  CC=2  out:2
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.health_uri  [1 funcs]
    command_port_from_runtime  CC=5  out:7
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.lifecycle  [15 funcs]
    _emit_run_agent_result  CC=2  out:1
    _execute_run_agent_plan  CC=3  out:5
    _finalize_run_plan  CC=5  out:4
    _is_process_start_failure  CC=2  out:2
    _lifecycle_payload  CC=1  out:1
    _load_active_runtime_state  CC=3  out:5
    _repo_root  CC=2  out:3
    _resolve_initial_run_plan  CC=2  out:4
    _resolve_running_process  CC=6  out:9
    _run_non_local_target  CC=4  out:6
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.lifecycle_status  [2 funcs]
    agent_logs_uri  CC=3  out:6
    agent_status  CC=5  out:10
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.loader  [1 funcs]
    load_deployment_registry  CC=5  out:8
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.local_targets  [2 funcs]
    build_local_run_plan  CC=4  out:15
    local_target_to_relative_path  CC=3  out:6
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.local_verify  [1 funcs]
    verify_local_deployment  CC=8  out:6
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.port_conflict  [2 funcs]
    classify_port_listeners  CC=6  out:8
    port_conflict_detail  CC=7  out:3
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.port_utils  [4 funcs]
    find_free_port  CC=4  out:4
    health_matches_agent  CC=4  out:6
    is_port_free  CC=2  out:3
    port_from_http_uri  CC=2  out:1
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.process  [4 funcs]
    _safe_log_stem  CC=5  out:2
    process_log_path  CC=3  out:5
    process_log_uri  CC=2  out:2
    start_process  CC=4  out:11
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.process_discovery  [3 funcs]
    command_line  CC=6  out:10
    command_matches_plan  CC=7  out:6
    pids_listening_on_port  CC=8  out:13
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.registry_sync  [1 funcs]
    sync_deployment_health_uri  CC=2  out:3
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.run_executor  [13 funcs]
    attach_started_process  CC=1  out:1
    build_agent_run_plan  CC=1  out:1
    load_or_clear_runtime_state  CC=1  out:1
    persist_rebound_port  CC=7  out:6
    prepare_runtime_env  CC=8  out:5
    process_start_failure_payload  CC=5  out:13
    rebind_plan_port_if_busy  CC=3  out:5
    resolve_running_mode  CC=10  out:5
    reuse_existing_process_plan  CC=2  out:4
    sync_runtime_health_uri  CC=3  out:4
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.run_plans  [1 funcs]
    build_run_plan  CC=5  out:7
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.runtime_state  [4 funcs]
    clear_runtime_state  CC=2  out:3
    is_process_alive  CC=5  out:1
    load_runtime_state  CC=3  out:6
    save_runtime_state  CC=12  out:18
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.selector  [2 funcs]
    parse_hypervisor_uri  CC=14  out:4
    resolve_deployment  CC=12  out:17
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.ssh_deploy  [2 funcs]
    apply_ssh_deploy_plan  CC=7  out:6
    build_ssh_deploy_plan  CC=3  out:10
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.ssh_run  [1 funcs]
    apply_ssh_run_plan  CC=10  out:18
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.ssh_verify  [1 funcs]
    verify_remote_deployment  CC=12  out:6
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.status  [2 funcs]
    infer_port  CC=3  out:3
    registry_summary  CC=4  out:2
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.stopper  [1 funcs]
    stop_agent  CC=3  out:8
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.supervisor  [2 funcs]
    ensure_agent_healthy  CC=10  out:16
    inspect_agent  CC=1  out:6
  packages.resource-agent-hypervisor.hypervisor.domain_pack.artifact_generators.agent_contract  [1 funcs]
    generate_agent_contract  CC=2  out:3
  packages.resource-agent-hypervisor.hypervisor.domain_pack.artifact_generators.commands  [1 funcs]
    generate_commands  CC=2  out:6
  packages.resource-agent-hypervisor.hypervisor.domain_pack.artifact_generators.handlers  [1 funcs]
    generate_handlers  CC=3  out:2
  packages.resource-agent-hypervisor.hypervisor.domain_pack.artifact_generators.proto  [1 funcs]
    generate_proto  CC=2  out:2
  packages.resource-agent-hypervisor.hypervisor.domain_pack.artifact_generators.renderers  [1 funcs]
    generate_renderers  CC=3  out:5
  packages.resource-agent-hypervisor.hypervisor.domain_pack.artifact_generators.resources  [1 funcs]
    generate_resources  CC=2  out:5
  packages.resource-agent-hypervisor.hypervisor.domain_pack.artifact_generators.views  [1 funcs]
    generate_views  CC=2  out:1
  packages.resource-agent-hypervisor.hypervisor.domain_pack.generator  [2 funcs]
    generate_domain_pack  CC=1  out:3
    generate_domain_pack_from_tree  CC=2  out:11
  packages.resource-agent-hypervisor.hypervisor.domain_pack.pack_writer  [1 funcs]
    write_domain_pack  CC=8  out:34
  packages.resource-agent-hypervisor.hypervisor.domain_pack.parser  [2 funcs]
    derive_domain_model  CC=1  out:2
    parse_uri_tree  CC=1  out:3
  packages.resource-agent-hypervisor.hypervisor.domain_pack.templates  [2 funcs]
    generic_proto  CC=1  out:1
    package_name  CC=1  out:0
  packages.resource-agent-hypervisor.hypervisor.domain_pack.writer  [1 funcs]
    write_file  CC=1  out:3
  packages.resource-agent-hypervisor.hypervisor.events  [3 funcs]
    _repo_root  CC=2  out:2
    emit_operation_event  CC=6  out:2
    emit_result_event  CC=5  out:7
  packages.resource-agent-hypervisor.hypervisor.evolution.cli  [1 funcs]
    main  CC=10  out:11
  packages.resource-agent-hypervisor.hypervisor.evolution.proposal_from_source  [3 funcs]
    build_evolution_proposal  CC=3  out:7
    build_evolution_proposal_from_ticket  CC=11  out:16
    build_repair_proposal_from_incident  CC=8  out:13
  packages.resource-agent-hypervisor.hypervisor.evolution.validator  [2 funcs]
    validate_proposal  CC=3  out:7
    validate_proposal_dict  CC=14  out:18
  packages.resource-agent-hypervisor.hypervisor.integrations.planfile.ticket_mapper  [5 funcs]
    _ticket_uri  CC=1  out:0
    import_tickets_from_planfile  CC=10  out:15
    load_planfile_strategy  CC=2  out:4
    planfile_task_to_ticket  CC=10  out:18
    propose_from_ticket_path  CC=3  out:8
  packages.resource-agent-hypervisor.hypervisor.paths  [1 funcs]
    find_repo_root  CC=6  out:9
  packages.resource-agent-hypervisor.hypervisor.repair.classifier  [5 funcs]
    _collect_text  CC=4  out:12
    _incident_text  CC=5  out:7
    _log_text  CC=7  out:8
    _warning_text  CC=5  out:7
    classify_inspection  CC=5  out:10
  packages.resource-agent-hypervisor.hypervisor.repair.healer  [1 funcs]
    run_uri_healer  CC=1  out:1
  packages.resource-agent-hypervisor.hypervisor.repair.incident  [9 funcs]
    _incident_id  CC=1  out:2
    _incident_uri_block  CC=3  out:6
    _symptom_from_item  CC=4  out:7
    _symptoms_from_inspection  CC=6  out:7
    build_incident_from_inspection  CC=8  out:13
    incident_storage_path  CC=1  out:2
    incident_uri  CC=1  out:0
    load_incident  CC=4  out:8
    write_incident  CC=3  out:8
  packages.resource-agent-hypervisor.hypervisor.repair.plan_builder  [6 funcs]
    _inspection_codes  CC=10  out:10
    _ordered_unique  CC=3  out:2
    _plan_id  CC=1  out:3
    _prioritized_playbooks  CC=5  out:6
    build_repair_plan_from_diagnosis  CC=11  out:17
    build_repair_plan_from_inspection  CC=2  out:2
  packages.resource-agent-hypervisor.hypervisor.repair.playbooks  [10 funcs]
    _playbook_clear_stale_runtime  CC=2  out:2
    _playbook_inspect  CC=1  out:1
    _playbook_not_implemented  CC=1  out:0
    _playbook_rebind_port  CC=8  out:15
    _playbook_requires_approval  CC=1  out:0
    _playbook_restart_agent  CC=1  out:1
    _playbook_sync_health_uri  CC=4  out:6
    _repo_root  CC=2  out:2
    apply_playbook  CC=4  out:3
    apply_playbook_sequence  CC=2  out:2
  packages.resource-agent-hypervisor.hypervisor.repair.policy  [3 funcs]
    is_playbook_allowed  CC=1  out:3
    playbook_requires_approval  CC=2  out:4
    policy_level_for_playbook  CC=1  out:1
  packages.resource-agent-hypervisor.hypervisor.repair.proposal_builder  [2 funcs]
    build_repair_proposal  CC=2  out:2
    link_proposal_to_incident  CC=2  out:8
  packages.resource-agent-hypervisor.hypervisor.repair.registry  [5 funcs]
    _case_matches_symptoms  CC=10  out:6
    find_matching_case  CC=8  out:11
    list_repair_cases  CC=2  out:4
    load_repair_case  CC=2  out:4
    repair_cases_dir  CC=2  out:1
  packages.resource-agent-hypervisor.hypervisor.repair.sandbox  [2 funcs]
    simulate_playbook  CC=1  out:0
    test_repair_plan_in_sandbox  CC=6  out:10
  packages.resource-agent-hypervisor.hypervisor.repair.supervisor  [10 funcs]
    _envelope  CC=1  out:3
    _execute_repair_playbooks  CC=7  out:9
    _healthy_repair_apply_body  CC=2  out:1
    _repair_playbook_candidates  CC=9  out:8
    _repo_root  CC=2  out:2
    _sync_registry_if_drifted  CC=10  out:10
    diagnose_agent  CC=4  out:19
    learn_from_incident  CC=11  out:21
    repair_apply  CC=8  out:21
    supervise_with_repair  CC=9  out:23
  packages.resource-agent-hypervisor.hypervisor.repair.validator  [4 funcs]
    read_yaml  CC=2  out:4
    validate_evolution_proposal_dict  CC=1  out:1
    validate_incident_dict  CC=1  out:1
    validate_ticket_dict  CC=1  out:1
  packages.resource-agent-hypervisor.hypervisor.routing.dispatcher  [1 funcs]
    call_uri  CC=6  out:16
  packages.resource-agent-hypervisor.hypervisor.routing.explain  [2 funcs]
    explain_executable_uri  CC=6  out:6
    explain_semantic_route  CC=2  out:2
  packages.resource-agent-hypervisor.hypervisor.routing.models  [2 funcs]
    to_dict  CC=1  out:4
    _public_context  CC=3  out:5
  packages.resource-agent-hypervisor.hypervisor.routing.policy  [4 funcs]
    _semantic_requires_approval  CC=3  out:3
    evaluate_route_policy  CC=13  out:10
    evaluate_route_policy_decision  CC=1  out:2
    policy_options  CC=3  out:1
  packages.resource-agent-hypervisor.hypervisor.routing.registry_bridge  [3 funcs]
    load_runtime_registry  CC=4  out:4
    resolve_operator_by_scheme  CC=7  out:7
    resolve_operator_deployment  CC=5  out:11
  packages.resource-agent-hypervisor.hypervisor.routing.resolver  [5 funcs]
    _normalize_environment  CC=8  out:6
    _operator_base_url  CC=7  out:8
    _payload_session  CC=2  out:2
    _select_environment_and_adapter  CC=11  out:8
    resolve_hypervisor_route  CC=14  out:16
  packages.resource-agent-hypervisor.hypervisor.routing.system_dispatch  [12 funcs]
    _agent_factory_request  CC=1  out:1
    _contract_request  CC=1  out:1
    _file_request  CC=1  out:1
    _health_request  CC=1  out:1
    _hypervisor_agent_request  CC=1  out:1
    _is_hypervisor_agent_request  CC=5  out:2
    _log_request  CC=1  out:1
    _repair_request  CC=1  out:1
    _runtime_request  CC=1  out:1
    _schema_request  CC=1  out:1
  packages.resource-agent-hypervisor.hypervisor.routing.system_handlers  [11 funcs]
    _contract_path_for_agent  CC=4  out:6
    _contract_uri_for_schema  CC=7  out:9
    _read_contract  CC=5  out:6
    handle_agent_factory_uri  CC=6  out:14
    handle_file_uri  CC=1  out:1
    handle_health_uri  CC=1  out:5
    handle_hypervisor_agent_uri  CC=6  out:8
    handle_log_uri  CC=1  out:1
    handle_repair_uri  CC=6  out:8
    handle_runtime_uri  CC=2  out:1
  packages.resource-agent-hypervisor.hypervisor.routing.system_request  [4 funcs]
    bool_param  CC=2  out:2
    int_param  CC=2  out:1
    query_params  CC=3  out:3
    uri_path_parts  CC=4  out:4
  packages.resource-agent-hypervisor.hypervisor.routing.view_handlers  [4 funcs]
    handle_view_uri  CC=5  out:6
    normalize_view_uri  CC=8  out:4
    resolve_view_envelope  CC=13  out:12
    supports_view_uri  CC=4  out:4
  packages.resource-agent-hypervisor.hypervisor.routing.views.process  [4 funcs]
    _human_title  CC=2  out:3
    _process_status_fields  CC=8  out:12
    _related_uris  CC=3  out:4
    build_process_view_data  CC=8  out:17
  packages.resource-agent-hypervisor.hypervisor.uri.client  [2 funcs]
    call  CC=3  out:4
    explain  CC=3  out:4
  packages.resource-agent-hypervisor.hypervisor.verifier.capability_tests  [1 funcs]
    build_capability_test_plan  CC=1  out:1
  packages.resource-agent-hypervisor.meta_agent.cli_commands  [6 funcs]
    cmd_generate  CC=2  out:5
    cmd_pipeline  CC=3  out:5
    cmd_plan  CC=2  out:5
    cmd_repair  CC=2  out:4
    cmd_validate  CC=3  out:5
    cmd_verify  CC=3  out:4
  packages.resource-agent-hypervisor.meta_agent.orchestrator  [4 funcs]
    asdict_result  CC=1  out:0
    pipeline_from_prompt  CC=1  out:2
    save_proposal_from_prompt  CC=2  out:6
    validate_repair_generate  CC=7  out:16
  www.assets.app  [1 funcs]
    handler  CC=1  out:0
  www.landing  [1 funcs]
    open  CC=1  out:0

EDGES:
  generator.validate.validate_agent → generator.model.load_agent_spec
  generator.validate.main → generator.validate.iter_agent_specs
  generator.validate.main → examples.38_autonomous_agents.run.print
  generator.validate.main → generator.validate.validate_agent
  packages.resource-agent-factory.generator.header.contract_source_ref → packages.resource-agent-factory.generator.paths.project_root
  packages.resource-agent-factory.generator.paths.project_root → packages.resource-agent-hypervisor.hypervisor.paths.find_repo_root
  packages.resource-agent-factory.generator.agent_generator._default_port_for_agent → packages.resource-agent-hypervisor.hypervisor.deployment_registry.loader.load_deployment_registry
  packages.resource-agent-factory.generator.agent_generator._default_port_for_agent → packages.resource-agent-hypervisor.hypervisor.deployment_registry.status.infer_port
  packages.resource-agent-factory.generator.agent_generator.generate_agent → generator.validate.validate_agent
  packages.resource-agent-factory.generator.agent_generator.generate_agent → generator.model.load_agent_spec
  packages.resource-agent-factory.generator.agent_generator.generate_agent → generator.hashutil.file_sha256
  packages.resource-agent-factory.generator.agent_generator.generate_agent → packages.resource-agent-factory.generator.header.contract_source_ref
  packages.resource-agent-factory.generator.agent_generator.generate_agent → generator.model.spec_to_plain_dict
  packages.resource-agent-factory.generator.agent_generator.generate_agent → packages.resource-agent-factory.generator.agent_generator._default_port_for_agent
  packages.resource-agent-factory.generator.agent_generator.generate_agent → packages.resource-agent-factory.generator.header.generated_marker_payload
  packages.resource-agent-factory.generator.agent_generator.main → packages.resource-agent-factory.generator.agent_generator.expand_paths
  packages.resource-agent-factory.generator.agent_generator.main → examples.38_autonomous_agents.run.print
  packages.resource-agent-factory.generator.agent_generator.main → packages.resource-agent-factory.generator.agent_generator.generate_agent
  packages.resource-agent-factory.generator.verify.verify_generated_agent → generator.hashutil.file_sha256
  packages.resource-agent-factory.generator.verify.verify_generated → packages.resource-agent-factory.generator.verify._agent_dirs
  packages.resource-agent-factory.generator.verify.verify_generated → packages.resource-agent-factory.generator.verify.verify_generated_agent
  packages.resource-agent-factory.generator.verify.main → packages.resource-agent-factory.generator.verify._agent_dirs
  packages.resource-agent-factory.generator.verify.main → packages.resource-agent-factory.generator.verify.verify_generated
  packages.resource-agent-factory.generator.verify.main → examples.38_autonomous_agents.run.print
  packages.resource-agent-factory.agents.generated.orders_agent.routes.read_resource → packages.resource-agent-factory.agents.generated.orders_agent.routes._uri_allowed
  packages.resource-agent-factory.agents.generated.user_agent.routes.read_resource → packages.resource-agent-factory.agents.generated.user_agent.routes._uri_allowed
  meta_agent.planner.infer_intent → meta_agent.planner.singularize
  meta_agent.planner.intent_to_agent_spec → meta_agent.planner.singularize
  meta_agent.planner.intent_to_agent_spec → meta_agent.planner.package_name
  meta_agent.api.proposal_from_prompt → packages.resource-agent-hypervisor.meta_agent.orchestrator.save_proposal_from_prompt
  meta_agent.api.validate → generator.validate.validate_agent
  meta_agent.api.repair → meta_agent.repair.pipeline.repair_agent_spec
  meta_agent.api.generate → packages.resource-agent-hypervisor.meta_agent.orchestrator.asdict_result
  meta_agent.api.generate → packages.resource-agent-hypervisor.meta_agent.orchestrator.validate_repair_generate
  meta_agent.api.pipeline → packages.resource-agent-hypervisor.meta_agent.orchestrator.pipeline_from_prompt
  meta_agent.api.pipeline → packages.resource-agent-hypervisor.meta_agent.orchestrator.asdict_result
  meta_agent.api.verify → packages.resource-agent-factory.generator.verify.verify_generated
  packages.resource-agent-hypervisor.meta_agent.orchestrator.save_proposal_from_prompt → meta_agent.planner.infer_intent
  packages.resource-agent-hypervisor.meta_agent.orchestrator.save_proposal_from_prompt → meta_agent.planner.intent_to_agent_spec
  packages.resource-agent-hypervisor.meta_agent.orchestrator.save_proposal_from_prompt → meta_agent.planner.package_name
  packages.resource-agent-hypervisor.meta_agent.orchestrator.validate_repair_generate → generator.validate.validate_agent
  packages.resource-agent-hypervisor.meta_agent.orchestrator.validate_repair_generate → meta_agent.repair.pipeline.repair_agent_spec
  packages.resource-agent-hypervisor.meta_agent.orchestrator.validate_repair_generate → packages.resource-agent-factory.generator.agent_generator.generate_agent
  packages.resource-agent-hypervisor.meta_agent.orchestrator.validate_repair_generate → packages.resource-agent-factory.generator.verify.verify_generated_agent
  packages.resource-agent-hypervisor.meta_agent.orchestrator.pipeline_from_prompt → packages.resource-agent-hypervisor.meta_agent.orchestrator.save_proposal_from_prompt
  packages.resource-agent-hypervisor.meta_agent.orchestrator.pipeline_from_prompt → packages.resource-agent-hypervisor.meta_agent.orchestrator.validate_repair_generate
  packages.resource-agent-hypervisor.meta_agent.cli_commands.cmd_plan → packages.resource-agent-hypervisor.meta_agent.orchestrator.save_proposal_from_prompt
  packages.resource-agent-hypervisor.meta_agent.cli_commands.cmd_plan → examples.38_autonomous_agents.run.print
  packages.resource-agent-hypervisor.meta_agent.cli_commands.cmd_validate → generator.validate.validate_agent
  packages.resource-agent-hypervisor.meta_agent.cli_commands.cmd_validate → examples.38_autonomous_agents.run.print
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Api (1)

**`Auto-generated API Smoke Tests`**
- assert `_status < 500`
- assert `_status >= 200`
- detectors: FastAPIDetector, ConfigEndpointDetector

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Intent

WronAI resource agent monorepo — uri3, nl2uri, uri2flow, uri2ops, touri, hypervisor, agent factory

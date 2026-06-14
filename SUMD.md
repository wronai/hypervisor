# Resource Agent System v0.6

WronAI resource agent monorepo — uri3, nl2uri, uri2flow, uri2ops, hypervisor, agent factory

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

- **name**: `resource-agent-system`
- **version**: `0.5.11`
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
  name: resource-agent-system;
  version: 0.5.11;
}

dependencies {
  runtime: "fastapi>=0.115, httpx>=0.27, jinja2>=3.1, jsonschema>=4.23, pydantic>=2.0, python-dotenv>=1.0.0, pyyaml>=6.0, typer>=0.12";
  dev: "pytest>=7.0, pytest-cov>=4.0, pytest-asyncio>=0.21.0, ruff>=0.1.0, mypy>=1.0, build>=1.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60, rich>=13.0.0";
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

workflow[name="uri-tree"] {
  trigger: manual;
  step-1: run cmd=python -m nl2uri.cli --no-llm -p "$(WEATHER_PROMPT)" --out domains/weather_map/uri_tree.yaml;
}

workflow[name="graph"] {
  trigger: manual;
  step-1: run cmd=python -m uri3.cli graph domains/weather_map/uri_tree.yaml;
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
  name: resource-agent-system
  version: 0.5.11
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
fastapi>=0.115
httpx>=0.27
jinja2>=3.1
jsonschema>=4.23
pydantic>=2.0
python-dotenv>=1.0.0
pyyaml>=6.0
typer>=0.12
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
```

## Deployment

```bash markpact:run
pip install resource-agent-system

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
- **version files**: `VERSION`, `pyproject.toml:version`, `packages/uri2ops/uri2ops/__init__.py:__version__`

## Makefile Targets

- `validate`
- `generate`
- `verify`
- `test`
- `uri2flow-test`
- `uri2flow-validate`
- `uri2flow-expand`
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

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# hypervisor | 351f 15897L | python:337,shell:13,less:1 | 2026-06-14
# stats: 772 func | 72 cls | 351 mod | CC̄=3.7 | critical:37 | cycles:0
# alerts[5]: CC default_operation_for_uri=21; CC run_workflow=21; CC classify_output_kind=20; CC test_nl2a_full_pipeline_weather_map=20; CC sanitize_node=16
# hotspots[5]: create_app fan=24; run_workflow fan=23; test_playwright_task_executes_against_local_server fan=21; test_playwright_browser_workflow fan=18; generate_agent fan=17
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[351]:
  agents/__init__.py,1
  agents/custom/__init__.py,1
  agents/generated/__init__.py,1
  agents/generated/user_agent/__init__.py,5
  agents/generated/user_agent/agent_card.py,63
  agents/generated/user_agent/main.py,16
  agents/generated/user_agent/routes.py,91
  agents/generated/user_agent/tests/test_contract.py,18
  agents/generated/weather_map_agent/__init__.py,5
  agents/generated/weather_map_agent/agent_card.py,40
  agents/generated/weather_map_agent/main.py,16
  agents/generated/weather_map_agent/routes.py,85
  agents/generated/weather_map_agent/tests/test_contract.py,18
  app.doql.less,196
  domains/__init__.py,1
  domains/weather_map/__init__.py,1
  domains/weather_map/handlers/__init__.py,1
  domains/weather_map/handlers/generate_weather_map.py,25
  examples/01_quickstart_local/run.sh,8
  examples/10_browser_operator/run.sh,6
  examples/11_playwright_browser/run.sh,86
  examples/12_android_operator/run.sh,9
  examples/13_nl2uri_multi_uri_graph/run.sh,42
  examples/13_pcwin_operator/run.sh,9
  examples/14_uri2ops_serve/run.sh,21
  examples/14_workflow_executor_mock/run.sh,39
  examples/15_compact_uri_flow/run.sh,8
  examples/16_llm_graph_planner/run.sh,18
  packages/nl2uri/nl2a/__init__.py,1
  packages/nl2uri/nl2a/cli.py,26
  packages/nl2uri/nl2uri/__init__.py,1
  packages/nl2uri/nl2uri/cli.py,201
  packages/nl2uri/nl2uri/domain_planner.py,34
  packages/nl2uri/nl2uri/graph_planner.py,319
  packages/nl2uri/nl2uri/graph_planner_llm.py,148
  packages/nl2uri/nl2uri/graph_repair.py,196
  packages/nl2uri/nl2uri/llm_planner.py,9
  packages/nl2uri/nl2uri/output_classifier.py,64
  packages/nl2uri/nl2uri/pipeline.py,142
  packages/nl2uri/nl2uri/planner.py,14
  packages/nl2uri/nl2uri/planner_llm.py,60
  packages/nl2uri/nl2uri/planner_templates.py,103
  packages/nl2uri/nl2uri/planner_validation.py,66
  packages/nl2uri/nl2uri/prompts/__init__.py,1
  packages/nl2uri/nl2uri/writer.py,8
  packages/resource-agent-factory/agents/generated/orders_agent/__init__.py,5
  packages/resource-agent-factory/agents/generated/orders_agent/agent_card.py,37
  packages/resource-agent-factory/agents/generated/orders_agent/main.py,16
  packages/resource-agent-factory/agents/generated/orders_agent/routes.py,85
  packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py,18
  packages/resource-agent-factory/agents/generated/user_agent/__init__.py,5
  packages/resource-agent-factory/agents/generated/user_agent/agent_card.py,63
  packages/resource-agent-factory/agents/generated/user_agent/main.py,16
  packages/resource-agent-factory/agents/generated/user_agent/routes.py,91
  packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py,18
  packages/resource-agent-factory/generator/__init__.py,1
  packages/resource-agent-factory/generator/agent_generator.py,107
  packages/resource-agent-factory/generator/hashutil.py,10
  packages/resource-agent-factory/generator/header.py,52
  packages/resource-agent-factory/generator/model.py,95
  packages/resource-agent-factory/generator/paths.py,13
  packages/resource-agent-factory/generator/validate.py,70
  packages/resource-agent-factory/generator/verify.py,74
  packages/resource-agent-hypervisor/hypervisor/__init__.py,14
  packages/resource-agent-hypervisor/hypervisor/_version.py,21
  packages/resource-agent-hypervisor/hypervisor/cli.py,149
  packages/resource-agent-hypervisor/hypervisor/cli_commands.py,129
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
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/capabilities.py,33
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/proto_index.py,17
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/resources.py,23
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py,37
  packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py,81
  packages/resource-agent-hypervisor/hypervisor/contract_registry/merge_helpers.py,62
  packages/resource-agent-hypervisor/hypervisor/contract_registry/merger.py,27
  packages/resource-agent-hypervisor/hypervisor/contract_registry/models.py,57
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py,61
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/__init__.py,5
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/capabilities.py,41
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/resources.py,27
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_exporter.py,30
  packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py,55
  packages/resource-agent-hypervisor/hypervisor/contract_registry/validate.py,14
  packages/resource-agent-hypervisor/hypervisor/core.py,85
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/__init__.py,60
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/docker_runner.py,77
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/env.py,51
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_config.py,29
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_merge.py,32
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py,167
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py,45
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py,76
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py,51
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/process.py,31
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/remote_runner.py,16
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_plans.py,34
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/runner.py,25
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py,66
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/selector.py,26
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_deploy.py,96
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_helpers.py,15
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_run.py,59
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_verify.py,39
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py,152
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
  packages/resource-agent-hypervisor/hypervisor/domain_pack/pack_writer.py,80
  packages/resource-agent-hypervisor/hypervisor/domain_pack/parser.py,18
  packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py,116
  packages/resource-agent-hypervisor/hypervisor/domain_pack/writer.py,12
  packages/resource-agent-hypervisor/hypervisor/evolution/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/evolution/cli.py,34
  packages/resource-agent-hypervisor/hypervisor/evolution/models.py,33
  packages/resource-agent-hypervisor/hypervisor/evolution/validator.py,17
  packages/resource-agent-hypervisor/hypervisor/paths.py,6
  packages/resource-agent-hypervisor/hypervisor/policy_gate/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py,27
  packages/resource-agent-hypervisor/hypervisor/uri/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/uri/client.py,39
  packages/resource-agent-hypervisor/hypervisor/uri2llm/__init__.py,16
  packages/resource-agent-hypervisor/hypervisor/uri2llm/env_resolver.py,6
  packages/resource-agent-hypervisor/hypervisor/uri2llm/function_resolver.py,6
  packages/resource-agent-hypervisor/hypervisor/uri2llm/llm_resolver.py,6
  packages/resource-agent-hypervisor/hypervisor/uri2llm/protocol_resolver.py,11
  packages/resource-agent-hypervisor/hypervisor/uri2llm/pypi_resolver.py,6
  packages/resource-agent-hypervisor/hypervisor/uri2llm/router.py,6
  packages/resource-agent-hypervisor/hypervisor/verifier/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/verifier/capability_tests.py,33
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
  packages/uri2flow/uri2flow/__init__.py,8
  packages/uri2flow/uri2flow/cli.py,67
  packages/uri2flow/uri2flow/expander.py,82
  packages/uri2flow/uri2flow/models.py,48
  packages/uri2flow/uri2flow/parser.py,91
  packages/uri2flow/uri2flow/resolver.py,67
  packages/uri2flow/uri2flow/utils.py,39
  packages/uri2flow/uri2flow/validator.py,24
  packages/uri2ops/uri2ops/__init__.py,4
  packages/uri2ops/uri2ops/cli.py,136
  packages/uri2ops/uri2ops/operation_registry/__init__.py,1
  packages/uri2ops/uri2ops/operation_registry/dispatcher.py,34
  packages/uri2ops/uri2ops/operation_registry/loader.py,34
  packages/uri2ops/uri2ops/operation_registry/models.py,68
  packages/uri2ops/uri2ops/operation_registry/validator.py,44
  packages/uri2ops/uri2ops/remote_registry/__init__.py,1
  packages/uri2ops/uri2ops/remote_registry/loader.py,131
  packages/uri2ops/uri2ops/schemas/__init__.py,1
  packages/uri2ops/uri2ops/server/__init__.py,1
  packages/uri2ops/uri2ops/server/a2a_wrapper.py,46
  packages/uri2ops/uri2ops/server/app.py,126
  packages/uri2ops/uri2ops/server/mcp_wrapper.py,48
  packages/uri2ops/uri2ops/server/service.py,51
  packages/uri3/domains/weather_map/__init__.py,1
  packages/uri3/domains/weather_map/handlers/__init__.py,1
  packages/uri3/domains/weather_map/handlers/generate_weather_map.py,25
  packages/uri3/uri3/__init__.py,1
  packages/uri3/uri3/cli.py,248
  packages/uri3/uri3/config/__init__.py,13
  packages/uri3/uri3/config/cli_shortcuts.py,42
  packages/uri3/uri3/config/docker_stacks.py,58
  packages/uri3/uri3/config/llm_profile_builder.py,45
  packages/uri3/uri3/config/llm_profiles.py,84
  packages/uri3/uri3/config/repo_root.py,45
  packages/uri3/uri3/config/ssh_auth.py,97
  packages/uri3/uri3/config/uri_yaml.py,90
  packages/uri3/uri3/discovery/__init__.py,1
  packages/uri3/uri3/docker/__init__.py,1
  packages/uri3/uri3/docker/actions/__init__.py,5
  packages/uri3/uri3/docker/actions/compose.py,100
  packages/uri3/uri3/docker/actions/container.py,38
  packages/uri3/uri3/docker/compose_generator.py,47
  packages/uri3/uri3/docker/controller.py,37
  packages/uri3/uri3/docker/runner.py,24
  packages/uri3/uri3/graph/__init__.py,58
  packages/uri3/uri3/graph/adapters/__init__.py,4
  packages/uri3/uri3/graph/adapters/base.py,13
  packages/uri3/uri3/graph/adapters/browser_mock.py,45
  packages/uri3/uri3/graph/adapters/browser_playwright.py,78
  packages/uri3/uri3/graph/adapters/browser_router.py,59
  packages/uri3/uri3/graph/adapters/registry.py,94
  packages/uri3/uri3/graph/artifacts.py,34
  packages/uri3/uri3/graph/conditions.py,25
  packages/uri3/uri3/graph/dependency_graph.py,83
  packages/uri3/uri3/graph/event_log.py,21
  packages/uri3/uri3/graph/execution_models.py,123
  packages/uri3/uri3/graph/graph_executor.py,251
  packages/uri3/uri3/graph/graph_serializer.py,64
  packages/uri3/uri3/graph/graph_validator.py,74
  packages/uri3/uri3/graph/models.py,89
  packages/uri3/uri3/graph/operation_registry.py,72
  packages/uri3/uri3/graph/policy.py,21
  packages/uri3/uri3/graph/uri_graph.py,52
  packages/uri3/uri3/logs/__init__.py,4
  packages/uri3/uri3/logs/filters.py,74
  packages/uri3/uri3/logs/parsing.py,74
  packages/uri3/uri3/logs/reader.py,105
  packages/uri3/uri3/logs/writer.py,35
  packages/uri3/uri3/paths.py,6
  packages/uri3/uri3/protocols/__init__.py,1
  packages/uri3/uri3/protocols/normalizer.py,10
  packages/uri3/uri3/protocols/parser.py,18
  packages/uri3/uri3/protocols/scheme_registry.py,25
  packages/uri3/uri3/protocols/schemes/__init__.py,5
  packages/uri3/uri3/protocols/schemes/a2a.py,16
  packages/uri3/uri3/protocols/schemes/analyze.py,74
  packages/uri3/uri3/protocols/schemes/base.py,68
  packages/uri3/uri3/protocols/schemes/constants.py,28
  packages/uri3/uri3/protocols/schemes/docker.py,44
  packages/uri3/uri3/protocols/schemes/env.py,23
  packages/uri3/uri3/protocols/schemes/http.py,16
  packages/uri3/uri3/protocols/schemes/instance_parser.py,120
  packages/uri3/uri3/protocols/schemes/llm.py,17
  packages/uri3/uri3/protocols/schemes/log.py,77
  packages/uri3/uri3/protocols/schemes/mcp.py,16
  packages/uri3/uri3/protocols/schemes/pypi.py,16
  packages/uri3/uri3/protocols/schemes/python.py,19
  packages/uri3/uri3/protocols/schemes/registry.py,28
  packages/uri3/uri3/protocols/schemes/resource_like.py,17
  packages/uri3/uri3/protocols/schemes/spec_registry.py,100
  packages/uri3/uri3/resolvers/__init__.py,4
  packages/uri3/uri3/resolvers/dispatch.py,68
  packages/uri3/uri3/resolvers/docker_resolver.py,155
  packages/uri3/uri3/resolvers/env_resolver.py,95
  packages/uri3/uri3/resolvers/http_resolver.py,21
  packages/uri3/uri3/resolvers/llm_resolver.py,46
  packages/uri3/uri3/resolvers/log_query.py,56
  packages/uri3/uri3/resolvers/log_resolver.py,86
  packages/uri3/uri3/resolvers/protocol_resolver.py,28
  packages/uri3/uri3/resolvers/pypi_resolver.py,17
  packages/uri3/uri3/resolvers/python_resolver.py,37
  packages/uri3/uri3/resolvers/registry.py,22
  packages/uri3/uri3/resolvers/resolve_core.py,46
  packages/uri3/uri3/resolvers/router.py,29
  packages/uri3/uri3/resolvers/ssh_resolver.py,111
  packages/uri3/uri3/scanner/__init__.py,1
  packages/uri3/uri3/scanner/base.py,8
  packages/uri3/uri3/scanner/docker_scanner.py,92
  packages/uri3/uri3/scanner/http_scanner.py,77
  packages/uri3/uri3/scanner/scanner.py,43
  packages/uri3/uri3/scanner/ssh_scanner.py,91
  packages/uri3/uri3/validators/__init__.py,1
  packages/uri3/uri3/validators/uri_tree_validator.py,21
  packages/uri3/uri3/validators/uri_validator.py,10
  project.sh,59
  testenv/ssh_agent_host/entrypoint.sh,8
  testenv/ssh_agent_host/mock_agent_server.py,58
  tests/__init__.py,1
  tests/domain_pack/__init__.py,2
  tests/domain_pack/test_generator.py,84
  tests/generator/__init__.py,2
  tests/generator/test_headers.py,53
  tests/hypervisor/__init__.py,2
  tests/hypervisor/test_agent_runner.py,64
  tests/hypervisor/test_config.py,82
  tests/hypervisor/test_deployment_registry.py,97
  tests/hypervisor/test_docker_runner.py,22
  tests/hypervisor/test_hypervisor_cli.py,45
  tests/hypervisor/test_remote_runner.py,64
  tests/hypervisor/test_runtime_state.py,51
  tests/integration/__init__.py,2
  tests/integration/test_nl2a_e2e.py,93
  tests/meta_agent/__init__.py,2
  tests/meta_agent/test_repair.py,80
  tests/nl2uri/test_domain_planner.py,32
  tests/nl2uri/test_graph_planner.py,60
  tests/nl2uri/test_graph_planner_llm.py,119
  tests/test_capability_tests.py,11
  tests/test_contract_registry.py,21
  tests/test_cross_validation_v03.py,6
  tests/test_evolution_proposal.py,9
  tests/test_generate.py,11
  tests/test_hypervisor.py,87
  tests/test_meta_agent.py,63
  tests/test_nl2a_v04.py,23
  tests/test_nl2uri.py,10
  tests/test_operation_registry.py,13
  tests/test_operator_task.py,23
  tests/test_policy_gate.py,19
  tests/test_registry_builder_v03.py,21
  tests/test_runtime_client.py,9
  tests/test_schema_validation_v03.py,8
  tests/test_uri2llm_v04.py,22
  tests/test_uri2ops_android.py,72
  tests/test_uri2ops_browser.py,100
  tests/test_uri2ops_pcwin.py,69
  tests/test_uri2ops_serve.py,67
  tests/test_uri2ops_v01.py,64
  tests/test_uri3.py,12
  tests/test_uri_tree_validator.py,5
  tests/test_validate.py,9
  tests/uri2flow/conftest.py,15
  tests/uri2flow/test_cli.py,13
  tests/uri2flow/test_expand_branching_flow.py,14
  tests/uri2flow/test_expand_linear_flow.py,15
  tests/uri2flow/test_parser_forms.py,16
  tests/uri3/__init__.py,2
  tests/uri3/test_browser_adapter.py,109
  tests/uri3/test_cli.py,88
  tests/uri3/test_dispatch.py,23
  tests/uri3/test_docker_control.py,93
  tests/uri3/test_http_scanner.py,43
  tests/uri3/test_llm_profiles.py,34
  tests/uri3/test_log_reader_meta.py,20
  tests/uri3/test_log_uri.py,87
  tests/uri3/test_resolvers.py,107
  tests/uri3/test_router_call.py,20
  tests/uri3/test_schema.py,99
  tests/uri3/test_ssh_auth.py,55
  tests/uri3/test_ssh_scanner.py,65
  tests/uri3/test_uri_yaml.py,27
  tests/uri3/test_workflow_executor.py,96
  tests/uri3/test_workflow_graph.py,53
  tree.sh,2
D:
  agents/__init__.py:
  agents/custom/__init__.py:
  agents/generated/__init__.py:
  agents/generated/user_agent/__init__.py:
  agents/generated/user_agent/agent_card.py:
  agents/generated/user_agent/main.py:
  agents/generated/user_agent/routes.py:
  agents/generated/user_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  agents/generated/weather_map_agent/__init__.py:
  agents/generated/weather_map_agent/agent_card.py:
  agents/generated/weather_map_agent/main.py:
  agents/generated/weather_map_agent/routes.py:
  agents/generated/weather_map_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  domains/__init__.py:
  domains/weather_map/__init__.py:
  domains/weather_map/handlers/__init__.py:
  domains/weather_map/handlers/generate_weather_map.py:
    e: handler
    handler(payload)
  packages/nl2uri/nl2a/__init__.py:
  packages/nl2uri/nl2a/cli.py:
    e: generate,main
    generate(prompt;no_llm;out_dir)
    main()
  packages/nl2uri/nl2uri/__init__.py:
  packages/nl2uri/nl2uri/cli.py:
    e: _default_use_llm,_resolve_use_llm,_emit,_plan_command,plan,classify,single,list_cmd,tree,task,graph,generate,main
    _default_use_llm()
    _resolve_use_llm()
    _emit(payload)
    _plan_command(prompt)
    plan(prompt;json_out;llm;no_llm;validate)
    classify(prompt;json_out)
    single(prompt;json_out;no_llm)
    list_cmd(prompt;json_out;no_llm)
    tree(prompt;out;json_out;no_llm)
    task(prompt;json_out;llm;no_llm;validate;dry_run)
    graph(prompt;json_out;llm;no_llm;validate;dry_run)
    generate(prompt;out;no_llm;json_out)
    main()
  packages/nl2uri/nl2uri/domain_planner.py:
    e: plan_from_prompt
    plan_from_prompt(prompt;use_llm)
  packages/nl2uri/nl2uri/graph_planner.py:
    e: _slug,_detect_agent_id,_detect_health_uri,wrap_nl2uri_output,plan_single,plan_list,plan_tree,plan_task,plan_workflow_graph,plan_auto,plan_by_kind
    _slug(text)
    _detect_agent_id(prompt)
    _detect_health_uri(prompt)
    wrap_nl2uri_output(kind;prompt;body)
    plan_single(prompt)
    plan_list(prompt)
    plan_tree(prompt)
    plan_task(prompt)
    plan_workflow_graph(prompt)
    plan_auto(prompt)
    plan_by_kind(prompt)
  packages/nl2uri/nl2uri/graph_planner_llm.py:
    e: build_graph_planner_system_prompt,call_graph_planner_llm,plan_graph_with_llm
    build_graph_planner_system_prompt()
    call_graph_planner_llm(prompt)
    plan_graph_with_llm(prompt)
  packages/nl2uri/nl2uri/graph_repair.py:
    e: _slug,_coerce_operation,extract_graph_payload,normalize_to_kind,sanitize_node,_sanitize_nodes,repair_graph_body,repair_and_validate_graph
    _slug(text)
    _coerce_operation(scheme;operation)
    extract_graph_payload(raw)
    normalize_to_kind(body)
    sanitize_node(node)
    _sanitize_nodes(nodes)
    repair_graph_body(raw;prompt)
    repair_and_validate_graph(raw;prompt)
  packages/nl2uri/nl2uri/llm_planner.py:
    e: llm_plan
    llm_plan(prompt)
  packages/nl2uri/nl2uri/output_classifier.py:
    e: classify_output_kind
    classify_output_kind(prompt)
  packages/nl2uri/nl2uri/pipeline.py:
    e: generate_tree,_append_pipeline_logs,run_generate_pipeline,run_full_pipeline,PipelineResult,FullPipelineResult
    PipelineResult:
    FullPipelineResult:
    generate_tree(prompt)
    _append_pipeline_logs()
    run_generate_pipeline(prompt)
    run_full_pipeline(prompt)
  packages/nl2uri/nl2uri/planner.py:
    e: rule_based_plan,PlanResult
    PlanResult:
    rule_based_plan(prompt)
  packages/nl2uri/nl2uri/planner_llm.py:
    e: extract_json,call_openrouter
    extract_json(text)
    call_openrouter(prompt)
  packages/nl2uri/nl2uri/planner_templates.py:
    e: slug,llm_uri_from_env,is_weather_prompt,deterministic_weather_plan,generic_plan
    slug(text)
    llm_uri_from_env()
    is_weather_prompt(prompt)
    deterministic_weather_plan(prompt)
    generic_plan(prompt)
  packages/nl2uri/nl2uri/planner_validation.py:
    e: validate_tree_data,is_structured_uri_tree,normalize_llm_tree
    validate_tree_data(tree)
    is_structured_uri_tree(tree)
    normalize_llm_tree(prompt;candidate)
  packages/nl2uri/nl2uri/prompts/__init__.py:
  packages/nl2uri/nl2uri/writer.py:
    e: write_uri_tree
    write_uri_tree(tree;out)
  packages/resource-agent-factory/agents/generated/orders_agent/__init__.py:
  packages/resource-agent-factory/agents/generated/orders_agent/agent_card.py:
  packages/resource-agent-factory/agents/generated/orders_agent/main.py:
  packages/resource-agent-factory/agents/generated/orders_agent/routes.py:
  packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  packages/resource-agent-factory/agents/generated/user_agent/__init__.py:
  packages/resource-agent-factory/agents/generated/user_agent/agent_card.py:
  packages/resource-agent-factory/agents/generated/user_agent/main.py:
  packages/resource-agent-factory/agents/generated/user_agent/routes.py:
  packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py:
    e: test_agent_card_has_expected_name,test_agent_card_has_capabilities,test_agent_card_has_contract_hash
    test_agent_card_has_expected_name()
    test_agent_card_has_capabilities()
    test_agent_card_has_contract_hash()
  packages/resource-agent-factory/generator/__init__.py:
  packages/resource-agent-factory/generator/agent_generator.py:
    e: render_template,generate_agent,expand_paths,main
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
    e: verify_generated_agent,verify_generated,main
    verify_generated_agent(agent_dir)
    verify_generated(root)
    main(argv)
  packages/resource-agent-hypervisor/hypervisor/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/_version.py:
  packages/resource-agent-hypervisor/hypervisor/cli.py:
    e: call,scan,resolve,status,config_cmd,deployments_list,run_agent_cmd,stop_agent_cmd,restart_agent_cmd,agent_status_cmd,logs_cmd,deploy_agent_cmd,verify_agent_cmd,docker_cmd,main
    call(uri)
    scan(uri)
    resolve(uri)
    status()
    config_cmd(path)
    deployments_list()
    run_agent_cmd(selector;port;host;reload;detach;dry_run)
    stop_agent_cmd(selector)
    restart_agent_cmd(selector;port;host;reload;detach)
    agent_status_cmd(selector;no_health)
    logs_cmd(selector;limit)
    deploy_agent_cmd(selector;apply)
    verify_agent_cmd(selector;no_health)
    docker_cmd(uri;dry_run)
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
    e: validate_capability_cross_refs
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
    e: validate_resource_read_capability,validate_command_capability,validate_capabilities
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
  packages/resource-agent-hypervisor/hypervisor/contract_registry/validate.py:
    e: validate_registry
    validate_registry(registry)
  packages/resource-agent-hypervisor/hypervisor/core.py:
    e: Hypervisor
    Hypervisor: __post_init__(0),from_config(2),start(0),stop(0),register_agent(1),status(0),__repr__(0)  # Main Hypervisor controller.
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/__init__.py:
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
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py:
    e: _repo_root,run_agent,stop_agent,restart_agent,agent_status,agent_logs_uri
    _repo_root(root)
    run_agent(selector)
    stop_agent(selector)
    restart_agent(selector)
    agent_status(selector)
    agent_logs_uri(selector)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py:
    e: default_registry_path,_read_yaml,_parse_deployment,load_deployment_registry
    default_registry_path(root)
    _read_yaml(path)
    _parse_deployment(item)
    load_deployment_registry(root)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py:
    e: local_target_to_relative_path,local_target_to_module,build_local_run_plan
    local_target_to_relative_path(target_uri)
    local_target_to_module(target_uri)
    build_local_run_plan(deployment)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py:
    e: AgentDeployment,DeploymentRegistry
    AgentDeployment: to_dict(0)
    DeploymentRegistry: by_id(1),by_agent_ref(1)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/process.py:
    e: start_process
    start_process(plan)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/remote_runner.py:
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_plans.py:
    e: build_run_plan
    build_run_plan(deployment)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/runner.py:
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py:
    e: runtime_root,state_path,load_runtime_state,save_runtime_state,clear_runtime_state,is_process_alive,runtime_status,now_iso
    runtime_root(root)
    state_path(deployment_id;root)
    load_runtime_state(deployment_id;root)
    save_runtime_state(deployment_id;state;root)
    clear_runtime_state(deployment_id;root)
    is_process_alive(pid)
    runtime_status(deployment_id;root)
    now_iso()
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/selector.py:
    e: resolve_deployment
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
    e: build_ssh_run_plan
    build_ssh_run_plan(deployment)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_verify.py:
    e: verify_remote_deployment
    verify_remote_deployment(deployment)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py:
    e: infer_port,deployment_id_for_agent,infer_health_uri,infer_card_uri,deployment_from_uri_tree,sync_from_uri_tree,resolve_status,list_deployments,get_deployment_for_agent,registry_summary
    infer_port(deployment)
    deployment_id_for_agent(agent_id)
    infer_health_uri(target_uri;agent_id)
    infer_card_uri(agent;agent_id)
    deployment_from_uri_tree(tree)
    sync_from_uri_tree(tree)
    resolve_status(deployment)
    list_deployments(registry)
    get_deployment_for_agent(agent_ref)
    registry_summary(registry)
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
  packages/resource-agent-hypervisor/hypervisor/evolution/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/evolution/cli.py:
    e: main
    main(argv)
  packages/resource-agent-hypervisor/hypervisor/evolution/models.py:
    e: load_proposal,EvolutionProposal
    EvolutionProposal:
    load_proposal(path)
  packages/resource-agent-hypervisor/hypervisor/evolution/validator.py:
    e: validate_proposal
    validate_proposal(proposal)
  packages/resource-agent-hypervisor/hypervisor/paths.py:
  packages/resource-agent-hypervisor/hypervisor/policy_gate/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py:
    e: evaluate_change,GateDecision
    GateDecision:
    evaluate_change(change_report;approved)
  packages/resource-agent-hypervisor/hypervisor/uri/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/uri/client.py:
    e: Uri3Client
    Uri3Client: __init__(0),resolve(1),call(2),scan(1),logs(1),schema(1),graph(1),nl2uri(1)  # Thin hypervisor adapter over uri3 routing, scanning and grap
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
    e: default_operation_for_uri,OperationDefaults
    OperationDefaults:
    default_operation_for_uri(uri)
  packages/uri2flow/uri2flow/utils.py:
    e: slugify,scheme_of,path_parts,node_id_from_uri
    slugify(value)
    scheme_of(uri)
    path_parts(uri)
    node_id_from_uri(uri;used)
  packages/uri2flow/uri2flow/validator.py:
    e: validate_flow
    validate_flow(path)
  packages/uri2ops/uri2ops/__init__.py:
  packages/uri2ops/uri2ops/cli.py:
    e: _print,operations_cmd,registry_cmd,validate_cmd,plan_cmd,run_cmd,serve_cmd,main
    _print(data)
    operations_cmd(args)
    registry_cmd(args)
    validate_cmd(args)
    plan_cmd(args)
    run_cmd(args)
    serve_cmd(args)
    main(argv)
  packages/uri2ops/uri2ops/operation_registry/__init__.py:
  packages/uri2ops/uri2ops/operation_registry/dispatcher.py:
    e: _split_python_uri,call_handler,dispatch
    _split_python_uri(uri)
    call_handler(spec;payload;context)
    dispatch(scheme;operation;payload;context)
  packages/uri2ops/uri2ops/operation_registry/loader.py:
    e: default_registry_path,registry_schema_path,load_operation_registry
    default_registry_path()
    registry_schema_path()
    load_operation_registry(path)
  packages/uri2ops/uri2ops/operation_registry/models.py:
    e: OperationSpec,OperationRegistry
    OperationSpec: from_mapping(4),to_dict(0)
    OperationRegistry: get(2),require(2),list(0)
  packages/uri2ops/uri2ops/operation_registry/validator.py:
    e: validate_registry_schema,validate_operation_registry
    validate_registry_schema(data)
    validate_operation_registry(registry)
  packages/uri2ops/uri2ops/remote_registry/__init__.py:
  packages/uri2ops/uri2ops/remote_registry/loader.py:
    e: registry_config_path,load_registry_config,_load_source,merge_registry_documents,registry_from_document,resolve_operation_registry,registry_document,list_remote_sources
    registry_config_path(root)
    load_registry_config(root)
    _load_source(uri_or_path)
    merge_registry_documents()
    registry_from_document(data)
    resolve_operation_registry(path)
    registry_document(registry)
    list_remote_sources(root)
  packages/uri2ops/uri2ops/schemas/__init__.py:
  packages/uri2ops/uri2ops/server/__init__.py:
  packages/uri2ops/uri2ops/server/a2a_wrapper.py:
    e: build_agent_card
    build_agent_card(base_url;registry)
  packages/uri2ops/uri2ops/server/app.py:
    e: create_app,TaskRequest,McpToolCallRequest
    TaskRequest:
    McpToolCallRequest:
    create_app()
  packages/uri2ops/uri2ops/server/mcp_wrapper.py:
    e: list_mcp_tools,mcp_tool_name_for_operation
    list_mcp_tools(registry)
    mcp_tool_name_for_operation(scheme;operation)
  packages/uri2ops/uri2ops/server/service.py:
    e: OperatorService
    OperatorService: __init__(0),registry(0),registry_export(0),list_operations(0),describe_operation(2),list_registry_sources(0),validate_task(1),plan_task(1),run_task(1)
  packages/uri3/domains/weather_map/__init__.py:
  packages/uri3/domains/weather_map/handlers/__init__.py:
  packages/uri3/domains/weather_map/handlers/generate_weather_map.py:
    e: handler
    handler(payload)
  packages/uri3/uri3/__init__.py:
  packages/uri3/uri3/cli.py:
    e: _quick_reference,_list_payload,main,list_cmd,validate,validate_tree,graph,validate_workflow,plan_workflow,run_workflow_cmd,resolve,call,scan,logs,schema,main
    _quick_reference()
    _list_payload()
    main(ctx)
    list_cmd(schemes;json_out)
    validate(uri)
    validate_tree(path)
    graph(path)
    validate_workflow(path)
    plan_workflow(path)
    run_workflow_cmd(path;dry_run;approve;browser)
    resolve(uri)
    call(uri)
    scan(target;all_shortcuts)
    logs(uri;summary)
    schema(target;list_all;analyze)
    main()
  packages/uri3/uri3/config/__init__.py:
  packages/uri3/uri3/config/cli_shortcuts.py:
    e: cli_config_path,load_cli_config,scan_shortcuts,resolve_scan_target,cli_examples
    cli_config_path(root)
    load_cli_config(root)
    scan_shortcuts(root)
    resolve_scan_target(name_or_uri)
    cli_examples(root)
  packages/uri3/uri3/config/docker_stacks.py:
    e: docker_config_path,load_docker_config,resolve_stack,resolve_agent_stack
    docker_config_path(root)
    load_docker_config(root)
    resolve_stack(stack_id)
    resolve_agent_stack(agent_id)
  packages/uri3/uri3/config/llm_profile_builder.py:
    e: parse_llm_query,chosen_profile_name,resolve_profile_api_key,normalize_model_name
    parse_llm_query(model_uri)
    chosen_profile_name(profile_name;defaults)
    resolve_profile_api_key(api_key_uri)
    normalize_model_name(model)
  packages/uri3/uri3/config/llm_profiles.py:
    e: llm_config_path,load_llm_config,resolve_llm_profile,LlmProfile
    LlmProfile: to_dict(0)
    llm_config_path(root)
    load_llm_config(root)
    resolve_llm_profile(profile_name)
  packages/uri3/uri3/config/repo_root.py:
    e: _walk_up,find_repo_root,config_repo_root,repo_root
    _walk_up(start)
    find_repo_root(start)
    config_repo_root(root)
    repo_root()
  packages/uri3/uri3/config/ssh_auth.py:
    e: ssh_config_path,load_ssh_config,_profile_matches,_password_from_env_file,_resolve_password_value,resolve_ssh_password,ssh_auth_hint
    ssh_config_path(root)
    load_ssh_config(root)
    _profile_matches(ref;match)
    _password_from_env_file(root)
    _resolve_password_value(value)
    resolve_ssh_password(ref)
    ssh_auth_hint(ref)
  packages/uri3/uri3/config/uri_yaml.py:
    e: is_uri,load_uri_yaml,resolve_uri_values
    is_uri(value)
    load_uri_yaml(path)
    resolve_uri_values(value)
  packages/uri3/uri3/discovery/__init__.py:
  packages/uri3/uri3/docker/__init__.py:
  packages/uri3/uri3/docker/actions/__init__.py:
  packages/uri3/uri3/docker/actions/compose.py:
    e: compose_base,_parse_ps_stdout,control_compose_ps,control_compose_up,control_compose_down,control_compose_lifecycle,control_compose_logs,control_compose
    compose_base(ref)
    _parse_ps_stdout(stdout)
    control_compose_ps(ref)
    control_compose_up(ref)
    control_compose_down(ref)
    control_compose_lifecycle(ref)
    control_compose_logs(ref)
    control_compose(ref)
  packages/uri3/uri3/docker/actions/container.py:
    e: _container_name,handles_container_action,control_container
    _container_name(ref)
    handles_container_action(ref)
    control_container(ref)
  packages/uri3/uri3/docker/compose_generator.py:
    e: build_generate_plan,write_generated_compose
    build_generate_plan(ref)
    write_generated_compose(ref)
  packages/uri3/uri3/docker/controller.py:
    e: control_docker
    control_docker(uri)
  packages/uri3/uri3/docker/runner.py:
    e: run_command
    run_command(cmd)
  packages/uri3/uri3/graph/__init__.py:
  packages/uri3/uri3/graph/adapters/__init__.py:
  packages/uri3/uri3/graph/adapters/base.py:
    e: StepAdapter
    StepAdapter: execute(2)
  packages/uri3/uri3/graph/adapters/browser_mock.py:
    e: json_dumps,BrowserMockAdapter
    BrowserMockAdapter: execute(2)
    json_dumps(payload)
  packages/uri3/uri3/graph/adapters/browser_playwright.py:
    e: _session_state,close_playwright_session,PlaywrightBrowserAdapter
    PlaywrightBrowserAdapter: execute(2)
    _session_state(context)
    close_playwright_session(context)
  packages/uri3/uri3/graph/adapters/browser_router.py:
    e: _playwright_ready,resolve_browser_mode,cleanup_browser_adapters,BrowserRouterAdapter
    BrowserRouterAdapter: __init__(0),execute(2)
    _playwright_ready()
    resolve_browser_mode(context)
    cleanup_browser_adapters(context)
  packages/uri3/uri3/graph/adapters/registry.py:
    e: adapter_for_uri,AssertionAdapter,HypervisorAdapter
    AssertionAdapter: execute(2)
    HypervisorAdapter: execute(2)
    adapter_for_uri(uri)
  packages/uri3/uri3/graph/artifacts.py:
    e: artifact_path,artifact_uri,write_artifact
    artifact_path(context;step_id;suffix)
    artifact_uri(context;step_id;suffix)
    write_artifact(context;step_id;suffix;content)
  packages/uri3/uri3/graph/conditions.py:
    e: evaluate_condition
    evaluate_condition(condition;context)
  packages/uri3/uri3/graph/dependency_graph.py:
    e: adjacency,reverse_adjacency,detect_cycles,topological_sort,dependency_summary
    adjacency(graph)
    reverse_adjacency(graph)
    detect_cycles(graph)
    topological_sort(graph)
    dependency_summary(graph)
  packages/uri3/uri3/graph/event_log.py:
    e: workflow_event_path,append_workflow_event
    workflow_event_path(workflow_id;root)
    append_workflow_event(workflow_id;event)
  packages/uri3/uri3/graph/execution_models.py:
    e: utc_now_iso,new_execution_context,ExecutionContext,StepExecutionResult,GraphExecutionPlan,GraphExecutionResult
    ExecutionContext: resolve_ref(1)
    StepExecutionResult: to_dict(0)
    GraphExecutionPlan: to_dict(0)
    GraphExecutionResult: to_dict(0)
    utc_now_iso()
    new_execution_context(workflow_id)
  packages/uri3/uri3/graph/graph_executor.py:
    e: build_execution_plan,dry_run_workflow,_dependencies_ok,_execute_step,run_workflow
    build_execution_plan(graph)
    dry_run_workflow(source)
    _dependencies_ok(node;completed)
    _execute_step(node;context)
    run_workflow(source)
  packages/uri3/uri3/graph/graph_serializer.py:
    e: edges_from_depends_on,normalize_graph_payload,task_steps_to_graph,workflow_manifest
    edges_from_depends_on(nodes)
    normalize_graph_payload(data)
    task_steps_to_graph(task;steps)
    workflow_manifest(graph)
  packages/uri3/uri3/graph/graph_validator.py:
    e: _schema_path,load_workflow_graph,validate_workflow_schema,validate_workflow_graph
    _schema_path(name)
    load_workflow_graph(source)
    validate_workflow_schema(graph)
    validate_workflow_graph(source)
  packages/uri3/uri3/graph/models.py:
    e: GraphNode,GraphEdge,WorkflowGraph
    GraphNode: from_dict(2),to_dict(0)
    GraphEdge: to_dict(0)
    WorkflowGraph: add_node(1),to_dict(0)
  packages/uri3/uri3/graph/operation_registry.py:
    e: scheme_from_uri,effective_kind,requires_approval,allowed_operations,validate_node_operation,operation_registry_summary
    scheme_from_uri(uri)
    effective_kind(node)
    requires_approval(node)
    allowed_operations(scheme)
    validate_node_operation(node)
    operation_registry_summary()
  packages/uri3/uri3/graph/policy.py:
    e: can_execute_step
    can_execute_step(node)
  packages/uri3/uri3/graph/uri_graph.py:
    e: build_graph_from_tree,UriNode,UriEdge,UriGraph
    UriNode:
    UriEdge:
    UriGraph: add_node(3),add_edge(3)
    build_graph_from_tree(path)
  packages/uri3/uri3/logs/__init__.py:
  packages/uri3/uri3/logs/filters.py:
    e: level_rank,entry_timestamp,matches_level,matches_logger,matches_grep,matches_time_window,matches_filters
    level_rank(level)
    entry_timestamp(entry)
    matches_level(entry;ref)
    matches_logger(entry;ref)
    matches_grep(entry;ref)
    matches_time_window(entry;since_dt;until_dt)
    matches_filters(entry;ref;since_dt;until_dt)
  packages/uri3/uri3/logs/parsing.py:
    e: empty_entry,parse_json_entry,parse_text_entry,parse_log_line
    empty_entry(line;line_no)
    parse_json_entry(line;line_no)
    parse_text_entry(line;line_no)
    parse_log_line(line;line_no)
  packages/uri3/uri3/logs/reader.py:
    e: resolve_log_path,_parse_since,read_logs,read_logs_result,summarize_logs
    resolve_log_path(ref)
    _parse_since(value)
    read_logs(uri)
    read_logs_result(uri)
    summarize_logs(uri)
  packages/uri3/uri3/logs/writer.py:
    e: append_log
    append_log(stream;message)
  packages/uri3/uri3/paths.py:
  packages/uri3/uri3/protocols/__init__.py:
  packages/uri3/uri3/protocols/normalizer.py:
    e: normalize_uri
    normalize_uri(uri)
  packages/uri3/uri3/protocols/parser.py:
    e: parse_uri,ParsedURI
    ParsedURI:
    parse_uri(uri)
  packages/uri3/uri3/protocols/scheme_registry.py:
  packages/uri3/uri3/protocols/schemes/__init__.py:
  packages/uri3/uri3/protocols/schemes/a2a.py:
    e: spec
    spec()
  packages/uri3/uri3/protocols/schemes/analyze.py:
    e: _analyze_query,analyze_uri,describe_uri
    _analyze_query(uri;spec)
    analyze_uri(uri)
    describe_uri(value)
  packages/uri3/uri3/protocols/schemes/base.py:
    e: QueryOption,SchemeSpec
    QueryOption: to_dict(0)
    SchemeSpec: to_dict(0)
  packages/uri3/uri3/protocols/schemes/constants.py:
  packages/uri3/uri3/protocols/schemes/docker.py:
    e: spec
    spec()
  packages/uri3/uri3/protocols/schemes/env.py:
    e: spec
    spec()
  packages/uri3/uri3/protocols/schemes/http.py:
    e: spec
    spec(scheme)
  packages/uri3/uri3/protocols/schemes/instance_parser.py:
    e: _parse_log,_parse_env,_parse_python,_parse_llm,_parse_pypi,_parse_http,_parse_a2a,_parse_mcp,_parse_docker,_parse_ssh,_parse_resource,parse_instance,normalize_scheme
    _parse_log(uri)
    _parse_env(uri)
    _parse_python(uri)
    _parse_llm(uri)
    _parse_pypi(uri)
    _parse_http(uri)
    _parse_a2a(uri)
    _parse_mcp(uri)
    _parse_docker(uri)
    _parse_ssh(uri)
    _parse_resource(uri)
    parse_instance(scheme;uri)
    normalize_scheme(value)
  packages/uri3/uri3/protocols/schemes/llm.py:
    e: spec
    spec()
  packages/uri3/uri3/protocols/schemes/log.py:
    e: spec
    spec()
  packages/uri3/uri3/protocols/schemes/mcp.py:
    e: spec
    spec()
  packages/uri3/uri3/protocols/schemes/pypi.py:
    e: spec
    spec()
  packages/uri3/uri3/protocols/schemes/python.py:
    e: spec
    spec()
  packages/uri3/uri3/protocols/schemes/registry.py:
  packages/uri3/uri3/protocols/schemes/resource_like.py:
    e: resource_like_spec
    resource_like_spec(scheme;description)
  packages/uri3/uri3/protocols/schemes/spec_registry.py:
    e: build_scheme_registry,is_concrete_uri,get_scheme_schema,list_schemes,query_names
    build_scheme_registry()
    is_concrete_uri(value)
    get_scheme_schema(scheme_or_uri)
    list_schemes()
    query_names(spec)
  packages/uri3/uri3/resolvers/__init__.py:
  packages/uri3/uri3/resolvers/dispatch.py:
    e: _resolve_docker,resolve_target,scheme_from_uri
    _resolve_docker(uri)
    resolve_target(scheme;uri)
    scheme_from_uri(uri)
  packages/uri3/uri3/resolvers/docker_resolver.py:
    e: _first,_bool,_int,parse_docker_uri,resolve_docker,resolve_docker_target,DockerRef
    DockerRef: to_dict(0)
    _first(query;key;default)
    _bool(query;key;default)
    _int(query;key;default)
    parse_docker_uri(uri)
    resolve_docker(uri)
    resolve_docker_target(uri)
  packages/uri3/uri3/resolvers/env_resolver.py:
    e: _env_var_name,resolve_env,_upsert_env_file,_first,call_env,EnvResolver
    EnvResolver: resolve(1),call(2)
    _env_var_name(uri)
    resolve_env(uri)
    _upsert_env_file(path;name;value)
    _first(query;key)
    call_env(uri;payload)
  packages/uri3/uri3/resolvers/http_resolver.py:
    e: HttpResolver
    HttpResolver: resolve(1),fetch(1)
  packages/uri3/uri3/resolvers/llm_resolver.py:
    e: resolve_llm,LLMRef,LLMResolver
    LLMRef:
    LLMResolver: resolve(1)
    resolve_llm(uri)
  packages/uri3/uri3/resolvers/log_query.py:
    e: first,query_int,query_bool,resolve_path,resolve_level,parse_query
    first(query;key;default)
    query_int(query;key;default)
    query_bool(query;key;default)
    resolve_path(parsed)
    resolve_level(query)
    parse_query(uri)
  packages/uri3/uri3/resolvers/log_resolver.py:
    e: parse_log_uri,resolve_log,LogRef,LogResolver
    LogRef: to_dict(0)
    LogResolver: resolve(1),read(1)
    parse_log_uri(uri)
    resolve_log(uri)
  packages/uri3/uri3/resolvers/protocol_resolver.py:
    e: resolve_http_like,resolve_a2a,resolve_mcp,resolve_resource
    resolve_http_like(uri)
    resolve_a2a(uri)
    resolve_mcp(uri)
    resolve_resource(uri)
  packages/uri3/uri3/resolvers/pypi_resolver.py:
    e: resolve_pypi
    resolve_pypi(uri)
  packages/uri3/uri3/resolvers/python_resolver.py:
    e: _split_python_uri,resolve_python,call_python,PythonResolver
    PythonResolver: resolve(1),call(2)
    _split_python_uri(uri)
    resolve_python(uri)
    call_python(uri;payload)
  packages/uri3/uri3/resolvers/registry.py:
    e: build_resolver_registry
    build_resolver_registry()
  packages/uri3/uri3/resolvers/resolve_core.py:
    e: resolve,call,UriResolution
    UriResolution:
    resolve(uri)
    call(uri;payload)
  packages/uri3/uri3/resolvers/router.py:
    e: Uri3Router
    Uri3Router: __init__(0),resolve(1),call(2)
  packages/uri3/uri3/resolvers/ssh_resolver.py:
    e: parse_ssh_uri,_resolve_ssh_password,resolve_ssh,_ssh_options,build_ssh_command,ssh_transport_option,run_ssh
    parse_ssh_uri(uri)
    _resolve_ssh_password(ref)
    resolve_ssh(uri)
    _ssh_options(ref)
    build_ssh_command(ref;remote_command)
    ssh_transport_option(ref)
    run_ssh(ref;remote_command)
  packages/uri3/uri3/scanner/__init__.py:
  packages/uri3/uri3/scanner/base.py:
    e: ScanItem
    ScanItem:
  packages/uri3/uri3/scanner/docker_scanner.py:
    e: _inspect_container,scan_container,_compose_ps,scan_compose_stack,scan_docker
    _inspect_container(name)
    scan_container(uri;ref)
    _compose_ps(ref)
    scan_compose_stack(uri;ref)
    scan_docker(uri)
  packages/uri3/uri3/scanner/http_scanner.py:
    e: _origin,_kind_for_path,_status_for,_probe,health_scan_ok,scan_http
    _origin(url)
    _kind_for_path(path)
    _status_for(kind;status_code)
    _probe(url)
    health_scan_ok(items)
    scan_http(base_url)
  packages/uri3/uri3/scanner/scanner.py:
    e: scan_log,scan
    scan_log(uri)
    scan(uri)
  packages/uri3/uri3/scanner/ssh_scanner.py:
    e: _invalid_ssh_item,_connectivity_item,_remote_item_uri,_remote_path_item,_remote_listing_item,scan_ssh
    _invalid_ssh_item(uri;exc)
    _connectivity_item(uri;ref)
    _remote_item_uri(uri;remote_path)
    _remote_path_item(item_uri;ref)
    _remote_listing_item(item_uri;ref)
    scan_ssh(uri)
  packages/uri3/uri3/validators/__init__.py:
  packages/uri3/uri3/validators/uri_tree_validator.py:
    e: load_yaml,validate_uri_tree
    load_yaml(path)
    validate_uri_tree(path)
  packages/uri3/uri3/validators/uri_validator.py:
    e: validate_uri
    validate_uri(uri)
  testenv/ssh_agent_host/mock_agent_server.py:
    e: Handler
    Handler: _json(2),do_GET(0),log_message(1)
  tests/__init__.py:
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
  tests/generator/__init__.py:
  tests/generator/test_headers.py:
    e: test_generated_python_files_have_standard_header,test_contract_source_ref_is_repo_relative
    test_generated_python_files_have_standard_header(tmp_path;monkeypatch)
    test_contract_source_ref_is_repo_relative()
  tests/hypervisor/__init__.py:
  tests/hypervisor/test_agent_runner.py:
    e: test_local_target_to_module,test_build_run_plan_for_local_deployment,test_build_run_plan_missing_path,test_agent_status_without_health,test_ssh_run_plan_via_build_run_plan,test_ssh_target_cannot_start_without_dry_run
    test_local_target_to_module()
    test_build_run_plan_for_local_deployment()
    test_build_run_plan_missing_path(tmp_path;monkeypatch)
    test_agent_status_without_health()
    test_ssh_run_plan_via_build_run_plan()
    test_ssh_target_cannot_start_without_dry_run()
  tests/hypervisor/test_config.py:
    e: test_default_config_has_structured_sections,test_load_config_merges_user_file,test_env_overrides,test_validate_config_reports_invalid_profile,test_load_hypervisor_config_model,test_load_config_merges_llm_uri_yaml
    test_default_config_has_structured_sections()
    test_load_config_merges_user_file(tmp_path)
    test_env_overrides(monkeypatch)
    test_validate_config_reports_invalid_profile()
    test_load_hypervisor_config_model()
    test_load_config_merges_llm_uri_yaml()
  tests/hypervisor/test_deployment_registry.py:
    e: test_load_default_deployments,test_deployment_from_weather_uri_tree,test_sync_from_uri_tree_writes_registry,test_upsert_replaces_existing_deployment,test_resolve_status_without_health_check,test_registry_summary,test_ssh_target_uri_supported_in_model
    test_load_default_deployments()
    test_deployment_from_weather_uri_tree()
    test_sync_from_uri_tree_writes_registry(tmp_path)
    test_upsert_replaces_existing_deployment(tmp_path)
    test_resolve_status_without_health_check()
    test_registry_summary()
    test_ssh_target_uri_supported_in_model(tmp_path)
  tests/hypervisor/test_docker_runner.py:
    e: test_build_docker_deploy_plan,test_build_docker_control_plan_up
    test_build_docker_deploy_plan()
    test_build_docker_control_plan_up()
  tests/hypervisor/test_hypervisor_cli.py:
    e: test_cli_deployments_and_run_agent_dry_run,test_cli_ssh_run_agent_dry_run,test_cli_deploy_agent_dry_run,test_cli_agent_status_includes_runtime_fields
    test_cli_deployments_and_run_agent_dry_run(capsys)
    test_cli_ssh_run_agent_dry_run(capsys)
    test_cli_deploy_agent_dry_run(capsys)
    test_cli_agent_status_includes_runtime_fields(capsys)
  tests/hypervisor/test_remote_runner.py:
    e: test_build_ssh_deploy_plan,test_build_ssh_run_plan_dry_run,test_build_run_plan_ssh_delegates,test_verify_remote_deployment
    test_build_ssh_deploy_plan()
    test_build_ssh_run_plan_dry_run()
    test_build_run_plan_ssh_delegates()
    test_verify_remote_deployment(monkeypatch)
  tests/hypervisor/test_runtime_state.py:
    e: test_build_run_plan_includes_env_and_runtime_paths,test_resolve_deployment_env_merges_uri_yaml,test_runtime_state_roundtrip
    test_build_run_plan_includes_env_and_runtime_paths()
    test_resolve_deployment_env_merges_uri_yaml(tmp_path;monkeypatch)
    test_runtime_state_roundtrip(tmp_path)
  tests/integration/__init__.py:
  tests/integration/test_nl2a_e2e.py:
    e: isolated_project,test_nl2a_full_pipeline_weather_map,test_nl2a_cli_generate_no_llm
    isolated_project(tmp_path;monkeypatch)
    test_nl2a_full_pipeline_weather_map(isolated_project)
    test_nl2a_cli_generate_no_llm(isolated_project)
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
  tests/nl2uri/test_graph_planner.py:
    e: test_classify_resource_tree,test_classify_task_graph,test_classify_workflow_graph,test_plan_single_status,test_plan_list_health_and_card,test_plan_tree_contains_domain_root,test_plan_task_linear_steps,test_plan_workflow_generate_run_check,test_plan_auto_matches_classifier
    test_classify_resource_tree()
    test_classify_task_graph()
    test_classify_workflow_graph()
    test_plan_single_status()
    test_plan_list_health_and_card()
    test_plan_tree_contains_domain_root()
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
  tests/test_nl2a_v04.py:
    e: test_weather_prompt_generates_uri_tree,test_domain_pack_generation
    test_weather_prompt_generates_uri_tree()
    test_domain_pack_generation(tmp_path)
  tests/test_nl2uri.py:
    e: test_weather_prompt_generates_weather_uri_tree
    test_weather_prompt_generates_weather_uri_tree()
  tests/test_operation_registry.py:
    e: test_registry_loads,test_registry_validates
    test_registry_loads()
    test_registry_validates()
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
  tests/test_uri2ops_android.py:
    e: test_parse_android_uri,test_resolve_adapter_mode_mock,test_resolve_adapter_mode_auto_without_adb,test_android_mock_task,test_android_tap_blocked_without_approve,test_android_adb_task_when_device_present
    test_parse_android_uri()
    test_resolve_adapter_mode_mock()
    test_resolve_adapter_mode_auto_without_adb(monkeypatch)
    test_android_mock_task(tmp_path)
    test_android_tap_blocked_without_approve(tmp_path)
    test_android_adb_task_when_device_present(tmp_path)
  tests/test_uri2ops_browser.py:
    e: test_resolve_adapter_mode_mock,test_resolve_adapter_mode_auto_falls_back_without_playwright,test_mock_task_writes_artifacts,test_playwright_task_executes_against_local_server
    test_resolve_adapter_mode_mock()
    test_resolve_adapter_mode_auto_falls_back_without_playwright(monkeypatch)
    test_mock_task_writes_artifacts(tmp_path)
    test_playwright_task_executes_against_local_server(tmp_path)
  tests/test_uri2ops_pcwin.py:
    e: test_parse_pcwin_window_uri,test_parse_pcwin_control_uri,test_parse_pcwin_path_only_form,test_resolve_adapter_mode_mock,test_resolve_adapter_mode_auto_on_linux,test_pcwin_mock_task,test_pcwin_blocked_without_approve,test_pcwin_uia_available_only_on_windows
    test_parse_pcwin_window_uri()
    test_parse_pcwin_control_uri()
    test_parse_pcwin_path_only_form()
    test_resolve_adapter_mode_mock()
    test_resolve_adapter_mode_auto_on_linux()
    test_pcwin_mock_task(tmp_path)
    test_pcwin_blocked_without_approve(tmp_path)
    test_pcwin_uia_available_only_on_windows()
  tests/test_uri2ops_serve.py:
    e: test_merge_remote_registry_adds_browser_wait,test_serve_health_and_registry_export,test_serve_agent_card_and_mcp_tools,test_serve_run_task_via_a2a,test_serve_mcp_run_operator_task,test_merge_registry_documents_overlays_operations
    test_merge_remote_registry_adds_browser_wait()
    test_serve_health_and_registry_export()
    test_serve_agent_card_and_mcp_tools()
    test_serve_run_task_via_a2a()
    test_serve_mcp_run_operator_task()
    test_merge_registry_documents_overlays_operations()
  tests/test_uri2ops_v01.py:
    e: test_redact_secret_payload_field,test_registry_schema_validates_yaml,test_artifact_resolver_reads_written_file,test_policy_blocks_command_without_approve,test_policy_allows_dry_run_without_approve,test_task_blocks_without_approve
    test_redact_secret_payload_field()
    test_registry_schema_validates_yaml()
    test_artifact_resolver_reads_written_file(tmp_path)
    test_policy_blocks_command_without_approve()
    test_policy_allows_dry_run_without_approve()
    test_task_blocks_without_approve(tmp_path)
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
  tests/uri2flow/test_parser_forms.py:
    e: test_accepts_string_and_mapping_forms
    test_accepts_string_and_mapping_forms()
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
  tests/uri3/test_http_scanner.py:
    e: test_scan_http_health_uri_does_not_double_path,test_scan_http_404_health_is_error,test_health_scan_ok_requires_200
    test_scan_http_health_uri_does_not_double_path(monkeypatch)
    test_scan_http_404_health_is_error(monkeypatch)
    test_health_scan_ok_requires_200()
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
    e: test_is_uri,test_load_llm_uri_yaml,test_resolve_uri_values_keeps_secrets_by_default
    test_is_uri()
    test_load_llm_uri_yaml()
    test_resolve_uri_values_keeps_secrets_by_default()
  tests/uri3/test_workflow_executor.py:
    e: test_run_workflow_dry_run_completes,test_run_workflow_blocks_command_without_approve,test_run_workflow_execute_mock_with_approve,test_run_workflow_accepts_workflow_graph_object,test_run_workflow_skips_conditional_branch
    test_run_workflow_dry_run_completes()
    test_run_workflow_blocks_command_without_approve()
    test_run_workflow_execute_mock_with_approve(tmp_path)
    test_run_workflow_accepts_workflow_graph_object(tmp_path)
    test_run_workflow_skips_conditional_branch(tmp_path)
  tests/uri3/test_workflow_graph.py:
    e: test_load_task_payload,test_validate_task_payload,test_execution_plan_order,test_detect_cycle
    test_load_task_payload()
    test_validate_task_payload()
    test_execution_plan_order()
    test_detect_cycle()
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('hypervisor', '0.5.11', 'python').

% ── Project Files ────────────────────────────────────────
project_file('agents/__init__.py', 1, 'python').
project_file('agents/custom/__init__.py', 1, 'python').
project_file('agents/generated/__init__.py', 1, 'python').
project_file('agents/generated/user_agent/__init__.py', 5, 'python').
project_file('agents/generated/user_agent/agent_card.py', 63, 'python').
project_file('agents/generated/user_agent/main.py', 16, 'python').
project_file('agents/generated/user_agent/routes.py', 91, 'python').
project_file('agents/generated/user_agent/tests/test_contract.py', 18, 'python').
project_file('agents/generated/weather_map_agent/__init__.py', 5, 'python').
project_file('agents/generated/weather_map_agent/agent_card.py', 40, 'python').
project_file('agents/generated/weather_map_agent/main.py', 16, 'python').
project_file('agents/generated/weather_map_agent/routes.py', 85, 'python').
project_file('agents/generated/weather_map_agent/tests/test_contract.py', 18, 'python').
project_file('app.doql.less', 196, 'less').
project_file('domains/__init__.py', 1, 'python').
project_file('domains/weather_map/__init__.py', 1, 'python').
project_file('domains/weather_map/handlers/__init__.py', 1, 'python').
project_file('domains/weather_map/handlers/generate_weather_map.py', 25, 'python').
project_file('examples/01_quickstart_local/run.sh', 8, 'shell').
project_file('examples/10_browser_operator/run.sh', 6, 'shell').
project_file('examples/11_playwright_browser/run.sh', 86, 'shell').
project_file('examples/12_android_operator/run.sh', 9, 'shell').
project_file('examples/13_nl2uri_multi_uri_graph/run.sh', 42, 'shell').
project_file('examples/13_pcwin_operator/run.sh', 9, 'shell').
project_file('examples/14_uri2ops_serve/run.sh', 21, 'shell').
project_file('examples/14_workflow_executor_mock/run.sh', 39, 'shell').
project_file('examples/15_compact_uri_flow/run.sh', 8, 'shell').
project_file('examples/16_llm_graph_planner/run.sh', 18, 'shell').
project_file('packages/nl2uri/nl2a/__init__.py', 1, 'python').
project_file('packages/nl2uri/nl2a/cli.py', 26, 'python').
project_file('packages/nl2uri/nl2uri/__init__.py', 1, 'python').
project_file('packages/nl2uri/nl2uri/cli.py', 201, 'python').
project_file('packages/nl2uri/nl2uri/domain_planner.py', 34, 'python').
project_file('packages/nl2uri/nl2uri/graph_planner.py', 319, 'python').
project_file('packages/nl2uri/nl2uri/graph_planner_llm.py', 148, 'python').
project_file('packages/nl2uri/nl2uri/graph_repair.py', 196, 'python').
project_file('packages/nl2uri/nl2uri/llm_planner.py', 9, 'python').
project_file('packages/nl2uri/nl2uri/output_classifier.py', 64, 'python').
project_file('packages/nl2uri/nl2uri/pipeline.py', 142, 'python').
project_file('packages/nl2uri/nl2uri/planner.py', 14, 'python').
project_file('packages/nl2uri/nl2uri/planner_llm.py', 60, 'python').
project_file('packages/nl2uri/nl2uri/planner_templates.py', 103, 'python').
project_file('packages/nl2uri/nl2uri/planner_validation.py', 66, 'python').
project_file('packages/nl2uri/nl2uri/prompts/__init__.py', 1, 'python').
project_file('packages/nl2uri/nl2uri/writer.py', 8, 'python').
project_file('packages/resource-agent-factory/agents/generated/orders_agent/__init__.py', 5, 'python').
project_file('packages/resource-agent-factory/agents/generated/orders_agent/agent_card.py', 37, 'python').
project_file('packages/resource-agent-factory/agents/generated/orders_agent/main.py', 16, 'python').
project_file('packages/resource-agent-factory/agents/generated/orders_agent/routes.py', 85, 'python').
project_file('packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py', 18, 'python').
project_file('packages/resource-agent-factory/agents/generated/user_agent/__init__.py', 5, 'python').
project_file('packages/resource-agent-factory/agents/generated/user_agent/agent_card.py', 63, 'python').
project_file('packages/resource-agent-factory/agents/generated/user_agent/main.py', 16, 'python').
project_file('packages/resource-agent-factory/agents/generated/user_agent/routes.py', 91, 'python').
project_file('packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py', 18, 'python').
project_file('packages/resource-agent-factory/generator/__init__.py', 1, 'python').
project_file('packages/resource-agent-factory/generator/agent_generator.py', 107, 'python').
project_file('packages/resource-agent-factory/generator/hashutil.py', 10, 'python').
project_file('packages/resource-agent-factory/generator/header.py', 52, 'python').
project_file('packages/resource-agent-factory/generator/model.py', 95, 'python').
project_file('packages/resource-agent-factory/generator/paths.py', 13, 'python').
project_file('packages/resource-agent-factory/generator/validate.py', 70, 'python').
project_file('packages/resource-agent-factory/generator/verify.py', 74, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/__init__.py', 14, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/_version.py', 21, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/cli.py', 149, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 129, 'python').
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
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/capabilities.py', 33, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/proto_index.py', 17, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/resources.py', 23, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py', 37, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py', 81, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/merge_helpers.py', 62, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/merger.py', 27, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/models.py', 57, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py', 61, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/__init__.py', 5, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/capabilities.py', 41, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/resources.py', 27, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_exporter.py', 30, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', 55, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/validate.py', 14, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/core.py', 85, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/__init__.py', 60, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/docker_runner.py', 77, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env.py', 51, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_config.py', 29, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/env_merge.py', 32, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', 167, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', 45, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', 76, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', 51, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process.py', 31, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/remote_runner.py', 16, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_plans.py', 34, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runner.py', 25, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 66, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/selector.py', 26, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_deploy.py', 96, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_helpers.py', 15, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_run.py', 59, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_verify.py', 39, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 152, 'python').
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
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/pack_writer.py', 80, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/parser.py', 18, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 116, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/writer.py', 12, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/cli.py', 34, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/models.py', 33, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/validator.py', 17, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/paths.py', 6, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/policy_gate/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py', 27, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri/client.py', 39, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/__init__.py', 16, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/env_resolver.py', 6, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/function_resolver.py', 6, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/llm_resolver.py', 6, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/protocol_resolver.py', 11, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/pypi_resolver.py', 6, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri2llm/router.py', 6, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/verifier/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/verifier/capability_tests.py', 33, 'python').
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
project_file('packages/uri2flow/uri2flow/__init__.py', 8, 'python').
project_file('packages/uri2flow/uri2flow/cli.py', 67, 'python').
project_file('packages/uri2flow/uri2flow/expander.py', 82, 'python').
project_file('packages/uri2flow/uri2flow/models.py', 48, 'python').
project_file('packages/uri2flow/uri2flow/parser.py', 91, 'python').
project_file('packages/uri2flow/uri2flow/resolver.py', 67, 'python').
project_file('packages/uri2flow/uri2flow/utils.py', 39, 'python').
project_file('packages/uri2flow/uri2flow/validator.py', 24, 'python').
project_file('packages/uri2ops/uri2ops/__init__.py', 4, 'python').
project_file('packages/uri2ops/uri2ops/cli.py', 136, 'python').
project_file('packages/uri2ops/uri2ops/operation_registry/__init__.py', 1, 'python').
project_file('packages/uri2ops/uri2ops/operation_registry/dispatcher.py', 34, 'python').
project_file('packages/uri2ops/uri2ops/operation_registry/loader.py', 34, 'python').
project_file('packages/uri2ops/uri2ops/operation_registry/models.py', 68, 'python').
project_file('packages/uri2ops/uri2ops/operation_registry/validator.py', 44, 'python').
project_file('packages/uri2ops/uri2ops/remote_registry/__init__.py', 1, 'python').
project_file('packages/uri2ops/uri2ops/remote_registry/loader.py', 131, 'python').
project_file('packages/uri2ops/uri2ops/schemas/__init__.py', 1, 'python').
project_file('packages/uri2ops/uri2ops/server/__init__.py', 1, 'python').
project_file('packages/uri2ops/uri2ops/server/a2a_wrapper.py', 46, 'python').
project_file('packages/uri2ops/uri2ops/server/app.py', 126, 'python').
project_file('packages/uri2ops/uri2ops/server/mcp_wrapper.py', 48, 'python').
project_file('packages/uri2ops/uri2ops/server/service.py', 51, 'python').
project_file('packages/uri3/domains/weather_map/__init__.py', 1, 'python').
project_file('packages/uri3/domains/weather_map/handlers/__init__.py', 1, 'python').
project_file('packages/uri3/domains/weather_map/handlers/generate_weather_map.py', 25, 'python').
project_file('packages/uri3/uri3/__init__.py', 1, 'python').
project_file('packages/uri3/uri3/cli.py', 248, 'python').
project_file('packages/uri3/uri3/config/__init__.py', 13, 'python').
project_file('packages/uri3/uri3/config/cli_shortcuts.py', 42, 'python').
project_file('packages/uri3/uri3/config/docker_stacks.py', 58, 'python').
project_file('packages/uri3/uri3/config/llm_profile_builder.py', 45, 'python').
project_file('packages/uri3/uri3/config/llm_profiles.py', 84, 'python').
project_file('packages/uri3/uri3/config/repo_root.py', 45, 'python').
project_file('packages/uri3/uri3/config/ssh_auth.py', 97, 'python').
project_file('packages/uri3/uri3/config/uri_yaml.py', 90, 'python').
project_file('packages/uri3/uri3/discovery/__init__.py', 1, 'python').
project_file('packages/uri3/uri3/docker/__init__.py', 1, 'python').
project_file('packages/uri3/uri3/docker/actions/__init__.py', 5, 'python').
project_file('packages/uri3/uri3/docker/actions/compose.py', 100, 'python').
project_file('packages/uri3/uri3/docker/actions/container.py', 38, 'python').
project_file('packages/uri3/uri3/docker/compose_generator.py', 47, 'python').
project_file('packages/uri3/uri3/docker/controller.py', 37, 'python').
project_file('packages/uri3/uri3/docker/runner.py', 24, 'python').
project_file('packages/uri3/uri3/graph/__init__.py', 58, 'python').
project_file('packages/uri3/uri3/graph/adapters/__init__.py', 4, 'python').
project_file('packages/uri3/uri3/graph/adapters/base.py', 13, 'python').
project_file('packages/uri3/uri3/graph/adapters/browser_mock.py', 45, 'python').
project_file('packages/uri3/uri3/graph/adapters/browser_playwright.py', 78, 'python').
project_file('packages/uri3/uri3/graph/adapters/browser_router.py', 59, 'python').
project_file('packages/uri3/uri3/graph/adapters/registry.py', 94, 'python').
project_file('packages/uri3/uri3/graph/artifacts.py', 34, 'python').
project_file('packages/uri3/uri3/graph/conditions.py', 25, 'python').
project_file('packages/uri3/uri3/graph/dependency_graph.py', 83, 'python').
project_file('packages/uri3/uri3/graph/event_log.py', 21, 'python').
project_file('packages/uri3/uri3/graph/execution_models.py', 123, 'python').
project_file('packages/uri3/uri3/graph/graph_executor.py', 251, 'python').
project_file('packages/uri3/uri3/graph/graph_serializer.py', 64, 'python').
project_file('packages/uri3/uri3/graph/graph_validator.py', 74, 'python').
project_file('packages/uri3/uri3/graph/models.py', 89, 'python').
project_file('packages/uri3/uri3/graph/operation_registry.py', 72, 'python').
project_file('packages/uri3/uri3/graph/policy.py', 21, 'python').
project_file('packages/uri3/uri3/graph/uri_graph.py', 52, 'python').
project_file('packages/uri3/uri3/logs/__init__.py', 4, 'python').
project_file('packages/uri3/uri3/logs/filters.py', 74, 'python').
project_file('packages/uri3/uri3/logs/parsing.py', 74, 'python').
project_file('packages/uri3/uri3/logs/reader.py', 105, 'python').
project_file('packages/uri3/uri3/logs/writer.py', 35, 'python').
project_file('packages/uri3/uri3/paths.py', 6, 'python').
project_file('packages/uri3/uri3/protocols/__init__.py', 1, 'python').
project_file('packages/uri3/uri3/protocols/normalizer.py', 10, 'python').
project_file('packages/uri3/uri3/protocols/parser.py', 18, 'python').
project_file('packages/uri3/uri3/protocols/scheme_registry.py', 25, 'python').
project_file('packages/uri3/uri3/protocols/schemes/__init__.py', 5, 'python').
project_file('packages/uri3/uri3/protocols/schemes/a2a.py', 16, 'python').
project_file('packages/uri3/uri3/protocols/schemes/analyze.py', 74, 'python').
project_file('packages/uri3/uri3/protocols/schemes/base.py', 68, 'python').
project_file('packages/uri3/uri3/protocols/schemes/constants.py', 28, 'python').
project_file('packages/uri3/uri3/protocols/schemes/docker.py', 44, 'python').
project_file('packages/uri3/uri3/protocols/schemes/env.py', 23, 'python').
project_file('packages/uri3/uri3/protocols/schemes/http.py', 16, 'python').
project_file('packages/uri3/uri3/protocols/schemes/instance_parser.py', 120, 'python').
project_file('packages/uri3/uri3/protocols/schemes/llm.py', 17, 'python').
project_file('packages/uri3/uri3/protocols/schemes/log.py', 77, 'python').
project_file('packages/uri3/uri3/protocols/schemes/mcp.py', 16, 'python').
project_file('packages/uri3/uri3/protocols/schemes/pypi.py', 16, 'python').
project_file('packages/uri3/uri3/protocols/schemes/python.py', 19, 'python').
project_file('packages/uri3/uri3/protocols/schemes/registry.py', 28, 'python').
project_file('packages/uri3/uri3/protocols/schemes/resource_like.py', 17, 'python').
project_file('packages/uri3/uri3/protocols/schemes/spec_registry.py', 100, 'python').
project_file('packages/uri3/uri3/resolvers/__init__.py', 4, 'python').
project_file('packages/uri3/uri3/resolvers/dispatch.py', 68, 'python').
project_file('packages/uri3/uri3/resolvers/docker_resolver.py', 155, 'python').
project_file('packages/uri3/uri3/resolvers/env_resolver.py', 95, 'python').
project_file('packages/uri3/uri3/resolvers/http_resolver.py', 21, 'python').
project_file('packages/uri3/uri3/resolvers/llm_resolver.py', 46, 'python').
project_file('packages/uri3/uri3/resolvers/log_query.py', 56, 'python').
project_file('packages/uri3/uri3/resolvers/log_resolver.py', 86, 'python').
project_file('packages/uri3/uri3/resolvers/protocol_resolver.py', 28, 'python').
project_file('packages/uri3/uri3/resolvers/pypi_resolver.py', 17, 'python').
project_file('packages/uri3/uri3/resolvers/python_resolver.py', 37, 'python').
project_file('packages/uri3/uri3/resolvers/registry.py', 22, 'python').
project_file('packages/uri3/uri3/resolvers/resolve_core.py', 46, 'python').
project_file('packages/uri3/uri3/resolvers/router.py', 29, 'python').
project_file('packages/uri3/uri3/resolvers/ssh_resolver.py', 111, 'python').
project_file('packages/uri3/uri3/scanner/__init__.py', 1, 'python').
project_file('packages/uri3/uri3/scanner/base.py', 8, 'python').
project_file('packages/uri3/uri3/scanner/docker_scanner.py', 92, 'python').
project_file('packages/uri3/uri3/scanner/http_scanner.py', 77, 'python').
project_file('packages/uri3/uri3/scanner/scanner.py', 43, 'python').
project_file('packages/uri3/uri3/scanner/ssh_scanner.py', 91, 'python').
project_file('packages/uri3/uri3/validators/__init__.py', 1, 'python').
project_file('packages/uri3/uri3/validators/uri_tree_validator.py', 21, 'python').
project_file('packages/uri3/uri3/validators/uri_validator.py', 10, 'python').
project_file('project.sh', 59, 'shell').
project_file('testenv/ssh_agent_host/entrypoint.sh', 8, 'shell').
project_file('testenv/ssh_agent_host/mock_agent_server.py', 58, 'python').
project_file('tests/__init__.py', 1, 'python').
project_file('tests/domain_pack/__init__.py', 2, 'python').
project_file('tests/domain_pack/test_generator.py', 84, 'python').
project_file('tests/generator/__init__.py', 2, 'python').
project_file('tests/generator/test_headers.py', 53, 'python').
project_file('tests/hypervisor/__init__.py', 2, 'python').
project_file('tests/hypervisor/test_agent_runner.py', 64, 'python').
project_file('tests/hypervisor/test_config.py', 82, 'python').
project_file('tests/hypervisor/test_deployment_registry.py', 97, 'python').
project_file('tests/hypervisor/test_docker_runner.py', 22, 'python').
project_file('tests/hypervisor/test_hypervisor_cli.py', 45, 'python').
project_file('tests/hypervisor/test_remote_runner.py', 64, 'python').
project_file('tests/hypervisor/test_runtime_state.py', 51, 'python').
project_file('tests/integration/__init__.py', 2, 'python').
project_file('tests/integration/test_nl2a_e2e.py', 93, 'python').
project_file('tests/meta_agent/__init__.py', 2, 'python').
project_file('tests/meta_agent/test_repair.py', 80, 'python').
project_file('tests/nl2uri/test_domain_planner.py', 32, 'python').
project_file('tests/nl2uri/test_graph_planner.py', 60, 'python').
project_file('tests/nl2uri/test_graph_planner_llm.py', 119, 'python').
project_file('tests/test_capability_tests.py', 11, 'python').
project_file('tests/test_contract_registry.py', 21, 'python').
project_file('tests/test_cross_validation_v03.py', 6, 'python').
project_file('tests/test_evolution_proposal.py', 9, 'python').
project_file('tests/test_generate.py', 11, 'python').
project_file('tests/test_hypervisor.py', 87, 'python').
project_file('tests/test_meta_agent.py', 63, 'python').
project_file('tests/test_nl2a_v04.py', 23, 'python').
project_file('tests/test_nl2uri.py', 10, 'python').
project_file('tests/test_operation_registry.py', 13, 'python').
project_file('tests/test_operator_task.py', 23, 'python').
project_file('tests/test_policy_gate.py', 19, 'python').
project_file('tests/test_registry_builder_v03.py', 21, 'python').
project_file('tests/test_runtime_client.py', 9, 'python').
project_file('tests/test_schema_validation_v03.py', 8, 'python').
project_file('tests/test_uri2llm_v04.py', 22, 'python').
project_file('tests/test_uri2ops_android.py', 72, 'python').
project_file('tests/test_uri2ops_browser.py', 100, 'python').
project_file('tests/test_uri2ops_pcwin.py', 69, 'python').
project_file('tests/test_uri2ops_serve.py', 67, 'python').
project_file('tests/test_uri2ops_v01.py', 64, 'python').
project_file('tests/test_uri3.py', 12, 'python').
project_file('tests/test_uri_tree_validator.py', 5, 'python').
project_file('tests/test_validate.py', 9, 'python').
project_file('tests/uri2flow/conftest.py', 15, 'python').
project_file('tests/uri2flow/test_cli.py', 13, 'python').
project_file('tests/uri2flow/test_expand_branching_flow.py', 14, 'python').
project_file('tests/uri2flow/test_expand_linear_flow.py', 15, 'python').
project_file('tests/uri2flow/test_parser_forms.py', 16, 'python').
project_file('tests/uri3/__init__.py', 2, 'python').
project_file('tests/uri3/test_browser_adapter.py', 109, 'python').
project_file('tests/uri3/test_cli.py', 88, 'python').
project_file('tests/uri3/test_dispatch.py', 23, 'python').
project_file('tests/uri3/test_docker_control.py', 93, 'python').
project_file('tests/uri3/test_http_scanner.py', 43, 'python').
project_file('tests/uri3/test_llm_profiles.py', 34, 'python').
project_file('tests/uri3/test_log_reader_meta.py', 20, 'python').
project_file('tests/uri3/test_log_uri.py', 87, 'python').
project_file('tests/uri3/test_resolvers.py', 107, 'python').
project_file('tests/uri3/test_router_call.py', 20, 'python').
project_file('tests/uri3/test_schema.py', 99, 'python').
project_file('tests/uri3/test_ssh_auth.py', 55, 'python').
project_file('tests/uri3/test_ssh_scanner.py', 65, 'python').
project_file('tests/uri3/test_uri_yaml.py', 27, 'python').
project_file('tests/uri3/test_workflow_executor.py', 96, 'python').
project_file('tests/uri3/test_workflow_graph.py', 53, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/weather_map_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/weather_map_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/weather_map_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('domains/weather_map/handlers/generate_weather_map.py', 'handler', 1, 3, 7).
python_function('packages/nl2uri/nl2a/cli.py', 'generate', 3, 1, 5).
python_function('packages/nl2uri/nl2a/cli.py', 'main', 0, 1, 1).
python_function('packages/nl2uri/nl2uri/cli.py', '_default_use_llm', 0, 1, 1).
python_function('packages/nl2uri/nl2uri/cli.py', '_resolve_use_llm', 0, 5, 2).
python_function('packages/nl2uri/nl2uri/cli.py', '_emit', 1, 2, 3).
python_function('packages/nl2uri/nl2uri/cli.py', '_plan_command', 1, 5, 5).
python_function('packages/nl2uri/nl2uri/cli.py', 'plan', 5, 5, 8).
python_function('packages/nl2uri/nl2uri/cli.py', 'classify', 2, 1, 4).
python_function('packages/nl2uri/nl2uri/cli.py', 'single', 3, 1, 3).
python_function('packages/nl2uri/nl2uri/cli.py', 'list_cmd', 3, 1, 3).
python_function('packages/nl2uri/nl2uri/cli.py', 'tree', 4, 4, 9).
python_function('packages/nl2uri/nl2uri/cli.py', 'task', 6, 5, 9).
python_function('packages/nl2uri/nl2uri/cli.py', 'graph', 6, 5, 9).
python_function('packages/nl2uri/nl2uri/cli.py', 'generate', 4, 4, 9).
python_function('packages/nl2uri/nl2uri/cli.py', 'main', 0, 1, 1).
python_function('packages/nl2uri/nl2uri/domain_planner.py', 'plan_from_prompt', 2, 7, 8).
python_function('packages/nl2uri/nl2uri/graph_planner.py', '_slug', 1, 2, 3).
python_function('packages/nl2uri/nl2uri/graph_planner.py', '_detect_agent_id', 1, 3, 2).
python_function('packages/nl2uri/nl2uri/graph_planner.py', '_detect_health_uri', 1, 4, 3).
python_function('packages/nl2uri/nl2uri/graph_planner.py', 'wrap_nl2uri_output', 3, 1, 0).
python_function('packages/nl2uri/nl2uri/graph_planner.py', 'plan_single', 1, 4, 4).
python_function('packages/nl2uri/nl2uri/graph_planner.py', 'plan_list', 1, 2, 4).
python_function('packages/nl2uri/nl2uri/graph_planner.py', 'plan_tree', 1, 9, 5).
python_function('packages/nl2uri/nl2uri/graph_planner.py', 'plan_task', 1, 3, 7).
python_function('packages/nl2uri/nl2uri/graph_planner.py', 'plan_workflow_graph', 1, 12, 9).
python_function('packages/nl2uri/nl2uri/graph_planner.py', 'plan_auto', 1, 1, 2).
python_function('packages/nl2uri/nl2uri/graph_planner.py', 'plan_by_kind', 1, 1, 2).
python_function('packages/nl2uri/nl2uri/graph_planner_llm.py', 'build_graph_planner_system_prompt', 0, 2, 4).
python_function('packages/nl2uri/nl2uri/graph_planner_llm.py', 'call_graph_planner_llm', 1, 4, 9).
python_function('packages/nl2uri/nl2uri/graph_planner_llm.py', 'plan_graph_with_llm', 1, 4, 6).
python_function('packages/nl2uri/nl2uri/graph_repair.py', '_slug', 1, 2, 3).
python_function('packages/nl2uri/nl2uri/graph_repair.py', '_coerce_operation', 2, 5, 6).
python_function('packages/nl2uri/nl2uri/graph_repair.py', 'extract_graph_payload', 1, 14, 4).
python_function('packages/nl2uri/nl2uri/graph_repair.py', 'normalize_to_kind', 1, 12, 10).
python_function('packages/nl2uri/nl2uri/graph_repair.py', 'sanitize_node', 1, 16, 9).
python_function('packages/nl2uri/nl2uri/graph_repair.py', '_sanitize_nodes', 1, 12, 5).
python_function('packages/nl2uri/nl2uri/graph_repair.py', 'repair_graph_body', 2, 12, 12).
python_function('packages/nl2uri/nl2uri/graph_repair.py', 'repair_and_validate_graph', 2, 13, 8).
python_function('packages/nl2uri/nl2uri/llm_planner.py', 'llm_plan', 1, 2, 4).
python_function('packages/nl2uri/nl2uri/output_classifier.py', 'classify_output_kind', 1, 20, 5).
python_function('packages/nl2uri/nl2uri/pipeline.py', 'generate_tree', 1, 1, 1).
python_function('packages/nl2uri/nl2uri/pipeline.py', '_append_pipeline_logs', 0, 2, 2).
python_function('packages/nl2uri/nl2uri/pipeline.py', 'run_generate_pipeline', 1, 4, 10).
python_function('packages/nl2uri/nl2uri/pipeline.py', 'run_full_pipeline', 1, 3, 10).
python_function('packages/nl2uri/nl2uri/planner.py', 'rule_based_plan', 1, 1, 2).
python_function('packages/nl2uri/nl2uri/planner_llm.py', 'extract_json', 1, 3, 5).
python_function('packages/nl2uri/nl2uri/planner_llm.py', 'call_openrouter', 1, 4, 8).
python_function('packages/nl2uri/nl2uri/planner_templates.py', 'slug', 1, 2, 3).
python_function('packages/nl2uri/nl2uri/planner_templates.py', 'llm_uri_from_env', 0, 6, 4).
python_function('packages/nl2uri/nl2uri/planner_templates.py', 'is_weather_prompt', 1, 1, 2).
python_function('packages/nl2uri/nl2uri/planner_templates.py', 'deterministic_weather_plan', 1, 2, 2).
python_function('packages/nl2uri/nl2uri/planner_templates.py', 'generic_plan', 1, 1, 2).
python_function('packages/nl2uri/nl2uri/planner_validation.py', 'validate_tree_data', 1, 2, 6).
python_function('packages/nl2uri/nl2uri/planner_validation.py', 'is_structured_uri_tree', 1, 10, 2).
python_function('packages/nl2uri/nl2uri/planner_validation.py', 'normalize_llm_tree', 2, 7, 7).
python_function('packages/nl2uri/nl2uri/writer.py', 'write_uri_tree', 2, 1, 4).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('packages/resource-agent-factory/agents/generated/orders_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('packages/resource-agent-factory/agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('packages/resource-agent-factory/generator/agent_generator.py', 'render_template', 4, 1, 4).
python_function('packages/resource-agent-factory/generator/agent_generator.py', 'generate_agent', 1, 5, 17).
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
python_function('packages/resource-agent-factory/generator/verify.py', 'verify_generated', 1, 6, 5).
python_function('packages/resource-agent-factory/generator/verify.py', 'main', 1, 9, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'call', 1, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'scan', 1, 3, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'resolve', 1, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'status', 0, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'config_cmd', 1, 2, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'deployments_list', 0, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'run_agent_cmd', 6, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'stop_agent_cmd', 1, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'restart_agent_cmd', 5, 1, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'agent_status_cmd', 2, 1, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'logs_cmd', 2, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'deploy_agent_cmd', 2, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'verify_agent_cmd', 2, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'docker_cmd', 2, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'main', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 'echo_json', 1, 2, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 'run_local_agent', 1, 6, 11).
python_function('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 'deploy_agent', 1, 7, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/cli_commands.py', 'verify_agent', 1, 4, 7).
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
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_checks/capabilities.py', 'validate_capability_cross_refs', 1, 13, 2).
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
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_checks/capabilities.py', 'validate_resource_read_capability', 2, 7, 2).
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
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/validate.py', 'validate_registry', 1, 1, 3).
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
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', '_repo_root', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', 'run_agent', 1, 8, 14).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', 'stop_agent', 1, 7, 13).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', 'restart_agent', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', 'agent_status', 1, 5, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py', 'agent_logs_uri', 1, 3, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', 'default_registry_path', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', '_read_yaml', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', '_parse_deployment', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', 'load_deployment_registry', 1, 5, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', 'local_target_to_relative_path', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', 'local_target_to_module', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py', 'build_local_run_plan', 1, 6, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/process.py', 'start_process', 1, 4, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/run_plans.py', 'build_run_plan', 1, 5, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'runtime_root', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'state_path', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'load_runtime_state', 2, 3, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'save_runtime_state', 3, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'clear_runtime_state', 2, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'is_process_alive', 1, 4, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'runtime_status', 2, 6, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py', 'now_iso', 0, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/selector.py', 'resolve_deployment', 1, 7, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_deploy.py', 'build_ssh_deploy_plan', 1, 3, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_deploy.py', 'apply_ssh_deploy_plan', 1, 7, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_helpers.py', 'generated_agent_dir', 2, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_helpers.py', 'remote_module_for', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_run.py', 'build_ssh_run_plan', 1, 7, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/ssh_verify.py', 'verify_remote_deployment', 1, 12, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'infer_port', 1, 3, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'deployment_id_for_agent', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'infer_health_uri', 2, 6, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'infer_card_uri', 2, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'deployment_from_uri_tree', 1, 8, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'sync_from_uri_tree', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'resolve_status', 1, 11, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'list_deployments', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'get_deployment_for_agent', 1, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'registry_summary', 1, 4, 2).
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
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/pack_writer.py', 'write_domain_pack', 1, 3, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/parser.py', 'parse_uri_tree', 1, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/parser.py', 'derive_domain_model', 2, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'package_name', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'generic_proto', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'weather_proto', 0, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'weather_handler', 0, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'generic_handler', 0, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/writer.py', 'write_file', 2, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/cli.py', 'main', 1, 10, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/models.py', 'load_proposal', 1, 5, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/validator.py', 'validate_proposal', 1, 6, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py', 'evaluate_change', 2, 5, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/verifier/capability_tests.py', 'build_capability_test_plan', 1, 4, 1).
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
python_function('packages/uri2flow/uri2flow/parser.py', 'load_flow', 1, 3, 6).
python_function('packages/uri2flow/uri2flow/resolver.py', 'default_operation_for_uri', 1, 21, 3).
python_function('packages/uri2flow/uri2flow/utils.py', 'slugify', 1, 2, 3).
python_function('packages/uri2flow/uri2flow/utils.py', 'scheme_of', 1, 1, 1).
python_function('packages/uri2flow/uri2flow/utils.py', 'path_parts', 1, 4, 4).
python_function('packages/uri2flow/uri2flow/utils.py', 'node_id_from_uri', 2, 5, 7).
python_function('packages/uri2flow/uri2flow/validator.py', 'validate_flow', 1, 9, 6).
python_function('packages/uri2ops/uri2ops/cli.py', '_print', 1, 1, 2).
python_function('packages/uri2ops/uri2ops/cli.py', 'operations_cmd', 1, 6, 7).
python_function('packages/uri2ops/uri2ops/cli.py', 'registry_cmd', 1, 4, 7).
python_function('packages/uri2ops/uri2ops/cli.py', 'validate_cmd', 1, 2, 2).
python_function('packages/uri2ops/uri2ops/cli.py', 'plan_cmd', 1, 1, 3).
python_function('packages/uri2ops/uri2ops/cli.py', 'run_cmd', 1, 2, 4).
python_function('packages/uri2ops/uri2ops/cli.py', 'serve_cmd', 1, 2, 4).
python_function('packages/uri2ops/uri2ops/cli.py', 'main', 1, 1, 7).
python_function('packages/uri2ops/uri2ops/operation_registry/dispatcher.py', '_split_python_uri', 1, 3, 3).
python_function('packages/uri2ops/uri2ops/operation_registry/dispatcher.py', 'call_handler', 3, 2, 4).
python_function('packages/uri2ops/uri2ops/operation_registry/dispatcher.py', 'dispatch', 4, 1, 3).
python_function('packages/uri2ops/uri2ops/operation_registry/loader.py', 'default_registry_path', 0, 1, 2).
python_function('packages/uri2ops/uri2ops/operation_registry/loader.py', 'registry_schema_path', 0, 1, 2).
python_function('packages/uri2ops/uri2ops/operation_registry/loader.py', 'load_operation_registry', 1, 10, 11).
python_function('packages/uri2ops/uri2ops/operation_registry/validator.py', 'validate_registry_schema', 1, 2, 7).
python_function('packages/uri2ops/uri2ops/operation_registry/validator.py', 'validate_operation_registry', 1, 14, 6).
python_function('packages/uri2ops/uri2ops/remote_registry/loader.py', 'registry_config_path', 1, 2, 2).
python_function('packages/uri2ops/uri2ops/remote_registry/loader.py', 'load_registry_config', 1, 3, 6).
python_function('packages/uri2ops/uri2ops/remote_registry/loader.py', '_load_source', 1, 14, 13).
python_function('packages/uri2ops/uri2ops/remote_registry/loader.py', 'merge_registry_documents', 0, 6, 4).
python_function('packages/uri2ops/uri2ops/remote_registry/loader.py', 'registry_from_document', 1, 8, 7).
python_function('packages/uri2ops/uri2ops/remote_registry/loader.py', 'resolve_operation_registry', 1, 12, 11).
python_function('packages/uri2ops/uri2ops/remote_registry/loader.py', 'registry_document', 1, 4, 4).
python_function('packages/uri2ops/uri2ops/remote_registry/loader.py', 'list_remote_sources', 1, 4, 4).
python_function('packages/uri2ops/uri2ops/server/a2a_wrapper.py', 'build_agent_card', 2, 3, 3).
python_function('packages/uri2ops/uri2ops/server/app.py', 'create_app', 0, 1, 24).
python_function('packages/uri2ops/uri2ops/server/mcp_wrapper.py', 'list_mcp_tools', 1, 2, 2).
python_function('packages/uri2ops/uri2ops/server/mcp_wrapper.py', 'mcp_tool_name_for_operation', 2, 1, 0).
python_function('packages/uri3/domains/weather_map/handlers/generate_weather_map.py', 'handler', 1, 3, 7).
python_function('packages/uri3/uri3/cli.py', '_quick_reference', 0, 5, 4).
python_function('packages/uri3/uri3/cli.py', '_list_payload', 0, 2, 3).
python_function('packages/uri3/uri3/cli.py', 'main', 1, 1, 4).
python_function('packages/uri3/uri3/cli.py', 'list_cmd', 2, 4, 7).
python_function('packages/uri3/uri3/cli.py', 'validate', 1, 1, 3).
python_function('packages/uri3/uri3/cli.py', 'validate_tree', 1, 3, 4).
python_function('packages/uri3/uri3/cli.py', 'graph', 1, 3, 5).
python_function('packages/uri3/uri3/cli.py', 'validate_workflow', 1, 3, 4).
python_function('packages/uri3/uri3/cli.py', 'plan_workflow', 1, 1, 5).
python_function('packages/uri3/uri3/cli.py', 'run_workflow_cmd', 4, 2, 8).
python_function('packages/uri3/uri3/cli.py', 'resolve', 1, 2, 8).
python_function('packages/uri3/uri3/cli.py', 'call', 1, 2, 8).
python_function('packages/uri3/uri3/cli.py', 'scan', 2, 8, 12).
python_function('packages/uri3/uri3/cli.py', 'logs', 2, 2, 6).
python_function('packages/uri3/uri3/cli.py', 'schema', 3, 4, 8).
python_function('packages/uri3/uri3/cli.py', 'main', 0, 1, 1).
python_function('packages/uri3/uri3/config/cli_shortcuts.py', 'cli_config_path', 1, 1, 1).
python_function('packages/uri3/uri3/config/cli_shortcuts.py', 'load_cli_config', 1, 2, 3).
python_function('packages/uri3/uri3/config/cli_shortcuts.py', 'scan_shortcuts', 1, 4, 4).
python_function('packages/uri3/uri3/config/cli_shortcuts.py', 'resolve_scan_target', 1, 4, 4).
python_function('packages/uri3/uri3/config/cli_shortcuts.py', 'cli_examples', 1, 3, 3).
python_function('packages/uri3/uri3/config/docker_stacks.py', 'docker_config_path', 1, 1, 1).
python_function('packages/uri3/uri3/config/docker_stacks.py', 'load_docker_config', 1, 2, 3).
python_function('packages/uri3/uri3/config/docker_stacks.py', 'resolve_stack', 1, 5, 6).
python_function('packages/uri3/uri3/config/docker_stacks.py', 'resolve_agent_stack', 1, 4, 7).
python_function('packages/uri3/uri3/config/llm_profile_builder.py', 'parse_llm_query', 1, 7, 5).
python_function('packages/uri3/uri3/config/llm_profile_builder.py', 'chosen_profile_name', 2, 3, 1).
python_function('packages/uri3/uri3/config/llm_profile_builder.py', 'resolve_profile_api_key', 1, 4, 4).
python_function('packages/uri3/uri3/config/llm_profile_builder.py', 'normalize_model_name', 1, 2, 2).
python_function('packages/uri3/uri3/config/llm_profiles.py', 'llm_config_path', 1, 1, 1).
python_function('packages/uri3/uri3/config/llm_profiles.py', 'load_llm_config', 1, 2, 3).
python_function('packages/uri3/uri3/config/llm_profiles.py', 'resolve_llm_profile', 1, 10, 14).
python_function('packages/uri3/uri3/config/repo_root.py', '_walk_up', 1, 7, 5).
python_function('packages/uri3/uri3/config/repo_root.py', 'find_repo_root', 1, 4, 4).
python_function('packages/uri3/uri3/config/repo_root.py', 'config_repo_root', 1, 3, 3).
python_function('packages/uri3/uri3/config/repo_root.py', 'repo_root', 0, 1, 1).
python_function('packages/uri3/uri3/config/ssh_auth.py', 'ssh_config_path', 1, 1, 1).
python_function('packages/uri3/uri3/config/ssh_auth.py', 'load_ssh_config', 1, 2, 3).
python_function('packages/uri3/uri3/config/ssh_auth.py', '_profile_matches', 2, 4, 2).
python_function('packages/uri3/uri3/config/ssh_auth.py', '_password_from_env_file', 1, 5, 4).
python_function('packages/uri3/uri3/config/ssh_auth.py', '_resolve_password_value', 1, 8, 6).
python_function('packages/uri3/uri3/config/ssh_auth.py', 'resolve_ssh_password', 1, 12, 7).
python_function('packages/uri3/uri3/config/ssh_auth.py', 'ssh_auth_hint', 1, 3, 2).
python_function('packages/uri3/uri3/config/uri_yaml.py', 'is_uri', 1, 4, 3).
python_function('packages/uri3/uri3/config/uri_yaml.py', 'load_uri_yaml', 1, 2, 5).
python_function('packages/uri3/uri3/config/uri_yaml.py', 'resolve_uri_values', 1, 15, 9).
python_function('packages/uri3/uri3/docker/actions/compose.py', 'compose_base', 1, 3, 2).
python_function('packages/uri3/uri3/docker/actions/compose.py', '_parse_ps_stdout', 1, 4, 4).
python_function('packages/uri3/uri3/docker/actions/compose.py', 'control_compose_ps', 1, 3, 4).
python_function('packages/uri3/uri3/docker/actions/compose.py', 'control_compose_up', 1, 9, 4).
python_function('packages/uri3/uri3/docker/actions/compose.py', 'control_compose_down', 1, 2, 3).
python_function('packages/uri3/uri3/docker/actions/compose.py', 'control_compose_lifecycle', 1, 1, 2).
python_function('packages/uri3/uri3/docker/actions/compose.py', 'control_compose_logs', 1, 1, 3).
python_function('packages/uri3/uri3/docker/actions/compose.py', 'control_compose', 1, 6, 6).
python_function('packages/uri3/uri3/docker/actions/container.py', '_container_name', 1, 2, 0).
python_function('packages/uri3/uri3/docker/actions/container.py', 'handles_container_action', 1, 3, 1).
python_function('packages/uri3/uri3/docker/actions/container.py', 'control_container', 1, 8, 6).
python_function('packages/uri3/uri3/docker/compose_generator.py', 'build_generate_plan', 1, 2, 6).
python_function('packages/uri3/uri3/docker/compose_generator.py', 'write_generated_compose', 1, 1, 6).
python_function('packages/uri3/uri3/docker/controller.py', 'control_docker', 1, 11, 11).
python_function('packages/uri3/uri3/docker/runner.py', 'run_command', 1, 4, 4).
python_function('packages/uri3/uri3/graph/adapters/browser_mock.py', 'json_dumps', 1, 1, 1).
python_function('packages/uri3/uri3/graph/adapters/browser_playwright.py', '_session_state', 1, 1, 1).
python_function('packages/uri3/uri3/graph/adapters/browser_playwright.py', 'close_playwright_session', 1, 5, 4).
python_function('packages/uri3/uri3/graph/adapters/browser_router.py', '_playwright_ready', 0, 3, 5).
python_function('packages/uri3/uri3/graph/adapters/browser_router.py', 'resolve_browser_mode', 1, 5, 3).
python_function('packages/uri3/uri3/graph/adapters/browser_router.py', 'cleanup_browser_adapters', 1, 2, 2).
python_function('packages/uri3/uri3/graph/adapters/registry.py', 'adapter_for_uri', 1, 3, 1).
python_function('packages/uri3/uri3/graph/artifacts.py', 'artifact_path', 3, 1, 0).
python_function('packages/uri3/uri3/graph/artifacts.py', 'artifact_uri', 3, 1, 0).
python_function('packages/uri3/uri3/graph/artifacts.py', 'write_artifact', 4, 2, 6).
python_function('packages/uri3/uri3/graph/conditions.py', 'evaluate_condition', 2, 7, 7).
python_function('packages/uri3/uri3/graph/dependency_graph.py', 'adjacency', 1, 3, 3).
python_function('packages/uri3/uri3/graph/dependency_graph.py', 'reverse_adjacency', 1, 3, 3).
python_function('packages/uri3/uri3/graph/dependency_graph.py', 'detect_cycles', 1, 15, 5).
python_function('packages/uri3/uri3/graph/dependency_graph.py', 'topological_sort', 1, 13, 8).
python_function('packages/uri3/uri3/graph/dependency_graph.py', 'dependency_summary', 1, 8, 4).
python_function('packages/uri3/uri3/graph/event_log.py', 'workflow_event_path', 2, 1, 0).
python_function('packages/uri3/uri3/graph/event_log.py', 'append_workflow_event', 2, 1, 6).
python_function('packages/uri3/uri3/graph/execution_models.py', 'utc_now_iso', 0, 1, 3).
python_function('packages/uri3/uri3/graph/execution_models.py', 'new_execution_context', 1, 2, 3).
python_function('packages/uri3/uri3/graph/graph_executor.py', 'build_execution_plan', 1, 3, 9).
python_function('packages/uri3/uri3/graph/graph_executor.py', 'dry_run_workflow', 1, 1, 2).
python_function('packages/uri3/uri3/graph/graph_executor.py', '_dependencies_ok', 2, 6, 1).
python_function('packages/uri3/uri3/graph/graph_executor.py', '_execute_step', 2, 2, 2).
python_function('packages/uri3/uri3/graph/graph_executor.py', 'run_workflow', 1, 21, 23).
python_function('packages/uri3/uri3/graph/graph_serializer.py', 'edges_from_depends_on', 1, 4, 5).
python_function('packages/uri3/uri3/graph/graph_serializer.py', 'normalize_graph_payload', 1, 12, 13).
python_function('packages/uri3/uri3/graph/graph_serializer.py', 'task_steps_to_graph', 2, 3, 6).
python_function('packages/uri3/uri3/graph/graph_serializer.py', 'workflow_manifest', 1, 1, 1).
python_function('packages/uri3/uri3/graph/graph_validator.py', '_schema_path', 1, 1, 1).
python_function('packages/uri3/uri3/graph/graph_validator.py', 'load_workflow_graph', 1, 10, 8).
python_function('packages/uri3/uri3/graph/graph_validator.py', 'validate_workflow_schema', 1, 2, 7).
python_function('packages/uri3/uri3/graph/graph_validator.py', 'validate_workflow_graph', 1, 9, 9).
python_function('packages/uri3/uri3/graph/operation_registry.py', 'scheme_from_uri', 1, 2, 1).
python_function('packages/uri3/uri3/graph/operation_registry.py', 'effective_kind', 1, 2, 2).
python_function('packages/uri3/uri3/graph/operation_registry.py', 'requires_approval', 1, 1, 1).
python_function('packages/uri3/uri3/graph/operation_registry.py', 'allowed_operations', 1, 1, 2).
python_function('packages/uri3/uri3/graph/operation_registry.py', 'validate_node_operation', 1, 2, 4).
python_function('packages/uri3/uri3/graph/operation_registry.py', 'operation_registry_summary', 0, 2, 3).
python_function('packages/uri3/uri3/graph/policy.py', 'can_execute_step', 1, 6, 2).
python_function('packages/uri3/uri3/graph/uri_graph.py', 'build_graph_from_tree', 1, 10, 9).
python_function('packages/uri3/uri3/logs/filters.py', 'level_rank', 1, 3, 2).
python_function('packages/uri3/uri3/logs/filters.py', 'entry_timestamp', 1, 4, 4).
python_function('packages/uri3/uri3/logs/filters.py', 'matches_level', 2, 2, 2).
python_function('packages/uri3/uri3/logs/filters.py', 'matches_logger', 2, 3, 3).
python_function('packages/uri3/uri3/logs/filters.py', 'matches_grep', 2, 4, 4).
python_function('packages/uri3/uri3/logs/filters.py', 'matches_time_window', 3, 7, 1).
python_function('packages/uri3/uri3/logs/filters.py', 'matches_filters', 4, 4, 4).
python_function('packages/uri3/uri3/logs/parsing.py', 'empty_entry', 2, 1, 0).
python_function('packages/uri3/uri3/logs/parsing.py', 'parse_json_entry', 2, 14, 7).
python_function('packages/uri3/uri3/logs/parsing.py', 'parse_text_entry', 2, 5, 5).
python_function('packages/uri3/uri3/logs/parsing.py', 'parse_log_line', 2, 4, 4).
python_function('packages/uri3/uri3/logs/reader.py', 'resolve_log_path', 1, 4, 3).
python_function('packages/uri3/uri3/logs/reader.py', '_parse_since', 1, 7, 7).
python_function('packages/uri3/uri3/logs/reader.py', 'read_logs', 1, 9, 9).
python_function('packages/uri3/uri3/logs/reader.py', 'read_logs_result', 1, 3, 2).
python_function('packages/uri3/uri3/logs/reader.py', 'summarize_logs', 1, 6, 12).
python_function('packages/uri3/uri3/logs/writer.py', 'append_log', 2, 3, 9).
python_function('packages/uri3/uri3/protocols/normalizer.py', 'normalize_uri', 1, 3, 3).
python_function('packages/uri3/uri3/protocols/parser.py', 'parse_uri', 1, 2, 4).
python_function('packages/uri3/uri3/protocols/schemes/a2a.py', 'spec', 0, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/analyze.py', '_analyze_query', 2, 14, 6).
python_function('packages/uri3/uri3/protocols/schemes/analyze.py', 'analyze_uri', 1, 2, 7).
python_function('packages/uri3/uri3/protocols/schemes/analyze.py', 'describe_uri', 1, 2, 3).
python_function('packages/uri3/uri3/protocols/schemes/docker.py', 'spec', 0, 1, 2).
python_function('packages/uri3/uri3/protocols/schemes/env.py', 'spec', 0, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/http.py', 'spec', 1, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', '_parse_log', 1, 1, 2).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', '_parse_env', 1, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', '_parse_python', 1, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', '_parse_llm', 1, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', '_parse_pypi', 1, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', '_parse_http', 1, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', '_parse_a2a', 1, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', '_parse_mcp', 1, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', '_parse_docker', 1, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', '_parse_ssh', 1, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', '_parse_resource', 1, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', 'parse_instance', 2, 3, 4).
python_function('packages/uri3/uri3/protocols/schemes/instance_parser.py', 'normalize_scheme', 1, 4, 5).
python_function('packages/uri3/uri3/protocols/schemes/llm.py', 'spec', 0, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/log.py', 'spec', 0, 3, 5).
python_function('packages/uri3/uri3/protocols/schemes/mcp.py', 'spec', 0, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/pypi.py', 'spec', 0, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/python.py', 'spec', 0, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/resource_like.py', 'resource_like_spec', 2, 1, 1).
python_function('packages/uri3/uri3/protocols/schemes/spec_registry.py', 'build_scheme_registry', 0, 2, 2).
python_function('packages/uri3/uri3/protocols/schemes/spec_registry.py', 'is_concrete_uri', 1, 4, 3).
python_function('packages/uri3/uri3/protocols/schemes/spec_registry.py', 'get_scheme_schema', 1, 3, 5).
python_function('packages/uri3/uri3/protocols/schemes/spec_registry.py', 'list_schemes', 0, 5, 4).
python_function('packages/uri3/uri3/protocols/schemes/spec_registry.py', 'query_names', 1, 2, 3).
python_function('packages/uri3/uri3/resolvers/dispatch.py', '_resolve_docker', 1, 1, 1).
python_function('packages/uri3/uri3/resolvers/dispatch.py', 'resolve_target', 2, 3, 4).
python_function('packages/uri3/uri3/resolvers/dispatch.py', 'scheme_from_uri', 1, 2, 2).
python_function('packages/uri3/uri3/resolvers/docker_resolver.py', '_first', 3, 2, 1).
python_function('packages/uri3/uri3/resolvers/docker_resolver.py', '_bool', 3, 3, 2).
python_function('packages/uri3/uri3/resolvers/docker_resolver.py', '_int', 3, 3, 2).
python_function('packages/uri3/uri3/resolvers/docker_resolver.py', 'parse_docker_uri', 1, 12, 14).
python_function('packages/uri3/uri3/resolvers/docker_resolver.py', 'resolve_docker', 1, 2, 4).
python_function('packages/uri3/uri3/resolvers/docker_resolver.py', 'resolve_docker_target', 1, 1, 1).
python_function('packages/uri3/uri3/resolvers/env_resolver.py', '_env_var_name', 1, 3, 3).
python_function('packages/uri3/uri3/resolvers/env_resolver.py', 'resolve_env', 1, 1, 2).
python_function('packages/uri3/uri3/resolvers/env_resolver.py', '_upsert_env_file', 3, 7, 13).
python_function('packages/uri3/uri3/resolvers/env_resolver.py', '_first', 2, 2, 1).
python_function('packages/uri3/uri3/resolvers/env_resolver.py', 'call_env', 2, 8, 12).
python_function('packages/uri3/uri3/resolvers/llm_resolver.py', 'resolve_llm', 1, 5, 4).
python_function('packages/uri3/uri3/resolvers/log_query.py', 'first', 3, 2, 1).
python_function('packages/uri3/uri3/resolvers/log_query.py', 'query_int', 3, 3, 3).
python_function('packages/uri3/uri3/resolvers/log_query.py', 'query_bool', 3, 3, 2).
python_function('packages/uri3/uri3/resolvers/log_query.py', 'resolve_path', 1, 8, 3).
python_function('packages/uri3/uri3/resolvers/log_query.py', 'resolve_level', 1, 3, 2).
python_function('packages/uri3/uri3/resolvers/log_query.py', 'parse_query', 1, 3, 4).
python_function('packages/uri3/uri3/resolvers/log_resolver.py', 'parse_log_uri', 1, 7, 6).
python_function('packages/uri3/uri3/resolvers/log_resolver.py', 'resolve_log', 1, 1, 2).
python_function('packages/uri3/uri3/resolvers/protocol_resolver.py', 'resolve_http_like', 1, 1, 0).
python_function('packages/uri3/uri3/resolvers/protocol_resolver.py', 'resolve_a2a', 1, 2, 1).
python_function('packages/uri3/uri3/resolvers/protocol_resolver.py', 'resolve_mcp', 1, 2, 1).
python_function('packages/uri3/uri3/resolvers/protocol_resolver.py', 'resolve_resource', 1, 4, 4).
python_function('packages/uri3/uri3/resolvers/pypi_resolver.py', 'resolve_pypi', 1, 5, 4).
python_function('packages/uri3/uri3/resolvers/python_resolver.py', '_split_python_uri', 1, 2, 4).
python_function('packages/uri3/uri3/resolvers/python_resolver.py', 'resolve_python', 1, 1, 1).
python_function('packages/uri3/uri3/resolvers/python_resolver.py', 'call_python', 2, 1, 4).
python_function('packages/uri3/uri3/resolvers/registry.py', 'build_resolver_registry', 0, 1, 5).
python_function('packages/uri3/uri3/resolvers/resolve_core.py', 'resolve', 1, 2, 3).
python_function('packages/uri3/uri3/resolvers/resolve_core.py', 'call', 2, 8, 8).
python_function('packages/uri3/uri3/resolvers/ssh_resolver.py', 'parse_ssh_uri', 1, 8, 5).
python_function('packages/uri3/uri3/resolvers/ssh_resolver.py', '_resolve_ssh_password', 1, 1, 1).
python_function('packages/uri3/uri3/resolvers/ssh_resolver.py', 'resolve_ssh', 1, 1, 5).
python_function('packages/uri3/uri3/resolvers/ssh_resolver.py', '_ssh_options', 1, 2, 2).
python_function('packages/uri3/uri3/resolvers/ssh_resolver.py', 'build_ssh_command', 2, 4, 4).
python_function('packages/uri3/uri3/resolvers/ssh_resolver.py', 'ssh_transport_option', 1, 4, 6).
python_function('packages/uri3/uri3/resolvers/ssh_resolver.py', 'run_ssh', 2, 1, 2).
python_function('packages/uri3/uri3/scanner/docker_scanner.py', '_inspect_container', 1, 5, 4).
python_function('packages/uri3/uri3/scanner/docker_scanner.py', 'scan_container', 2, 2, 2).
python_function('packages/uri3/uri3/scanner/docker_scanner.py', '_compose_ps', 1, 6, 6).
python_function('packages/uri3/uri3/scanner/docker_scanner.py', 'scan_compose_stack', 2, 5, 4).
python_function('packages/uri3/uri3/scanner/docker_scanner.py', 'scan_docker', 1, 4, 4).
python_function('packages/uri3/uri3/scanner/http_scanner.py', '_origin', 1, 1, 3).
python_function('packages/uri3/uri3/scanner/http_scanner.py', '_kind_for_path', 1, 5, 2).
python_function('packages/uri3/uri3/scanner/http_scanner.py', '_status_for', 2, 5, 0).
python_function('packages/uri3/uri3/scanner/http_scanner.py', '_probe', 1, 3, 6).
python_function('packages/uri3/uri3/scanner/http_scanner.py', 'health_scan_ok', 1, 6, 2).
python_function('packages/uri3/uri3/scanner/http_scanner.py', 'scan_http', 1, 7, 5).
python_function('packages/uri3/uri3/scanner/scanner.py', 'scan_log', 1, 2, 5).
python_function('packages/uri3/uri3/scanner/scanner.py', 'scan', 1, 5, 5).
python_function('packages/uri3/uri3/scanner/ssh_scanner.py', '_invalid_ssh_item', 2, 1, 2).
python_function('packages/uri3/uri3/scanner/ssh_scanner.py', '_connectivity_item', 2, 8, 7).
python_function('packages/uri3/uri3/scanner/ssh_scanner.py', '_remote_item_uri', 2, 2, 2).
python_function('packages/uri3/uri3/scanner/ssh_scanner.py', '_remote_path_item', 2, 5, 4).
python_function('packages/uri3/uri3/scanner/ssh_scanner.py', '_remote_listing_item', 2, 4, 4).
python_function('packages/uri3/uri3/scanner/ssh_scanner.py', 'scan_ssh', 1, 3, 6).
python_function('packages/uri3/uri3/validators/uri_tree_validator.py', 'load_yaml', 1, 1, 2).
python_function('packages/uri3/uri3/validators/uri_tree_validator.py', 'validate_uri_tree', 1, 2, 7).
python_function('packages/uri3/uri3/validators/uri_validator.py', 'validate_uri', 1, 2, 2).
python_function('tests/domain_pack/test_generator.py', '_weather_tree', 0, 1, 0).
python_function('tests/domain_pack/test_generator.py', 'test_derive_domain_model', 0, 3, 3).
python_function('tests/domain_pack/test_generator.py', 'test_generate_proto_weather', 0, 2, 4).
python_function('tests/domain_pack/test_generator.py', 'test_generate_resources_and_views', 0, 3, 5).
python_function('tests/domain_pack/test_generator.py', 'test_generate_domain_pack_from_tree', 1, 3, 4).
python_function('tests/domain_pack/test_generator.py', 'test_generate_domain_pack_from_uri_tree_file', 1, 3, 5).
python_function('tests/domain_pack/test_generator.py', 'test_deprecated_meta_agent_reexport', 0, 3, 4).
python_function('tests/generator/test_headers.py', 'test_generated_python_files_have_standard_header', 2, 9, 9).
python_function('tests/generator/test_headers.py', 'test_contract_source_ref_is_repo_relative', 0, 2, 3).
python_function('tests/hypervisor/test_agent_runner.py', 'test_local_target_to_module', 0, 2, 1).
python_function('tests/hypervisor/test_agent_runner.py', 'test_build_run_plan_for_local_deployment', 0, 6, 2).
python_function('tests/hypervisor/test_agent_runner.py', 'test_build_run_plan_missing_path', 2, 1, 4).
python_function('tests/hypervisor/test_agent_runner.py', 'test_agent_status_without_health', 0, 3, 1).
python_function('tests/hypervisor/test_agent_runner.py', 'test_ssh_run_plan_via_build_run_plan', 0, 3, 2).
python_function('tests/hypervisor/test_agent_runner.py', 'test_ssh_target_cannot_start_without_dry_run', 0, 1, 2).
python_function('tests/hypervisor/test_config.py', 'test_default_config_has_structured_sections', 0, 8, 2).
python_function('tests/hypervisor/test_config.py', 'test_load_config_merges_user_file', 1, 7, 2).
python_function('tests/hypervisor/test_config.py', 'test_env_overrides', 1, 4, 2).
python_function('tests/hypervisor/test_config.py', 'test_validate_config_reports_invalid_profile', 0, 3, 2).
python_function('tests/hypervisor/test_config.py', 'test_load_hypervisor_config_model', 0, 5, 4).
python_function('tests/hypervisor/test_config.py', 'test_load_config_merges_llm_uri_yaml', 0, 5, 5).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_load_default_deployments', 0, 5, 5).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_deployment_from_weather_uri_tree', 0, 5, 2).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_sync_from_uri_tree_writes_registry', 1, 4, 5).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_upsert_replaces_existing_deployment', 1, 2, 6).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_resolve_status_without_health_check', 0, 2, 2).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_registry_summary', 0, 3, 4).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_ssh_target_uri_supported_in_model', 1, 2, 9).
python_function('tests/hypervisor/test_docker_runner.py', 'test_build_docker_deploy_plan', 0, 4, 3).
python_function('tests/hypervisor/test_docker_runner.py', 'test_build_docker_control_plan_up', 0, 3, 2).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_deployments_and_run_agent_dry_run', 1, 7, 4).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_ssh_run_agent_dry_run', 1, 4, 3).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_deploy_agent_dry_run', 1, 3, 3).
python_function('tests/hypervisor/test_hypervisor_cli.py', 'test_cli_agent_status_includes_runtime_fields', 1, 4, 3).
python_function('tests/hypervisor/test_remote_runner.py', 'test_build_ssh_deploy_plan', 0, 4, 3).
python_function('tests/hypervisor/test_remote_runner.py', 'test_build_ssh_run_plan_dry_run', 0, 5, 2).
python_function('tests/hypervisor/test_remote_runner.py', 'test_build_run_plan_ssh_delegates', 0, 2, 2).
python_function('tests/hypervisor/test_remote_runner.py', 'test_verify_remote_deployment', 1, 4, 4).
python_function('tests/hypervisor/test_runtime_state.py', 'test_build_run_plan_includes_env_and_runtime_paths', 0, 5, 3).
python_function('tests/hypervisor/test_runtime_state.py', 'test_resolve_deployment_env_merges_uri_yaml', 2, 3, 4).
python_function('tests/hypervisor/test_runtime_state.py', 'test_runtime_state_roundtrip', 1, 4, 4).
python_function('tests/integration/test_nl2a_e2e.py', 'isolated_project', 2, 3, 7).
python_function('tests/integration/test_nl2a_e2e.py', 'test_nl2a_full_pipeline_weather_map', 1, 20, 9).
python_function('tests/integration/test_nl2a_e2e.py', 'test_nl2a_cli_generate_no_llm', 1, 8, 4).
python_function('tests/meta_agent/test_repair.py', 'test_repair_agent_block_fills_metadata', 0, 5, 1).
python_function('tests/meta_agent/test_repair.py', 'test_repair_resource_read_fills_renderer_and_schema', 0, 3, 1).
python_function('tests/meta_agent/test_repair.py', 'test_repair_command_fills_fields', 0, 3, 1).
python_function('tests/meta_agent/test_repair.py', 'test_repair_capabilities_deduplicates_names', 0, 3, 3).
python_function('tests/meta_agent/test_repair.py', 'test_repair_agent_spec_integration', 1, 4, 6).
python_function('tests/nl2uri/test_domain_planner.py', 'test_normalize_bad_llm_weather_tree_uses_deterministic_template', 0, 6, 2).
python_function('tests/nl2uri/test_domain_planner.py', 'test_plan_from_prompt_weather_no_llm_full_tree', 0, 6, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_classify_resource_tree', 0, 2, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_classify_task_graph', 0, 2, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_classify_workflow_graph', 0, 2, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_plan_single_status', 0, 3, 1).
python_function('tests/nl2uri/test_graph_planner.py', 'test_plan_list_health_and_card', 0, 3, 2).
python_function('tests/nl2uri/test_graph_planner.py', 'test_plan_tree_contains_domain_root', 0, 3, 1).
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
python_function('tests/test_capability_tests.py', 'test_capability_test_plan_is_built_from_registry', 0, 4, 2).
python_function('tests/test_contract_registry.py', 'test_contract_registry_loads_and_validates', 0, 5, 3).
python_function('tests/test_contract_registry.py', 'test_user_read_capability_matches_resource_contract', 0, 5, 3).
python_function('tests/test_cross_validation_v03.py', 'test_cross_validation_ok', 0, 2, 1).
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
python_function('tests/test_nl2a_v04.py', 'test_weather_prompt_generates_uri_tree', 0, 5, 1).
python_function('tests/test_nl2a_v04.py', 'test_domain_pack_generation', 1, 6, 4).
python_function('tests/test_nl2uri.py', 'test_weather_prompt_generates_weather_uri_tree', 0, 5, 1).
python_function('tests/test_operation_registry.py', 'test_registry_loads', 0, 3, 2).
python_function('tests/test_operation_registry.py', 'test_registry_validates', 0, 2, 2).
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
python_function('tests/test_uri2ops_android.py', 'test_parse_android_uri', 0, 3, 1).
python_function('tests/test_uri2ops_android.py', 'test_resolve_adapter_mode_mock', 0, 2, 1).
python_function('tests/test_uri2ops_android.py', 'test_resolve_adapter_mode_auto_without_adb', 1, 2, 2).
python_function('tests/test_uri2ops_android.py', 'test_android_mock_task', 1, 6, 5).
python_function('tests/test_uri2ops_android.py', 'test_android_tap_blocked_without_approve', 1, 3, 3).
python_function('tests/test_uri2ops_android.py', 'test_android_adb_task_when_device_present', 1, 5, 8).
python_function('tests/test_uri2ops_browser.py', 'test_resolve_adapter_mode_mock', 0, 2, 1).
python_function('tests/test_uri2ops_browser.py', 'test_resolve_adapter_mode_auto_falls_back_without_playwright', 1, 2, 2).
python_function('tests/test_uri2ops_browser.py', 'test_mock_task_writes_artifacts', 1, 4, 5).
python_function('tests/test_uri2ops_browser.py', 'test_playwright_task_executes_against_local_server', 1, 5, 21).
python_function('tests/test_uri2ops_pcwin.py', 'test_parse_pcwin_window_uri', 0, 4, 1).
python_function('tests/test_uri2ops_pcwin.py', 'test_parse_pcwin_control_uri', 0, 4, 1).
python_function('tests/test_uri2ops_pcwin.py', 'test_parse_pcwin_path_only_form', 0, 4, 1).
python_function('tests/test_uri2ops_pcwin.py', 'test_resolve_adapter_mode_mock', 0, 2, 1).
python_function('tests/test_uri2ops_pcwin.py', 'test_resolve_adapter_mode_auto_on_linux', 0, 2, 1).
python_function('tests/test_uri2ops_pcwin.py', 'test_pcwin_mock_task', 1, 6, 4).
python_function('tests/test_uri2ops_pcwin.py', 'test_pcwin_blocked_without_approve', 1, 3, 2).
python_function('tests/test_uri2ops_pcwin.py', 'test_pcwin_uia_available_only_on_windows', 0, 3, 5).
python_function('tests/test_uri2ops_serve.py', 'test_merge_remote_registry_adds_browser_wait', 0, 2, 3).
python_function('tests/test_uri2ops_serve.py', 'test_serve_health_and_registry_export', 0, 5, 5).
python_function('tests/test_uri2ops_serve.py', 'test_serve_agent_card_and_mcp_tools', 0, 7, 5).
python_function('tests/test_uri2ops_serve.py', 'test_serve_run_task_via_a2a', 0, 3, 8).
python_function('tests/test_uri2ops_serve.py', 'test_serve_mcp_run_operator_task', 0, 3, 8).
python_function('tests/test_uri2ops_serve.py', 'test_merge_registry_documents_overlays_operations', 0, 3, 1).
python_function('tests/test_uri2ops_v01.py', 'test_redact_secret_payload_field', 0, 3, 1).
python_function('tests/test_uri2ops_v01.py', 'test_registry_schema_validates_yaml', 0, 3, 6).
python_function('tests/test_uri2ops_v01.py', 'test_artifact_resolver_reads_written_file', 1, 3, 4).
python_function('tests/test_uri2ops_v01.py', 'test_policy_blocks_command_without_approve', 0, 3, 5).
python_function('tests/test_uri2ops_v01.py', 'test_policy_allows_dry_run_without_approve', 0, 2, 3).
python_function('tests/test_uri2ops_v01.py', 'test_task_blocks_without_approve', 1, 3, 2).
python_function('tests/test_uri3.py', 'test_validate_uri', 0, 3, 1).
python_function('tests/test_uri3.py', 'test_graph_weather_tree', 0, 3, 3).
python_function('tests/test_uri_tree_validator.py', 'test_uri_tree_schema_ok', 0, 2, 1).
python_function('tests/test_validate.py', 'test_user_agent_contract_is_valid', 0, 2, 2).
python_function('tests/uri2flow/conftest.py', 'repo_root', 0, 4, 6).
python_function('tests/uri2flow/test_cli.py', 'test_cli_expand', 2, 4, 3).
python_function('tests/uri2flow/test_expand_branching_flow.py', 'test_expand_branching_flow', 1, 6, 1).
python_function('tests/uri2flow/test_expand_linear_flow.py', 'test_expand_linear_flow', 1, 7, 1).
python_function('tests/uri2flow/test_parser_forms.py', 'test_accepts_string_and_mapping_forms', 0, 4, 2).
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
python_function('tests/uri3/test_docker_control.py', 'test_control_docker_generate_writes_file', 2, 3, 5).
python_function('tests/uri3/test_docker_control.py', 'test_control_docker_container_stop_dry_run', 0, 2, 1).
python_function('tests/uri3/test_docker_control.py', 'test_control_docker_up_recovers_from_name_conflict', 1, 4, 5).
python_function('tests/uri3/test_http_scanner.py', 'test_scan_http_health_uri_does_not_double_path', 1, 6, 7).
python_function('tests/uri3/test_http_scanner.py', 'test_scan_http_404_health_is_error', 1, 5, 5).
python_function('tests/uri3/test_http_scanner.py', 'test_health_scan_ok_requires_200', 0, 2, 2).
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
python_function('tests/uri3/test_uri_yaml.py', 'test_resolve_uri_values_keeps_secrets_by_default', 0, 2, 2).
python_function('tests/uri3/test_workflow_executor.py', 'test_run_workflow_dry_run_completes', 0, 5, 3).
python_function('tests/uri3/test_workflow_executor.py', 'test_run_workflow_blocks_command_without_approve', 0, 4, 1).
python_function('tests/uri3/test_workflow_executor.py', 'test_run_workflow_execute_mock_with_approve', 1, 8, 7).
python_function('tests/uri3/test_workflow_executor.py', 'test_run_workflow_accepts_workflow_graph_object', 1, 3, 2).
python_function('tests/uri3/test_workflow_executor.py', 'test_run_workflow_skips_conditional_branch', 1, 5, 1).
python_function('tests/uri3/test_workflow_graph.py', 'test_load_task_payload', 0, 4, 2).
python_function('tests/uri3/test_workflow_graph.py', 'test_validate_task_payload', 0, 2, 1).
python_function('tests/uri3/test_workflow_graph.py', 'test_execution_plan_order', 0, 2, 1).
python_function('tests/uri3/test_workflow_graph.py', 'test_detect_cycle', 0, 4, 6).

% ── Python Classes ───────────────────────────────────────
python_class('packages/nl2uri/nl2uri/pipeline.py', 'PipelineResult').
python_class('packages/nl2uri/nl2uri/pipeline.py', 'FullPipelineResult').
python_class('packages/nl2uri/nl2uri/planner.py', 'PlanResult').
python_class('packages/resource-agent-factory/generator/model.py', 'Capability').
python_class('packages/resource-agent-factory/generator/model.py', 'AgentSpec').
python_method('AgentSpec', 'output_dir_name', 0, 1, 0).
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
python_class('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', 'AgentDeployment').
python_method('AgentDeployment', 'to_dict', 0, 5, 0).
python_class('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', 'DeploymentRegistry').
python_method('DeploymentRegistry', 'by_id', 1, 3, 1).
python_method('DeploymentRegistry', 'by_agent_ref', 1, 3, 0).
python_class('packages/resource-agent-hypervisor/hypervisor/domain_pack/model.py', 'DomainModel').
python_method('DomainModel', 'from_uri_tree', 3, 1, 1).
python_class('packages/resource-agent-hypervisor/hypervisor/evolution/models.py', 'EvolutionProposal').
python_class('packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py', 'GateDecision').
python_class('packages/resource-agent-hypervisor/hypervisor/uri/client.py', 'Uri3Client').
python_method('Uri3Client', '__init__', 0, 1, 1).
python_method('Uri3Client', 'resolve', 1, 1, 1).
python_method('Uri3Client', 'call', 2, 1, 1).
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
python_class('packages/uri2ops/uri2ops/operation_registry/models.py', 'OperationSpec').
python_method('OperationSpec', 'from_mapping', 4, 1, 4).
python_method('OperationSpec', 'to_dict', 0, 1, 0).
python_class('packages/uri2ops/uri2ops/operation_registry/models.py', 'OperationRegistry').
python_method('OperationRegistry', 'get', 2, 1, 1).
python_method('OperationRegistry', 'require', 2, 2, 2).
python_method('OperationRegistry', 'list', 0, 1, 2).
python_class('packages/uri2ops/uri2ops/server/app.py', 'TaskRequest').
python_class('packages/uri2ops/uri2ops/server/app.py', 'McpToolCallRequest').
python_class('packages/uri2ops/uri2ops/server/service.py', 'OperatorService').
python_method('OperatorService', '__init__', 0, 2, 2).
python_method('OperatorService', 'registry', 0, 1, 1).
python_method('OperatorService', 'registry_export', 0, 1, 2).
python_method('OperatorService', 'list_operations', 0, 2, 3).
python_method('OperatorService', 'describe_operation', 2, 1, 2).
python_method('OperatorService', 'list_registry_sources', 0, 1, 1).
python_method('OperatorService', 'validate_task', 1, 1, 2).
python_method('OperatorService', 'plan_task', 1, 1, 2).
python_method('OperatorService', 'run_task', 1, 1, 3).
python_class('packages/uri3/uri3/config/llm_profiles.py', 'LlmProfile').
python_method('LlmProfile', 'to_dict', 0, 1, 1).
python_class('packages/uri3/uri3/graph/adapters/base.py', 'StepAdapter').
python_method('StepAdapter', 'execute', 2, 1, 0).
python_class('packages/uri3/uri3/graph/adapters/browser_mock.py', 'BrowserMockAdapter').
python_method('BrowserMockAdapter', 'execute', 2, 8, 4).
python_class('packages/uri3/uri3/graph/adapters/browser_playwright.py', 'PlaywrightBrowserAdapter').
python_method('PlaywrightBrowserAdapter', 'execute', 2, 11, 18).
python_class('packages/uri3/uri3/graph/adapters/browser_router.py', 'BrowserRouterAdapter').
python_method('BrowserRouterAdapter', '__init__', 0, 1, 2).
python_method('BrowserRouterAdapter', 'execute', 2, 2, 2).
python_class('packages/uri3/uri3/graph/adapters/registry.py', 'AssertionAdapter').
python_method('AssertionAdapter', 'execute', 2, 11, 6).
python_class('packages/uri3/uri3/graph/adapters/registry.py', 'HypervisorAdapter').
python_method('HypervisorAdapter', 'execute', 2, 11, 6).
python_class('packages/uri3/uri3/graph/execution_models.py', 'ExecutionContext').
python_method('ExecutionContext', 'resolve_ref', 1, 2, 2).
python_class('packages/uri3/uri3/graph/execution_models.py', 'StepExecutionResult').
python_method('StepExecutionResult', 'to_dict', 0, 4, 0).
python_class('packages/uri3/uri3/graph/execution_models.py', 'GraphExecutionPlan').
python_method('GraphExecutionPlan', 'to_dict', 0, 4, 0).
python_class('packages/uri3/uri3/graph/execution_models.py', 'GraphExecutionResult').
python_method('GraphExecutionResult', 'to_dict', 0, 4, 1).
python_class('packages/uri3/uri3/graph/models.py', 'GraphNode').
python_method('GraphNode', 'from_dict', 2, 5, 5).
python_method('GraphNode', 'to_dict', 0, 4, 0).
python_class('packages/uri3/uri3/graph/models.py', 'GraphEdge').
python_method('GraphEdge', 'to_dict', 0, 4, 0).
python_class('packages/uri3/uri3/graph/models.py', 'WorkflowGraph').
python_method('WorkflowGraph', 'add_node', 1, 1, 0).
python_method('WorkflowGraph', 'to_dict', 0, 4, 2).
python_class('packages/uri3/uri3/graph/uri_graph.py', 'UriNode').
python_class('packages/uri3/uri3/graph/uri_graph.py', 'UriEdge').
python_class('packages/uri3/uri3/graph/uri_graph.py', 'UriGraph').
python_method('UriGraph', 'add_node', 3, 3, 1).
python_method('UriGraph', 'add_edge', 3, 3, 2).
python_class('packages/uri3/uri3/protocols/parser.py', 'ParsedURI').
python_class('packages/uri3/uri3/protocols/schemes/base.py', 'QueryOption').
python_method('QueryOption', 'to_dict', 0, 2, 1).
python_class('packages/uri3/uri3/protocols/schemes/base.py', 'SchemeSpec').
python_method('SchemeSpec', 'to_dict', 0, 2, 2).
python_class('packages/uri3/uri3/resolvers/docker_resolver.py', 'DockerRef').
python_method('DockerRef', 'to_dict', 0, 1, 0).
python_class('packages/uri3/uri3/resolvers/env_resolver.py', 'EnvResolver').
python_method('EnvResolver', 'resolve', 1, 1, 1).
python_method('EnvResolver', 'call', 2, 1, 1).
python_class('packages/uri3/uri3/resolvers/http_resolver.py', 'HttpResolver').
python_method('HttpResolver', 'resolve', 1, 1, 1).
python_method('HttpResolver', 'fetch', 1, 2, 3).
python_class('packages/uri3/uri3/resolvers/llm_resolver.py', 'LLMRef').
python_class('packages/uri3/uri3/resolvers/llm_resolver.py', 'LLMResolver').
python_method('LLMResolver', 'resolve', 1, 2, 4).
python_class('packages/uri3/uri3/resolvers/log_resolver.py', 'LogRef').
python_method('LogRef', 'to_dict', 0, 2, 1).
python_class('packages/uri3/uri3/resolvers/log_resolver.py', 'LogResolver').
python_method('LogResolver', 'resolve', 1, 1, 1).
python_method('LogResolver', 'read', 1, 2, 2).
python_class('packages/uri3/uri3/resolvers/python_resolver.py', 'PythonResolver').
python_method('PythonResolver', 'resolve', 1, 1, 1).
python_method('PythonResolver', 'call', 2, 2, 1).
python_class('packages/uri3/uri3/resolvers/resolve_core.py', 'UriResolution').
python_class('packages/uri3/uri3/resolvers/router.py', 'Uri3Router').
python_method('Uri3Router', '__init__', 0, 1, 1).
python_method('Uri3Router', 'resolve', 1, 2, 3).
python_method('Uri3Router', 'call', 2, 1, 1).
python_class('packages/uri3/uri3/scanner/base.py', 'ScanItem').
python_class('testenv/ssh_agent_host/mock_agent_server.py', 'Handler').
python_method('Handler', '_json', 2, 1, 8).
python_method('Handler', 'do_GET', 0, 5, 4).
python_method('Handler', 'log_message', 1, 1, 1).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────
makefile_target('validate', '').
makefile_target('generate', '').
makefile_target('verify', '').
makefile_target('test', '').
makefile_target('uri2flow-test', '').
makefile_target('uri2flow-validate', '').
makefile_target('uri2flow-expand', '').
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
sumd_workflow('validate', 'manual').
sumd_workflow_step('validate', 1, 'python -m generator.validate contracts').
sumd_workflow('generate', 'manual').
sumd_workflow_step('generate', 1, 'python -m generator.agent_generator contracts/agents/*.yaml').
sumd_workflow('verify', 'manual').
sumd_workflow_step('verify', 1, 'python -m generator.verify agents/generated').
sumd_workflow('test', 'manual').
sumd_workflow_step('test', 1, 'pytest -q').
sumd_workflow('uri2flow-test', 'manual').
sumd_workflow_step('uri2flow-test', 1, 'pytest tests/uri2flow -q').
sumd_workflow('uri2flow-validate', 'manual').
sumd_workflow_step('uri2flow-validate', 1, 'uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml').
sumd_workflow('uri2flow-expand', 'manual').
sumd_workflow_step('uri2flow-expand', 1, 'mkdir -p output').
sumd_workflow_step('uri2flow-expand', 2, 'uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml').
sumd_workflow('uri-tree', 'manual').
sumd_workflow_step('uri-tree', 1, 'python -m nl2uri.cli --no-llm -p "$(WEATHER_PROMPT)" --out domains/weather_map/uri_tree.yaml').
sumd_workflow('graph', 'manual').
sumd_workflow_step('graph', 1, 'python -m uri3.cli graph domains/weather_map/uri_tree.yaml').
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
sumd_deploy_target('docker_compose').
sumd_deploy_compose_file('docker-compose.yml').
```

## Call Graph

*398 nodes · 500 edges · 128 modules · CC̄=3.6*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `run_workflow` *(in packages.uri3.uri3.graph.graph_executor)* | 21 ⚠ | 2 | 39 | **41** |
| `load_contract_registry` *(in hypervisor.contract_registry.loader)* | 9 | 6 | 33 | **39** |
| `resolve_llm_profile` *(in packages.uri3.uri3.config.llm_profiles)* | 10 ⚠ | 3 | 32 | **35** |
| `list` *(in uri2ops.operation_registry.models.OperationRegistry)* | 1 | 31 | 2 | **33** |
| `write_domain_pack` *(in packages.resource-agent-hypervisor.hypervisor.domain_pack.pack_writer)* | 3 | 1 | 30 | **31** |
| `infer_intent` *(in meta_agent.planner)* | 9 | 1 | 30 | **31** |
| `build_graph_from_tree` *(in uri3.graph.uri_graph)* | 10 ⚠ | 2 | 28 | **30** |
| `parse_docker_uri` *(in packages.uri3.uri3.resolvers.docker_resolver)* | 12 ⚠ | 5 | 23 | **28** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/hypervisor
# generated in 0.21s
# nodes: 398 | edges: 500 | modules: 128
# CC̄=3.6

HUBS[20]:
  packages.uri3.uri3.graph.graph_executor.run_workflow
    CC=21  in:2  out:39  total:41
  hypervisor.contract_registry.loader.load_contract_registry
    CC=9  in:6  out:33  total:39
  packages.uri3.uri3.config.llm_profiles.resolve_llm_profile
    CC=10  in:3  out:32  total:35
  uri2ops.operation_registry.models.OperationRegistry.list
    CC=1  in:31  out:2  total:33
  packages.resource-agent-hypervisor.hypervisor.domain_pack.pack_writer.write_domain_pack
    CC=3  in:1  out:30  total:31
  meta_agent.planner.infer_intent
    CC=9  in:1  out:30  total:31
  uri3.graph.uri_graph.build_graph_from_tree
    CC=10  in:2  out:28  total:30
  packages.uri3.uri3.resolvers.docker_resolver.parse_docker_uri
    CC=12  in:5  out:23  total:28
  packages.nl2uri.nl2uri.graph_repair.repair_graph_body
    CC=12  in:1  out:25  total:26
  packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload
    CC=12  in:2  out:24  total:26
  generator.model.load_agent_spec
    CC=7  in:2  out:24  total:26
  packages.nl2uri.nl2uri.graph_repair.sanitize_node
    CC=16  in:1  out:25  total:26
  packages.uri3.uri3.logs.reader.summarize_logs
    CC=6  in:6  out:18  total:24
  packages.uri3.uri3.graph.adapters.browser_playwright.PlaywrightBrowserAdapter.execute
    CC=11  in:0  out:23  total:23
  packages.uri3.uri3.config.repo_root.find_repo_root
    CC=4  in:18  out:4  total:22
  packages.uri3.uri3.resolvers.log_resolver.parse_log_uri
    CC=7  in:5  out:16  total:21
  packages.resource-agent-hypervisor.hypervisor.cli_commands.echo_json
    CC=2  in:16  out:5  total:21
  packages.uri3.uri3.cli.scan
    CC=8  in:0  out:21  total:21
  packages.uri3.uri3.graph.graph_validator.validate_workflow_graph
    CC=9  in:8  out:13  total:21
  packages.resource-agent-factory.generator.agent_generator.generate_agent
    CC=5  in:3  out:17  total:20

MODULES:
  generator.hashutil  [1 funcs]
    file_sha256  CC=1  out:4
  generator.model  [1 funcs]
    load_agent_spec  CC=7  out:24
  generator.validate  [3 funcs]
    iter_agent_specs  CC=3  out:6
    main  CC=7  out:9
    validate_agent  CC=11  out:10
  generator.verify  [3 funcs]
    main  CC=9  out:10
    verify_generated  CC=6  out:5
    verify_generated_agent  CC=7  out:10
  hypervisor.config.env  [4 funcs]
    _parse_bool  CC=1  out:1
    apply_env_overrides  CC=1  out:2
    apply_legacy_env_overrides  CC=6  out:4
    apply_structured_env_overrides  CC=9  out:17
  hypervisor.config.models  [1 funcs]
    to_dict  CC=1  out:1
  hypervisor.contract_registry.loader  [2 funcs]
    _read_yaml  CC=3  out:4
    load_contract_registry  CC=9  out:33
  hypervisor.contract_registry.registry_builder  [1 funcs]
    write_registry_manifest  CC=2  out:6
  hypervisor.contract_registry.registry_exporter  [1 funcs]
    export_json  CC=1  out:1
  hypervisor.domain_pack.templates  [2 funcs]
    generic_proto  CC=1  out:1
    package_name  CC=1  out:0
  hypervisor.evolution.models  [1 funcs]
    load_proposal  CC=5  out:11
  hypervisor.evolution.validator  [1 funcs]
    validate_proposal  CC=6  out:6
  hypervisor.uri2llm.pypi_resolver  [1 funcs]
    resolve_pypi  CC=5  out:6
  hypervisor.verifier.capability_tests  [1 funcs]
    build_capability_test_plan  CC=4  out:2
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
  nl2a.cli  [1 funcs]
    generate  CC=1  out:5
  nl2uri.writer  [1 funcs]
    write_uri_tree  CC=1  out:4
  packages.nl2uri.nl2uri.cli  [12 funcs]
    _default_use_llm  CC=1  out:2
    _emit  CC=2  out:3
    _plan_command  CC=5  out:6
    _resolve_use_llm  CC=5  out:2
    classify  CC=1  out:5
    generate  CC=4  out:14
    graph  CC=5  out:15
    list_cmd  CC=1  out:5
    plan  CC=5  out:13
    single  CC=1  out:5
  packages.nl2uri.nl2uri.domain_planner  [1 funcs]
    plan_from_prompt  CC=7  out:11
  packages.nl2uri.nl2uri.graph_planner  [11 funcs]
    _detect_agent_id  CC=3  out:3
    _detect_health_uri  CC=4  out:6
    _slug  CC=2  out:3
    plan_auto  CC=1  out:2
    plan_by_kind  CC=1  out:2
    plan_list  CC=2  out:4
    plan_single  CC=4  out:6
    plan_task  CC=3  out:7
    plan_tree  CC=9  out:14
    plan_workflow_graph  CC=12  out:15
  packages.nl2uri.nl2uri.graph_planner_llm  [3 funcs]
    build_graph_planner_system_prompt  CC=2  out:5
    call_graph_planner_llm  CC=4  out:9
    plan_graph_with_llm  CC=4  out:7
  packages.nl2uri.nl2uri.graph_repair  [7 funcs]
    _coerce_operation  CC=5  out:6
    _sanitize_nodes  CC=12  out:8
    extract_graph_payload  CC=14  out:10
    normalize_to_kind  CC=12  out:14
    repair_and_validate_graph  CC=13  out:12
    repair_graph_body  CC=12  out:25
    sanitize_node  CC=16  out:25
  packages.nl2uri.nl2uri.llm_planner  [1 funcs]
    llm_plan  CC=2  out:4
  packages.nl2uri.nl2uri.output_classifier  [1 funcs]
    classify_output_kind  CC=20  out:13
  packages.nl2uri.nl2uri.pipeline  [4 funcs]
    _append_pipeline_logs  CC=2  out:4
    generate_tree  CC=1  out:1
    run_full_pipeline  CC=3  out:15
    run_generate_pipeline  CC=4  out:13
  packages.nl2uri.nl2uri.planner  [1 funcs]
    rule_based_plan  CC=1  out:2
  packages.nl2uri.nl2uri.planner_llm  [2 funcs]
    call_openrouter  CC=4  out:8
    extract_json  CC=3  out:8
  packages.nl2uri.nl2uri.planner_templates  [5 funcs]
    deterministic_weather_plan  CC=2  out:2
    generic_plan  CC=1  out:3
    is_weather_prompt  CC=1  out:2
    llm_uri_from_env  CC=6  out:7
    slug  CC=2  out:3
  packages.nl2uri.nl2uri.planner_validation  [3 funcs]
    is_structured_uri_tree  CC=10  out:13
    normalize_llm_tree  CC=7  out:12
    validate_tree_data  CC=2  out:6
  packages.resource-agent-factory.generator.agent_generator  [3 funcs]
    expand_paths  CC=4  out:7
    generate_agent  CC=5  out:17
    main  CC=5  out:4
  packages.resource-agent-factory.generator.header  [3 funcs]
    contract_source_ref  CC=3  out:7
    dockerfile_header  CC=1  out:0
    python_file_header  CC=1  out:0
  packages.resource-agent-factory.generator.paths  [1 funcs]
    project_root  CC=1  out:1
  packages.resource-agent-hypervisor.hypervisor.cli  [14 funcs]
    agent_status_cmd  CC=1  out:5
    call  CC=1  out:4
    config_cmd  CC=2  out:7
    deploy_agent_cmd  CC=1  out:4
    deployments_list  CC=1  out:4
    docker_cmd  CC=1  out:4
    logs_cmd  CC=1  out:4
    main  CC=4  out:3
    resolve  CC=1  out:4
    restart_agent_cmd  CC=1  out:8
  packages.resource-agent-hypervisor.hypervisor.cli_commands  [6 funcs]
    call_docker  CC=5  out:6
    deploy_agent  CC=7  out:16
    echo_json  CC=2  out:5
    read_agent_logs  CC=3  out:4
    run_local_agent  CC=6  out:15
    verify_agent  CC=4  out:8
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
  packages.resource-agent-hypervisor.hypervisor.contract_registry.merger  [1 funcs]
    merge_main_contracts  CC=2  out:4
  packages.resource-agent-hypervisor.hypervisor.contract_registry.validate  [1 funcs]
    validate_registry  CC=1  out:3
  packages.resource-agent-hypervisor.hypervisor.core  [2 funcs]
    from_config  CC=1  out:2
    status  CC=1  out:4
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.docker_runner  [2 funcs]
    build_docker_deploy_plan  CC=4  out:6
    verify_docker_deployment  CC=9  out:5
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.lifecycle  [6 funcs]
    _repo_root  CC=2  out:3
    agent_logs_uri  CC=3  out:6
    agent_status  CC=5  out:9
    restart_agent  CC=1  out:2
    run_agent  CC=8  out:15
    stop_agent  CC=7  out:17
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.run_plans  [1 funcs]
    build_run_plan  CC=5  out:7
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.selector  [1 funcs]
    resolve_deployment  CC=7  out:9
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.ssh_deploy  [2 funcs]
    apply_ssh_deploy_plan  CC=7  out:6
    build_ssh_deploy_plan  CC=3  out:10
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.ssh_verify  [1 funcs]
    verify_remote_deployment  CC=12  out:6
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.status  [2 funcs]
    registry_summary  CC=4  out:2
    sync_from_uri_tree  CC=2  out:4
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
    write_domain_pack  CC=3  out:30
  packages.resource-agent-hypervisor.hypervisor.domain_pack.parser  [2 funcs]
    derive_domain_model  CC=1  out:2
    parse_uri_tree  CC=1  out:3
  packages.resource-agent-hypervisor.hypervisor.domain_pack.writer  [1 funcs]
    write_file  CC=1  out:3
  packages.resource-agent-hypervisor.hypervisor.evolution.cli  [1 funcs]
    main  CC=10  out:11
  packages.resource-agent-hypervisor.hypervisor.uri.client  [4 funcs]
    graph  CC=1  out:1
    logs  CC=2  out:2
    nl2uri  CC=1  out:1
    schema  CC=1  out:1
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
  packages.uri3.uri3.cli  [13 funcs]
    _list_payload  CC=2  out:3
    _quick_reference  CC=5  out:5
    graph  CC=3  out:5
    list_cmd  CC=4  out:10
    logs  CC=2  out:6
    plan_workflow  CC=1  out:5
    resolve  CC=2  out:8
    run_workflow_cmd  CC=2  out:10
    scan  CC=8  out:21
    schema  CC=4  out:9
  packages.uri3.uri3.config.cli_shortcuts  [5 funcs]
    cli_config_path  CC=1  out:1
    cli_examples  CC=3  out:3
    load_cli_config  CC=2  out:3
    resolve_scan_target  CC=4  out:4
    scan_shortcuts  CC=4  out:6
  packages.uri3.uri3.config.docker_stacks  [4 funcs]
    docker_config_path  CC=1  out:1
    load_docker_config  CC=2  out:3
    resolve_agent_stack  CC=4  out:15
    resolve_stack  CC=5  out:13
  packages.uri3.uri3.config.llm_profile_builder  [4 funcs]
    chosen_profile_name  CC=3  out:2
    normalize_model_name  CC=2  out:2
    parse_llm_query  CC=7  out:6
    resolve_profile_api_key  CC=4  out:4
  packages.uri3.uri3.config.llm_profiles  [3 funcs]
    llm_config_path  CC=1  out:1
    load_llm_config  CC=2  out:3
    resolve_llm_profile  CC=10  out:32
  packages.uri3.uri3.config.repo_root  [4 funcs]
    _walk_up  CC=7  out:6
    config_repo_root  CC=3  out:4
    find_repo_root  CC=4  out:4
    repo_root  CC=1  out:1
  packages.uri3.uri3.config.ssh_auth  [6 funcs]
    _password_from_env_file  CC=5  out:4
    _resolve_password_value  CC=8  out:10
    load_ssh_config  CC=2  out:3
    resolve_ssh_password  CC=12  out:13
    ssh_auth_hint  CC=3  out:2
    ssh_config_path  CC=1  out:1
  packages.uri3.uri3.config.uri_yaml  [3 funcs]
    is_uri  CC=4  out:3
    load_uri_yaml  CC=2  out:5
    resolve_uri_values  CC=15  out:13
  packages.uri3.uri3.docker.actions.compose  [8 funcs]
    _parse_ps_stdout  CC=4  out:5
    compose_base  CC=3  out:2
    control_compose  CC=6  out:6
    control_compose_down  CC=2  out:3
    control_compose_lifecycle  CC=1  out:2
    control_compose_logs  CC=1  out:3
    control_compose_ps  CC=3  out:4
    control_compose_up  CC=9  out:8
  packages.uri3.uri3.docker.actions.container  [3 funcs]
    _container_name  CC=2  out:0
    control_container  CC=8  out:9
    handles_container_action  CC=3  out:1
  packages.uri3.uri3.docker.compose_generator  [2 funcs]
    build_generate_plan  CC=2  out:9
    write_generated_compose  CC=1  out:6
  packages.uri3.uri3.docker.controller  [1 funcs]
    control_docker  CC=11  out:11
  packages.uri3.uri3.docker.runner  [1 funcs]
    run_command  CC=4  out:5
  packages.uri3.uri3.graph.adapters.browser_mock  [2 funcs]
    execute  CC=8  out:7
    json_dumps  CC=1  out:1
  packages.uri3.uri3.graph.adapters.browser_playwright  [3 funcs]
    execute  CC=11  out:23
    _session_state  CC=1  out:1
    close_playwright_session  CC=5  out:8
  packages.uri3.uri3.graph.adapters.browser_router  [4 funcs]
    execute  CC=2  out:3
    _playwright_ready  CC=3  out:5
    cleanup_browser_adapters  CC=2  out:2
    resolve_browser_mode  CC=5  out:3
  packages.uri3.uri3.graph.adapters.registry  [2 funcs]
    execute  CC=11  out:6
    adapter_for_uri  CC=3  out:1
  packages.uri3.uri3.graph.artifacts  [3 funcs]
    artifact_path  CC=1  out:0
    artifact_uri  CC=1  out:0
    write_artifact  CC=2  out:6
  packages.uri3.uri3.graph.dependency_graph  [3 funcs]
    dependency_summary  CC=8  out:7
    detect_cycles  CC=15  out:7
    topological_sort  CC=13  out:13
  packages.uri3.uri3.graph.event_log  [2 funcs]
    append_workflow_event  CC=1  out:6
    workflow_event_path  CC=1  out:0
  packages.uri3.uri3.graph.execution_models  [2 funcs]
    new_execution_context  CC=2  out:3
    utc_now_iso  CC=1  out:3
  packages.uri3.uri3.graph.graph_executor  [4 funcs]
    _execute_step  CC=2  out:2
    build_execution_plan  CC=3  out:10
    dry_run_workflow  CC=1  out:2
    run_workflow  CC=21  out:39
  packages.uri3.uri3.graph.graph_serializer  [4 funcs]
    edges_from_depends_on  CC=4  out:5
    normalize_graph_payload  CC=12  out:24
    task_steps_to_graph  CC=3  out:7
    workflow_manifest  CC=1  out:1
  packages.uri3.uri3.graph.graph_validator  [4 funcs]
    _schema_path  CC=1  out:1
    load_workflow_graph  CC=10  out:11
    validate_workflow_graph  CC=9  out:13
    validate_workflow_schema  CC=2  out:7
  packages.uri3.uri3.graph.models  [1 funcs]
    from_dict  CC=5  out:15
  packages.uri3.uri3.graph.operation_registry  [6 funcs]
    allowed_operations  CC=1  out:2
    effective_kind  CC=2  out:2
    operation_registry_summary  CC=2  out:5
    requires_approval  CC=1  out:1
    scheme_from_uri  CC=2  out:1
    validate_node_operation  CC=2  out:5
  packages.uri3.uri3.graph.policy  [1 funcs]
    can_execute_step  CC=6  out:2
  packages.uri3.uri3.logs.filters  [7 funcs]
    entry_timestamp  CC=4  out:5
    level_rank  CC=3  out:2
    matches_filters  CC=4  out:4
    matches_grep  CC=4  out:5
    matches_level  CC=2  out:3
    matches_logger  CC=3  out:4
    matches_time_window  CC=7  out:1
  packages.uri3.uri3.logs.parsing  [4 funcs]
    empty_entry  CC=1  out:0
    parse_json_entry  CC=14  out:16
    parse_log_line  CC=4  out:5
    parse_text_entry  CC=5  out:8
  packages.uri3.uri3.logs.reader  [5 funcs]
    _parse_since  CC=7  out:14
    read_logs  CC=9  out:10
    read_logs_result  CC=3  out:2
    resolve_log_path  CC=4  out:3
    summarize_logs  CC=6  out:18
  packages.uri3.uri3.logs.writer  [1 funcs]
    append_log  CC=3  out:9
  packages.uri3.uri3.protocols.schemes.analyze  [3 funcs]
    _analyze_query  CC=14  out:10
    analyze_uri  CC=2  out:7
    describe_uri  CC=2  out:3
  packages.uri3.uri3.protocols.schemes.base  [2 funcs]
    to_dict  CC=4  out:2
    to_dict  CC=2  out:5
  packages.uri3.uri3.protocols.schemes.instance_parser  [13 funcs]
    _parse_a2a  CC=1  out:1
    _parse_docker  CC=1  out:1
    _parse_env  CC=1  out:1
    _parse_http  CC=1  out:1
    _parse_llm  CC=1  out:1
    _parse_log  CC=1  out:2
    _parse_mcp  CC=1  out:1
    _parse_pypi  CC=1  out:1
    _parse_python  CC=1  out:1
    _parse_resource  CC=1  out:1
  packages.uri3.uri3.protocols.schemes.spec_registry  [4 funcs]
    get_scheme_schema  CC=3  out:5
    is_concrete_uri  CC=4  out:3
    list_schemes  CC=5  out:5
    query_names  CC=2  out:3
  packages.uri3.uri3.resolvers.dispatch  [2 funcs]
    _resolve_docker  CC=1  out:1
    resolve_target  CC=3  out:4
  packages.uri3.uri3.resolvers.docker_resolver  [6 funcs]
    _bool  CC=3  out:2
    _first  CC=2  out:1
    _int  CC=3  out:2
    parse_docker_uri  CC=12  out:23
    resolve_docker  CC=2  out:4
    resolve_docker_target  CC=1  out:1
  packages.uri3.uri3.resolvers.env_resolver  [6 funcs]
    call  CC=1  out:1
    resolve  CC=1  out:1
    _env_var_name  CC=3  out:3
    _first  CC=2  out:1
    call_env  CC=8  out:17
    resolve_env  CC=1  out:2
  packages.uri3.uri3.resolvers.log_query  [6 funcs]
    first  CC=2  out:1
    parse_query  CC=3  out:4
    query_bool  CC=3  out:2
    query_int  CC=3  out:3
    resolve_level  CC=3  out:3
    resolve_path  CC=8  out:5
  packages.uri3.uri3.resolvers.log_resolver  [4 funcs]
    read  CC=2  out:2
    resolve  CC=1  out:1
    parse_log_uri  CC=7  out:16
    resolve_log  CC=1  out:2
  packages.uri3.uri3.resolvers.protocol_resolver  [4 funcs]
    resolve_a2a  CC=2  out:1
    resolve_http_like  CC=1  out:0
    resolve_mcp  CC=2  out:1
    resolve_resource  CC=4  out:4
  packages.uri3.uri3.resolvers.registry  [1 funcs]
    build_resolver_registry  CC=1  out:5
  packages.uri3.uri3.resolvers.resolve_core  [2 funcs]
    call  CC=8  out:8
    resolve  CC=2  out:3
  packages.uri3.uri3.resolvers.router  [1 funcs]
    __init__  CC=1  out:1
  packages.uri3.uri3.resolvers.ssh_resolver  [7 funcs]
    _resolve_ssh_password  CC=1  out:1
    _ssh_options  CC=2  out:3
    build_ssh_command  CC=4  out:4
    parse_ssh_uri  CC=8  out:7
    resolve_ssh  CC=1  out:6
    run_ssh  CC=1  out:2
    ssh_transport_option  CC=4  out:7
  packages.uri3.uri3.scanner.docker_scanner  [5 funcs]
    _compose_ps  CC=6  out:8
    _inspect_container  CC=5  out:9
    scan_compose_stack  CC=5  out:4
    scan_container  CC=2  out:2
    scan_docker  CC=4  out:4
  packages.uri3.uri3.scanner.http_scanner  [5 funcs]
    _kind_for_path  CC=5  out:3
    _origin  CC=1  out:3
    _probe  CC=3  out:7
    _status_for  CC=5  out:0
    scan_http  CC=7  out:8
  packages.uri3.uri3.scanner.scanner  [2 funcs]
    scan  CC=5  out:5
    scan_log  CC=2  out:5
  packages.uri3.uri3.scanner.ssh_scanner  [6 funcs]
    _connectivity_item  CC=8  out:9
    _invalid_ssh_item  CC=1  out:2
    _remote_item_uri  CC=2  out:2
    _remote_listing_item  CC=4  out:5
    _remote_path_item  CC=5  out:5
    scan_ssh  CC=3  out:6
  packages.uri3.uri3.validators.uri_tree_validator  [2 funcs]
    load_yaml  CC=1  out:2
    validate_uri_tree  CC=2  out:7
  uri2ops.operation_registry.models  [1 funcs]
    list  CC=1  out:2
  uri3.graph.uri_graph  [1 funcs]
    build_graph_from_tree  CC=10  out:28
  uri3.protocols.normalizer  [1 funcs]
    normalize_uri  CC=3  out:4
  uri3.protocols.parser  [1 funcs]
    parse_uri  CC=2  out:4
  uri3.resolvers.http_resolver  [1 funcs]
    resolve  CC=1  out:1
  uri3.resolvers.llm_resolver  [2 funcs]
    resolve  CC=2  out:4
    resolve_llm  CC=5  out:5
  uri3.resolvers.python_resolver  [5 funcs]
    call  CC=2  out:1
    resolve  CC=1  out:1
    _split_python_uri  CC=2  out:4
    call_python  CC=1  out:4
    resolve_python  CC=1  out:1
  uri3.validators.uri_validator  [1 funcs]
    validate_uri  CC=2  out:2

EDGES:
  packages.uri3.uri3.cli._quick_reference → packages.uri3.uri3.config.cli_shortcuts.scan_shortcuts
  packages.uri3.uri3.cli._quick_reference → packages.uri3.uri3.config.cli_shortcuts.cli_examples
  packages.uri3.uri3.cli._list_payload → packages.uri3.uri3.config.cli_shortcuts.cli_examples
  packages.uri3.uri3.cli._list_payload → packages.uri3.uri3.protocols.schemes.spec_registry.list_schemes
  packages.uri3.uri3.cli._list_payload → packages.uri3.uri3.config.cli_shortcuts.scan_shortcuts
  packages.uri3.uri3.cli.list_cmd → packages.uri3.uri3.cli._list_payload
  packages.uri3.uri3.cli.list_cmd → packages.uri3.uri3.cli._quick_reference
  packages.uri3.uri3.cli.validate → uri3.validators.uri_validator.validate_uri
  packages.uri3.uri3.cli.validate_tree → packages.uri3.uri3.validators.uri_tree_validator.validate_uri_tree
  packages.uri3.uri3.cli.graph → uri3.graph.uri_graph.build_graph_from_tree
  packages.uri3.uri3.cli.validate_workflow → packages.uri3.uri3.graph.graph_validator.validate_workflow_graph
  packages.uri3.uri3.cli.plan_workflow → packages.uri3.uri3.graph.graph_executor.build_execution_plan
  packages.uri3.uri3.cli.plan_workflow → packages.uri3.uri3.graph.graph_validator.load_workflow_graph
  packages.uri3.uri3.cli.run_workflow_cmd → packages.uri3.uri3.graph.graph_executor.run_workflow
  packages.uri3.uri3.cli.run_workflow_cmd → packages.uri3.uri3.graph.graph_validator.load_workflow_graph
  packages.uri3.uri3.cli.scan → packages.uri3.uri3.config.cli_shortcuts.scan_shortcuts
  packages.uri3.uri3.cli.scan → packages.uri3.uri3.config.cli_shortcuts.resolve_scan_target
  packages.uri3.uri3.cli.logs → packages.uri3.uri3.logs.reader.summarize_logs
  packages.uri3.uri3.cli.logs → packages.uri3.uri3.logs.reader.read_logs_result
  packages.uri3.uri3.cli.schema → packages.uri3.uri3.protocols.schemes.spec_registry.list_schemes
  packages.uri3.uri3.cli.schema → packages.uri3.uri3.protocols.schemes.analyze.analyze_uri
  packages.uri3.uri3.cli.schema → packages.uri3.uri3.protocols.schemes.analyze.describe_uri
  packages.uri3.uri3.logs.parsing.parse_log_line → packages.uri3.uri3.logs.parsing.empty_entry
  packages.uri3.uri3.logs.parsing.parse_log_line → packages.uri3.uri3.logs.parsing.parse_json_entry
  packages.uri3.uri3.logs.parsing.parse_log_line → packages.uri3.uri3.logs.parsing.parse_text_entry
  packages.uri3.uri3.logs.filters.matches_level → packages.uri3.uri3.logs.filters.level_rank
  packages.uri3.uri3.logs.filters.matches_time_window → packages.uri3.uri3.logs.filters.entry_timestamp
  packages.uri3.uri3.logs.filters.matches_filters → packages.uri3.uri3.logs.filters.matches_level
  packages.uri3.uri3.logs.filters.matches_filters → packages.uri3.uri3.logs.filters.matches_logger
  packages.uri3.uri3.logs.filters.matches_filters → packages.uri3.uri3.logs.filters.matches_grep
  packages.uri3.uri3.logs.filters.matches_filters → packages.uri3.uri3.logs.filters.matches_time_window
  packages.uri3.uri3.logs.reader.resolve_log_path → packages.uri3.uri3.config.repo_root.find_repo_root
  packages.uri3.uri3.logs.reader.read_logs → packages.uri3.uri3.resolvers.log_resolver.parse_log_uri
  packages.uri3.uri3.logs.reader.read_logs → packages.uri3.uri3.logs.reader.resolve_log_path
  packages.uri3.uri3.logs.reader.read_logs → packages.uri3.uri3.logs.reader._parse_since
  packages.uri3.uri3.logs.reader.read_logs → packages.uri3.uri3.logs.parsing.parse_log_line
  packages.uri3.uri3.logs.reader.read_logs → packages.uri3.uri3.logs.filters.matches_filters
  packages.uri3.uri3.logs.reader.read_logs_result → packages.uri3.uri3.logs.reader.summarize_logs
  packages.uri3.uri3.logs.reader.read_logs_result → packages.uri3.uri3.logs.reader.read_logs
  packages.uri3.uri3.logs.reader.summarize_logs → packages.uri3.uri3.resolvers.log_resolver.parse_log_uri
  packages.uri3.uri3.logs.reader.summarize_logs → packages.uri3.uri3.logs.reader.resolve_log_path
  packages.uri3.uri3.logs.reader.summarize_logs → packages.uri3.uri3.logs.reader.read_logs
  packages.uri3.uri3.logs.writer.append_log → packages.uri3.uri3.config.repo_root.find_repo_root
  packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload → uri2ops.operation_registry.models.OperationRegistry.list
  packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload → packages.uri3.uri3.graph.graph_serializer.edges_from_depends_on
  packages.uri3.uri3.graph.graph_serializer.task_steps_to_graph → packages.uri3.uri3.graph.graph_serializer.edges_from_depends_on
  packages.uri3.uri3.graph.artifacts.write_artifact → packages.uri3.uri3.graph.artifacts.artifact_path
  packages.uri3.uri3.graph.artifacts.write_artifact → packages.uri3.uri3.graph.artifacts.artifact_uri
  packages.uri3.uri3.graph.dependency_graph.topological_sort → packages.uri3.uri3.graph.dependency_graph.detect_cycles
  packages.uri3.uri3.graph.dependency_graph.dependency_summary → packages.uri3.uri3.graph.dependency_graph.detect_cycles
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

WronAI resource agent monorepo — uri3, nl2uri, uri2flow, uri2ops, hypervisor, agent factory

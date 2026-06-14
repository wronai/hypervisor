# Resource Agent Meta-Factory v0.1

WronAI resource agent monorepo — uri3, nl2uri, hypervisor, agent factory

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
- **version**: `0.5.5`
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
  version: 0.5.5;
}

dependencies {
  runtime: "uri3, nl2uri, resource-agent-hypervisor, resource-agent-factory";
  dev: "pytest>=7.0, pytest-cov>=4.0, pytest-asyncio>=0.21.0, ruff>=0.1.0, mypy>=1.0, build>=1.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60, rich>=13.0.0";
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
  step-1: run cmd=python -m meta_agent.cli repair examples/broken_agent.yaml --write;
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
  keys: OPENROUTER_API_KEY, LLM_MODEL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, RESOURCE_RUNTIME_URL;
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
  vars: LLM_BASE_URL, LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE, OPENROUTER_API_KEY, RESOURCE_RUNTIME_URL;
  runtime_llm: OPENROUTER_API_KEY;
}
```

## Interfaces

### CLI Entry Points

- `hypervisor`
- `uri3`
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
  version: 0.5.5
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
uri3
nl2uri
resource-agent-hypervisor
resource-agent-factory
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

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`hypervisor`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `hypervisor/__init__.py:__version__`

## Makefile Targets

- `validate`
- `generate`
- `verify`
- `test`
- `run-user-agent`
- `run-meta-agent`
- `meta-plan`
- `meta-pipeline`
- `meta-repair`
- `clean`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# hypervisor | 162f 5721L | python:157,shell:4,less:1 | 2026-06-14
# stats: 258 func | 44 cls | 162 mod | CC̄=3.6 | critical:11 | cycles:0
# alerts[5]: CC validate_cross_references=22; CC main=20; CC validate_registry=20; CC test_nl2a_full_pipeline_weather_map=20; CC validate_config=17
# hotspots[5]: generate_agent fan=17; main fan=16; infer_intent fan=14; _call_openrouter fan=12; llm_plan fan=12
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[162]:
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
  app.doql.less,106
  domains/__init__.py,1
  domains/weather_map/__init__.py,1
  domains/weather_map/handlers/__init__.py,1
  domains/weather_map/handlers/generate_weather_map.py,25
  examples/01_quickstart_local/run.sh,8
  packages/nl2uri/nl2a/__init__.py,1
  packages/nl2uri/nl2a/cli.py,26
  packages/nl2uri/nl2uri/__init__.py,1
  packages/nl2uri/nl2uri/cli.py,17
  packages/nl2uri/nl2uri/domain_planner.py,152
  packages/nl2uri/nl2uri/llm_planner.py,19
  packages/nl2uri/nl2uri/pipeline.py,96
  packages/nl2uri/nl2uri/planner.py,33
  packages/nl2uri/nl2uri/prompts/__init__.py,1
  packages/nl2uri/nl2uri/writer.py,8
  packages/resource-agent-factory/generator/__init__.py,1
  packages/resource-agent-factory/generator/agent_generator.py,106
  packages/resource-agent-factory/generator/hashutil.py,10
  packages/resource-agent-factory/generator/header.py,52
  packages/resource-agent-factory/generator/model.py,95
  packages/resource-agent-factory/generator/paths.py,18
  packages/resource-agent-factory/generator/validate.py,70
  packages/resource-agent-factory/generator/verify.py,74
  packages/resource-agent-hypervisor/hypervisor/__init__.py,14
  packages/resource-agent-hypervisor/hypervisor/_version.py,21
  packages/resource-agent-hypervisor/hypervisor/cli.py,56
  packages/resource-agent-hypervisor/hypervisor/compatibility/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/compatibility/checker.py,44
  packages/resource-agent-hypervisor/hypervisor/config/__init__.py,25
  packages/resource-agent-hypervisor/hypervisor/config/defaults.py,64
  packages/resource-agent-hypervisor/hypervisor/config/env.py,55
  packages/resource-agent-hypervisor/hypervisor/config/loader.py,91
  packages/resource-agent-hypervisor/hypervisor/config/models.py,159
  packages/resource-agent-hypervisor/hypervisor/config/validators.py,58
  packages/resource-agent-hypervisor/hypervisor/contract_registry/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cli.py,78
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py,57
  packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py,81
  packages/resource-agent-hypervisor/hypervisor/contract_registry/merger.py,69
  packages/resource-agent-hypervisor/hypervisor/contract_registry/models.py,57
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py,61
  packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_exporter.py,30
  packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py,55
  packages/resource-agent-hypervisor/hypervisor/contract_registry/validate.py,51
  packages/resource-agent-hypervisor/hypervisor/core.py,87
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/__init__.py,34
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py,44
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py,48
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py,137
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py,46
  packages/resource-agent-hypervisor/hypervisor/domain_pack/__init__.py,32
  packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py,273
  packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py,116
  packages/resource-agent-hypervisor/hypervisor/domain_pack/writer.py,12
  packages/resource-agent-hypervisor/hypervisor/evolution/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/evolution/cli.py,34
  packages/resource-agent-hypervisor/hypervisor/evolution/models.py,33
  packages/resource-agent-hypervisor/hypervisor/evolution/validator.py,17
  packages/resource-agent-hypervisor/hypervisor/paths.py,19
  packages/resource-agent-hypervisor/hypervisor/policy_gate/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py,27
  packages/resource-agent-hypervisor/hypervisor/uri/__init__.py,1
  packages/resource-agent-hypervisor/hypervisor/uri/client.py,29
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
  packages/resource-agent-hypervisor/meta_agent/cli.py,94
  packages/resource-agent-hypervisor/meta_agent/domain_planner/__init__.py,2
  packages/resource-agent-hypervisor/meta_agent/domain_planner/domain_pack_generator.py,17
  packages/resource-agent-hypervisor/meta_agent/domain_planner/llm_planner.py,16
  packages/resource-agent-hypervisor/meta_agent/models.py,44
  packages/resource-agent-hypervisor/meta_agent/orchestrator.py,73
  packages/resource-agent-hypervisor/meta_agent/planner.py,160
  packages/resource-agent-hypervisor/meta_agent/repair/__init__.py,4
  packages/resource-agent-hypervisor/meta_agent/repair/loader.py,18
  packages/resource-agent-hypervisor/meta_agent/repair/pipeline.py,40
  packages/resource-agent-hypervisor/meta_agent/repair/rules.py,83
  packages/resource-agent-hypervisor/runtime_client/__init__.py,1
  packages/resource-agent-hypervisor/runtime_client/client.py,48
  packages/uri3/uri3/__init__.py,1
  packages/uri3/uri3/cli.py,37
  packages/uri3/uri3/discovery/__init__.py,1
  packages/uri3/uri3/graph/__init__.py,1
  packages/uri3/uri3/graph/uri_graph.py,52
  packages/uri3/uri3/paths.py,18
  packages/uri3/uri3/protocols/__init__.py,1
  packages/uri3/uri3/protocols/normalizer.py,10
  packages/uri3/uri3/protocols/parser.py,18
  packages/uri3/uri3/protocols/schemes.py,5
  packages/uri3/uri3/resolvers/__init__.py,4
  packages/uri3/uri3/resolvers/env_resolver.py,22
  packages/uri3/uri3/resolvers/http_resolver.py,21
  packages/uri3/uri3/resolvers/llm_resolver.py,46
  packages/uri3/uri3/resolvers/protocol_resolver.py,23
  packages/uri3/uri3/resolvers/pypi_resolver.py,17
  packages/uri3/uri3/resolvers/python_resolver.py,37
  packages/uri3/uri3/resolvers/router.py,88
  packages/uri3/uri3/scanner/__init__.py,1
  packages/uri3/uri3/scanner/base.py,8
  packages/uri3/uri3/scanner/http_scanner.py,17
  packages/uri3/uri3/scanner/scanner.py,8
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
  tests/hypervisor/test_config.py,74
  tests/hypervisor/test_deployment_registry.py,95
  tests/integration/__init__.py,2
  tests/integration/test_nl2a_e2e.py,93
  tests/meta_agent/__init__.py,2
  tests/meta_agent/test_repair.py,80
  tests/test_capability_tests.py,11
  tests/test_contract_registry.py,21
  tests/test_cross_validation_v03.py,6
  tests/test_evolution_proposal.py,9
  tests/test_generate.py,11
  tests/test_hypervisor.py,85
  tests/test_meta_agent.py,63
  tests/test_nl2a_v04.py,23
  tests/test_nl2uri.py,10
  tests/test_policy_gate.py,19
  tests/test_registry_builder_v03.py,21
  tests/test_runtime_client.py,9
  tests/test_schema_validation_v03.py,8
  tests/test_uri2llm_v04.py,22
  tests/test_uri3.py,12
  tests/test_uri_tree_validator.py,5
  tests/test_validate.py,9
  tests/uri3/__init__.py,2
  tests/uri3/test_resolvers.py,83
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
    e: generate,main
    generate(prompt;out;no_llm;json_out)
    main()
  packages/nl2uri/nl2uri/domain_planner.py:
    e: _slug,_llm_uri_from_env,_deterministic_weather_plan,_generic_plan,_extract_json,_call_openrouter,plan_from_prompt
    _slug(text)
    _llm_uri_from_env()
    _deterministic_weather_plan(prompt)
    _generic_plan(prompt)
    _extract_json(text)
    _call_openrouter(prompt)
    plan_from_prompt(prompt;use_llm)
  packages/nl2uri/nl2uri/llm_planner.py:
    e: llm_plan
    llm_plan(prompt)
  packages/nl2uri/nl2uri/pipeline.py:
    e: generate_tree,run_generate_pipeline,run_full_pipeline,PipelineResult,FullPipelineResult
    PipelineResult:
    FullPipelineResult:
    generate_tree(prompt)
    run_generate_pipeline(prompt)
    run_full_pipeline(prompt)
  packages/nl2uri/nl2uri/planner.py:
    e: _slug,rule_based_plan,PlanResult
    PlanResult:
    _slug(text)
    rule_based_plan(prompt)
  packages/nl2uri/nl2uri/prompts/__init__.py:
  packages/nl2uri/nl2uri/writer.py:
    e: write_uri_tree
    write_uri_tree(tree;out)
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
    e: find_repo_root,project_root
    find_repo_root(start)
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
    e: scan,resolve,status,config_cmd,main
    scan(uri)
    resolve(uri)
    status()
    config_cmd(path)
    main(argv)
  packages/resource-agent-hypervisor/hypervisor/compatibility/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/compatibility/checker.py:
    e: _load_policy,classify_registry_change
    _load_policy(root)
    classify_registry_change(old_root;new_root)
  packages/resource-agent-hypervisor/hypervisor/config/__init__.py:
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
  packages/resource-agent-hypervisor/hypervisor/config/validators.py:
    e: merge_config,validate_config
    merge_config(base;overlay)
    validate_config(cfg)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cli.py:
    e: main
    main(argv)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py:
    e: _load_proto_text,_schema_exists,validate_cross_references,validate_root
    _load_proto_text(root)
    _schema_exists(proto_text;schema_ref)
    validate_cross_references(registry)
    validate_root(root)
  packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py:
    e: _read_yaml,load_contract_registry
    _read_yaml(path)
    load_contract_registry(root)
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
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py:
    e: default_registry_path,_read_yaml,_parse_deployment,load_deployment_registry
    default_registry_path(root)
    _read_yaml(path)
    _parse_deployment(item)
    load_deployment_registry(root)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py:
    e: AgentDeployment,DeploymentRegistry
    AgentDeployment: to_dict(0)
    DeploymentRegistry: by_id(1),by_agent_ref(1)
  packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py:
    e: deployment_id_for_agent,infer_health_uri,infer_card_uri,deployment_from_uri_tree,sync_from_uri_tree,resolve_status,list_deployments,get_deployment_for_agent,registry_summary
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
  packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py:
    e: parse_uri_tree,derive_domain_model,generate_proto,generate_resources,generate_views,generate_commands,generate_renderers,generate_handlers,generate_agent_contract,write_domain_pack,generate_domain_pack_from_tree,generate_domain_pack,DomainModel
    DomainModel: from_uri_tree(3)
    parse_uri_tree(uri_tree_path)
    derive_domain_model(tree;out_dir)
    generate_proto(model)
    generate_resources(model)
    generate_views(resources)
    generate_commands(model)
    generate_renderers(model)
    generate_handlers(model)
    generate_agent_contract(model)
    write_domain_pack(model)
    generate_domain_pack_from_tree(tree;out_dir)
    generate_domain_pack(uri_tree_path;domain_dir)
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
    e: find_repo_root,repo_root
    find_repo_root(start)
    repo_root()
  packages/resource-agent-hypervisor/hypervisor/policy_gate/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py:
    e: evaluate_change,GateDecision
    GateDecision:
    evaluate_change(change_report;approved)
  packages/resource-agent-hypervisor/hypervisor/uri/__init__.py:
  packages/resource-agent-hypervisor/hypervisor/uri/client.py:
    e: Uri3Client
    Uri3Client: __init__(0),resolve(1),call(2),scan(1),graph(1),nl2uri(1)  # Thin hypervisor adapter over uri3 routing, scanning and grap
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
  packages/uri3/uri3/__init__.py:
  packages/uri3/uri3/cli.py:
    e: validate,validate_tree,graph,resolve,scan,main
    validate(uri)
    validate_tree(path)
    graph(path)
    resolve(uri)
    scan(uri)
    main()
  packages/uri3/uri3/discovery/__init__.py:
  packages/uri3/uri3/graph/__init__.py:
  packages/uri3/uri3/graph/uri_graph.py:
    e: build_graph_from_tree,UriNode,UriEdge,UriGraph
    UriNode:
    UriEdge:
    UriGraph: add_node(3),add_edge(3)
    build_graph_from_tree(path)
  packages/uri3/uri3/paths.py:
    e: find_repo_root,repo_root
    find_repo_root(start)
    repo_root()
  packages/uri3/uri3/protocols/__init__.py:
  packages/uri3/uri3/protocols/normalizer.py:
    e: normalize_uri
    normalize_uri(uri)
  packages/uri3/uri3/protocols/parser.py:
    e: parse_uri,ParsedURI
    ParsedURI:
    parse_uri(uri)
  packages/uri3/uri3/protocols/schemes.py:
  packages/uri3/uri3/resolvers/__init__.py:
  packages/uri3/uri3/resolvers/env_resolver.py:
    e: resolve_env,EnvResolver
    EnvResolver: resolve(1)
    resolve_env(uri)
  packages/uri3/uri3/resolvers/http_resolver.py:
    e: HttpResolver
    HttpResolver: resolve(1),fetch(1)
  packages/uri3/uri3/resolvers/llm_resolver.py:
    e: resolve_llm,LLMRef,LLMResolver
    LLMRef:
    LLMResolver: resolve(1)
    resolve_llm(uri)
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
  packages/uri3/uri3/resolvers/router.py:
    e: resolve,call,UriResolution,Uri3Router
    UriResolution:
    Uri3Router: __init__(0),resolve(1),call(2)
    resolve(uri)
    call(uri;payload)
  packages/uri3/uri3/scanner/__init__.py:
  packages/uri3/uri3/scanner/base.py:
    e: ScanItem
    ScanItem:
  packages/uri3/uri3/scanner/http_scanner.py:
    e: scan_http
    scan_http(base_url)
  packages/uri3/uri3/scanner/scanner.py:
    e: scan
    scan(uri)
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
  tests/hypervisor/test_config.py:
    e: test_default_config_has_structured_sections,test_load_config_merges_user_file,test_env_overrides,test_validate_config_reports_invalid_profile,test_load_hypervisor_config_model
    test_default_config_has_structured_sections()
    test_load_config_merges_user_file(tmp_path)
    test_env_overrides(monkeypatch)
    test_validate_config_reports_invalid_profile()
    test_load_hypervisor_config_model()
  tests/hypervisor/test_deployment_registry.py:
    e: test_load_default_deployments,test_deployment_from_weather_uri_tree,test_sync_from_uri_tree_writes_registry,test_upsert_replaces_existing_deployment,test_resolve_status_without_health_check,test_registry_summary,test_ssh_target_uri_supported_in_model
    test_load_default_deployments()
    test_deployment_from_weather_uri_tree()
    test_sync_from_uri_tree_writes_registry(tmp_path)
    test_upsert_replaces_existing_deployment(tmp_path)
    test_resolve_status_without_health_check()
    test_registry_summary()
    test_ssh_target_uri_supported_in_model(tmp_path)
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
  tests/uri3/__init__.py:
  tests/uri3/test_resolvers.py:
    e: test_env_uri_resolution,test_llm_uri_resolution,test_pypi_uri_resolution,test_python_uri_resolution,test_http_uri_resolution,test_a2a_uri_resolution,test_mcp_uri_resolution,test_resource_uri_resolution,test_python_call,test_router_resolve_returns_uri_resolution,test_unsupported_scheme,test_deprecated_uri2llm_reexport
    test_env_uri_resolution(monkeypatch)
    test_llm_uri_resolution()
    test_pypi_uri_resolution()
    test_python_uri_resolution()
    test_http_uri_resolution()
    test_a2a_uri_resolution()
    test_mcp_uri_resolution()
    test_resource_uri_resolution()
    test_python_call()
    test_router_resolve_returns_uri_resolution()
    test_unsupported_scheme()
    test_deprecated_uri2llm_reexport()
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('hypervisor', '0.5.5', 'python').

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
project_file('app.doql.less', 106, 'less').
project_file('domains/__init__.py', 1, 'python').
project_file('domains/weather_map/__init__.py', 1, 'python').
project_file('domains/weather_map/handlers/__init__.py', 1, 'python').
project_file('domains/weather_map/handlers/generate_weather_map.py', 25, 'python').
project_file('examples/01_quickstart_local/run.sh', 8, 'shell').
project_file('packages/nl2uri/nl2a/__init__.py', 1, 'python').
project_file('packages/nl2uri/nl2a/cli.py', 26, 'python').
project_file('packages/nl2uri/nl2uri/__init__.py', 1, 'python').
project_file('packages/nl2uri/nl2uri/cli.py', 17, 'python').
project_file('packages/nl2uri/nl2uri/domain_planner.py', 152, 'python').
project_file('packages/nl2uri/nl2uri/llm_planner.py', 19, 'python').
project_file('packages/nl2uri/nl2uri/pipeline.py', 96, 'python').
project_file('packages/nl2uri/nl2uri/planner.py', 33, 'python').
project_file('packages/nl2uri/nl2uri/prompts/__init__.py', 1, 'python').
project_file('packages/nl2uri/nl2uri/writer.py', 8, 'python').
project_file('packages/resource-agent-factory/generator/__init__.py', 1, 'python').
project_file('packages/resource-agent-factory/generator/agent_generator.py', 106, 'python').
project_file('packages/resource-agent-factory/generator/hashutil.py', 10, 'python').
project_file('packages/resource-agent-factory/generator/header.py', 52, 'python').
project_file('packages/resource-agent-factory/generator/model.py', 95, 'python').
project_file('packages/resource-agent-factory/generator/paths.py', 18, 'python').
project_file('packages/resource-agent-factory/generator/validate.py', 70, 'python').
project_file('packages/resource-agent-factory/generator/verify.py', 74, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/__init__.py', 14, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/_version.py', 21, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/cli.py', 56, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/compatibility/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/compatibility/checker.py', 44, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/__init__.py', 25, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/defaults.py', 64, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/env.py', 55, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/loader.py', 91, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/models.py', 159, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/config/validators.py', 58, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cli.py', 78, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py', 57, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py', 81, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/merger.py', 69, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/models.py', 57, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py', 61, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_exporter.py', 30, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', 55, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/contract_registry/validate.py', 51, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/core.py', 87, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/__init__.py', 34, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', 44, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', 48, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 137, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py', 46, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/__init__.py', 32, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 273, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 116, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/domain_pack/writer.py', 12, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/cli.py', 34, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/models.py', 33, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/evolution/validator.py', 17, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/paths.py', 19, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/policy_gate/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py', 27, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/hypervisor/uri/client.py', 29, 'python').
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
project_file('packages/resource-agent-hypervisor/meta_agent/cli.py', 94, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/domain_planner/__init__.py', 2, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/domain_planner/domain_pack_generator.py', 17, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/domain_planner/llm_planner.py', 16, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/models.py', 44, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/orchestrator.py', 73, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/planner.py', 160, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/repair/__init__.py', 4, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/repair/loader.py', 18, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/repair/pipeline.py', 40, 'python').
project_file('packages/resource-agent-hypervisor/meta_agent/repair/rules.py', 83, 'python').
project_file('packages/resource-agent-hypervisor/runtime_client/__init__.py', 1, 'python').
project_file('packages/resource-agent-hypervisor/runtime_client/client.py', 48, 'python').
project_file('packages/uri3/uri3/__init__.py', 1, 'python').
project_file('packages/uri3/uri3/cli.py', 37, 'python').
project_file('packages/uri3/uri3/discovery/__init__.py', 1, 'python').
project_file('packages/uri3/uri3/graph/__init__.py', 1, 'python').
project_file('packages/uri3/uri3/graph/uri_graph.py', 52, 'python').
project_file('packages/uri3/uri3/paths.py', 18, 'python').
project_file('packages/uri3/uri3/protocols/__init__.py', 1, 'python').
project_file('packages/uri3/uri3/protocols/normalizer.py', 10, 'python').
project_file('packages/uri3/uri3/protocols/parser.py', 18, 'python').
project_file('packages/uri3/uri3/protocols/schemes.py', 5, 'python').
project_file('packages/uri3/uri3/resolvers/__init__.py', 4, 'python').
project_file('packages/uri3/uri3/resolvers/env_resolver.py', 22, 'python').
project_file('packages/uri3/uri3/resolvers/http_resolver.py', 21, 'python').
project_file('packages/uri3/uri3/resolvers/llm_resolver.py', 46, 'python').
project_file('packages/uri3/uri3/resolvers/protocol_resolver.py', 23, 'python').
project_file('packages/uri3/uri3/resolvers/pypi_resolver.py', 17, 'python').
project_file('packages/uri3/uri3/resolvers/python_resolver.py', 37, 'python').
project_file('packages/uri3/uri3/resolvers/router.py', 88, 'python').
project_file('packages/uri3/uri3/scanner/__init__.py', 1, 'python').
project_file('packages/uri3/uri3/scanner/base.py', 8, 'python').
project_file('packages/uri3/uri3/scanner/http_scanner.py', 17, 'python').
project_file('packages/uri3/uri3/scanner/scanner.py', 8, 'python').
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
project_file('tests/hypervisor/test_config.py', 74, 'python').
project_file('tests/hypervisor/test_deployment_registry.py', 95, 'python').
project_file('tests/integration/__init__.py', 2, 'python').
project_file('tests/integration/test_nl2a_e2e.py', 93, 'python').
project_file('tests/meta_agent/__init__.py', 2, 'python').
project_file('tests/meta_agent/test_repair.py', 80, 'python').
project_file('tests/test_capability_tests.py', 11, 'python').
project_file('tests/test_contract_registry.py', 21, 'python').
project_file('tests/test_cross_validation_v03.py', 6, 'python').
project_file('tests/test_evolution_proposal.py', 9, 'python').
project_file('tests/test_generate.py', 11, 'python').
project_file('tests/test_hypervisor.py', 85, 'python').
project_file('tests/test_meta_agent.py', 63, 'python').
project_file('tests/test_nl2a_v04.py', 23, 'python').
project_file('tests/test_nl2uri.py', 10, 'python').
project_file('tests/test_policy_gate.py', 19, 'python').
project_file('tests/test_registry_builder_v03.py', 21, 'python').
project_file('tests/test_runtime_client.py', 9, 'python').
project_file('tests/test_schema_validation_v03.py', 8, 'python').
project_file('tests/test_uri2llm_v04.py', 22, 'python').
project_file('tests/test_uri3.py', 12, 'python').
project_file('tests/test_uri_tree_validator.py', 5, 'python').
project_file('tests/test_validate.py', 9, 'python').
project_file('tests/uri3/__init__.py', 2, 'python').
project_file('tests/uri3/test_resolvers.py', 83, 'python').
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
python_function('packages/nl2uri/nl2uri/cli.py', 'generate', 4, 4, 8).
python_function('packages/nl2uri/nl2uri/cli.py', 'main', 0, 1, 1).
python_function('packages/nl2uri/nl2uri/domain_planner.py', '_slug', 1, 2, 3).
python_function('packages/nl2uri/nl2uri/domain_planner.py', '_llm_uri_from_env', 0, 5, 3).
python_function('packages/nl2uri/nl2uri/domain_planner.py', '_deterministic_weather_plan', 1, 2, 2).
python_function('packages/nl2uri/nl2uri/domain_planner.py', '_generic_plan', 1, 1, 2).
python_function('packages/nl2uri/nl2uri/domain_planner.py', '_extract_json', 1, 3, 5).
python_function('packages/nl2uri/nl2uri/domain_planner.py', '_call_openrouter', 1, 4, 12).
python_function('packages/nl2uri/nl2uri/domain_planner.py', 'plan_from_prompt', 2, 6, 5).
python_function('packages/nl2uri/nl2uri/llm_planner.py', 'llm_plan', 1, 4, 12).
python_function('packages/nl2uri/nl2uri/pipeline.py', 'generate_tree', 1, 1, 1).
python_function('packages/nl2uri/nl2uri/pipeline.py', 'run_generate_pipeline', 1, 3, 9).
python_function('packages/nl2uri/nl2uri/pipeline.py', 'run_full_pipeline', 1, 2, 8).
python_function('packages/nl2uri/nl2uri/planner.py', '_slug', 1, 2, 3).
python_function('packages/nl2uri/nl2uri/planner.py', 'rule_based_plan', 1, 8, 5).
python_function('packages/nl2uri/nl2uri/writer.py', 'write_uri_tree', 2, 1, 4).
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
python_function('packages/resource-agent-factory/generator/paths.py', 'find_repo_root', 1, 6, 5).
python_function('packages/resource-agent-factory/generator/paths.py', 'project_root', 0, 1, 1).
python_function('packages/resource-agent-factory/generator/validate.py', 'validate_agent', 1, 11, 4).
python_function('packages/resource-agent-factory/generator/validate.py', 'iter_agent_specs', 1, 3, 4).
python_function('packages/resource-agent-factory/generator/validate.py', 'main', 1, 7, 6).
python_function('packages/resource-agent-factory/generator/verify.py', 'verify_generated_agent', 1, 7, 7).
python_function('packages/resource-agent-factory/generator/verify.py', 'verify_generated', 1, 6, 5).
python_function('packages/resource-agent-factory/generator/verify.py', 'main', 1, 9, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'scan', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'resolve', 1, 1, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'status', 0, 2, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'config_cmd', 1, 2, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/cli.py', 'main', 1, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/compatibility/checker.py', '_load_policy', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/compatibility/checker.py', 'classify_registry_change', 2, 8, 6).
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
python_function('packages/resource-agent-hypervisor/hypervisor/config/loader.py', 'load_config', 1, 2, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/config/loader.py', 'get_config', 0, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/config/loader.py', 'load_hypervisor_config', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/config/validators.py', 'merge_config', 2, 5, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/config/validators.py', 'validate_config', 1, 17, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cli.py', 'main', 1, 20, 11).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py', '_load_proto_text', 1, 2, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py', '_schema_exists', 2, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py', 'validate_cross_references', 1, 22, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/cross_validator.py', 'validate_root', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py', '_read_yaml', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py', 'load_contract_registry', 1, 9, 11).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/merger.py', 'merge_main_contracts', 4, 12, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py', '_hash_file', 1, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py', '_contract_hash', 1, 3, 10).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py', 'build_registry_manifest', 1, 5, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_builder.py', 'write_registry_manifest', 2, 2, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_exporter.py', 'export_json', 2, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/registry_exporter.py', 'export_markdown', 2, 6, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', '_read_yaml', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', '_read_json', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', 'validate_file', 2, 3, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/schema_validator.py', 'validate_contract_files', 1, 6, 6).
python_function('packages/resource-agent-hypervisor/hypervisor/contract_registry/validate.py', 'validate_registry', 1, 20, 8).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', 'default_registry_path', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', '_read_yaml', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', '_parse_deployment', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py', 'load_deployment_registry', 1, 5, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'deployment_id_for_agent', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'infer_health_uri', 2, 4, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'infer_card_uri', 2, 5, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'deployment_from_uri_tree', 1, 8, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'sync_from_uri_tree', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'resolve_status', 1, 11, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'list_deployments', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'get_deployment_for_agent', 1, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/status.py', 'registry_summary', 1, 3, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py', 'save_deployment_registry', 1, 2, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py', 'upsert_deployment', 2, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py', 'remove_deployment', 2, 3, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/deployment_registry/writer.py', 'write_deployment_registry', 1, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'parse_uri_tree', 1, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'derive_domain_model', 2, 1, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'generate_proto', 1, 2, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'generate_resources', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'generate_views', 1, 2, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'generate_commands', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'generate_renderers', 1, 3, 4).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'generate_handlers', 1, 3, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'generate_agent_contract', 1, 2, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'write_domain_pack', 1, 3, 9).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'generate_domain_pack_from_tree', 2, 2, 11).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'generate_domain_pack', 2, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'package_name', 1, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'generic_proto', 1, 1, 1).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'weather_proto', 0, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'weather_handler', 0, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py', 'generic_handler', 0, 1, 0).
python_function('packages/resource-agent-hypervisor/hypervisor/domain_pack/writer.py', 'write_file', 2, 1, 3).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/cli.py', 'main', 1, 10, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/models.py', 'load_proposal', 1, 5, 7).
python_function('packages/resource-agent-hypervisor/hypervisor/evolution/validator.py', 'validate_proposal', 1, 6, 2).
python_function('packages/resource-agent-hypervisor/hypervisor/paths.py', 'find_repo_root', 1, 6, 5).
python_function('packages/resource-agent-hypervisor/hypervisor/paths.py', 'repo_root', 0, 1, 1).
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
python_function('packages/resource-agent-hypervisor/meta_agent/cli.py', 'main', 0, 16, 16).
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
python_function('packages/uri3/uri3/cli.py', 'validate', 1, 1, 3).
python_function('packages/uri3/uri3/cli.py', 'validate_tree', 1, 3, 4).
python_function('packages/uri3/uri3/cli.py', 'graph', 1, 3, 5).
python_function('packages/uri3/uri3/cli.py', 'resolve', 1, 2, 8).
python_function('packages/uri3/uri3/cli.py', 'scan', 1, 2, 4).
python_function('packages/uri3/uri3/cli.py', 'main', 0, 1, 1).
python_function('packages/uri3/uri3/graph/uri_graph.py', 'build_graph_from_tree', 1, 10, 9).
python_function('packages/uri3/uri3/paths.py', 'find_repo_root', 1, 6, 5).
python_function('packages/uri3/uri3/paths.py', 'repo_root', 0, 1, 1).
python_function('packages/uri3/uri3/protocols/normalizer.py', 'normalize_uri', 1, 3, 3).
python_function('packages/uri3/uri3/protocols/parser.py', 'parse_uri', 1, 2, 4).
python_function('packages/uri3/uri3/resolvers/env_resolver.py', 'resolve_env', 1, 3, 4).
python_function('packages/uri3/uri3/resolvers/llm_resolver.py', 'resolve_llm', 1, 5, 4).
python_function('packages/uri3/uri3/resolvers/protocol_resolver.py', 'resolve_http_like', 1, 1, 0).
python_function('packages/uri3/uri3/resolvers/protocol_resolver.py', 'resolve_a2a', 1, 2, 1).
python_function('packages/uri3/uri3/resolvers/protocol_resolver.py', 'resolve_mcp', 1, 2, 1).
python_function('packages/uri3/uri3/resolvers/protocol_resolver.py', 'resolve_resource', 1, 1, 1).
python_function('packages/uri3/uri3/resolvers/pypi_resolver.py', 'resolve_pypi', 1, 5, 4).
python_function('packages/uri3/uri3/resolvers/python_resolver.py', '_split_python_uri', 1, 2, 4).
python_function('packages/uri3/uri3/resolvers/python_resolver.py', 'resolve_python', 1, 1, 1).
python_function('packages/uri3/uri3/resolvers/python_resolver.py', 'call_python', 2, 1, 4).
python_function('packages/uri3/uri3/resolvers/router.py', 'resolve', 1, 2, 11).
python_function('packages/uri3/uri3/resolvers/router.py', 'call', 2, 1, 3).
python_function('packages/uri3/uri3/scanner/http_scanner.py', 'scan_http', 1, 6, 6).
python_function('packages/uri3/uri3/scanner/scanner.py', 'scan', 1, 2, 2).
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
python_function('tests/hypervisor/test_config.py', 'test_default_config_has_structured_sections', 0, 8, 2).
python_function('tests/hypervisor/test_config.py', 'test_load_config_merges_user_file', 1, 7, 2).
python_function('tests/hypervisor/test_config.py', 'test_env_overrides', 1, 4, 2).
python_function('tests/hypervisor/test_config.py', 'test_validate_config_reports_invalid_profile', 0, 3, 2).
python_function('tests/hypervisor/test_config.py', 'test_load_hypervisor_config_model', 0, 5, 4).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_load_default_deployments', 0, 4, 4).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_deployment_from_weather_uri_tree', 0, 5, 2).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_sync_from_uri_tree_writes_registry', 1, 4, 5).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_upsert_replaces_existing_deployment', 1, 2, 6).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_resolve_status_without_health_check', 0, 2, 2).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_registry_summary', 0, 3, 4).
python_function('tests/hypervisor/test_deployment_registry.py', 'test_ssh_target_uri_supported_in_model', 1, 2, 9).
python_function('tests/integration/test_nl2a_e2e.py', 'isolated_project', 2, 3, 7).
python_function('tests/integration/test_nl2a_e2e.py', 'test_nl2a_full_pipeline_weather_map', 1, 20, 9).
python_function('tests/integration/test_nl2a_e2e.py', 'test_nl2a_cli_generate_no_llm', 1, 8, 4).
python_function('tests/meta_agent/test_repair.py', 'test_repair_agent_block_fills_metadata', 0, 5, 1).
python_function('tests/meta_agent/test_repair.py', 'test_repair_resource_read_fills_renderer_and_schema', 0, 3, 1).
python_function('tests/meta_agent/test_repair.py', 'test_repair_command_fills_fields', 0, 3, 1).
python_function('tests/meta_agent/test_repair.py', 'test_repair_capabilities_deduplicates_names', 0, 3, 3).
python_function('tests/meta_agent/test_repair.py', 'test_repair_agent_spec_integration', 1, 4, 6).
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
python_function('tests/test_hypervisor.py', 'test_cli_status_runs', 1, 4, 2).
python_function('tests/test_hypervisor.py', 'test_cli_config_path', 1, 3, 3).
python_function('tests/test_meta_agent.py', 'test_save_proposal_from_prompt', 1, 4, 5).
python_function('tests/test_meta_agent.py', 'test_repair_broken_agent', 1, 6, 8).
python_function('tests/test_meta_agent.py', 'test_pipeline_from_prompt_generates_agent', 1, 5, 5).
python_function('tests/test_nl2a_v04.py', 'test_weather_prompt_generates_uri_tree', 0, 5, 1).
python_function('tests/test_nl2a_v04.py', 'test_domain_pack_generation', 1, 6, 4).
python_function('tests/test_nl2uri.py', 'test_weather_prompt_generates_weather_uri_tree', 0, 5, 1).
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
python_function('tests/uri3/test_resolvers.py', 'test_env_uri_resolution', 1, 4, 2).
python_function('tests/uri3/test_resolvers.py', 'test_llm_uri_resolution', 0, 4, 1).
python_function('tests/uri3/test_resolvers.py', 'test_pypi_uri_resolution', 0, 2, 1).
python_function('tests/uri3/test_resolvers.py', 'test_python_uri_resolution', 0, 3, 1).
python_function('tests/uri3/test_resolvers.py', 'test_http_uri_resolution', 0, 2, 1).
python_function('tests/uri3/test_resolvers.py', 'test_a2a_uri_resolution', 0, 3, 1).
python_function('tests/uri3/test_resolvers.py', 'test_mcp_uri_resolution', 0, 2, 1).
python_function('tests/uri3/test_resolvers.py', 'test_resource_uri_resolution', 0, 3, 1).
python_function('tests/uri3/test_resolvers.py', 'test_python_call', 0, 2, 1).
python_function('tests/uri3/test_resolvers.py', 'test_router_resolve_returns_uri_resolution', 0, 2, 4).
python_function('tests/uri3/test_resolvers.py', 'test_unsupported_scheme', 0, 1, 2).
python_function('tests/uri3/test_resolvers.py', 'test_deprecated_uri2llm_reexport', 0, 3, 5).

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
python_method('Hypervisor', 'start', 0, 2, 1).
python_method('Hypervisor', 'stop', 0, 2, 1).
python_method('Hypervisor', 'register_agent', 1, 3, 3).
python_method('Hypervisor', 'status', 0, 1, 2).
python_method('Hypervisor', '__repr__', 0, 1, 1).
python_class('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', 'AgentDeployment').
python_method('AgentDeployment', 'to_dict', 0, 4, 0).
python_class('packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py', 'DeploymentRegistry').
python_method('DeploymentRegistry', 'by_id', 1, 3, 1).
python_method('DeploymentRegistry', 'by_agent_ref', 1, 3, 0).
python_class('packages/resource-agent-hypervisor/hypervisor/domain_pack/generator.py', 'DomainModel').
python_method('DomainModel', 'from_uri_tree', 3, 1, 1).
python_class('packages/resource-agent-hypervisor/hypervisor/evolution/models.py', 'EvolutionProposal').
python_class('packages/resource-agent-hypervisor/hypervisor/policy_gate/gate.py', 'GateDecision').
python_class('packages/resource-agent-hypervisor/hypervisor/uri/client.py', 'Uri3Client').
python_method('Uri3Client', '__init__', 0, 1, 1).
python_method('Uri3Client', 'resolve', 1, 1, 1).
python_method('Uri3Client', 'call', 2, 1, 1).
python_method('Uri3Client', 'scan', 1, 1, 1).
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
python_class('packages/uri3/uri3/graph/uri_graph.py', 'UriNode').
python_class('packages/uri3/uri3/graph/uri_graph.py', 'UriEdge').
python_class('packages/uri3/uri3/graph/uri_graph.py', 'UriGraph').
python_method('UriGraph', 'add_node', 3, 3, 1).
python_method('UriGraph', 'add_edge', 3, 3, 2).
python_class('packages/uri3/uri3/protocols/parser.py', 'ParsedURI').
python_class('packages/uri3/uri3/resolvers/env_resolver.py', 'EnvResolver').
python_method('EnvResolver', 'resolve', 1, 1, 1).
python_class('packages/uri3/uri3/resolvers/http_resolver.py', 'HttpResolver').
python_method('HttpResolver', 'resolve', 1, 1, 1).
python_method('HttpResolver', 'fetch', 1, 2, 3).
python_class('packages/uri3/uri3/resolvers/llm_resolver.py', 'LLMRef').
python_class('packages/uri3/uri3/resolvers/llm_resolver.py', 'LLMResolver').
python_method('LLMResolver', 'resolve', 1, 2, 4).
python_class('packages/uri3/uri3/resolvers/python_resolver.py', 'PythonResolver').
python_method('PythonResolver', 'resolve', 1, 1, 1).
python_method('PythonResolver', 'call', 2, 2, 1).
python_class('packages/uri3/uri3/resolvers/router.py', 'UriResolution').
python_class('packages/uri3/uri3/resolvers/router.py', 'Uri3Router').
python_method('Uri3Router', '__init__', 0, 1, 4).
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
makefile_target('run-user-agent', '').
makefile_target('run-meta-agent', '').
makefile_target('meta-plan', '').
makefile_target('meta-pipeline', '').
makefile_target('meta-repair', '').
makefile_target('clean', '').

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', 'sk-or-v1-...', '').
env_variable('LLM_MODEL', 'llm://openrouter/qwen/qwen3-coder-next', '').
env_variable('LLM_BASE_URL', 'https://openrouter.ai/api/v1', '').
env_variable('LLM_TEMPERATURE', '0.1', '').
env_variable('LLM_MAX_TOKENS', '8000', '').
env_variable('RESOURCE_RUNTIME_URL', 'http://localhost:8000', '').

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
sumd_workflow('validate', 'manual').
sumd_workflow_step('validate', 1, 'python -m generator.validate contracts').
sumd_workflow('generate', 'manual').
sumd_workflow_step('generate', 1, 'python -m generator.agent_generator contracts/agents/*.yaml').
sumd_workflow('verify', 'manual').
sumd_workflow_step('verify', 1, 'python -m generator.verify agents/generated').
sumd_workflow('test', 'manual').
sumd_workflow_step('test', 1, 'pytest -q').
sumd_workflow('run-user-agent', 'manual').
sumd_workflow_step('run-user-agent', 1, 'uvicorn agents.generated.user_agent.main:app --reload --port 8101').
sumd_workflow('run-meta-agent', 'manual').
sumd_workflow_step('run-meta-agent', 1, 'uvicorn meta_agent.api:app --reload --port 8200').
sumd_workflow('meta-plan', 'manual').
sumd_workflow_step('meta-plan', 1, 'python -m meta_agent.cli plan "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia"').
sumd_workflow('meta-pipeline', 'manual').
sumd_workflow_step('meta-pipeline', 1, 'python -m meta_agent.cli pipeline "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia"').
sumd_workflow('meta-repair', 'manual').
sumd_workflow_step('meta-repair', 1, 'python -m meta_agent.cli repair examples/broken_agent.yaml --write').
sumd_workflow('clean', 'manual').
sumd_workflow_step('clean', 1, 'rm -rf agents/generated/* output/* .pytest_cache').
sumd_deploy_target('docker_compose').
sumd_deploy_compose_file('docker-compose.yml').
```

## Call Graph

*147 nodes · 155 edges · 60 modules · CC̄=3.3*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `load_contract_registry` *(in hypervisor.contract_registry.loader)* | 9 | 6 | 33 | **39** |
| `merge_main_contracts` *(in hypervisor.contract_registry.merger)* | 12 ⚠ | 1 | 31 | **32** |
| `write_domain_pack` *(in hypervisor.domain_pack.generator)* | 3 | 1 | 30 | **31** |
| `infer_intent` *(in meta_agent.planner)* | 9 | 1 | 30 | **31** |
| `build_graph_from_tree` *(in uri3.graph.uri_graph)* | 10 ⚠ | 2 | 28 | **30** |
| `load_agent_spec` *(in generator.model)* | 7 | 2 | 24 | **26** |
| `main` *(in hypervisor.contract_registry.cli)* | 20 ⚠ | 0 | 26 | **26** |
| `validate_registry` *(in hypervisor.contract_registry.validate)* | 20 ⚠ | 2 | 20 | **22** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/hypervisor
# generated in 0.06s
# nodes: 147 | edges: 155 | modules: 60
# CC̄=3.3

HUBS[20]:
  hypervisor.contract_registry.loader.load_contract_registry
    CC=9  in:6  out:33  total:39
  hypervisor.contract_registry.merger.merge_main_contracts
    CC=12  in:1  out:31  total:32
  hypervisor.domain_pack.generator.write_domain_pack
    CC=3  in:1  out:30  total:31
  meta_agent.planner.infer_intent
    CC=9  in:1  out:30  total:31
  uri3.graph.uri_graph.build_graph_from_tree
    CC=10  in:2  out:28  total:30
  generator.model.load_agent_spec
    CC=7  in:2  out:24  total:26
  hypervisor.contract_registry.cli.main
    CC=20  in:0  out:26  total:26
  hypervisor.contract_registry.validate.validate_registry
    CC=20  in:2  out:20  total:22
  generator.agent_generator.generate_agent
    CC=5  in:3  out:17  total:20
  hypervisor.config.defaults.apply_builtin_defaults
    CC=1  in:2  out:17  total:19
  meta_agent.orchestrator.validate_repair_generate
    CC=7  in:3  out:16  total:19
  hypervisor.domain_pack.writer.write_file
    CC=1  in:15  out:3  total:18
  hypervisor.config.env.apply_structured_env_overrides
    CC=9  in:1  out:17  total:18
  hypervisor.deployment_registry.status.deployment_from_uri_tree
    CC=8  in:1  out:17  total:18
  nl2uri.domain_planner._call_openrouter
    CC=4  in:1  out:17  total:18
  generator.validate.validate_agent
    CC=11  in:8  out:10  total:18
  nl2uri.llm_planner.llm_plan
    CC=4  in:1  out:16  total:17
  meta_agent.repair.rules.repair_resource_read_capability
    CC=8  in:1  out:14  total:15
  hypervisor.contract_registry.schema_validator.validate_contract_files
    CC=6  in:2  out:13  total:15
  meta_agent.repair.pipeline.repair_agent_spec
    CC=2  in:3  out:12  total:15

MODULES:
  generator.agent_generator  [3 funcs]
    expand_paths  CC=4  out:7
    generate_agent  CC=5  out:17
    main  CC=5  out:4
  generator.hashutil  [1 funcs]
    file_sha256  CC=1  out:4
  generator.header  [4 funcs]
    contract_source_ref  CC=3  out:7
    dockerfile_header  CC=1  out:0
    project_root  CC=1  out:2
    python_file_header  CC=1  out:0
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
  hypervisor.cli  [1 funcs]
    config_cmd  CC=2  out:8
  hypervisor.compatibility.checker  [1 funcs]
    classify_registry_change  CC=8  out:11
  hypervisor.config.defaults  [4 funcs]
    apply_builtin_defaults  CC=1  out:17
    embedded_defaults_raw  CC=1  out:1
    get_default_config  CC=1  out:3
    load_yaml_file  CC=4  out:4
  hypervisor.config.env  [4 funcs]
    _parse_bool  CC=1  out:1
    apply_env_overrides  CC=1  out:2
    apply_legacy_env_overrides  CC=6  out:4
    apply_structured_env_overrides  CC=9  out:17
  hypervisor.config.loader  [5 funcs]
    config_search_paths  CC=6  out:11
    get_config  CC=1  out:1
    load_config  CC=2  out:7
    load_hypervisor_config  CC=1  out:2
    resolve_config_path  CC=3  out:2
  hypervisor.config.validators  [1 funcs]
    merge_config  CC=5  out:5
  hypervisor.contract_registry.cli  [1 funcs]
    main  CC=20  out:26
  hypervisor.contract_registry.cross_validator  [4 funcs]
    _load_proto_text  CC=2  out:5
    _schema_exists  CC=1  out:3
    validate_cross_references  CC=22  out:11
    validate_root  CC=1  out:2
  hypervisor.contract_registry.loader  [2 funcs]
    _read_yaml  CC=3  out:4
    load_contract_registry  CC=9  out:33
  hypervisor.contract_registry.merger  [1 funcs]
    merge_main_contracts  CC=12  out:31
  hypervisor.contract_registry.registry_builder  [3 funcs]
    _contract_hash  CC=3  out:13
    build_registry_manifest  CC=5  out:9
    write_registry_manifest  CC=2  out:6
  hypervisor.contract_registry.registry_exporter  [2 funcs]
    export_json  CC=1  out:1
    export_markdown  CC=6  out:13
  hypervisor.contract_registry.schema_validator  [4 funcs]
    _read_json  CC=1  out:2
    _read_yaml  CC=2  out:2
    validate_contract_files  CC=6  out:13
    validate_file  CC=3  out:8
  hypervisor.contract_registry.validate  [1 funcs]
    validate_registry  CC=20  out:20
  hypervisor.core  [1 funcs]
    from_config  CC=1  out:2
  hypervisor.deployment_registry.loader  [4 funcs]
    _parse_deployment  CC=2  out:10
    _read_yaml  CC=3  out:4
    default_registry_path  CC=1  out:1
    load_deployment_registry  CC=5  out:8
  hypervisor.deployment_registry.status  [5 funcs]
    deployment_from_uri_tree  CC=8  out:17
    get_deployment_for_agent  CC=3  out:2
    list_deployments  CC=2  out:2
    registry_summary  CC=3  out:1
    sync_from_uri_tree  CC=2  out:4
  hypervisor.deployment_registry.writer  [3 funcs]
    save_deployment_registry  CC=2  out:4
    upsert_deployment  CC=3  out:2
    write_deployment_registry  CC=1  out:2
  hypervisor.domain_pack.generator  [12 funcs]
    derive_domain_model  CC=1  out:2
    generate_agent_contract  CC=2  out:3
    generate_commands  CC=2  out:6
    generate_domain_pack  CC=1  out:3
    generate_domain_pack_from_tree  CC=2  out:11
    generate_handlers  CC=3  out:2
    generate_proto  CC=2  out:2
    generate_renderers  CC=3  out:5
    generate_resources  CC=2  out:5
    generate_views  CC=2  out:1
  hypervisor.domain_pack.templates  [2 funcs]
    generic_proto  CC=1  out:1
    package_name  CC=1  out:0
  hypervisor.domain_pack.writer  [2 funcs]
    repo_root  CC=1  out:2
    write_file  CC=1  out:3
  hypervisor.evolution.cli  [1 funcs]
    main  CC=10  out:11
  hypervisor.evolution.models  [1 funcs]
    load_proposal  CC=5  out:11
  hypervisor.evolution.validator  [1 funcs]
    validate_proposal  CC=6  out:6
  hypervisor.uri.client  [2 funcs]
    graph  CC=1  out:1
    nl2uri  CC=1  out:1
  hypervisor.uri2llm.protocol_resolver  [1 funcs]
    resolve_http_like  CC=1  out:0
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
  meta_agent.orchestrator  [4 funcs]
    asdict_result  CC=1  out:0
    pipeline_from_prompt  CC=1  out:2
    save_proposal_from_prompt  CC=2  out:6
    validate_repair_generate  CC=7  out:16
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
  nl2uri.cli  [1 funcs]
    generate  CC=4  out:12
  nl2uri.domain_planner  [7 funcs]
    _call_openrouter  CC=4  out:17
    _deterministic_weather_plan  CC=2  out:2
    _extract_json  CC=3  out:8
    _generic_plan  CC=1  out:3
    _llm_uri_from_env  CC=5  out:5
    _slug  CC=2  out:3
    plan_from_prompt  CC=6  out:8
  nl2uri.llm_planner  [1 funcs]
    llm_plan  CC=4  out:16
  nl2uri.pipeline  [3 funcs]
    generate_tree  CC=1  out:1
    run_full_pipeline  CC=2  out:9
    run_generate_pipeline  CC=3  out:11
  nl2uri.planner  [2 funcs]
    _slug  CC=2  out:4
    rule_based_plan  CC=8  out:6
  nl2uri.writer  [1 funcs]
    write_uri_tree  CC=1  out:4
  uri3.cli  [3 funcs]
    graph  CC=3  out:5
    validate  CC=1  out:3
    validate_tree  CC=3  out:5
  uri3.graph.uri_graph  [1 funcs]
    build_graph_from_tree  CC=10  out:28
  uri3.protocols.normalizer  [1 funcs]
    normalize_uri  CC=3  out:4
  uri3.protocols.parser  [1 funcs]
    parse_uri  CC=2  out:4
  uri3.resolvers.env_resolver  [2 funcs]
    resolve  CC=1  out:1
    resolve_env  CC=3  out:4
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
  uri3.resolvers.router  [1 funcs]
    call  CC=3  out:3
  uri3.scanner.http_scanner  [1 funcs]
    scan_http  CC=6  out:8
  uri3.scanner.scanner  [1 funcs]
    scan  CC=2  out:2
  uri3.validators.uri_tree_validator  [2 funcs]
    load_yaml  CC=1  out:2
    validate_uri_tree  CC=2  out:7
  uri3.validators.uri_validator  [1 funcs]
    validate_uri  CC=2  out:2

EDGES:
  generator.validate.validate_agent → generator.model.load_agent_spec
  generator.validate.main → generator.validate.iter_agent_specs
  generator.validate.main → generator.validate.validate_agent
  meta_agent.planner.infer_intent → meta_agent.planner.singularize
  meta_agent.planner.intent_to_agent_spec → meta_agent.planner.singularize
  meta_agent.planner.intent_to_agent_spec → meta_agent.planner.package_name
  meta_agent.api.proposal_from_prompt → meta_agent.orchestrator.save_proposal_from_prompt
  meta_agent.api.validate → generator.validate.validate_agent
  meta_agent.api.repair → meta_agent.repair.pipeline.repair_agent_spec
  meta_agent.api.generate → meta_agent.orchestrator.asdict_result
  meta_agent.api.generate → meta_agent.orchestrator.validate_repair_generate
  meta_agent.api.pipeline → meta_agent.orchestrator.pipeline_from_prompt
  meta_agent.api.pipeline → meta_agent.orchestrator.asdict_result
  meta_agent.api.verify → generator.verify.verify_generated
  uri3.cli.validate → uri3.validators.uri_validator.validate_uri
  uri3.cli.validate_tree → uri3.validators.uri_tree_validator.validate_uri_tree
  uri3.cli.graph → uri3.graph.uri_graph.build_graph_from_tree
  uri3.validators.uri_validator.validate_uri → uri3.protocols.parser.parse_uri
  uri3.validators.uri_tree_validator.validate_uri_tree → uri3.validators.uri_tree_validator.load_yaml
  uri3.scanner.scanner.scan → uri3.scanner.http_scanner.scan_http
  uri3.scanner.scanner.scan → uri3.protocols.parser.parse_uri
  uri3.protocols.normalizer.normalize_uri → uri3.protocols.parser.parse_uri
  uri3.resolvers.http_resolver.HttpResolver.resolve → hypervisor.uri2llm.protocol_resolver.resolve_http_like
  uri3.resolvers.llm_resolver.LLMResolver.resolve → uri3.resolvers.llm_resolver.resolve_llm
  uri3.resolvers.llm_resolver.LLMResolver.resolve → uri3.protocols.parser.parse_uri
  uri3.resolvers.router.call → uri3.resolvers.python_resolver.call_python
  uri3.resolvers.env_resolver.EnvResolver.resolve → uri3.resolvers.env_resolver.resolve_env
  uri3.resolvers.python_resolver.resolve_python → uri3.resolvers.python_resolver._split_python_uri
  uri3.resolvers.python_resolver.call_python → uri3.resolvers.python_resolver._split_python_uri
  uri3.resolvers.python_resolver.PythonResolver.resolve → uri3.resolvers.python_resolver.resolve_python
  uri3.resolvers.python_resolver.PythonResolver.call → uri3.resolvers.python_resolver.call_python
  hypervisor.cli.config_cmd → hypervisor.config.loader.load_config
  hypervisor.cli.config_cmd → hypervisor.config.loader.get_config
  hypervisor.core.Hypervisor.from_config → hypervisor.config.loader.load_config
  hypervisor.domain_pack.templates.generic_proto → hypervisor.domain_pack.templates.package_name
  hypervisor.verifier.cli.main → hypervisor.contract_registry.loader.load_contract_registry
  hypervisor.verifier.cli.main → hypervisor.contract_registry.validate.validate_registry
  hypervisor.verifier.cli.main → hypervisor.verifier.capability_tests.build_capability_test_plan
  hypervisor.evolution.cli.main → hypervisor.evolution.models.load_proposal
  hypervisor.evolution.cli.main → hypervisor.evolution.validator.validate_proposal
  hypervisor.uri.client.Uri3Client.graph → uri3.graph.uri_graph.build_graph_from_tree
  hypervisor.uri.client.Uri3Client.nl2uri → nl2uri.planner.rule_based_plan
  hypervisor.contract_registry.loader.load_contract_registry → hypervisor.contract_registry.loader._read_yaml
  hypervisor.contract_registry.cli.main → hypervisor.contract_registry.schema_validator.validate_contract_files
  hypervisor.contract_registry.cli.main → hypervisor.contract_registry.loader.load_contract_registry
  hypervisor.contract_registry.cli.main → hypervisor.contract_registry.validate.validate_registry
  hypervisor.contract_registry.cli.main → hypervisor.contract_registry.cross_validator.validate_root
  hypervisor.contract_registry.cli.main → hypervisor.contract_registry.registry_builder.write_registry_manifest
  hypervisor.contract_registry.registry_exporter.export_json → hypervisor.contract_registry.registry_builder.write_registry_manifest
  hypervisor.contract_registry.registry_exporter.export_markdown → hypervisor.contract_registry.registry_builder.build_registry_manifest
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

WronAI resource agent monorepo — uri3, nl2uri, hypervisor, agent factory

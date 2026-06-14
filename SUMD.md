# Resource Agent Meta-Factory v0.1

WronAI Hypervisor — orchestrator and control plane for AI desktop agents, NLP-to-URI resolution, koru drivers, and virtualized execution

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
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `hypervisor`
- **version**: `0.1.0`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(3), app.doql.less, goal.yaml, .env.example, Dockerfile, docker-compose.yml, src(4 mod), project/(3 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: hypervisor;
  version: 0.1.0;
}

dependencies {
  runtime: "pyyaml>=6.0, python-dotenv>=1.0.0";
  dev: "pytest>=7.0, pytest-cov>=4.0, pytest-asyncio>=0.21.0, ruff>=0.1.0, mypy>=1.0, build>=1.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
  cli: rich>=13.0.0;
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

### Source Modules

- `hypervisor._version`
- `hypervisor.cli`
- `hypervisor.config`
- `hypervisor.core`

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
  name: hypervisor
  version: 0.1.0
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
pyyaml>=6.0
python-dotenv>=1.0.0
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
```

## Deployment

```bash markpact:run
pip install hypervisor

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
- **version files**: `VERSION`, `pyproject.toml:version`, `.venv/lib/python3.13/site-packages/_pytest/__init__.py:__version__`

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
# hypervisor | 123f 3712L | python:120,shell:2,less:1 | 2026-06-14
# stats: 156 func | 30 cls | 123 mod | CC̄=4.0 | critical:12 | cycles:0
# alerts[5]: CC repair_agent_spec=26; CC validate_cross_references=22; CC main=20; CC validate_registry=20; CC load_config=16
# hotspots[5]: load_config fan=18; generate_domain_pack_from_tree fan=18; repair_agent_spec fan=18; main fan=16; infer_intent fan=14
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[123]:
  agents/__init__.py,1
  agents/custom/__init__.py,1
  agents/generated/__init__.py,1
  agents/generated/user_agent/__init__.py,3
  agents/generated/user_agent/agent_card.py,63
  agents/generated/user_agent/main.py,16
  agents/generated/user_agent/routes.py,91
  agents/generated/user_agent/tests/test_contract.py,18
  agents/generated/weather_map_agent/__init__.py,3
  agents/generated/weather_map_agent/agent_card.py,40
  agents/generated/weather_map_agent/main.py,16
  agents/generated/weather_map_agent/routes.py,85
  agents/generated/weather_map_agent/tests/test_contract.py,18
  app.doql.less,103
  domains/__init__.py,1
  domains/weather_map/__init__.py,1
  domains/weather_map/handlers/__init__.py,1
  domains/weather_map/handlers/generate_weather_map.py,25
  generator/__init__.py,1
  generator/agent_generator.py,85
  generator/hashutil.py,10
  generator/model.py,89
  generator/validate.py,70
  generator/verify.py,66
  hypervisor/__init__.py,1
  hypervisor/_version.py,21
  hypervisor/cli.py,11
  hypervisor/compatibility/__init__.py,1
  hypervisor/compatibility/checker.py,44
  hypervisor/config.py,109
  hypervisor/contract_registry/__init__.py,1
  hypervisor/contract_registry/cli.py,78
  hypervisor/contract_registry/cross_validator.py,57
  hypervisor/contract_registry/loader.py,81
  hypervisor/contract_registry/models.py,57
  hypervisor/contract_registry/registry_builder.py,61
  hypervisor/contract_registry/registry_exporter.py,30
  hypervisor/contract_registry/schema_validator.py,55
  hypervisor/contract_registry/validate.py,51
  hypervisor/core.py,87
  hypervisor/deployment_registry/__init__.py,1
  hypervisor/domain_pack/__init__.py,1
  hypervisor/domain_pack/generator.py,43
  hypervisor/evolution/__init__.py,1
  hypervisor/evolution/cli.py,34
  hypervisor/evolution/models.py,33
  hypervisor/evolution/validator.py,17
  hypervisor/policy_gate/__init__.py,1
  hypervisor/policy_gate/gate.py,27
  hypervisor/uri/__init__.py,1
  hypervisor/uri/client.py,11
  hypervisor/uri2llm/__init__.py,4
  hypervisor/uri2llm/env_resolver.py,13
  hypervisor/uri2llm/function_resolver.py,27
  hypervisor/uri2llm/llm_resolver.py,19
  hypervisor/uri2llm/protocol_resolver.py,23
  hypervisor/uri2llm/pypi_resolver.py,17
  hypervisor/uri2llm/router.py,52
  hypervisor/verifier/__init__.py,1
  hypervisor/verifier/capability_tests.py,33
  hypervisor/verifier/cli.py,29
  meta_agent/__init__.py,2
  meta_agent/api.py,84
  meta_agent/cli.py,94
  meta_agent/domain_planner/__init__.py,2
  meta_agent/domain_planner/domain_pack_generator.py,249
  meta_agent/domain_planner/llm_planner.py,142
  meta_agent/models.py,44
  meta_agent/orchestrator.py,72
  meta_agent/planner.py,160
  meta_agent/repair.py,108
  nl2a/__init__.py,1
  nl2a/cli.py,20
  nl2uri/__init__.py,1
  nl2uri/cli.py,17
  nl2uri/llm_planner.py,19
  nl2uri/planner.py,33
  nl2uri/prompts/__init__.py,1
  nl2uri/writer.py,8
  project.sh,59
  runtime_client/__init__.py,1
  runtime_client/client.py,48
  tests/__init__.py,1
  tests/test_capability_tests.py,11
  tests/test_contract_registry.py,21
  tests/test_cross_validation_v03.py,6
  tests/test_evolution_proposal.py,9
  tests/test_generate.py,11
  tests/test_hypervisor.py,85
  tests/test_meta_agent.py,63
  tests/test_nl2a_v04.py,21
  tests/test_nl2uri.py,10
  tests/test_policy_gate.py,19
  tests/test_registry_builder_v03.py,21
  tests/test_runtime_client.py,9
  tests/test_schema_validation_v03.py,8
  tests/test_uri2llm_v04.py,20
  tests/test_uri3.py,12
  tests/test_uri_tree_validator.py,5
  tests/test_validate.py,9
  tree.sh,2
  uri3/__init__.py,1
  uri3/cli.py,37
  uri3/discovery/__init__.py,1
  uri3/graph/__init__.py,1
  uri3/graph/uri_graph.py,52
  uri3/protocols/__init__.py,1
  uri3/protocols/normalizer.py,10
  uri3/protocols/parser.py,18
  uri3/protocols/schemes.py,5
  uri3/resolvers/__init__.py,1
  uri3/resolvers/env_resolver.py,12
  uri3/resolvers/http_resolver.py,8
  uri3/resolvers/llm_resolver.py,15
  uri3/resolvers/python_resolver.py,15
  uri3/resolvers/router.py,22
  uri3/scanner/__init__.py,1
  uri3/scanner/base.py,8
  uri3/scanner/http_scanner.py,17
  uri3/scanner/scanner.py,8
  uri3/validators/__init__.py,1
  uri3/validators/uri_tree_validator.py,19
  uri3/validators/uri_validator.py,10
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
  generator/__init__.py:
  generator/agent_generator.py:
    e: render_template,generate_agent,expand_paths,main
    render_template(env;template_name;dest;context)
    generate_agent(spec_path)
    expand_paths(patterns)
    main(argv)
  generator/hashutil.py:
    e: file_sha256
    file_sha256(path)
  generator/model.py:
    e: load_agent_spec,spec_to_plain_dict,Capability,AgentSpec
    Capability:
    AgentSpec: output_dir_name(0)
    load_agent_spec(path)
    spec_to_plain_dict(spec;contract_hash)
  generator/validate.py:
    e: validate_agent,iter_agent_specs,main
    validate_agent(path)
    iter_agent_specs(root)
    main(argv)
  generator/verify.py:
    e: verify_generated_agent,verify_generated,main
    verify_generated_agent(agent_dir)
    verify_generated(root)
    main(argv)
  hypervisor/__init__.py:
  hypervisor/_version.py:
  hypervisor/cli.py:
    e: scan,resolve,main
    scan(uri)
    resolve(uri)
    main()
  hypervisor/compatibility/__init__.py:
  hypervisor/compatibility/checker.py:
    e: _load_policy,classify_registry_change
    _load_policy(root)
    classify_registry_change(old_root;new_root)
  hypervisor/config.py:
    e: _load_yaml,get_default_config,load_config,get_config
    _load_yaml(path)
    get_default_config()
    load_config(path)
    get_config()
  hypervisor/contract_registry/__init__.py:
  hypervisor/contract_registry/cli.py:
    e: main
    main(argv)
  hypervisor/contract_registry/cross_validator.py:
    e: _load_proto_text,_schema_exists,validate_cross_references,validate_root
    _load_proto_text(root)
    _schema_exists(proto_text;schema_ref)
    validate_cross_references(registry)
    validate_root(root)
  hypervisor/contract_registry/loader.py:
    e: _read_yaml,load_contract_registry
    _read_yaml(path)
    load_contract_registry(root)
  hypervisor/contract_registry/models.py:
    e: ResourceContract,ViewContract,CapabilityContract,ContractRegistry
    ResourceContract:
    ViewContract:
    CapabilityContract:
    ContractRegistry: resource_by_uri(1),view_by_name(1),capability_by_name(2)
  hypervisor/contract_registry/registry_builder.py:
    e: _hash_file,_contract_hash,build_registry_manifest,write_registry_manifest
    _hash_file(path)
    _contract_hash(root)
    build_registry_manifest(root)
    write_registry_manifest(root;output)
  hypervisor/contract_registry/registry_exporter.py:
    e: export_json,export_markdown
    export_json(root;output)
    export_markdown(root;output)
  hypervisor/contract_registry/schema_validator.py:
    e: _read_yaml,_read_json,validate_file,validate_contract_files,SchemaValidationResult
    SchemaValidationResult:
    _read_yaml(path)
    _read_json(path)
    validate_file(data_path;schema_path)
    validate_contract_files(root)
  hypervisor/contract_registry/validate.py:
    e: validate_registry
    validate_registry(registry)
  hypervisor/core.py:
    e: Hypervisor
    Hypervisor: __post_init__(0),from_config(2),start(0),stop(0),register_agent(1),status(0),__repr__(0)  # Main Hypervisor controller.
  hypervisor/deployment_registry/__init__.py:
  hypervisor/domain_pack/__init__.py:
  hypervisor/domain_pack/generator.py:
  hypervisor/evolution/__init__.py:
  hypervisor/evolution/cli.py:
    e: main
    main(argv)
  hypervisor/evolution/models.py:
    e: load_proposal,EvolutionProposal
    EvolutionProposal:
    load_proposal(path)
  hypervisor/evolution/validator.py:
    e: validate_proposal
    validate_proposal(proposal)
  hypervisor/policy_gate/__init__.py:
  hypervisor/policy_gate/gate.py:
    e: evaluate_change,GateDecision
    GateDecision:
    evaluate_change(change_report;approved)
  hypervisor/uri/__init__.py:
  hypervisor/uri/client.py:
    e: Uri3Client
    Uri3Client: __init__(0),resolve(1),scan(1),graph(1),nl2uri(1)
  hypervisor/uri2llm/__init__.py:
  hypervisor/uri2llm/env_resolver.py:
    e: resolve_env
    resolve_env(uri)
  hypervisor/uri2llm/function_resolver.py:
    e: _split_python_uri,resolve_python,call_python
    _split_python_uri(uri)
    resolve_python(uri)
    call_python(uri;payload)
  hypervisor/uri2llm/llm_resolver.py:
    e: resolve_llm
    resolve_llm(uri)
  hypervisor/uri2llm/protocol_resolver.py:
    e: resolve_http_like,resolve_a2a,resolve_mcp,resolve_resource
    resolve_http_like(uri)
    resolve_a2a(uri)
    resolve_mcp(uri)
    resolve_resource(uri)
  hypervisor/uri2llm/pypi_resolver.py:
    e: resolve_pypi
    resolve_pypi(uri)
  hypervisor/uri2llm/router.py:
    e: resolve,call,UriResolution
    UriResolution:
    resolve(uri)
    call(uri;payload)
  hypervisor/verifier/__init__.py:
  hypervisor/verifier/capability_tests.py:
    e: build_capability_test_plan
    build_capability_test_plan(registry)
  hypervisor/verifier/cli.py:
    e: main
    main(argv)
  meta_agent/__init__.py:
  meta_agent/api.py:
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
  meta_agent/cli.py:
    e: main
    main()
  meta_agent/domain_planner/__init__.py:
  meta_agent/domain_planner/domain_pack_generator.py:
    e: _write,_package,_generic_proto,_weather_proto,_weather_handler,_generic_handler,_merge_main_contracts,generate_domain_pack_from_tree
    _write(path;content)
    _package(domain_id)
    _generic_proto(domain_id)
    _weather_proto()
    _weather_handler()
    _generic_handler()
    _merge_main_contracts(domain_id;resources;views;proto_text)
    generate_domain_pack_from_tree(tree;out_dir)
  meta_agent/domain_planner/llm_planner.py:
    e: _slug,_llm_uri_from_env,_deterministic_weather_plan,_generic_plan,_extract_json,_call_openrouter,plan_domain_from_prompt
    _slug(text)
    _llm_uri_from_env()
    _deterministic_weather_plan(prompt)
    _generic_plan(prompt)
    _extract_json(text)
    _call_openrouter(prompt)
    plan_domain_from_prompt(prompt;use_llm)
  meta_agent/models.py:
    e: dump_yaml,AgentCreationIntent,RepairResult,PipelineResult
    AgentCreationIntent:  # Normalized request to create an agent.
    RepairResult:
    PipelineResult:
    dump_yaml(data)
  meta_agent/orchestrator.py:
    e: save_proposal_from_prompt,validate_repair_generate,pipeline_from_prompt,asdict_result
    save_proposal_from_prompt(prompt;output_path)
    validate_repair_generate(spec_path)
    pipeline_from_prompt(prompt)
    asdict_result(result)
  meta_agent/planner.py:
    e: slugify,package_name,singularize,infer_intent,intent_to_agent_spec
    slugify(value)
    package_name(agent_name)
    singularize(word)
    infer_intent(prompt)
    intent_to_agent_spec(intent)
  meta_agent/repair.py:
    e: _load_yaml,_write_yaml,repair_agent_spec
    _load_yaml(path)
    _write_yaml(path;data)
    repair_agent_spec(path)
  nl2a/__init__.py:
  nl2a/cli.py:
    e: generate,main
    generate(prompt;no_llm;out_dir)
    main()
  nl2uri/__init__.py:
  nl2uri/cli.py:
    e: generate,main
    generate(prompt;out;no_llm;json_out)
    main()
  nl2uri/llm_planner.py:
    e: llm_plan
    llm_plan(prompt)
  nl2uri/planner.py:
    e: _slug,rule_based_plan,PlanResult
    PlanResult:
    _slug(text)
    rule_based_plan(prompt)
  nl2uri/prompts/__init__.py:
  nl2uri/writer.py:
    e: write_uri_tree
    write_uri_tree(tree;out)
  runtime_client/__init__.py:
  runtime_client/client.py:
    e: ResourceRuntimeClient
    ResourceRuntimeClient: __init__(2),read_resource(1),dispatch_command(2)  # Small HTTP client used by generated thin agents.
  tests/__init__.py:
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
  uri3/__init__.py:
  uri3/cli.py:
    e: validate,validate_tree,graph,resolve,scan,main
    validate(uri)
    validate_tree(path)
    graph(path)
    resolve(uri)
    scan(uri)
    main()
  uri3/discovery/__init__.py:
  uri3/graph/__init__.py:
  uri3/graph/uri_graph.py:
    e: build_graph_from_tree,UriNode,UriEdge,UriGraph
    UriNode:
    UriEdge:
    UriGraph: add_node(3),add_edge(3)
    build_graph_from_tree(path)
  uri3/protocols/__init__.py:
  uri3/protocols/normalizer.py:
    e: normalize_uri
    normalize_uri(uri)
  uri3/protocols/parser.py:
    e: parse_uri,ParsedURI
    ParsedURI:
    parse_uri(uri)
  uri3/protocols/schemes.py:
  uri3/resolvers/__init__.py:
  uri3/resolvers/env_resolver.py:
    e: EnvResolver
    EnvResolver: resolve(1)
  uri3/resolvers/http_resolver.py:
    e: HttpResolver
    HttpResolver: resolve(1)
  uri3/resolvers/llm_resolver.py:
    e: LLMRef,LLMResolver
    LLMRef:
    LLMResolver: resolve(1)
  uri3/resolvers/python_resolver.py:
    e: PythonResolver
    PythonResolver: resolve(1),call(2)
  uri3/resolvers/router.py:
    e: Uri3Router
    Uri3Router: __init__(0),resolve(1),call(2)
  uri3/scanner/__init__.py:
  uri3/scanner/base.py:
    e: ScanItem
    ScanItem:
  uri3/scanner/http_scanner.py:
    e: scan_http
    scan_http(base_url)
  uri3/scanner/scanner.py:
    e: scan
    scan(uri)
  uri3/validators/__init__.py:
  uri3/validators/uri_tree_validator.py:
    e: load_yaml,validate_uri_tree
    load_yaml(path)
    validate_uri_tree(path)
  uri3/validators/uri_validator.py:
    e: validate_uri
    validate_uri(uri)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('hypervisor', '0.1.0', 'python').

% ── Project Files ────────────────────────────────────────
project_file('agents/__init__.py', 1, 'python').
project_file('agents/custom/__init__.py', 1, 'python').
project_file('agents/generated/__init__.py', 1, 'python').
project_file('agents/generated/user_agent/__init__.py', 3, 'python').
project_file('agents/generated/user_agent/agent_card.py', 63, 'python').
project_file('agents/generated/user_agent/main.py', 16, 'python').
project_file('agents/generated/user_agent/routes.py', 91, 'python').
project_file('agents/generated/user_agent/tests/test_contract.py', 18, 'python').
project_file('agents/generated/weather_map_agent/__init__.py', 3, 'python').
project_file('agents/generated/weather_map_agent/agent_card.py', 40, 'python').
project_file('agents/generated/weather_map_agent/main.py', 16, 'python').
project_file('agents/generated/weather_map_agent/routes.py', 85, 'python').
project_file('agents/generated/weather_map_agent/tests/test_contract.py', 18, 'python').
project_file('app.doql.less', 103, 'less').
project_file('domains/__init__.py', 1, 'python').
project_file('domains/weather_map/__init__.py', 1, 'python').
project_file('domains/weather_map/handlers/__init__.py', 1, 'python').
project_file('domains/weather_map/handlers/generate_weather_map.py', 25, 'python').
project_file('generator/__init__.py', 1, 'python').
project_file('generator/agent_generator.py', 85, 'python').
project_file('generator/hashutil.py', 10, 'python').
project_file('generator/model.py', 89, 'python').
project_file('generator/validate.py', 70, 'python').
project_file('generator/verify.py', 66, 'python').
project_file('hypervisor/__init__.py', 1, 'python').
project_file('hypervisor/_version.py', 21, 'python').
project_file('hypervisor/cli.py', 11, 'python').
project_file('hypervisor/compatibility/__init__.py', 1, 'python').
project_file('hypervisor/compatibility/checker.py', 44, 'python').
project_file('hypervisor/config.py', 109, 'python').
project_file('hypervisor/contract_registry/__init__.py', 1, 'python').
project_file('hypervisor/contract_registry/cli.py', 78, 'python').
project_file('hypervisor/contract_registry/cross_validator.py', 57, 'python').
project_file('hypervisor/contract_registry/loader.py', 81, 'python').
project_file('hypervisor/contract_registry/models.py', 57, 'python').
project_file('hypervisor/contract_registry/registry_builder.py', 61, 'python').
project_file('hypervisor/contract_registry/registry_exporter.py', 30, 'python').
project_file('hypervisor/contract_registry/schema_validator.py', 55, 'python').
project_file('hypervisor/contract_registry/validate.py', 51, 'python').
project_file('hypervisor/core.py', 87, 'python').
project_file('hypervisor/deployment_registry/__init__.py', 1, 'python').
project_file('hypervisor/domain_pack/__init__.py', 1, 'python').
project_file('hypervisor/domain_pack/generator.py', 43, 'python').
project_file('hypervisor/evolution/__init__.py', 1, 'python').
project_file('hypervisor/evolution/cli.py', 34, 'python').
project_file('hypervisor/evolution/models.py', 33, 'python').
project_file('hypervisor/evolution/validator.py', 17, 'python').
project_file('hypervisor/policy_gate/__init__.py', 1, 'python').
project_file('hypervisor/policy_gate/gate.py', 27, 'python').
project_file('hypervisor/uri/__init__.py', 1, 'python').
project_file('hypervisor/uri/client.py', 11, 'python').
project_file('hypervisor/uri2llm/__init__.py', 4, 'python').
project_file('hypervisor/uri2llm/env_resolver.py', 13, 'python').
project_file('hypervisor/uri2llm/function_resolver.py', 27, 'python').
project_file('hypervisor/uri2llm/llm_resolver.py', 19, 'python').
project_file('hypervisor/uri2llm/protocol_resolver.py', 23, 'python').
project_file('hypervisor/uri2llm/pypi_resolver.py', 17, 'python').
project_file('hypervisor/uri2llm/router.py', 52, 'python').
project_file('hypervisor/verifier/__init__.py', 1, 'python').
project_file('hypervisor/verifier/capability_tests.py', 33, 'python').
project_file('hypervisor/verifier/cli.py', 29, 'python').
project_file('meta_agent/__init__.py', 2, 'python').
project_file('meta_agent/api.py', 84, 'python').
project_file('meta_agent/cli.py', 94, 'python').
project_file('meta_agent/domain_planner/__init__.py', 2, 'python').
project_file('meta_agent/domain_planner/domain_pack_generator.py', 249, 'python').
project_file('meta_agent/domain_planner/llm_planner.py', 142, 'python').
project_file('meta_agent/models.py', 44, 'python').
project_file('meta_agent/orchestrator.py', 72, 'python').
project_file('meta_agent/planner.py', 160, 'python').
project_file('meta_agent/repair.py', 108, 'python').
project_file('nl2a/__init__.py', 1, 'python').
project_file('nl2a/cli.py', 20, 'python').
project_file('nl2uri/__init__.py', 1, 'python').
project_file('nl2uri/cli.py', 17, 'python').
project_file('nl2uri/llm_planner.py', 19, 'python').
project_file('nl2uri/planner.py', 33, 'python').
project_file('nl2uri/prompts/__init__.py', 1, 'python').
project_file('nl2uri/writer.py', 8, 'python').
project_file('project.sh', 59, 'shell').
project_file('runtime_client/__init__.py', 1, 'python').
project_file('runtime_client/client.py', 48, 'python').
project_file('tests/__init__.py', 1, 'python').
project_file('tests/test_capability_tests.py', 11, 'python').
project_file('tests/test_contract_registry.py', 21, 'python').
project_file('tests/test_cross_validation_v03.py', 6, 'python').
project_file('tests/test_evolution_proposal.py', 9, 'python').
project_file('tests/test_generate.py', 11, 'python').
project_file('tests/test_hypervisor.py', 85, 'python').
project_file('tests/test_meta_agent.py', 63, 'python').
project_file('tests/test_nl2a_v04.py', 21, 'python').
project_file('tests/test_nl2uri.py', 10, 'python').
project_file('tests/test_policy_gate.py', 19, 'python').
project_file('tests/test_registry_builder_v03.py', 21, 'python').
project_file('tests/test_runtime_client.py', 9, 'python').
project_file('tests/test_schema_validation_v03.py', 8, 'python').
project_file('tests/test_uri2llm_v04.py', 20, 'python').
project_file('tests/test_uri3.py', 12, 'python').
project_file('tests/test_uri_tree_validator.py', 5, 'python').
project_file('tests/test_validate.py', 9, 'python').
project_file('tree.sh', 2, 'shell').
project_file('uri3/__init__.py', 1, 'python').
project_file('uri3/cli.py', 37, 'python').
project_file('uri3/discovery/__init__.py', 1, 'python').
project_file('uri3/graph/__init__.py', 1, 'python').
project_file('uri3/graph/uri_graph.py', 52, 'python').
project_file('uri3/protocols/__init__.py', 1, 'python').
project_file('uri3/protocols/normalizer.py', 10, 'python').
project_file('uri3/protocols/parser.py', 18, 'python').
project_file('uri3/protocols/schemes.py', 5, 'python').
project_file('uri3/resolvers/__init__.py', 1, 'python').
project_file('uri3/resolvers/env_resolver.py', 12, 'python').
project_file('uri3/resolvers/http_resolver.py', 8, 'python').
project_file('uri3/resolvers/llm_resolver.py', 15, 'python').
project_file('uri3/resolvers/python_resolver.py', 15, 'python').
project_file('uri3/resolvers/router.py', 22, 'python').
project_file('uri3/scanner/__init__.py', 1, 'python').
project_file('uri3/scanner/base.py', 8, 'python').
project_file('uri3/scanner/http_scanner.py', 17, 'python').
project_file('uri3/scanner/scanner.py', 8, 'python').
project_file('uri3/validators/__init__.py', 1, 'python').
project_file('uri3/validators/uri_tree_validator.py', 19, 'python').
project_file('uri3/validators/uri_validator.py', 10, 'python').

% ── Python Functions ─────────────────────────────────────
python_function('agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/user_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('agents/generated/weather_map_agent/tests/test_contract.py', 'test_agent_card_has_expected_name', 0, 2, 0).
python_function('agents/generated/weather_map_agent/tests/test_contract.py', 'test_agent_card_has_capabilities', 0, 3, 0).
python_function('agents/generated/weather_map_agent/tests/test_contract.py', 'test_agent_card_has_contract_hash', 0, 2, 0).
python_function('domains/weather_map/handlers/generate_weather_map.py', 'handler', 1, 3, 7).
python_function('generator/agent_generator.py', 'render_template', 4, 1, 4).
python_function('generator/agent_generator.py', 'generate_agent', 1, 4, 10).
python_function('generator/agent_generator.py', 'expand_paths', 1, 4, 6).
python_function('generator/agent_generator.py', 'main', 1, 5, 3).
python_function('generator/hashutil.py', 'file_sha256', 1, 1, 4).
python_function('generator/model.py', 'load_agent_spec', 1, 7, 11).
python_function('generator/model.py', 'spec_to_plain_dict', 2, 2, 1).
python_function('generator/validate.py', 'validate_agent', 1, 11, 4).
python_function('generator/validate.py', 'iter_agent_specs', 1, 3, 4).
python_function('generator/validate.py', 'main', 1, 7, 6).
python_function('generator/verify.py', 'verify_generated_agent', 1, 6, 7).
python_function('generator/verify.py', 'verify_generated', 1, 6, 5).
python_function('generator/verify.py', 'main', 1, 9, 7).
python_function('hypervisor/cli.py', 'scan', 1, 2, 4).
python_function('hypervisor/cli.py', 'resolve', 1, 1, 4).
python_function('hypervisor/cli.py', 'main', 0, 1, 1).
python_function('hypervisor/compatibility/checker.py', '_load_policy', 1, 3, 4).
python_function('hypervisor/compatibility/checker.py', 'classify_registry_change', 2, 8, 6).
python_function('hypervisor/config.py', '_load_yaml', 1, 4, 4).
python_function('hypervisor/config.py', 'get_default_config', 0, 1, 2).
python_function('hypervisor/config.py', 'load_config', 1, 16, 18).
python_function('hypervisor/config.py', 'get_config', 0, 1, 1).
python_function('hypervisor/contract_registry/cli.py', 'main', 1, 20, 11).
python_function('hypervisor/contract_registry/cross_validator.py', '_load_proto_text', 1, 2, 5).
python_function('hypervisor/contract_registry/cross_validator.py', '_schema_exists', 2, 1, 3).
python_function('hypervisor/contract_registry/cross_validator.py', 'validate_cross_references', 1, 22, 3).
python_function('hypervisor/contract_registry/cross_validator.py', 'validate_root', 1, 1, 2).
python_function('hypervisor/contract_registry/loader.py', '_read_yaml', 1, 3, 4).
python_function('hypervisor/contract_registry/loader.py', 'load_contract_registry', 1, 9, 11).
python_function('hypervisor/contract_registry/registry_builder.py', '_hash_file', 1, 1, 3).
python_function('hypervisor/contract_registry/registry_builder.py', '_contract_hash', 1, 3, 10).
python_function('hypervisor/contract_registry/registry_builder.py', 'build_registry_manifest', 1, 5, 6).
python_function('hypervisor/contract_registry/registry_builder.py', 'write_registry_manifest', 2, 2, 5).
python_function('hypervisor/contract_registry/registry_exporter.py', 'export_json', 2, 1, 1).
python_function('hypervisor/contract_registry/registry_exporter.py', 'export_markdown', 2, 6, 7).
python_function('hypervisor/contract_registry/schema_validator.py', '_read_yaml', 1, 2, 2).
python_function('hypervisor/contract_registry/schema_validator.py', '_read_json', 1, 1, 2).
python_function('hypervisor/contract_registry/schema_validator.py', 'validate_file', 2, 3, 8).
python_function('hypervisor/contract_registry/schema_validator.py', 'validate_contract_files', 1, 6, 6).
python_function('hypervisor/contract_registry/validate.py', 'validate_registry', 1, 20, 8).
python_function('hypervisor/evolution/cli.py', 'main', 1, 10, 7).
python_function('hypervisor/evolution/models.py', 'load_proposal', 1, 5, 7).
python_function('hypervisor/evolution/validator.py', 'validate_proposal', 1, 6, 2).
python_function('hypervisor/policy_gate/gate.py', 'evaluate_change', 2, 5, 4).
python_function('hypervisor/uri2llm/env_resolver.py', 'resolve_env', 1, 3, 4).
python_function('hypervisor/uri2llm/function_resolver.py', '_split_python_uri', 1, 2, 4).
python_function('hypervisor/uri2llm/function_resolver.py', 'resolve_python', 1, 1, 1).
python_function('hypervisor/uri2llm/function_resolver.py', 'call_python', 2, 1, 4).
python_function('hypervisor/uri2llm/llm_resolver.py', 'resolve_llm', 1, 5, 4).
python_function('hypervisor/uri2llm/protocol_resolver.py', 'resolve_http_like', 1, 1, 0).
python_function('hypervisor/uri2llm/protocol_resolver.py', 'resolve_a2a', 1, 2, 1).
python_function('hypervisor/uri2llm/protocol_resolver.py', 'resolve_mcp', 1, 2, 1).
python_function('hypervisor/uri2llm/protocol_resolver.py', 'resolve_resource', 1, 1, 1).
python_function('hypervisor/uri2llm/pypi_resolver.py', 'resolve_pypi', 1, 5, 4).
python_function('hypervisor/uri2llm/router.py', 'resolve', 1, 10, 11).
python_function('hypervisor/uri2llm/router.py', 'call', 2, 3, 3).
python_function('hypervisor/verifier/capability_tests.py', 'build_capability_test_plan', 1, 4, 1).
python_function('hypervisor/verifier/cli.py', 'main', 1, 5, 6).
python_function('meta_agent/api.py', 'health', 0, 1, 1).
python_function('meta_agent/api.py', 'proposal_from_prompt', 1, 2, 6).
python_function('meta_agent/api.py', 'validate', 1, 2, 5).
python_function('meta_agent/api.py', 'repair', 1, 2, 5).
python_function('meta_agent/api.py', 'generate', 1, 2, 6).
python_function('meta_agent/api.py', 'pipeline', 1, 2, 4).
python_function('meta_agent/api.py', 'verify', 0, 1, 2).
python_function('meta_agent/cli.py', 'main', 0, 16, 16).
python_function('meta_agent/domain_planner/domain_pack_generator.py', '_write', 2, 1, 3).
python_function('meta_agent/domain_planner/domain_pack_generator.py', '_package', 1, 1, 0).
python_function('meta_agent/domain_planner/domain_pack_generator.py', '_generic_proto', 1, 1, 1).
python_function('meta_agent/domain_planner/domain_pack_generator.py', '_weather_proto', 0, 1, 0).
python_function('meta_agent/domain_planner/domain_pack_generator.py', '_weather_handler', 0, 1, 0).
python_function('meta_agent/domain_planner/domain_pack_generator.py', '_generic_handler', 0, 1, 0).
python_function('meta_agent/domain_planner/domain_pack_generator.py', '_merge_main_contracts', 4, 11, 9).
python_function('meta_agent/domain_planner/domain_pack_generator.py', 'generate_domain_pack_from_tree', 2, 11, 18).
python_function('meta_agent/domain_planner/llm_planner.py', '_slug', 1, 2, 3).
python_function('meta_agent/domain_planner/llm_planner.py', '_llm_uri_from_env', 0, 5, 3).
python_function('meta_agent/domain_planner/llm_planner.py', '_deterministic_weather_plan', 1, 2, 2).
python_function('meta_agent/domain_planner/llm_planner.py', '_generic_plan', 1, 1, 2).
python_function('meta_agent/domain_planner/llm_planner.py', '_extract_json', 1, 3, 5).
python_function('meta_agent/domain_planner/llm_planner.py', '_call_openrouter', 1, 4, 12).
python_function('meta_agent/domain_planner/llm_planner.py', 'plan_domain_from_prompt', 2, 6, 5).
python_function('meta_agent/models.py', 'dump_yaml', 1, 1, 1).
python_function('meta_agent/orchestrator.py', 'save_proposal_from_prompt', 2, 2, 6).
python_function('meta_agent/orchestrator.py', 'validate_repair_generate', 1, 6, 6).
python_function('meta_agent/orchestrator.py', 'pipeline_from_prompt', 1, 1, 2).
python_function('meta_agent/orchestrator.py', 'asdict_result', 1, 1, 0).
python_function('meta_agent/planner.py', 'slugify', 1, 2, 3).
python_function('meta_agent/planner.py', 'package_name', 1, 3, 5).
python_function('meta_agent/planner.py', 'singularize', 1, 4, 2).
python_function('meta_agent/planner.py', 'infer_intent', 1, 9, 14).
python_function('meta_agent/planner.py', 'intent_to_agent_spec', 1, 8, 9).
python_function('meta_agent/repair.py', '_load_yaml', 1, 2, 3).
python_function('meta_agent/repair.py', '_write_yaml', 2, 1, 2).
python_function('meta_agent/repair.py', 'repair_agent_spec', 1, 26, 18).
python_function('nl2a/cli.py', 'generate', 3, 2, 9).
python_function('nl2a/cli.py', 'main', 0, 1, 1).
python_function('nl2uri/cli.py', 'generate', 4, 4, 8).
python_function('nl2uri/cli.py', 'main', 0, 1, 1).
python_function('nl2uri/llm_planner.py', 'llm_plan', 1, 4, 12).
python_function('nl2uri/planner.py', '_slug', 1, 2, 3).
python_function('nl2uri/planner.py', 'rule_based_plan', 1, 8, 5).
python_function('nl2uri/writer.py', 'write_uri_tree', 2, 1, 4).
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
python_function('tests/test_nl2a_v04.py', 'test_domain_pack_generation', 1, 4, 4).
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
python_function('uri3/cli.py', 'validate', 1, 1, 3).
python_function('uri3/cli.py', 'validate_tree', 1, 3, 4).
python_function('uri3/cli.py', 'graph', 1, 3, 5).
python_function('uri3/cli.py', 'resolve', 1, 2, 8).
python_function('uri3/cli.py', 'scan', 1, 2, 4).
python_function('uri3/cli.py', 'main', 0, 1, 1).
python_function('uri3/graph/uri_graph.py', 'build_graph_from_tree', 1, 10, 9).
python_function('uri3/protocols/normalizer.py', 'normalize_uri', 1, 3, 3).
python_function('uri3/protocols/parser.py', 'parse_uri', 1, 2, 4).
python_function('uri3/scanner/http_scanner.py', 'scan_http', 1, 6, 6).
python_function('uri3/scanner/scanner.py', 'scan', 1, 2, 2).
python_function('uri3/validators/uri_tree_validator.py', 'load_yaml', 1, 1, 2).
python_function('uri3/validators/uri_tree_validator.py', 'validate_uri_tree', 1, 2, 7).
python_function('uri3/validators/uri_validator.py', 'validate_uri', 1, 2, 2).

% ── Python Classes ───────────────────────────────────────
python_class('generator/model.py', 'Capability').
python_class('generator/model.py', 'AgentSpec').
python_method('AgentSpec', 'output_dir_name', 0, 1, 0).
python_class('hypervisor/contract_registry/models.py', 'ResourceContract').
python_class('hypervisor/contract_registry/models.py', 'ViewContract').
python_class('hypervisor/contract_registry/models.py', 'CapabilityContract').
python_class('hypervisor/contract_registry/models.py', 'ContractRegistry').
python_method('ContractRegistry', 'resource_by_uri', 1, 3, 1).
python_method('ContractRegistry', 'view_by_name', 1, 3, 1).
python_method('ContractRegistry', 'capability_by_name', 2, 4, 1).
python_class('hypervisor/contract_registry/schema_validator.py', 'SchemaValidationResult').
python_class('hypervisor/core.py', 'Hypervisor').
python_method('Hypervisor', '__post_init__', 0, 1, 3).
python_method('Hypervisor', 'from_config', 2, 1, 2).
python_method('Hypervisor', 'start', 0, 2, 1).
python_method('Hypervisor', 'stop', 0, 2, 1).
python_method('Hypervisor', 'register_agent', 1, 3, 3).
python_method('Hypervisor', 'status', 0, 1, 2).
python_method('Hypervisor', '__repr__', 0, 1, 1).
python_class('hypervisor/evolution/models.py', 'EvolutionProposal').
python_class('hypervisor/policy_gate/gate.py', 'GateDecision').
python_class('hypervisor/uri/client.py', 'Uri3Client').
python_method('Uri3Client', '__init__', 0, 1, 1).
python_method('Uri3Client', 'resolve', 1, 1, 1).
python_method('Uri3Client', 'scan', 1, 1, 1).
python_method('Uri3Client', 'graph', 1, 1, 1).
python_method('Uri3Client', 'nl2uri', 1, 1, 1).
python_class('hypervisor/uri2llm/router.py', 'UriResolution').
python_class('meta_agent/api.py', 'PromptRequest').
python_class('meta_agent/api.py', 'SpecPathRequest').
python_class('meta_agent/models.py', 'AgentCreationIntent').
python_class('meta_agent/models.py', 'RepairResult').
python_class('meta_agent/models.py', 'PipelineResult').
python_class('nl2uri/planner.py', 'PlanResult').
python_class('runtime_client/client.py', 'ResourceRuntimeClient').
python_method('ResourceRuntimeClient', '__init__', 2, 1, 1).
python_method('ResourceRuntimeClient', 'read_resource', 1, 2, 4).
python_method('ResourceRuntimeClient', 'dispatch_command', 2, 2, 4).
python_class('uri3/graph/uri_graph.py', 'UriNode').
python_class('uri3/graph/uri_graph.py', 'UriEdge').
python_class('uri3/graph/uri_graph.py', 'UriGraph').
python_method('UriGraph', 'add_node', 3, 3, 1).
python_method('UriGraph', 'add_edge', 3, 3, 2).
python_class('uri3/protocols/parser.py', 'ParsedURI').
python_class('uri3/resolvers/env_resolver.py', 'EnvResolver').
python_method('EnvResolver', 'resolve', 1, 3, 3).
python_class('uri3/resolvers/http_resolver.py', 'HttpResolver').
python_method('HttpResolver', 'resolve', 1, 2, 3).
python_class('uri3/resolvers/llm_resolver.py', 'LLMRef').
python_class('uri3/resolvers/llm_resolver.py', 'LLMResolver').
python_method('LLMResolver', 'resolve', 1, 1, 3).
python_class('uri3/resolvers/python_resolver.py', 'PythonResolver').
python_method('PythonResolver', 'resolve', 1, 2, 6).
python_method('PythonResolver', 'call', 2, 2, 1).
python_class('uri3/resolvers/router.py', 'Uri3Router').
python_method('Uri3Router', '__init__', 0, 1, 4).
python_method('Uri3Router', 'resolve', 1, 2, 3).
python_method('Uri3Router', 'call', 2, 3, 5).
python_class('uri3/scanner/base.py', 'ScanItem').

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
```

## Source Map

*Top 3 modules by symbol density — signatures for LLM orientation.*

### `hypervisor.core` (`hypervisor/core.py`)

```python
class Hypervisor:  # Main Hypervisor controller.
    def __post_init__()  # CC=1
    def from_config(cls, path)  # CC=1
    def start()  # CC=2
    def stop()  # CC=2
    def register_agent(name)  # CC=3
    def status()  # CC=1
    def __repr__()  # CC=1
```

### `hypervisor.config` (`hypervisor/config.py`)

```python
def _load_yaml(path)  # CC=4, fan=4
def get_default_config()  # CC=1, fan=2
def load_config(path)  # CC=16, fan=18 ⚠
def get_config()  # CC=1, fan=1
```

### `hypervisor.cli` (`hypervisor/cli.py`)

```python
def scan(uri)  # CC=2, fan=4
def resolve(uri)  # CC=1, fan=4
def main()  # CC=1, fan=1
```

## Call Graph

*97 nodes · 98 edges · 46 modules · CC̄=3.8*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `repair_agent_spec` *(in meta_agent.repair)* | 26 ⚠ | 3 | 58 | **61** |
| `generate_domain_pack_from_tree` *(in meta_agent.domain_planner.domain_pack_generator)* | 11 ⚠ | 0 | 54 | **54** |
| `load_contract_registry` *(in hypervisor.contract_registry.loader)* | 9 | 6 | 33 | **39** |
| `infer_intent` *(in meta_agent.planner)* | 9 | 1 | 30 | **31** |
| `_merge_main_contracts` *(in meta_agent.domain_planner.domain_pack_generator)* | 11 ⚠ | 1 | 30 | **31** |
| `build_graph_from_tree` *(in uri3.graph.uri_graph)* | 10 ⚠ | 2 | 28 | **30** |
| `load_agent_spec` *(in generator.model)* | 7 | 2 | 24 | **26** |
| `main` *(in hypervisor.contract_registry.cli)* | 20 ⚠ | 0 | 26 | **26** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/hypervisor
# generated in 0.04s
# nodes: 97 | edges: 98 | modules: 46
# CC̄=3.8

HUBS[20]:
  meta_agent.repair.repair_agent_spec
    CC=26  in:3  out:58  total:61
  meta_agent.domain_planner.domain_pack_generator.generate_domain_pack_from_tree
    CC=11  in:0  out:54  total:54
  hypervisor.contract_registry.loader.load_contract_registry
    CC=9  in:6  out:33  total:39
  meta_agent.planner.infer_intent
    CC=9  in:1  out:30  total:31
  meta_agent.domain_planner.domain_pack_generator._merge_main_contracts
    CC=11  in:1  out:30  total:31
  uri3.graph.uri_graph.build_graph_from_tree
    CC=10  in:2  out:28  total:30
  generator.model.load_agent_spec
    CC=7  in:2  out:24  total:26
  hypervisor.contract_registry.cli.main
    CC=20  in:0  out:26  total:26
  hypervisor.config.load_config
    CC=16  in:2  out:24  total:26
  hypervisor.contract_registry.validate.validate_registry
    CC=20  in:2  out:20  total:22
  meta_agent.domain_planner.domain_pack_generator._write
    CC=1  in:15  out:3  total:18
  nl2uri.llm_planner.llm_plan
    CC=4  in:2  out:16  total:18
  generator.validate.validate_agent
    CC=11  in:8  out:10  total:18
  meta_agent.domain_planner.llm_planner._call_openrouter
    CC=4  in:1  out:17  total:18
  meta_agent.orchestrator.validate_repair_generate
    CC=6  in:3  out:15  total:18
  hypervisor.contract_registry.schema_validator.validate_contract_files
    CC=6  in:2  out:13  total:15
  hypervisor.contract_registry.registry_builder._contract_hash
    CC=3  in:1  out:13  total:14
  hypervisor.contract_registry.registry_exporter.export_markdown
    CC=6  in:1  out:13  total:14
  nl2uri.cli.generate
    CC=4  in:0  out:12  total:12
  uri3.protocols.parser.parse_uri
    CC=2  in:8  out:4  total:12

MODULES:
  generator.agent_generator  [4 funcs]
    expand_paths  CC=4  out:7
    generate_agent  CC=4  out:10
    main  CC=5  out:4
    render_template  CC=1  out:4
  generator.hashutil  [1 funcs]
    file_sha256  CC=1  out:4
  generator.model  [2 funcs]
    load_agent_spec  CC=7  out:24
    spec_to_plain_dict  CC=2  out:1
  generator.validate  [3 funcs]
    iter_agent_specs  CC=3  out:6
    main  CC=7  out:9
    validate_agent  CC=11  out:10
  generator.verify  [3 funcs]
    main  CC=9  out:10
    verify_generated  CC=6  out:5
    verify_generated_agent  CC=6  out:11
  hypervisor.compatibility.checker  [1 funcs]
    classify_registry_change  CC=8  out:11
  hypervisor.config  [4 funcs]
    _load_yaml  CC=4  out:4
    get_config  CC=1  out:1
    get_default_config  CC=1  out:3
    load_config  CC=16  out:24
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
  hypervisor.evolution.cli  [1 funcs]
    main  CC=10  out:11
  hypervisor.evolution.models  [1 funcs]
    load_proposal  CC=5  out:11
  hypervisor.evolution.validator  [1 funcs]
    validate_proposal  CC=6  out:6
  hypervisor.uri.client  [2 funcs]
    graph  CC=1  out:1
    nl2uri  CC=1  out:1
  hypervisor.uri2llm.function_resolver  [3 funcs]
    _split_python_uri  CC=2  out:4
    call_python  CC=1  out:4
    resolve_python  CC=1  out:1
  hypervisor.uri2llm.router  [1 funcs]
    call  CC=3  out:3
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
  meta_agent.domain_planner.domain_pack_generator  [5 funcs]
    _generic_proto  CC=1  out:1
    _merge_main_contracts  CC=11  out:30
    _package  CC=1  out:0
    _write  CC=1  out:3
    generate_domain_pack_from_tree  CC=11  out:54
  meta_agent.domain_planner.llm_planner  [7 funcs]
    _call_openrouter  CC=4  out:17
    _deterministic_weather_plan  CC=2  out:2
    _extract_json  CC=3  out:8
    _generic_plan  CC=1  out:2
    _llm_uri_from_env  CC=5  out:5
    _slug  CC=2  out:3
    plan_domain_from_prompt  CC=6  out:8
  meta_agent.orchestrator  [4 funcs]
    asdict_result  CC=1  out:0
    pipeline_from_prompt  CC=1  out:2
    save_proposal_from_prompt  CC=2  out:6
    validate_repair_generate  CC=6  out:15
  meta_agent.planner  [4 funcs]
    infer_intent  CC=9  out:30
    intent_to_agent_spec  CC=8  out:11
    package_name  CC=3  out:6
    singularize  CC=4  out:3
  meta_agent.repair  [2 funcs]
    _load_yaml  CC=2  out:3
    repair_agent_spec  CC=26  out:58
  nl2a.cli  [1 funcs]
    generate  CC=2  out:9
  nl2uri.cli  [1 funcs]
    generate  CC=4  out:12
  nl2uri.llm_planner  [1 funcs]
    llm_plan  CC=4  out:16
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
  uri3.resolvers.env_resolver  [1 funcs]
    resolve  CC=3  out:3
  uri3.resolvers.llm_resolver  [1 funcs]
    resolve  CC=1  out:3
  uri3.resolvers.python_resolver  [1 funcs]
    resolve  CC=2  out:6
  uri3.resolvers.router  [2 funcs]
    call  CC=3  out:5
    resolve  CC=2  out:3
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
  uri3.cli.validate → uri3.validators.uri_validator.validate_uri
  uri3.cli.validate_tree → uri3.validators.uri_tree_validator.validate_uri_tree
  uri3.cli.graph → uri3.graph.uri_graph.build_graph_from_tree
  uri3.validators.uri_validator.validate_uri → uri3.protocols.parser.parse_uri
  meta_agent.planner.infer_intent → meta_agent.planner.singularize
  meta_agent.planner.intent_to_agent_spec → meta_agent.planner.singularize
  meta_agent.planner.intent_to_agent_spec → meta_agent.planner.package_name
  generator.validate.validate_agent → generator.model.load_agent_spec
  generator.validate.main → generator.validate.iter_agent_specs
  generator.validate.main → generator.validate.validate_agent
  uri3.scanner.scanner.scan → uri3.scanner.http_scanner.scan_http
  uri3.scanner.scanner.scan → uri3.protocols.parser.parse_uri
  generator.verify.verify_generated_agent → generator.hashutil.file_sha256
  generator.verify.verify_generated → generator.verify.verify_generated_agent
  generator.verify.main → generator.verify.verify_generated
  uri3.protocols.normalizer.normalize_uri → uri3.protocols.parser.parse_uri
  uri3.resolvers.router.Uri3Router.resolve → uri3.protocols.parser.parse_uri
  uri3.resolvers.router.Uri3Router.call → uri3.protocols.parser.parse_uri
  uri3.resolvers.python_resolver.PythonResolver.resolve → uri3.protocols.parser.parse_uri
  uri3.resolvers.env_resolver.EnvResolver.resolve → uri3.protocols.parser.parse_uri
  hypervisor.config.get_default_config → hypervisor.config._load_yaml
  hypervisor.config.load_config → hypervisor.config.get_default_config
  hypervisor.config.get_config → hypervisor.config.load_config
  meta_agent.repair.repair_agent_spec → generator.validate.validate_agent
  meta_agent.repair.repair_agent_spec → meta_agent.repair._load_yaml
  hypervisor.verifier.cli.main → hypervisor.contract_registry.loader.load_contract_registry
  hypervisor.verifier.cli.main → hypervisor.contract_registry.validate.validate_registry
  hypervisor.verifier.cli.main → hypervisor.verifier.capability_tests.build_capability_test_plan
  hypervisor.uri2llm.function_resolver.resolve_python → hypervisor.uri2llm.function_resolver._split_python_uri
  hypervisor.uri2llm.function_resolver.call_python → hypervisor.uri2llm.function_resolver._split_python_uri
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
  uri3.resolvers.llm_resolver.LLMResolver.resolve → uri3.protocols.parser.parse_uri
  hypervisor.contract_registry.registry_exporter.export_json → hypervisor.contract_registry.registry_builder.write_registry_manifest
  hypervisor.contract_registry.registry_exporter.export_markdown → hypervisor.contract_registry.registry_builder.build_registry_manifest
  hypervisor.contract_registry.schema_validator.validate_file → hypervisor.contract_registry.schema_validator._read_yaml
  hypervisor.contract_registry.schema_validator.validate_file → hypervisor.contract_registry.schema_validator._read_json
  nl2uri.cli.generate → nl2uri.planner.rule_based_plan
  nl2uri.cli.generate → nl2uri.llm_planner.llm_plan
  nl2uri.cli.generate → nl2uri.writer.write_uri_tree
  hypervisor.contract_registry.registry_builder.build_registry_manifest → hypervisor.contract_registry.loader.load_contract_registry
  hypervisor.contract_registry.registry_builder.build_registry_manifest → hypervisor.contract_registry.registry_builder._contract_hash
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

WronAI Hypervisor — orchestrator and control plane for AI desktop agents, NLP-to-URI resolution, koru drivers, and virtualized execution

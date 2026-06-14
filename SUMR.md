# Resource Agent System v0.6

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `resource-agent-system`
- **version**: `0.5.12`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(3), app.doql.less, goal.yaml, .env.example, Dockerfile, docker-compose.yml, project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: resource-agent-system;
  version: 0.5.12;
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
interface[type="cli"] page[name="touri"] {
  entry: touri.cli:main;
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

## Workflows

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

## Call Graph

*407 nodes · 500 edges · 141 modules · CC̄=3.6*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `load_contract_registry` *(in hypervisor.contract_registry.loader)* | 9 | 6 | 33 | **39** |
| `resolve_llm_profile` *(in packages.uri3.uri3.config.llm_profiles)* | 10 ⚠ | 4 | 32 | **36** |
| `list` *(in packages.uri2ops.uri2ops.operation_registry.models.OperationRegistry)* | 1 | 33 | 2 | **35** |
| `infer_intent` *(in meta_agent.planner)* | 9 | 1 | 30 | **31** |
| `write_domain_pack` *(in packages.resource-agent-hypervisor.hypervisor.domain_pack.pack_writer)* | 3 | 1 | 30 | **31** |
| `_parse_step` *(in packages.uri2flow.uri2flow.parser)* | 10 ⚠ | 1 | 29 | **30** |
| `build_graph_from_tree` *(in uri3.graph.uri_graph)* | 10 ⚠ | 2 | 28 | **30** |
| `parse_docker_uri` *(in packages.uri3.uri3.resolvers.docker_resolver)* | 12 ⚠ | 5 | 23 | **28** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/hypervisor
# generated in 0.20s
# nodes: 407 | edges: 500 | modules: 141
# CC̄=3.6

HUBS[20]:
  hypervisor.contract_registry.loader.load_contract_registry
    CC=9  in:6  out:33  total:39
  packages.uri3.uri3.config.llm_profiles.resolve_llm_profile
    CC=10  in:4  out:32  total:36
  packages.uri2ops.uri2ops.operation_registry.models.OperationRegistry.list
    CC=1  in:33  out:2  total:35
  meta_agent.planner.infer_intent
    CC=9  in:1  out:30  total:31
  packages.resource-agent-hypervisor.hypervisor.domain_pack.pack_writer.write_domain_pack
    CC=3  in:1  out:30  total:31
  packages.uri2flow.uri2flow.parser._parse_step
    CC=10  in:1  out:29  total:30
  uri3.graph.uri_graph.build_graph_from_tree
    CC=10  in:2  out:28  total:30
  packages.uri3.uri3.resolvers.docker_resolver.parse_docker_uri
    CC=12  in:5  out:23  total:28
  packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload
    CC=12  in:2  out:24  total:26
  packages.nl2uri.nl2uri.graph_repair.sanitize_node
    CC=16  in:1  out:25  total:26
  packages.nl2uri.nl2uri.graph_repair.repair_graph_body
    CC=12  in:1  out:25  total:26
  generator.model.load_agent_spec
    CC=7  in:2  out:24  total:26
  packages.uri3.uri3.logs.reader.summarize_logs
    CC=6  in:6  out:18  total:24
  packages.uri3.uri3.graph.graph_validator.validate_workflow_graph
    CC=9  in:10  out:13  total:23
  packages.uri3.uri3.graph.adapters.browser_playwright.PlaywrightBrowserAdapter.execute
    CC=11  in:0  out:23  total:23
  packages.uri3.uri3.config.repo_root.find_repo_root
    CC=4  in:18  out:4  total:22
  packages.uri3.uri3.resolvers.log_resolver.parse_log_uri
    CC=7  in:5  out:16  total:21
  packages.resource-agent-hypervisor.hypervisor.cli_commands.echo_json
    CC=2  in:16  out:5  total:21
  packages.resource-agent-factory.generator.agent_generator.generate_agent
    CC=5  in:3  out:17  total:20
  packages.uri2flow.uri2flow.parser.parse_flow
    CC=12  in:3  out:16  total:19

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
  packages.nl2uri.nl2uri.domain_planner  [1 funcs]
    plan_from_prompt  CC=7  out:11
  packages.nl2uri.nl2uri.graph_planner  [1 funcs]
    wrap_nl2uri_output  CC=1  out:0
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
  packages.resource-agent-hypervisor.hypervisor.contract_registry.cli_commands  [5 funcs]
    run_build_command  CC=1  out:2
    run_check_command  CC=5  out:13
    run_cross_command  CC=3  out:4
    run_export_md_command  CC=1  out:2
    run_schema_command  CC=5  out:3
  packages.resource-agent-hypervisor.hypervisor.contract_registry.cross_checks.capabilities  [1 funcs]
    validate_capability_cross_refs  CC=13  out:6
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
  packages.resource-agent-hypervisor.hypervisor.contract_registry.registry_checks.capabilities  [3 funcs]
    validate_capabilities  CC=4  out:5
    validate_command_capability  CC=3  out:2
    validate_resource_read_capability  CC=7  out:3
  packages.resource-agent-hypervisor.hypervisor.contract_registry.registry_checks.resources  [2 funcs]
    validate_resources  CC=7  out:9
    validate_views  CC=3  out:2
  packages.resource-agent-hypervisor.hypervisor.contract_registry.validate  [1 funcs]
    validate_registry  CC=1  out:3
  packages.resource-agent-hypervisor.hypervisor.core  [2 funcs]
    from_config  CC=1  out:2
    status  CC=1  out:4
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.docker_runner  [3 funcs]
    build_docker_deploy_plan  CC=4  out:6
    stop_docker_deployment  CC=4  out:2
    verify_docker_deployment  CC=9  out:5
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.env  [2 funcs]
    default_log_uri  CC=5  out:7
    resolve_deployment_env  CC=1  out:2
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.env_config  [3 funcs]
    load_deployments_uri_config  CC=2  out:3
    load_runtime_uri_config  CC=2  out:3
    repo_config_dir  CC=2  out:2
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.lifecycle  [6 funcs]
    _repo_root  CC=2  out:3
    agent_logs_uri  CC=3  out:6
    agent_status  CC=5  out:9
    restart_agent  CC=1  out:2
    run_agent  CC=8  out:15
    stop_agent  CC=7  out:17
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.process  [1 funcs]
    start_process  CC=4  out:6
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.run_plans  [1 funcs]
    build_run_plan  CC=5  out:7
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.runtime_state  [4 funcs]
    is_process_alive  CC=4  out:1
    load_runtime_state  CC=3  out:5
    runtime_status  CC=6  out:7
    save_runtime_state  CC=1  out:4
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.selector  [1 funcs]
    resolve_deployment  CC=7  out:9
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.ssh_deploy  [2 funcs]
    apply_ssh_deploy_plan  CC=7  out:6
    build_ssh_deploy_plan  CC=3  out:10
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.ssh_verify  [1 funcs]
    verify_remote_deployment  CC=12  out:6
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.status  [3 funcs]
    registry_summary  CC=4  out:2
    resolve_status  CC=11  out:7
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
  packages.uri2flow.uri2flow.cli  [5 funcs]
    build_parser  CC=1  out:14
    cmd_expand  CC=3  out:8
    cmd_print  CC=1  out:4
    cmd_validate  CC=2  out:4
    main  CC=1  out:3
  packages.uri2flow.uri2flow.expander  [4 funcs]
    _edges_from_depends  CC=4  out:2
    _node_from_step  CC=11  out:3
    dump_yaml  CC=1  out:1
    expand_flow  CC=6  out:8
  packages.uri2flow.uri2flow.parser  [4 funcs]
    _as_list  CC=5  out:5
    _parse_step  CC=10  out:29
    load_flow  CC=3  out:6
    parse_flow  CC=12  out:16
  packages.uri2flow.uri2flow.resolver  [1 funcs]
    default_operation_for_uri  CC=3  out:4
  packages.uri2flow.uri2flow.utils  [4 funcs]
    node_id_from_uri  CC=5  out:7
    path_parts  CC=4  out:4
    scheme_of  CC=1  out:1
    slugify  CC=2  out:4
  packages.uri2flow.uri2flow.validator  [1 funcs]
    validate_flow  CC=11  out:5
  packages.uri2ops.uri2ops.operation_registry.models  [1 funcs]
    list  CC=1  out:2
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
  packages.uri3.uri3.graph.adapters.browser_playwright  [2 funcs]
    execute  CC=11  out:23
    _session_state  CC=1  out:1
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
  packages.uri3.uri3.graph.graph_serializer  [3 funcs]
    edges_from_depends_on  CC=4  out:5
    normalize_graph_payload  CC=12  out:24
    task_steps_to_graph  CC=3  out:7
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
  packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload → packages.uri2ops.uri2ops.operation_registry.models.OperationRegistry.list
  packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload → packages.uri3.uri3.graph.graph_serializer.edges_from_depends_on
  packages.uri3.uri3.graph.graph_serializer.task_steps_to_graph → packages.uri3.uri3.graph.graph_serializer.edges_from_depends_on
  packages.uri3.uri3.graph.artifacts.write_artifact → packages.uri3.uri3.graph.artifacts.artifact_path
  packages.uri3.uri3.graph.artifacts.write_artifact → packages.uri3.uri3.graph.artifacts.artifact_uri
  packages.uri3.uri3.graph.dependency_graph.topological_sort → packages.uri3.uri3.graph.dependency_graph.detect_cycles
  packages.uri3.uri3.graph.dependency_graph.dependency_summary → packages.uri3.uri3.graph.dependency_graph.detect_cycles
  packages.uri3.uri3.graph.dependency_graph.dependency_summary → packages.uri3.uri3.graph.dependency_graph.topological_sort
  packages.uri3.uri3.graph.policy.can_execute_step → packages.uri3.uri3.graph.operation_registry.effective_kind
  packages.uri3.uri3.graph.policy.can_execute_step → packages.uri3.uri3.graph.operation_registry.requires_approval
  packages.uri3.uri3.graph.models.GraphNode.from_dict → packages.uri2ops.uri2ops.operation_registry.models.OperationRegistry.list
  packages.uri3.uri3.graph.execution_models.new_execution_context → packages.uri3.uri3.config.repo_root.find_repo_root
  packages.uri3.uri3.graph.event_log.append_workflow_event → packages.uri3.uri3.graph.event_log.workflow_event_path
  packages.uri3.uri3.graph.event_log.append_workflow_event → packages.uri3.uri3.graph.execution_models.utc_now_iso
  packages.uri3.uri3.graph.graph_validator._schema_path → packages.uri3.uri3.config.repo_root.find_repo_root
  packages.uri3.uri3.graph.graph_validator.load_workflow_graph → packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload
  packages.uri3.uri3.graph.graph_validator.load_workflow_graph → packages.uri3.uri3.graph.graph_serializer.task_steps_to_graph
  packages.uri3.uri3.graph.graph_validator.validate_workflow_schema → packages.uri3.uri3.graph.graph_validator._schema_path
  packages.uri3.uri3.graph.graph_validator.validate_workflow_schema → packages.uri2ops.uri2ops.operation_registry.models.OperationRegistry.list
  packages.uri3.uri3.graph.graph_validator.validate_workflow_graph → packages.uri3.uri3.graph.graph_validator.load_workflow_graph
  packages.uri3.uri3.graph.graph_validator.validate_workflow_graph → packages.uri3.uri3.graph.graph_validator.validate_workflow_schema
  packages.uri3.uri3.graph.graph_validator.validate_workflow_graph → packages.uri3.uri3.graph.dependency_graph.detect_cycles
  packages.uri3.uri3.graph.graph_validator.validate_workflow_graph → uri3.validators.uri_validator.validate_uri
  packages.uri3.uri3.graph.operation_registry.effective_kind → packages.uri3.uri3.graph.operation_registry.scheme_from_uri
  packages.uri3.uri3.graph.operation_registry.requires_approval → packages.uri3.uri3.graph.operation_registry.effective_kind
  packages.uri3.uri3.graph.operation_registry.validate_node_operation → packages.uri3.uri3.graph.operation_registry.scheme_from_uri
  packages.uri3.uri3.graph.operation_registry.validate_node_operation → packages.uri3.uri3.graph.operation_registry.allowed_operations
  packages.uri3.uri3.graph.adapters.browser_mock.BrowserMockAdapter.execute → packages.uri3.uri3.graph.artifacts.write_artifact
  packages.uri3.uri3.graph.adapters.browser_mock.BrowserMockAdapter.execute → packages.uri3.uri3.graph.adapters.browser_mock.json_dumps
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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/hypervisor
# generated in 0.20s
# nodes: 407 | edges: 500 | modules: 141
# CC̄=3.6

HUBS[20]:
  hypervisor.contract_registry.loader.load_contract_registry
    CC=9  in:6  out:33  total:39
  packages.uri3.uri3.config.llm_profiles.resolve_llm_profile
    CC=10  in:4  out:32  total:36
  packages.uri2ops.uri2ops.operation_registry.models.OperationRegistry.list
    CC=1  in:33  out:2  total:35
  meta_agent.planner.infer_intent
    CC=9  in:1  out:30  total:31
  packages.resource-agent-hypervisor.hypervisor.domain_pack.pack_writer.write_domain_pack
    CC=3  in:1  out:30  total:31
  packages.uri2flow.uri2flow.parser._parse_step
    CC=10  in:1  out:29  total:30
  uri3.graph.uri_graph.build_graph_from_tree
    CC=10  in:2  out:28  total:30
  packages.uri3.uri3.resolvers.docker_resolver.parse_docker_uri
    CC=12  in:5  out:23  total:28
  packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload
    CC=12  in:2  out:24  total:26
  packages.nl2uri.nl2uri.graph_repair.sanitize_node
    CC=16  in:1  out:25  total:26
  packages.nl2uri.nl2uri.graph_repair.repair_graph_body
    CC=12  in:1  out:25  total:26
  generator.model.load_agent_spec
    CC=7  in:2  out:24  total:26
  packages.uri3.uri3.logs.reader.summarize_logs
    CC=6  in:6  out:18  total:24
  packages.uri3.uri3.graph.graph_validator.validate_workflow_graph
    CC=9  in:10  out:13  total:23
  packages.uri3.uri3.graph.adapters.browser_playwright.PlaywrightBrowserAdapter.execute
    CC=11  in:0  out:23  total:23
  packages.uri3.uri3.config.repo_root.find_repo_root
    CC=4  in:18  out:4  total:22
  packages.uri3.uri3.resolvers.log_resolver.parse_log_uri
    CC=7  in:5  out:16  total:21
  packages.resource-agent-hypervisor.hypervisor.cli_commands.echo_json
    CC=2  in:16  out:5  total:21
  packages.resource-agent-factory.generator.agent_generator.generate_agent
    CC=5  in:3  out:17  total:20
  packages.uri2flow.uri2flow.parser.parse_flow
    CC=12  in:3  out:16  total:19

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
  packages.nl2uri.nl2uri.domain_planner  [1 funcs]
    plan_from_prompt  CC=7  out:11
  packages.nl2uri.nl2uri.graph_planner  [1 funcs]
    wrap_nl2uri_output  CC=1  out:0
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
  packages.resource-agent-hypervisor.hypervisor.contract_registry.cli_commands  [5 funcs]
    run_build_command  CC=1  out:2
    run_check_command  CC=5  out:13
    run_cross_command  CC=3  out:4
    run_export_md_command  CC=1  out:2
    run_schema_command  CC=5  out:3
  packages.resource-agent-hypervisor.hypervisor.contract_registry.cross_checks.capabilities  [1 funcs]
    validate_capability_cross_refs  CC=13  out:6
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
  packages.resource-agent-hypervisor.hypervisor.contract_registry.registry_checks.capabilities  [3 funcs]
    validate_capabilities  CC=4  out:5
    validate_command_capability  CC=3  out:2
    validate_resource_read_capability  CC=7  out:3
  packages.resource-agent-hypervisor.hypervisor.contract_registry.registry_checks.resources  [2 funcs]
    validate_resources  CC=7  out:9
    validate_views  CC=3  out:2
  packages.resource-agent-hypervisor.hypervisor.contract_registry.validate  [1 funcs]
    validate_registry  CC=1  out:3
  packages.resource-agent-hypervisor.hypervisor.core  [2 funcs]
    from_config  CC=1  out:2
    status  CC=1  out:4
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.docker_runner  [3 funcs]
    build_docker_deploy_plan  CC=4  out:6
    stop_docker_deployment  CC=4  out:2
    verify_docker_deployment  CC=9  out:5
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.env  [2 funcs]
    default_log_uri  CC=5  out:7
    resolve_deployment_env  CC=1  out:2
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.env_config  [3 funcs]
    load_deployments_uri_config  CC=2  out:3
    load_runtime_uri_config  CC=2  out:3
    repo_config_dir  CC=2  out:2
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.lifecycle  [6 funcs]
    _repo_root  CC=2  out:3
    agent_logs_uri  CC=3  out:6
    agent_status  CC=5  out:9
    restart_agent  CC=1  out:2
    run_agent  CC=8  out:15
    stop_agent  CC=7  out:17
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.process  [1 funcs]
    start_process  CC=4  out:6
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.run_plans  [1 funcs]
    build_run_plan  CC=5  out:7
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.runtime_state  [4 funcs]
    is_process_alive  CC=4  out:1
    load_runtime_state  CC=3  out:5
    runtime_status  CC=6  out:7
    save_runtime_state  CC=1  out:4
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.selector  [1 funcs]
    resolve_deployment  CC=7  out:9
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.ssh_deploy  [2 funcs]
    apply_ssh_deploy_plan  CC=7  out:6
    build_ssh_deploy_plan  CC=3  out:10
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.ssh_verify  [1 funcs]
    verify_remote_deployment  CC=12  out:6
  packages.resource-agent-hypervisor.hypervisor.deployment_registry.status  [3 funcs]
    registry_summary  CC=4  out:2
    resolve_status  CC=11  out:7
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
  packages.uri2flow.uri2flow.cli  [5 funcs]
    build_parser  CC=1  out:14
    cmd_expand  CC=3  out:8
    cmd_print  CC=1  out:4
    cmd_validate  CC=2  out:4
    main  CC=1  out:3
  packages.uri2flow.uri2flow.expander  [4 funcs]
    _edges_from_depends  CC=4  out:2
    _node_from_step  CC=11  out:3
    dump_yaml  CC=1  out:1
    expand_flow  CC=6  out:8
  packages.uri2flow.uri2flow.parser  [4 funcs]
    _as_list  CC=5  out:5
    _parse_step  CC=10  out:29
    load_flow  CC=3  out:6
    parse_flow  CC=12  out:16
  packages.uri2flow.uri2flow.resolver  [1 funcs]
    default_operation_for_uri  CC=3  out:4
  packages.uri2flow.uri2flow.utils  [4 funcs]
    node_id_from_uri  CC=5  out:7
    path_parts  CC=4  out:4
    scheme_of  CC=1  out:1
    slugify  CC=2  out:4
  packages.uri2flow.uri2flow.validator  [1 funcs]
    validate_flow  CC=11  out:5
  packages.uri2ops.uri2ops.operation_registry.models  [1 funcs]
    list  CC=1  out:2
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
  packages.uri3.uri3.graph.adapters.browser_playwright  [2 funcs]
    execute  CC=11  out:23
    _session_state  CC=1  out:1
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
  packages.uri3.uri3.graph.graph_serializer  [3 funcs]
    edges_from_depends_on  CC=4  out:5
    normalize_graph_payload  CC=12  out:24
    task_steps_to_graph  CC=3  out:7
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
  packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload → packages.uri2ops.uri2ops.operation_registry.models.OperationRegistry.list
  packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload → packages.uri3.uri3.graph.graph_serializer.edges_from_depends_on
  packages.uri3.uri3.graph.graph_serializer.task_steps_to_graph → packages.uri3.uri3.graph.graph_serializer.edges_from_depends_on
  packages.uri3.uri3.graph.artifacts.write_artifact → packages.uri3.uri3.graph.artifacts.artifact_path
  packages.uri3.uri3.graph.artifacts.write_artifact → packages.uri3.uri3.graph.artifacts.artifact_uri
  packages.uri3.uri3.graph.dependency_graph.topological_sort → packages.uri3.uri3.graph.dependency_graph.detect_cycles
  packages.uri3.uri3.graph.dependency_graph.dependency_summary → packages.uri3.uri3.graph.dependency_graph.detect_cycles
  packages.uri3.uri3.graph.dependency_graph.dependency_summary → packages.uri3.uri3.graph.dependency_graph.topological_sort
  packages.uri3.uri3.graph.policy.can_execute_step → packages.uri3.uri3.graph.operation_registry.effective_kind
  packages.uri3.uri3.graph.policy.can_execute_step → packages.uri3.uri3.graph.operation_registry.requires_approval
  packages.uri3.uri3.graph.models.GraphNode.from_dict → packages.uri2ops.uri2ops.operation_registry.models.OperationRegistry.list
  packages.uri3.uri3.graph.execution_models.new_execution_context → packages.uri3.uri3.config.repo_root.find_repo_root
  packages.uri3.uri3.graph.event_log.append_workflow_event → packages.uri3.uri3.graph.event_log.workflow_event_path
  packages.uri3.uri3.graph.event_log.append_workflow_event → packages.uri3.uri3.graph.execution_models.utc_now_iso
  packages.uri3.uri3.graph.graph_validator._schema_path → packages.uri3.uri3.config.repo_root.find_repo_root
  packages.uri3.uri3.graph.graph_validator.load_workflow_graph → packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload
  packages.uri3.uri3.graph.graph_validator.load_workflow_graph → packages.uri3.uri3.graph.graph_serializer.task_steps_to_graph
  packages.uri3.uri3.graph.graph_validator.validate_workflow_schema → packages.uri3.uri3.graph.graph_validator._schema_path
  packages.uri3.uri3.graph.graph_validator.validate_workflow_schema → packages.uri2ops.uri2ops.operation_registry.models.OperationRegistry.list
  packages.uri3.uri3.graph.graph_validator.validate_workflow_graph → packages.uri3.uri3.graph.graph_validator.load_workflow_graph
  packages.uri3.uri3.graph.graph_validator.validate_workflow_graph → packages.uri3.uri3.graph.graph_validator.validate_workflow_schema
  packages.uri3.uri3.graph.graph_validator.validate_workflow_graph → packages.uri3.uri3.graph.dependency_graph.detect_cycles
  packages.uri3.uri3.graph.graph_validator.validate_workflow_graph → uri3.validators.uri_validator.validate_uri
  packages.uri3.uri3.graph.operation_registry.effective_kind → packages.uri3.uri3.graph.operation_registry.scheme_from_uri
  packages.uri3.uri3.graph.operation_registry.requires_approval → packages.uri3.uri3.graph.operation_registry.effective_kind
  packages.uri3.uri3.graph.operation_registry.validate_node_operation → packages.uri3.uri3.graph.operation_registry.scheme_from_uri
  packages.uri3.uri3.graph.operation_registry.validate_node_operation → packages.uri3.uri3.graph.operation_registry.allowed_operations
  packages.uri3.uri3.graph.adapters.browser_mock.BrowserMockAdapter.execute → packages.uri3.uri3.graph.artifacts.write_artifact
  packages.uri3.uri3.graph.adapters.browser_mock.BrowserMockAdapter.execute → packages.uri3.uri3.graph.adapters.browser_mock.json_dumps
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 355f 15943L | python:248,yaml:54,json:14,shell:13,toml:8,txt:4,yml:3,proto:2,j2:1,mk:1 | 2026-06-14
# generated in 0.06s
# CC̅=3.6 | critical:8/661 | dups:0 | cycles:0

HEALTH[8]:
  🟡 CC    detect_cycles CC=15 (limit:15)
  🟡 CC    resolve_uri_values CC=15 (limit:15)
  🟡 CC    sanitize_node CC=16 (limit:15)
  🟡 CC    classify_output_kind CC=23 (limit:15)
  🟡 CC    extract_flow_payload CC=20 (limit:15)
  🟡 CC    sanitize_flow_step CC=18 (limit:15)
  🟡 CC    _ensure_step_ids CC=19 (limit:15)
  🟡 CC    run_workflow CC=21 (limit:15)

REFACTOR[1]:
  1. split 8 high-CC methods  (CC>15)

PIPELINES[185]:
  [1] Src [adjacency]: adjacency
      PURITY: 100% pure
  [2] Src [reverse_adjacency]: reverse_adjacency
      PURITY: 100% pure
  [3] Src [dependency_summary]: dependency_summary → detect_cycles
      PURITY: 100% pure
  [4] Src [add_node]: add_node
      PURITY: 100% pure
  [5] Src [add_edge]: add_edge
      PURITY: 100% pure
  [6] Src [from_dict]: from_dict → list
      PURITY: 100% pure
  [7] Src [to_dict]: to_dict
      PURITY: 100% pure
  [8] Src [resolve_ref]: resolve_ref
      PURITY: 100% pure
  [9] Src [to_dict]: to_dict
      PURITY: 100% pure
  [10] Src [execute]: execute → write_artifact → artifact_path
      PURITY: 100% pure
  [11] Src [execute]: execute → _session_state
      PURITY: 100% pure
  [12] Src [scan]: scan → parse_uri
      PURITY: 100% pure
  [13] Src [normalize_uri]: normalize_uri → parse_uri
      PURITY: 100% pure
  [14] Src [spec]: spec → list
      PURITY: 100% pure
  [15] Src [spec]: spec
      PURITY: 100% pure
  [16] Src [to_dict]: to_dict → list
      PURITY: 100% pure
  [17] Src [to_dict]: to_dict → list
      PURITY: 100% pure
  [18] Src [spec]: spec
      PURITY: 100% pure
  [19] Src [spec]: spec
      PURITY: 100% pure
  [20] Src [spec]: spec
      PURITY: 100% pure
  [21] Src [spec]: spec
      PURITY: 100% pure
  [22] Src [spec]: spec
      PURITY: 100% pure
  [23] Src [spec]: spec
      PURITY: 100% pure
  [24] Src [resource_like_spec]: resource_like_spec
      PURITY: 100% pure
  [25] Src [_parse_log]: _parse_log → parse_log_uri → parse_query → resolve_path
      PURITY: 100% pure
  [26] Src [_parse_env]: _parse_env → resolve_env → _env_var_name
      PURITY: 100% pure
  [27] Src [_parse_python]: _parse_python → resolve_python → _split_python_uri
      PURITY: 100% pure
  [28] Src [_parse_llm]: _parse_llm → resolve_llm
      PURITY: 100% pure
  [29] Src [_parse_pypi]: _parse_pypi → resolve_pypi
      PURITY: 100% pure
  [30] Src [_parse_http]: _parse_http → resolve_http_like
      PURITY: 100% pure
  [31] Src [_parse_a2a]: _parse_a2a → resolve_a2a
      PURITY: 100% pure
  [32] Src [_parse_mcp]: _parse_mcp → resolve_mcp
      PURITY: 100% pure
  [33] Src [_parse_docker]: _parse_docker → resolve_docker → parse_docker_uri → _first
      PURITY: 100% pure
  [34] Src [_parse_ssh]: _parse_ssh → resolve_ssh → parse_ssh_uri
      PURITY: 100% pure
  [35] Src [build_scheme_registry]: build_scheme_registry
      PURITY: 100% pure
  [36] Src [spec]: spec
      PURITY: 100% pure
  [37] Src [to_dict]: to_dict
      PURITY: 100% pure
  [38] Src [fetch]: fetch
      PURITY: 100% pure
  [39] Src [resolve_docker_target]: resolve_docker_target → parse_docker_uri → _first
      PURITY: 100% pure
  [40] Src [_resolve_docker]: _resolve_docker → resolve_docker → parse_docker_uri → _first
      PURITY: 100% pure
  [41] Src [scheme_from_uri]: scheme_from_uri
      PURITY: 100% pure
  [42] Src [resolve]: resolve → resolve_llm
      PURITY: 100% pure
  [43] Src [__init__]: __init__ → build_resolver_registry
      PURITY: 100% pure
  [44] Src [resolve]: resolve → resolve_env → _env_var_name
      PURITY: 100% pure
  [45] Src [call]: call → call_env → _env_var_name
      PURITY: 100% pure
  [46] Src [resolve]: resolve → scheme_from_uri
      PURITY: 100% pure
  [47] Src [call]: call → call_python → _split_python_uri
      PURITY: 100% pure
  [48] Src [resolve]: resolve → resolve_python → _split_python_uri
      PURITY: 100% pure
  [49] Src [call]: call → call_python → _split_python_uri
      PURITY: 100% pure
  [50] Src [to_dict]: to_dict
      PURITY: 100% pure

LAYERS:
  generator/                      CC̄=6.0    ←in:14  →out:0
  │ validate                     0L  0C    3m  CC=11     ←5
  │ hashutil                     0L  0C    1m  CC=1      ←2
  │ verify                       0L  0C    3m  CC=9      ←4
  │ model                        0L  2C    2m  CC=7      ←2
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ Dockerfile.j2                0L  0C    0m  CC=0.0    ←0
  │
  packages/                       CC̄=3.7    ←in:0  →out:0
  │ graph_planner              322L  0C   11m  CC=12     ←5
  │ !! graph_executor             250L  0C    5m  CC=21     ←3
  │ cli                        246L  0C   15m  CC=6      ←0
  │ !! flow_repair                229L  0C   13m  CC=20     ←2
  │ !! graph_repair               195L  0C    8m  CC=16     ←2
  │ lifecycle                  166L  0C    6m  CC=8      ←8
  │ docker_resolver            154L  1C    7m  CC=12     ←5
  │ status                     151L  0C   10m  CC=11     ←5
  │ cli                        148L  0C   15m  CC=4      ←0
  │ graph_planner_llm          147L  0C    3m  CC=4      ←1
  │ pipeline                   141L  2C    4m  CC=4      ←1
  │ cli                        135L  0C    8m  CC=6      ←0
  │ loader                     130L  0C    8m  CC=14     ←4
  │ cli_commands               128L  0C    6m  CC=7      ←1
  │ app                        125L  2C    1m  CC=1      ←1
  │ execution_models           122L  4C    6m  CC=4      ←2
  │ uri2ops_adapter            122L  1C    9m  CC=9      ←2
  │ registry.yaml              121L  0C    0m  CC=0.0    ←0
  │ instance_parser            119L  0C   13m  CC=4      ←2
  │ registry                   113L  3C    5m  CC=11     ←1
  │ flow_planner_llm           112L  0C    3m  CC=4      ←1
  │ ssh_resolver               110L  0C    7m  CC=8      ←6
  │ resolver                   107L  1C   10m  CC=7      ←1
  │ agent_generator            106L  0C    4m  CC=5      ←2
  │ flow_planner               106L  0C    5m  CC=12     ←3
  │ reader                     104L  0C    5m  CC=9      ←5
  │ planner_templates          102L  0C    5m  CC=6      ←2
  │ flow                       100L  0C    3m  CC=6      ←0
  │ compose                     99L  0C    8m  CC=9      ←1
  │ spec_registry               99L  0C    5m  CC=5      ←3
  │ ssh_auth                    96L  0C    7m  CC=12     ←2
  │ loader                      96L  0C    5m  CC=6      ←2
  │ ssh_deploy                  95L  0C    2m  CC=7      ←1
  │ env_resolver                94L  1C    7m  CC=8      ←5
  │ docker_scanner              91L  0C    5m  CC=6      ←2
  │ ssh_scanner                 90L  0C    6m  CC=8      ←2
  │ parser                      90L  1C    4m  CC=12     ←3
  │ !! uri_yaml                    89L  0C    3m  CC=15     ←7
  │ models                      88L  3C    5m  CC=8      ←0
  │ log_resolver                85L  2C    5m  CC=7      ←3
  │ core                        84L  1C    7m  CC=3      ←0
  │ llm_profiles                83L  1C    4m  CC=10     ←4
  │ !! dependency_graph            82L  0C    5m  CC=15     ←2
  │ expander                    81L  0C    4m  CC=11     ←4
  │ pack_writer                 79L  0C    1m  CC=3      ←1
  │ discovery                   79L  0C    1m  CC=1      ←0
  │ !! output_classifier           78L  0C    1m  CC=23     ←2
  │ browser_playwright          77L  1C    3m  CC=11     ←1
  │ http_scanner                76L  0C    6m  CC=7      ←3
  │ log                         76L  0C    1m  CC=3      ←0
  │ docker_runner               76L  0C    6m  CC=9      ←3
  │ generator                   75L  0C    2m  CC=2      ←1
  │ local_targets               75L  0C    3m  CC=6      ←1
  │ parsing                     73L  0C    4m  CC=14     ←1
  │ filters                     73L  0C    7m  CC=7      ←1
  │ graph_validator             73L  0C    4m  CC=10     ←6
  │ analyze                     73L  0C    3m  CC=14     ←2
  │ orchestrator                73L  0C    4m  CC=7      ←2
  │ operation_registry          71L  0C    6m  CC=2      ←7
  │ cli_commands                69L  0C    6m  CC=3      ←1
  │ base                        67L  2C    2m  CC=4      ←0
  │ dispatch                    67L  0C    3m  CC=3      ←1
  │ models                      67L  2C    5m  CC=2      ←18
  │ cli                         66L  0C    5m  CC=3      ←1
  │ browser_router              66L  1C    5m  CC=5      ←0
  │ planner_validation          65L  0C    3m  CC=10     ←1
  │ cli_commands                65L  0C    5m  CC=5      ←0
  │ runtime_state               65L  0C    8m  CC=6      ←1
  │ helpers                     64L  0C    2m  CC=5      ←2
  │ validator                   64L  0C    3m  CC=11     ←2
  │ graph_serializer            63L  0C    4m  CC=12     ←3
  │ defaults                    63L  0C    4m  CC=4      ←1
  │ agent_card                  63L  0C    0m  CC=0.0    ←0
  │ merge_helpers               61L  0C    3m  CC=6      ←1
  │ planner_llm                 59L  0C    2m  CC=4      ←3
  │ __init__                    59L  0C    0m  CC=0.0    ←0
  │ ssh_run                     58L  0C    1m  CC=7      ←1
  │ docker_stacks               57L  0C    4m  CC=5      ←2
  │ __init__                    57L  0C    0m  CC=0.0    ←0
  │ log_query                   55L  0C    6m  CC=8      ←1
  │ header                      51L  0C    5m  CC=3      ←1
  │ cli                         51L  0C    1m  CC=7      ←0
  │ operator_task.schema.json    51L  0C    0m  CC=0.0    ←0
  │ config_checks               50L  0C    4m  CC=7      ←1
  │ models                      50L  2C    3m  CC=5      ←0
  │ env                         50L  0C    3m  CC=9      ←3
  │ service                     50L  1C    9m  CC=2      ←2
  │ nlp2uri.yaml                50L  0C    0m  CC=0.0    ←0
  │ agent_contract              48L  0C    1m  CC=2      ←1
  │ models                      47L  2C    1m  CC=11     ←0
  │ mcp_wrapper                 47L  0C    2m  CC=2      ←1
  │ compose_generator           46L  0C    2m  CC=2      ←2
  │ operation_registry.schema.json    46L  0C    0m  CC=0.0    ←0
  │ resolve_core                45L  1C    2m  CC=8      ←0
  │ workflow                    45L  0C    1m  CC=1      ←0
  │ a2a_wrapper                 45L  0C    1m  CC=3      ←1
  │ browser_mock                44L  1C    2m  CC=8      ←1
  │ llm_profile_builder         44L  0C    4m  CC=7      ←1
  │ repo_root                   44L  0C    4m  CC=7      ←18
  │ loader                      44L  0C    4m  CC=5      ←4
  │ docker                      43L  0C    1m  CC=1      ←0
  │ validator                   43L  0C    2m  CC=14     ←3
  │ scanner                     42L  0C    2m  CC=5      ←0
  │ cli_shortcuts               41L  0C    5m  CC=4      ←2
  │ cli                         41L  0C    2m  CC=5      ←0
  │ uri_config                  40L  0C    2m  CC=10     ←1
  │ capabilities                40L  0C    3m  CC=7      ←1
  │ uri_flow.schema.json        40L  0C    0m  CC=0.0    ←0
  │ utils                       38L  0C    4m  CC=5      ←3
  │ client                      38L  1C    8m  CC=2      ←0
  │ ssh_verify                  38L  0C    1m  CC=12     ←1
  │ container                   37L  0C    3m  CC=8      ←1
  │ agent_card                  37L  0C    0m  CC=0.0    ←0
  │ controller                  36L  0C    1m  CC=11     ←2
  │ cross_validator             36L  0C    2m  CC=5      ←1
  │ resolve                     36L  0C    1m  CC=1      ←0
  │ pyproject.toml              36L  0C    0m  CC=0.0    ←0
  │ writer                      34L  0C    1m  CC=3      ←2
  │ artifacts                   33L  0C    3m  CC=2      ←3
  │ domain_planner              33L  0C    1m  CC=7      ←5
  │ validators                  33L  0C    2m  CC=5      ←1
  │ cli                         33L  0C    1m  CC=10     ←0
  │ run_plans                   33L  0C    1m  CC=5      ←3
  │ dispatcher                  33L  0C    3m  CC=3      ←2
  │ loader                      33L  0C    3m  CC=10     ←2
  │ pyproject.toml              33L  0C    0m  CC=0.0    ←0
  │ capabilities                32L  0C    1m  CC=13     ←1
  │ env_merge                   31L  0C    2m  CC=6      ←1
  │ pyproject.toml              31L  0C    0m  CC=0.0    ←0
  │ process                     30L  0C    1m  CC=4      ←1
  │ pyproject.toml              30L  0C    0m  CC=0.0    ←0
  │ main                        29L  0C    2m  CC=2      ←0
  │ router                      28L  1C    3m  CC=2      ←0
  │ env_config                  28L  0C    3m  CC=2      ←1
  │ protocol_resolver           27L  0C    4m  CC=4      ←3
  │ registry                    27L  0C    0m  CC=0.0    ←0
  │ constants                   27L  0C    0m  CC=0.0    ←0
  │ merger                      26L  0C    1m  CC=2      ←1
  │ resources                   26L  0C    2m  CC=7      ←1
  │ model                       25L  1C    1m  CC=1      ←0
  │ selector                    25L  0C    1m  CC=7      ←3
  │ pyproject.toml              25L  0C    0m  CC=0.0    ←0
  │ conditions                  24L  0C    1m  CC=7      ←1
  │ resources                   24L  0C    1m  CC=2      ←1
  │ scheme_registry             24L  0C    0m  CC=0.0    ←0
  │ runner                      24L  0C    0m  CC=0.0    ←0
  │ runner                      23L  0C    1m  CC=4      ←2
  │ graph                       23L  0C    1m  CC=1      ←0
  │ env                         22L  0C    1m  CC=1      ←0
  │ resources                   22L  0C    1m  CC=6      ←1
  │ registry                    21L  0C    1m  CC=1      ←1
  │ policy                      20L  0C    1m  CC=6      ←1
  │ event_log                   20L  0C    2m  CC=1      ←1
  │ uri_tree_validator          20L  0C    2m  CC=2      ←3
  │ python                      18L  0C    1m  CC=1      ←0
  │ commands                    18L  0C    1m  CC=2      ←1
  │ parser                      17L  0C    2m  CC=1      ←1
  │ views.yaml                  17L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              17L  0C    0m  CC=0.0    ←0
  │ llm                         16L  0C    1m  CC=1      ←0
  │ resource_like               16L  0C    1m  CC=1      ←0
  │ views                       16L  0C    1m  CC=2      ←1
  │ proto_index                 16L  0C    2m  CC=2      ←3
  │ main                        16L  0C    0m  CC=0.0    ←0
  │ main                        16L  0C    0m  CC=0.0    ←0
  │ __init__                    16L  0C    0m  CC=0.0    ←0
  │ mcp                         15L  0C    1m  CC=1      ←0
  │ http                        15L  0C    1m  CC=1      ←0
  │ pypi                        15L  0C    1m  CC=1      ←0
  │ a2a                         15L  0C    1m  CC=1      ←0
  │ resources.yaml              15L  0C    0m  CC=0.0    ←0
  │ remote_runner               15L  0C    0m  CC=0.0    ←0
  │ renderers                   14L  0C    1m  CC=3      ←1
  │ ssh_helpers                 14L  0C    2m  CC=2      ←2
  │ planner                     13L  1C    1m  CC=1      ←1
  │ validate                    13L  0C    1m  CC=1      ←2
  │ base                        12L  1C    1m  CC=1      ←0
  │ paths                       12L  0C    1m  CC=1      ←1
  │ __init__                    12L  0C    0m  CC=0.0    ←0
  │ writer                      11L  0C    1m  CC=1      ←2
  │ handlers                    10L  0C    1m  CC=3      ←1
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ __init__                     9L  0C    0m  CC=0.0    ←0
  │ llm_planner                  8L  0C    1m  CC=2      ←0
  │ proto                        8L  0C    1m  CC=2      ←1
  │ paths                        5L  0C    0m  CC=0.0    ←0
  │ paths                        5L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  meta_agent/                     CC̄=3.5    ←in:4  →out:8  !! split
  │ planner                      0L  0C    5m  CC=9      ←2
  │ api                          0L  2C    7m  CC=2      ←0
  │ models                       0L  3C    1m  CC=1      ←0
  │ loader                       0L  0C    2m  CC=2      ←1
  │ pipeline                     0L  0C    1m  CC=2      ←3
  │ rules                        0L  0C    6m  CC=8      ←1
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ domain_pack_generator        0L  0C    0m  CC=0.0    ←0
  │ llm_planner                  0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  hypervisor/                     CC̄=3.2    ←in:0  →out:0
  │ pypi_resolver                0L  0C    1m  CC=5      ←1
  │ templates                    0L  0C    5m  CC=1      ←0
  │ cli                          0L  0C    1m  CC=5      ←0
  │ capability_tests             0L  0C    1m  CC=4      ←1
  │ gate                         0L  1C    1m  CC=5      ←0
  │ models                       0L  8C    9m  CC=4      ←0
  │ env                          0L  0C    4m  CC=9      ←1
  │ validator                    0L  0C    1m  CC=6      ←1
  │ models                       0L  1C    1m  CC=5      ←1
  │ loader                       0L  0C    2m  CC=9      ←5
  │ registry_exporter            0L  0C    2m  CC=6      ←1
  │ schema_validator             0L  1C    4m  CC=6      ←1
  │ models                       0L  4C    3m  CC=4      ←0
  │ registry_builder             0L  0C    4m  CC=5      ←3
  │ writer                       0L  0C    4m  CC=3      ←1
  │ checker                      0L  0C    2m  CC=8      ←0
  │ _version                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ function_resolver            0L  0C    0m  CC=0.0    ←0
  │ protocol_resolver            0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ llm_resolver                 0L  0C    0m  CC=0.0    ←0
  │ router                       0L  0C    0m  CC=0.0    ←0
  │ env_resolver                 0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  domains/                        CC̄=3.0    ←in:0  →out:0
  │ uri_tree.yaml               85L  0C    0m  CC=0.0    ←0
  │ weather_map.proto           41L  0C    0m  CC=0.0    ←0
  │ generate_weather_map        24L  0C    1m  CC=3      ←0
  │ resources.yaml              23L  0C    0m  CC=0.0    ←0
  │ views.yaml                  11L  0C    0m  CC=0.0    ←0
  │ renderers.yaml              10L  0C    0m  CC=0.0    ←0
  │ domain.yaml                  9L  0C    0m  CC=0.0    ←0
  │ commands.yaml                8L  0C    0m  CC=0.0    ←0
  │ registry.fragment.yaml       2L  0C    0m  CC=0.0    ←0
  │
  uri3/                           CC̄=2.7    ←in:0  →out:0
  │ uri_graph                    0L  3C    3m  CC=10     ←2
  │ uri_validator                0L  0C    1m  CC=2      ←2
  │ normalizer                   0L  0C    1m  CC=3      ←0
  │ parser                       0L  1C    1m  CC=2      ←4
  │ http_resolver                0L  1C    2m  CC=2      ←1
  │ llm_resolver                 0L  2C    2m  CC=5      ←2
  │ python_resolver              0L  1C    5m  CC=2      ←2
  │ base                         0L  1C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  testenv/                        CC̄=2.3    ←in:0  →out:0
  │ mock_agent_server           57L  1C    3m  CC=5      ←0
  │ Dockerfile                  20L  0C    0m  CC=0.0    ←0
  │ docker-compose.ssh.yml      10L  0C    0m  CC=0.0    ←0
  │ entrypoint.sh                7L  0C    0m  CC=0.0    ←0
  │
  runtime_client/                 CC̄=1.7    ←in:0  →out:0
  │ client                       0L  1C    3m  CC=2      ←0
  │
  nl2uri/                         CC̄=1.0    ←in:3  →out:0
  │ writer                       0L  0C    1m  CC=1      ←2
  │
  nl2a/                           CC̄=1.0    ←in:0  →out:1
  │ cli                          0L  0C    2m  CC=1      ←0
  │
  examples/                       CC̄=0.0    ←in:0  →out:0
  │ run.sh                      85L  1C    2m  CC=0.0    ←0
  │ run.sh                      41L  0C    0m  CC=0.0    ←0
  │ run.sh                      38L  0C    0m  CC=0.0    ←0
  │ expanded.expected.uri.graph.yaml    38L  0C    0m  CC=0.0    ←0
  │ task.android.yaml           35L  0C    0m  CC=0.0    ←0
  │ task_graph.yaml             28L  0C    0m  CC=0.0    ←0
  │ task.health.yaml            28L  0C    0m  CC=0.0    ←0
  │ task.health.yaml            28L  0C    0m  CC=0.0    ←0
  │ task.pcwin.yaml             26L  0C    0m  CC=0.0    ←0
  │ branching.uri.flow.yaml     20L  0C    0m  CC=0.0    ←0
  │ run.sh                      20L  0C    0m  CC=0.0    ←0
  │ run.sh                      17L  0C    0m  CC=0.0    ←0
  │ run.sh                      17L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │ weather.uri.flow.yaml        9L  0C    0m  CC=0.0    ←0
  │ weather.uri.flow.yaml        9L  0C    0m  CC=0.0    ←0
  │ run.sh                       8L  0C    0m  CC=0.0    ←0
  │ run.sh                       8L  0C    0m  CC=0.0    ←0
  │ run.sh                       7L  0C    0m  CC=0.0    ←0
  │ run.sh                       7L  0C    0m  CC=0.0    ←0
  │ run.sh                       5L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ create_orders_agent.yaml     0L  0C    0m  CC=0.0    ←0
  │ broken_agent.yaml            0L  0C    0m  CC=0.0    ←0
  │ create_invoices_agent_prompt.txt     0L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! planfile.yaml             1319L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  511L  0C    0m  CC=0.0    ←0
  │ tree.txt                   240L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             151L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                97L  0C    0m  CC=0.0    ←0
  │ Makefile                    86L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ manifest.yaml               20L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          18L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  13L  0C    0m  CC=0.0    ←0
  │ nlp2uri.yaml                 8L  0C    0m  CC=0.0    ←0
  │
  schemas/                        CC̄=0.0    ←in:0  →out:0
  │ contract_registry.schema.json   129L  0C    0m  CC=0.0    ←0
  │ agent_contract.schema.json    79L  0C    0m  CC=0.0    ←0
  │ uri_tree.schema.json        78L  0C    0m  CC=0.0    ←0
  │ workflow_graph.schema.json    69L  0C    0m  CC=0.0    ←0
  │ resources.schema.json       56L  0C    0m  CC=0.0    ←0
  │ views.schema.json           54L  0C    0m  CC=0.0    ←0
  │ evolution_proposal.schema.json    48L  0C    0m  CC=0.0    ←0
  │ command_contract.schema.json    43L  0C    0m  CC=0.0    ←0
  │ renderer_contract.schema.json    35L  0C    0m  CC=0.0    ←0
  │ uri_graph.schema.json       31L  0C    0m  CC=0.0    ←0
  │ domain_pack.schema.json     20L  0C    0m  CC=0.0    ←0
  │
  contracts/                      CC̄=0.0    ←in:0  →out:0
  │ user.proto                  39L  0C    0m  CC=0.0    ←0
  │ user_agent.yaml             38L  0C    0m  CC=0.0    ←0
  │ views.yaml                  34L  0C    0m  CC=0.0    ←0
  │ resources.yaml              29L  0C    0m  CC=0.0    ←0
  │ standards.yaml              28L  0C    0m  CC=0.0    ←0
  │ registry.yaml               28L  0C    0m  CC=0.0    ←0
  │ policy.yaml                 24L  0C    0m  CC=0.0    ←0
  │ weather_map_agent.yaml      22L  0C    0m  CC=0.0    ←0
  │
  evolution/                      CC̄=0.0    ←in:0  →out:0
  │ add_invoices_agent.yaml      0L  0C    0m  CC=0.0    ←0
  │ add_orders_agent.yaml        0L  0C    0m  CC=0.0    ←0
  │
  deployments/                    CC̄=0.0    ←in:0  →out:0
  │ agent_deployments.yaml      29L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-api-smoke.testql.toon.yaml    35L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    14L  0C    0m  CC=0.0    ←0
  │
  config/                         CC̄=0.0    ←in:0  →out:0
  │ flow_defaults.uri.yaml     132L  0C    0m  CC=0.0    ←0
  │ llm.uri.yaml                57L  0C    0m  CC=0.0    ←0
  │ operator_policy.uri.yaml    43L  0C    0m  CC=0.0    ←0
  │ docker.uri.yaml             25L  0C    0m  CC=0.0    ←0
  │ deployments.uri.yaml        18L  0C    0m  CC=0.0    ←0
  │ uri3.uri.yaml               17L  0C    0m  CC=0.0    ←0
  │ ssh.uri.yaml                15L  0C    0m  CC=0.0    ←0
  │ runtime.uri.yaml            12L  0C    0m  CC=0.0    ←0
  │ extra_operator_registry.yaml    11L  0C    0m  CC=0.0    ←0
  │ operator_registry.uri.yaml     9L  0C    0m  CC=0.0    ←0
  │
  agents/                         CC̄=0.0    ←in:0  →out:0
  │ agent_card                  63L  0C    0m  CC=0.0    ←0
  │ agent_card                  40L  0C    0m  CC=0.0    ←0
  │ main                        16L  0C    0m  CC=0.0    ←0
  │ main                        16L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              4L  0C    0m  CC=0.0    ←0
  │
  integration/                    CC̄=0.0    ←in:0  →out:0
  │ Makefile.optional.snippet.mk    11L  0C    0m  CC=0.0    ←0
  │ pyproject.optional.snippet.toml    10L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     evolution/proposals/add_invoices_agent.yaml  0L
     evolution/proposals/add_orders_agent.yaml  0L
     examples/broken_agent.yaml                0L
     examples/create_invoices_agent_prompt.txt  0L
     examples/create_orders_agent.yaml         0L
     generator/__init__.py                     0L
     generator/hashutil.py                     0L
     generator/model.py                        0L
     generator/templates/Dockerfile.j2         0L
     generator/validate.py                     0L
     generator/verify.py                       0L
     hypervisor/__init__.py                    0L
     hypervisor/_version.py                    0L
     hypervisor/compatibility/checker.py       0L
     hypervisor/config/__init__.py             0L
     hypervisor/config/env.py                  0L
     hypervisor/config/models.py               0L
     hypervisor/contract_registry/loader.py    0L
     hypervisor/contract_registry/models.py    0L
     hypervisor/contract_registry/registry_builder.py  0L
     hypervisor/contract_registry/registry_exporter.py  0L
     hypervisor/contract_registry/schema_validator.py  0L
     hypervisor/deployment_registry/writer.py  0L
     hypervisor/domain_pack/__init__.py        0L
     hypervisor/domain_pack/templates.py       0L
     hypervisor/evolution/models.py            0L
     hypervisor/evolution/validator.py         0L
     hypervisor/policy_gate/gate.py            0L
     hypervisor/uri2llm/__init__.py            0L
     hypervisor/uri2llm/env_resolver.py        0L
     hypervisor/uri2llm/function_resolver.py   0L
     hypervisor/uri2llm/llm_resolver.py        0L
     hypervisor/uri2llm/protocol_resolver.py   0L
     hypervisor/uri2llm/pypi_resolver.py       0L
     hypervisor/uri2llm/router.py              0L
     hypervisor/verifier/capability_tests.py   0L
     hypervisor/verifier/cli.py                0L
     meta_agent/__init__.py                    0L
     meta_agent/api.py                         0L
     meta_agent/domain_planner/__init__.py     0L
     meta_agent/domain_planner/domain_pack_generator.py  0L
     meta_agent/domain_planner/llm_planner.py  0L
     meta_agent/models.py                      0L
     meta_agent/planner.py                     0L
     meta_agent/repair/__init__.py             0L
     meta_agent/repair/loader.py               0L
     meta_agent/repair/pipeline.py             0L
     meta_agent/repair/rules.py                0L
     nl2a/cli.py                               0L
     nl2uri/writer.py                          0L
     packages/uri2ops/uri2ops/operation_registry/__init__.py  0L
     packages/uri2ops/uri2ops/remote_registry/__init__.py  0L
     packages/uri2ops/uri2ops/schemas/__init__.py  0L
     packages/uri2ops/uri2ops/server/__init__.py  0L
     runtime_client/client.py                  0L
     uri3/graph/uri_graph.py                   0L
     uri3/protocols/normalizer.py              0L
     uri3/protocols/parser.py                  0L
     uri3/resolvers/__init__.py                0L
     uri3/resolvers/http_resolver.py           0L
     uri3/resolvers/llm_resolver.py            0L
     uri3/resolvers/python_resolver.py         0L
     uri3/scanner/base.py                      0L
     uri3/validators/uri_validator.py          0L

COUPLING:
                                                           packages.uri3  packages.resource-agent-hypervisor                     packages.nl2uri                    packages.uri2ops                           generator                          meta_agent        hypervisor.contract_registry                   packages.uri2flow                   meta_agent.repair     packages.resource-agent-factory                      uri3.resolvers      hypervisor.deployment_registry                              nl2uri                      uri3.protocols                     uri3.validators
                       packages.uri3                                  ──                                  12                                 ←27                                  18                                                                                                                                               4                                                                      ←1                                   5                                                                                                           1                                   2  hub
  packages.resource-agent-hypervisor                                  43                                  ──                                   1                                   3                                   4                                   3                                   7                                   1                                   2                                   1                                                                       2                                                                                                              hub
                     packages.nl2uri                                  27                                   2                                  ──                                   9                                   1                                                                       1                                   5                                                                       1                                                                                                           3                                                                          !! fan-out
                    packages.uri2ops                                 ←18                                   2                                   1                                  ──                                                                                                                                                                                                                                                                                                                                                                                                              hub
                           generator                                                                      ←4                                  ←1                                                                      ──                                  ←2                                                                                                          ←3                                  ←4                                                                                                                                                                                      hub
                          meta_agent                                                                       5                                                                                                           2                                  ──                                                                                                           1                                                                                                                                                                                                                          !! fan-out
        hypervisor.contract_registry                                                                      ←7                                  ←1                                                                                                                                              ──                                                                                                                                                                                                                                                                                                  hub
                   packages.uri2flow                                   1                                  ←1                                  ←5                                                                                                                                                                                  ──                                                                                                                                                                                                                                                              hub
                   meta_agent.repair                                                                      ←2                                                                                                           3                                   1                                                                                                          ──                                                                                                                                                                                                                        
     packages.resource-agent-factory                                   1                                  ←1                                  ←1                                                                       4                                                                                                                                                                                  ──                                                                                                                                                                                    
                      uri3.resolvers                                   1                                                                                                                                                                                                                                                                                                                                                                      ──                                                                                                           1                                      hub
      hypervisor.deployment_registry                                                                       1                                                                                                                                                                                                                                                                                                                                                                      ──                                                                                                            
                              nl2uri                                                                                                          ←3                                                                                                                                                                                                                                                                                                                                                                      ──                                                                        
                      uri3.protocols                                  ←1                                                                                                                                                                                                                                                                                                                                                                      ←1                                                                                                          ──                                  ←1
                     uri3.validators                                  ←2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   1                                  ──
  CYCLES: none
  HUB: hypervisor.contract_registry/ (fan-in=11)
  HUB: packages.uri3/ (fan-in=73)
  HUB: packages.uri2ops/ (fan-in=31)
  HUB: packages.resource-agent-hypervisor/ (fan-in=23)
  HUB: packages.uri2flow/ (fan-in=10)
  HUB: uri3.resolvers/ (fan-in=5)
  HUB: generator/ (fan-in=14)
  SMELL: packages.uri3/ fan-out=44 → split needed
  SMELL: packages.resource-agent-hypervisor/ fan-out=71 → split needed
  SMELL: meta_agent/ fan-out=8 → split needed
  SMELL: packages.nl2uri/ fan-out=49 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 19 groups | 289f 13738L | 2026-06-14

SUMMARY:
  files_scanned: 289
  total_lines:   13738
  dup_groups:    19
  dup_fragments: 53
  saved_lines:   273
  scan_ms:       2989

HOTSPOTS[7] (files with most duplication):
  packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py  dup=76L  groups=1  frags=3  (0.6%)
  packages/nl2uri/nl2uri/cli.py  dup=50L  groups=2  frags=4  (0.4%)
  packages/uri3/uri3/protocols/schemes/instance_parser.py  dup=40L  groups=1  frags=10  (0.3%)
  domains/weather_map/handlers/generate_weather_map.py  dup=18L  groups=1  frags=1  (0.1%)
  packages/uri3/domains/weather_map/handlers/generate_weather_map.py  dup=18L  groups=1  frags=1  (0.1%)
  packages/resource-agent-factory/generator/header.py  dup=18L  groups=1  frags=3  (0.1%)
  packages/uri2ops/uri2ops/operator/adapters/browser_router.py  dup=17L  groups=1  frags=1  (0.1%)

DUPLICATES[19] (ranked by impact):
  [49d1d03e6ce392a1] ! STRU  weather_proto  L=43 N=3 saved=86 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py:36-78  (weather_proto)
      packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py:81-106  (weather_handler)
      packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py:109-115  (generic_handler)
  [5ec23e21699e8ab6] ! STRU  _parse_env  L=4 N=10 saved=36 sim=1.00
      packages/uri3/uri3/protocols/schemes/instance_parser.py:27-30  (_parse_env)
      packages/uri3/uri3/protocols/schemes/instance_parser.py:33-36  (_parse_python)
      packages/uri3/uri3/protocols/schemes/instance_parser.py:39-42  (_parse_llm)
      packages/uri3/uri3/protocols/schemes/instance_parser.py:45-48  (_parse_pypi)
      packages/uri3/uri3/protocols/schemes/instance_parser.py:51-54  (_parse_http)
      packages/uri3/uri3/protocols/schemes/instance_parser.py:57-60  (_parse_a2a)
      packages/uri3/uri3/protocols/schemes/instance_parser.py:63-66  (_parse_mcp)
      packages/uri3/uri3/protocols/schemes/instance_parser.py:69-72  (_parse_docker)
      packages/uri3/uri3/protocols/schemes/instance_parser.py:75-78  (_parse_ssh)
      packages/uri3/uri3/protocols/schemes/instance_parser.py:81-84  (_parse_resource)
  [3923fa783ad8b9c2]   STRU  task  L=19 N=2 saved=19 sim=1.00
      packages/nl2uri/nl2uri/cli.py:176-194  (task)
      packages/nl2uri/nl2uri/cli.py:198-216  (graph)
  [1b86825b8b7cb469]   EXAC  handler  L=18 N=2 saved=18 sim=1.00
      domains/weather_map/handlers/generate_weather_map.py:7-24  (handler)
      packages/uri3/domains/weather_map/handlers/generate_weather_map.py:7-24  (handler)
  [16b912bffbd4a264]   EXAC  _playwright_ready  L=17 N=2 saved=17 sim=1.00
      packages/uri2ops/uri2ops/operator/adapters/browser_router.py:12-28  (_playwright_ready)
      packages/uri3/uri3/graph/adapters/browser_router.py:15-31  (_playwright_ready)
  [70c693fa623a6ad1]   EXAC  _task_context  L=3 N=5 saved=12 sim=1.00
      packages/uri2ops/uri2ops/operator/adapters/android_adb.py:16-18  (_task_context)
      packages/uri2ops/uri2ops/operator/adapters/android_mock.py:10-12  (_task_context)
      packages/uri2ops/uri2ops/operator/adapters/browser_playwright.py:20-22  (_task_context)
      packages/uri2ops/uri2ops/operator/adapters/pcwin_mock.py:10-12  (_task_context)
      packages/uri2ops/uri2ops/operator/adapters/pcwin_uia.py:11-13  (_task_context)
  [f69df3cd4d46eb5f]   STRU  _slug  L=4 N=4 saved=12 sim=1.00
      packages/nl2uri/nl2uri/flow_repair.py:11-14  (_slug)
      packages/nl2uri/nl2uri/graph_planner.py:15-18  (_slug)
      packages/nl2uri/nl2uri/graph_repair.py:30-33  (_slug)
      packages/nl2uri/nl2uri/planner_templates.py:10-13  (slug)
  [277a3a34943f29ee]   STRU  python_file_header  L=6 N=3 saved=12 sim=1.00
      packages/resource-agent-factory/generator/header.py:21-26  (python_file_header)
      packages/resource-agent-factory/generator/header.py:29-34  (dockerfile_header)
      packages/resource-agent-factory/generator/header.py:37-42  (markdown_generated_banner)
  [71dc3d2f70a63bf5]   STRU  spec  L=12 N=2 saved=12 sim=1.00
      packages/uri3/uri3/protocols/schemes/a2a.py:4-15  (spec)
      packages/uri3/uri3/protocols/schemes/mcp.py:4-15  (spec)
  [0e9dc2bdedc9fb73]   STRU  window_id_from_payload  L=7 N=2 saved=7 sim=1.00
      packages/uri2ops/uri2ops/operator/adapters/pcwin_uri.py:32-38  (window_id_from_payload)
      packages/uri2ops/uri2ops/operator/adapters/pcwin_uri.py:41-47  (automation_id_from_payload)
  [c3b5ea290d7363ba]   STRU  single  L=6 N=2 saved=6 sim=1.00
      packages/nl2uri/nl2uri/cli.py:108-113  (single)
      packages/nl2uri/nl2uri/cli.py:117-122  (list_cmd)
  [fdc7786ef049b370]   STRU  deploy_agent_cmd  L=6 N=2 saved=6 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/cli.py:111-116  (deploy_agent_cmd)
      packages/resource-agent-hypervisor/hypervisor/cli.py:129-134  (docker_cmd)
  [25db8c6fcea03672]   STRU  adjacency  L=6 N=2 saved=6 sim=1.00
      packages/uri3/uri3/graph/dependency_graph.py:9-14  (adjacency)
      packages/uri3/uri3/graph/dependency_graph.py:17-22  (reverse_adjacency)
  [9a928c6cb43e19ba]   STRU  _first  L=5 N=2 saved=5 sim=1.00
      packages/uri3/uri3/resolvers/docker_resolver.py:61-65  (_first)
      packages/uri3/uri3/resolvers/log_query.py:7-11  (first)
  [06621f22a60e830d]   STRU  _bool  L=5 N=2 saved=5 sim=1.00
      packages/uri3/uri3/resolvers/docker_resolver.py:68-72  (_bool)
      packages/uri3/uri3/resolvers/log_query.py:24-28  (query_bool)
  [9fb5c83bb992966d]   STRU  validate_flow_document  L=4 N=2 saved=4 sim=1.00
      packages/nl2uri/nl2uri/flow_repair.py:207-210  (validate_flow_document)
      packages/nl2uri/nl2uri/flow_repair.py:213-216  (validate_expanded_flow)
  [060fe645d32f78c5]   STRU  run_build_command  L=4 N=2 saved=4 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py:33-36  (run_build_command)
      packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py:39-42  (run_export_md_command)
  [e9d49a2572194471]   STRU  policy_config_path  L=3 N=2 saved=3 sim=1.00
      packages/uri2ops/uri2ops/operator/policy_loader.py:60-62  (policy_config_path)
      packages/uri2ops/uri2ops/remote_registry/loader.py:17-19  (registry_config_path)
  [bc6d855bfb035b8b]   STRU  resolve_a2a  L=3 N=2 saved=3 sim=1.00
      packages/uri3/uri3/resolvers/protocol_resolver.py:10-12  (resolve_a2a)
      packages/uri3/uri3/resolvers/protocol_resolver.py:15-17  (resolve_mcp)

REFACTOR[19] (ranked by priority):
  [1] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/domain_pack/utils/weather_proto.py
      WHY: 3 occurrences of 43-line block across 1 files — saves 86 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py
  [2] ○ extract_function   → packages/uri3/uri3/protocols/schemes/utils/_parse_env.py
      WHY: 10 occurrences of 4-line block across 1 files — saves 36 lines
      FILES: packages/uri3/uri3/protocols/schemes/instance_parser.py
  [3] ○ extract_function   → packages/nl2uri/nl2uri/utils/task.py
      WHY: 2 occurrences of 19-line block across 1 files — saves 19 lines
      FILES: packages/nl2uri/nl2uri/cli.py
  [4] ○ extract_function   → utils/handler.py
      WHY: 2 occurrences of 18-line block across 2 files — saves 18 lines
      FILES: domains/weather_map/handlers/generate_weather_map.py, packages/uri3/domains/weather_map/handlers/generate_weather_map.py
  [5] ○ extract_function   → packages/utils/_playwright_ready.py
      WHY: 2 occurrences of 17-line block across 2 files — saves 17 lines
      FILES: packages/uri2ops/uri2ops/operator/adapters/browser_router.py, packages/uri3/uri3/graph/adapters/browser_router.py
  [6] ○ extract_function   → packages/uri2ops/uri2ops/operator/adapters/utils/_task_context.py
      WHY: 5 occurrences of 3-line block across 5 files — saves 12 lines
      FILES: packages/uri2ops/uri2ops/operator/adapters/android_adb.py, packages/uri2ops/uri2ops/operator/adapters/android_mock.py, packages/uri2ops/uri2ops/operator/adapters/browser_playwright.py, packages/uri2ops/uri2ops/operator/adapters/pcwin_mock.py, packages/uri2ops/uri2ops/operator/adapters/pcwin_uia.py
  [7] ○ extract_function   → packages/nl2uri/nl2uri/utils/_slug.py
      WHY: 4 occurrences of 4-line block across 4 files — saves 12 lines
      FILES: packages/nl2uri/nl2uri/flow_repair.py, packages/nl2uri/nl2uri/graph_planner.py, packages/nl2uri/nl2uri/graph_repair.py, packages/nl2uri/nl2uri/planner_templates.py
  [8] ○ extract_function   → packages/resource-agent-factory/generator/utils/python_file_header.py
      WHY: 3 occurrences of 6-line block across 1 files — saves 12 lines
      FILES: packages/resource-agent-factory/generator/header.py
  [9] ○ extract_function   → packages/uri3/uri3/protocols/schemes/utils/spec.py
      WHY: 2 occurrences of 12-line block across 2 files — saves 12 lines
      FILES: packages/uri3/uri3/protocols/schemes/a2a.py, packages/uri3/uri3/protocols/schemes/mcp.py
  [10] ○ extract_function   → packages/uri2ops/uri2ops/operator/adapters/utils/window_id_from_payload.py
      WHY: 2 occurrences of 7-line block across 1 files — saves 7 lines
      FILES: packages/uri2ops/uri2ops/operator/adapters/pcwin_uri.py
  [11] ○ extract_function   → packages/nl2uri/nl2uri/utils/single.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: packages/nl2uri/nl2uri/cli.py
  [12] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/utils/deploy_agent_cmd.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/cli.py
  [13] ○ extract_function   → packages/uri3/uri3/graph/utils/adjacency.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: packages/uri3/uri3/graph/dependency_graph.py
  [14] ○ extract_function   → packages/uri3/uri3/resolvers/utils/_first.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: packages/uri3/uri3/resolvers/docker_resolver.py, packages/uri3/uri3/resolvers/log_query.py
  [15] ○ extract_function   → packages/uri3/uri3/resolvers/utils/_bool.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: packages/uri3/uri3/resolvers/docker_resolver.py, packages/uri3/uri3/resolvers/log_query.py
  [16] ○ extract_function   → packages/nl2uri/nl2uri/utils/validate_flow_document.py
      WHY: 2 occurrences of 4-line block across 1 files — saves 4 lines
      FILES: packages/nl2uri/nl2uri/flow_repair.py
  [17] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/contract_registry/utils/run_build_command.py
      WHY: 2 occurrences of 4-line block across 1 files — saves 4 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py
  [18] ○ extract_function   → packages/uri2ops/uri2ops/utils/policy_config_path.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: packages/uri2ops/uri2ops/operator/policy_loader.py, packages/uri2ops/uri2ops/remote_registry/loader.py
  [19] ○ extract_function   → packages/uri3/uri3/resolvers/utils/resolve_a2a.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: packages/uri3/uri3/resolvers/protocol_resolver.py

QUICK_WINS[13] (low risk, high savings — do first):
  [1] extract_function   saved=86L  → packages/resource-agent-hypervisor/hypervisor/domain_pack/utils/weather_proto.py
      FILES: templates.py
  [2] extract_function   saved=36L  → packages/uri3/uri3/protocols/schemes/utils/_parse_env.py
      FILES: instance_parser.py
  [3] extract_function   saved=19L  → packages/nl2uri/nl2uri/utils/task.py
      FILES: cli.py
  [4] extract_function   saved=18L  → utils/handler.py
      FILES: generate_weather_map.py, generate_weather_map.py
  [5] extract_function   saved=17L  → packages/utils/_playwright_ready.py
      FILES: browser_router.py, browser_router.py
  [6] extract_function   saved=12L  → packages/uri2ops/uri2ops/operator/adapters/utils/_task_context.py
      FILES: android_adb.py, android_mock.py, browser_playwright.py +2
  [7] extract_function   saved=12L  → packages/nl2uri/nl2uri/utils/_slug.py
      FILES: flow_repair.py, graph_planner.py, graph_repair.py +1
  [8] extract_function   saved=12L  → packages/resource-agent-factory/generator/utils/python_file_header.py
      FILES: header.py
  [9] extract_function   saved=12L  → packages/uri3/uri3/protocols/schemes/utils/spec.py
      FILES: a2a.py, mcp.py
  [10] extract_function   saved=7L  → packages/uri2ops/uri2ops/operator/adapters/utils/window_id_from_payload.py
      FILES: pcwin_uri.py

DEPENDENCY_RISK[1] (duplicates spanning multiple packages):
  handler  packages=2  files=2
      domains/weather_map/handlers/generate_weather_map.py
      packages/uri3/domains/weather_map/handlers/generate_weather_map.py

EFFORT_ESTIMATE (total ≈ 11.1h):
  hard   weather_proto                       saved=86L  ~258min
  medium _parse_env                          saved=36L  ~72min
  medium task                                saved=19L  ~38min
  medium handler                             saved=18L  ~72min
  medium _playwright_ready                   saved=17L  ~34min
  easy   _task_context                       saved=12L  ~24min
  easy   _slug                               saved=12L  ~24min
  easy   python_file_header                  saved=12L  ~24min
  easy   spec                                saved=12L  ~24min
  easy   window_id_from_payload              saved=7L  ~14min
  ... +9 more (~84min)

METRICS-TARGET:
  dup_groups:  19 → 0
  saved_lines: 273 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 659 func | 195f | 2026-06-14
# generated in 0.00s

NEXT[9] (ranked by impact):
  [1] !  SPLIT-FUNC      run_workflow  CC=21  fan=24
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 504

  [2] !  SPLIT-FUNC      classify_output_kind  CC=23  fan=11
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 253

  [3] !  SPLIT-FUNC      _ensure_step_ids  CC=19  fan=13
      WHY: CC=19 exceeds 15
      EFFORT: ~1h  IMPACT: 247

  [4] !  SPLIT-FUNC      extract_flow_payload  CC=20  fan=10
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 200

  [5] !  SPLIT-FUNC      sanitize_flow_step  CC=18  fan=9
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 162

  [6] !  SPLIT-FUNC      sanitize_node  CC=16  fan=10
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 160

  [7] !  SPLIT-FUNC      resolve_uri_values  CC=15  fan=10
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 150

  [8] !! SPLIT           planfile.yaml
      WHY: 1319L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0

  [9] !! SPLIT           goal.yaml
      WHY: 511L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[2]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          3.6 → ≤2.5
  max-CC:      23 → ≤11
  god-modules: 2 → 0
  high-CC(≥15): 8 → ≤4
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=3.6 → now CC̄=3.6
```

## Intent

WronAI resource agent monorepo — uri3, nl2uri, uri2flow, uri2ops, touri, hypervisor, agent factory

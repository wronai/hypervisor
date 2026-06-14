# Resource Agent Meta-Factory v0.1

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
- **version**: `0.5.5`
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

## Workflows

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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 151f 8078L | python:95,yaml:29,json:10,yml:3,shell:3,txt:2,proto:2,toml:1,j2:1 | 2026-06-14
# generated in 0.02s
# CC̅=3.3 | critical:5/220 | dups:0 | cycles:3

HEALTH[5]:
  🟡 CC    main CC=16 (limit:15)
  🟡 CC    main CC=20 (limit:15)
  🟡 CC    validate_registry CC=20 (limit:15)
  🟡 CC    validate_cross_references CC=22 (limit:15)
  🟡 CC    validate_config CC=17 (limit:15)

REFACTOR[2]:
  1. split 5 high-CC methods  (CC>15)
  2. break 3 circular dependencies

PIPELINES[88]:
  [1] Src [main]: main → iter_agent_specs
      PURITY: 100% pure
  [2] Src [main]: main → save_proposal_from_prompt → infer_intent → singularize
      PURITY: 100% pure
  [3] Src [health]: health
      PURITY: 100% pure
  [4] Src [proposal_from_prompt]: proposal_from_prompt → save_proposal_from_prompt → infer_intent → singularize
      PURITY: 100% pure
  [5] Src [validate]: validate → validate_agent → load_agent_spec
      PURITY: 100% pure
  [6] Src [repair]: repair → repair_agent_spec → validate_agent → load_agent_spec
      PURITY: 100% pure
  [7] Src [generate]: generate → asdict_result
      PURITY: 100% pure
  [8] Src [pipeline]: pipeline → pipeline_from_prompt → save_proposal_from_prompt → infer_intent → ...(1 more)
      PURITY: 100% pure
  [9] Src [verify]: verify → verify_generated → verify_generated_agent → file_sha256
      PURITY: 100% pure
  [10] Src [dump_yaml]: dump_yaml
      PURITY: 100% pure
  [11] Src [validate]: validate → validate_uri → parse_uri
      PURITY: 100% pure
  [12] Src [validate_tree]: validate_tree → validate_uri_tree → load_yaml
      PURITY: 100% pure
  [13] Src [graph]: graph → build_graph_from_tree
      PURITY: 100% pure
  [14] Src [resolve]: resolve
      PURITY: 100% pure
  [15] Src [scan]: scan
      PURITY: 100% pure
  [16] Src [main]: main
      PURITY: 100% pure
  [17] Src [add_node]: add_node
      PURITY: 100% pure
  [18] Src [add_edge]: add_edge
      PURITY: 100% pure
  [19] Src [scan]: scan → scan_http
      PURITY: 100% pure
  [20] Src [normalize_uri]: normalize_uri → parse_uri
      PURITY: 100% pure
  [21] Src [resolve]: resolve → resolve_http_like
      PURITY: 100% pure
  [22] Src [fetch]: fetch
      PURITY: 100% pure
  [23] Src [resolve]: resolve → resolve_llm
      PURITY: 100% pure
  [24] Src [resolve]: resolve → resolve_env
      PURITY: 100% pure
  [25] Src [call]: call → call_python → _split_python_uri
      PURITY: 100% pure
  [26] Src [__init__]: __init__
      PURITY: 100% pure
  [27] Src [resolve]: resolve → resolve_env
      PURITY: 100% pure
  [28] Src [resolve]: resolve → resolve_python → _split_python_uri
      PURITY: 100% pure
  [29] Src [call]: call → call_python → _split_python_uri
      PURITY: 100% pure
  [30] Src [scan]: scan
      PURITY: 100% pure
  [31] Src [resolve]: resolve
      PURITY: 100% pure
  [32] Src [status]: status
      PURITY: 100% pure
  [33] Src [config_cmd]: config_cmd → load_config → get_default_config → apply_builtin_defaults
      PURITY: 100% pure
  [34] Src [main]: main
      PURITY: 100% pure
  [35] Src [__post_init__]: __post_init__
      PURITY: 100% pure
  [36] Src [from_config]: from_config → load_config → get_default_config → apply_builtin_defaults
      PURITY: 100% pure
  [37] Src [start]: start
      PURITY: 100% pure
  [38] Src [stop]: stop
      PURITY: 100% pure
  [39] Src [register_agent]: register_agent
      PURITY: 100% pure
  [40] Src [status]: status
      PURITY: 100% pure
  [41] Src [__repr__]: __repr__
      PURITY: 100% pure
  [42] Src [generic_proto]: generic_proto → package_name
      PURITY: 100% pure
  [43] Src [main]: main → load_contract_registry → _read_yaml
      PURITY: 100% pure
  [44] Src [evaluate_change]: evaluate_change
      PURITY: 100% pure
  [45] Src [main]: main → load_proposal
      PURITY: 100% pure
  [46] Src [__init__]: __init__
      PURITY: 100% pure
  [47] Src [resolve]: resolve
      PURITY: 100% pure
  [48] Src [call]: call
      PURITY: 100% pure
  [49] Src [graph]: graph → build_graph_from_tree
      PURITY: 100% pure
  [50] Src [nl2uri]: nl2uri → rule_based_plan → _slug
      PURITY: 100% pure

LAYERS:
  generator/                      CC̄=4.1    ←in:12  →out:0
  │ agent_generator            104L  0C    4m  CC=5      ←2
  │ model                       94L  2C    2m  CC=7      ←2
  │ verify                      73L  0C    3m  CC=9      ←4
  │ validate                    69L  0C    3m  CC=11     ←5
  │ header                      53L  0C    6m  CC=3      ←1
  │ hashutil                     9L  0C    1m  CC=1      ←2
  │ Dockerfile.j2                7L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  meta_agent/                     CC̄=3.8    ←in:1  →out:10  !! split
  │ planner                    159L  0C    5m  CC=9      ←2
  │ !! cli                         93L  0C    1m  CC=16     ←0
  │ api                         83L  2C    7m  CC=2      ←0
  │ rules                       82L  0C    6m  CC=8      ←1
  │ orchestrator                71L  0C    4m  CC=7      ←2
  │ models                      43L  3C    1m  CC=1      ←0
  │ pipeline                    39L  0C    1m  CC=2      ←3
  │ loader                      17L  0C    2m  CC=2      ←1
  │ domain_pack_generator       16L  0C    0m  CC=0.0    ←0
  │ llm_planner                 15L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  hypervisor/                     CC̄=3.4    ←in:0  →out:3
  │ generator                  272L  1C   13m  CC=3      ←1
  │ models                     158L  8C    9m  CC=4      ←0
  │ status                     136L  0C    9m  CC=11     ←1
  │ templates                  115L  0C    5m  CC=1      ←0
  │ loader                      90L  0C    5m  CC=6      ←2
  │ core                        86L  1C    7m  CC=3      ←0
  │ loader                      80L  0C    2m  CC=9      ←5
  │ !! cli                         77L  0C    1m  CC=20     ←0
  │ merger                      68L  0C    1m  CC=12     ←1
  │ defaults                    63L  0C    4m  CC=4      ←1
  │ registry_builder            60L  0C    4m  CC=5      ←3
  │ !! validators                  57L  0C    2m  CC=17     ←1
  │ !! cross_validator             56L  0C    4m  CC=22     ←1
  │ models                      56L  4C    3m  CC=4      ←0
  │ cli                         55L  0C    5m  CC=4      ←0
  │ schema_validator            54L  1C    4m  CC=6      ←1
  │ env                         54L  0C    4m  CC=9      ←1
  │ !! validate                    50L  0C    1m  CC=20     ←2
  │ nlp2uri.yaml                49L  0C    0m  CC=0.0    ←0
  │ models                      47L  2C    3m  CC=4      ←0
  │ writer                      45L  0C    4m  CC=3      ←1
  │ checker                     43L  0C    2m  CC=8      ←0
  │ loader                      43L  0C    4m  CC=5      ←2
  │ cli                         33L  0C    1m  CC=10     ←0
  │ __init__                    33L  0C    0m  CC=0.0    ←0
  │ capability_tests            32L  0C    1m  CC=4      ←1
  │ models                      32L  1C    1m  CC=5      ←1
  │ __init__                    31L  0C    0m  CC=0.0    ←0
  │ registry_exporter           29L  0C    2m  CC=6      ←1
  │ cli                         28L  0C    1m  CC=5      ←0
  │ client                      28L  1C    6m  CC=1      ←0
  │ gate                        26L  1C    1m  CC=5      ←0
  │ __init__                    24L  0C    0m  CC=0.0    ←0
  │ _version                    20L  0C    0m  CC=0.0    ←0
  │ validator                   16L  0C    1m  CC=6      ←1
  │ __init__                    15L  0C    0m  CC=0.0    ←0
  │ writer                      13L  0C    2m  CC=1      ←2
  │ __init__                    13L  0C    0m  CC=0.0    ←0
  │ protocol_resolver           10L  0C    4m  CC=2      ←2
  │ pypi_resolver                5L  0C    1m  CC=5      ←1
  │ function_resolver            5L  0C    0m  CC=0.0    ←0
  │ llm_resolver                 5L  0C    0m  CC=0.0    ←0
  │ router                       5L  0C    0m  CC=0.0    ←0
  │ env_resolver                 5L  0C    0m  CC=0.0    ←0
  │
  nl2uri/                         CC̄=3.1    ←in:2  →out:6
  │ domain_planner             151L  0C    7m  CC=6      ←1
  │ pipeline                    95L  2C    3m  CC=3      ←1
  │ planner                     32L  1C    2m  CC=8      ←3
  │ llm_planner                 18L  0C    1m  CC=4      ←1
  │ cli                         16L  0C    2m  CC=4      ←0
  │ writer                       7L  0C    1m  CC=1      ←2
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
  uri3/                           CC̄=2.6    ←in:0  →out:3
  │ router                      87L  2C    5m  CC=10     ←0
  │ uri_graph                   51L  3C    3m  CC=10     ←2
  │ llm_resolver                45L  2C    2m  CC=5      ←1
  │ cli                         36L  0C    6m  CC=3      ←0
  │ python_resolver             36L  1C    5m  CC=2      ←1
  │ env_resolver                21L  1C    2m  CC=3      ←1
  │ http_resolver               20L  1C    2m  CC=2      ←0
  │ uri_tree_validator          18L  0C    2m  CC=2      ←2
  │ parser                      17L  1C    1m  CC=2      ←4
  │ http_scanner                16L  0C    1m  CC=6      ←1
  │ uri_validator                9L  0C    1m  CC=2      ←1
  │ normalizer                   9L  0C    1m  CC=3      ←0
  │ scanner                      7L  0C    1m  CC=2      ←0
  │ base                         7L  1C    0m  CC=0.0    ←0
  │ schemes                      4L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  testenv/                        CC̄=2.3    ←in:0  →out:0
  │ mock_agent_server           57L  1C    3m  CC=5      ←0
  │ Dockerfile                  20L  0C    0m  CC=0.0    ←0
  │ docker-compose.ssh.yml      10L  0C    0m  CC=0.0    ←0
  │ entrypoint.sh                7L  0C    0m  CC=0.0    ←0
  │
  runtime_client/                 CC̄=1.7    ←in:0  →out:0
  │ client                      47L  1C    3m  CC=2      ←0
  │
  nl2a/                           CC̄=1.0    ←in:0  →out:1
  │ cli                         25L  0C    2m  CC=1      ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! planfile.yaml             1319L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  511L  0C    0m  CC=0.0    ←0
  │ tree.txt                   240L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             136L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                94L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ Makefile                    32L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          18L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  13L  0C    0m  CC=0.0    ←0
  │ nlp2uri.yaml                 8L  0C    0m  CC=0.0    ←0
  │
  schemas/                        CC̄=0.0    ←in:0  →out:0
  │ contract_registry.schema.json   129L  0C    0m  CC=0.0    ←0
  │ agent_contract.schema.json    79L  0C    0m  CC=0.0    ←0
  │ uri_tree.schema.json        78L  0C    0m  CC=0.0    ←0
  │ resources.schema.json       56L  0C    0m  CC=0.0    ←0
  │ views.schema.json           54L  0C    0m  CC=0.0    ←0
  │ evolution_proposal.schema.json    48L  0C    0m  CC=0.0    ←0
  │ command_contract.schema.json    43L  0C    0m  CC=0.0    ←0
  │ renderer_contract.schema.json    35L  0C    0m  CC=0.0    ←0
  │ domain_pack.schema.json     20L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=0.0    ←in:0  →out:0
  │ create_orders_agent.yaml    27L  0C    0m  CC=0.0    ←0
  │ broken_agent.yaml           14L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │ run.sh                       7L  0C    0m  CC=0.0    ←0
  │ create_invoices_agent_prompt.txt     1L  0C    0m  CC=0.0    ←0
  │
  output/                         CC̄=0.0    ←in:0  →out:0
  │ contract_registry.resolved.json   174L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-api-smoke.testql.toon.yaml    35L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    14L  0C    0m  CC=0.0    ←0
  │
  evolution/                      CC̄=0.0    ←in:0  →out:0
  │ add_invoices_agent.yaml     18L  0C    0m  CC=0.0    ←0
  │ add_orders_agent.yaml       17L  0C    0m  CC=0.0    ←0
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
  agents/                         CC̄=0.0    ←in:0  →out:0
  │ agent_card                  63L  0C    0m  CC=0.0    ←0
  │ agent_card                  40L  0C    0m  CC=0.0    ←0
  │ main                        16L  0C    0m  CC=0.0    ←0
  │ main                        16L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              4L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │
  deployments/                    CC̄=0.0    ←in:0  →out:0
  │ agent_deployments.yaml      20L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     generator/__init__.py                     0L

COUPLING:
                                                   generator                    meta_agent  hypervisor.contract_registry                        nl2uri             meta_agent.repair                uri3.resolvers        hypervisor.domain_pack            hypervisor.uri2llm               uri3.validators                    hypervisor             hypervisor.config                          uri3                uri3.protocols      hypervisor.compatibility                hypervisor.uri
                     generator                            ──                            ←7                                                          ←2                            ←3                                                                                                                                                                                                                                                                                                              hub
                    meta_agent                             7                            ──                                                                                         3                                                                                                                                                                                                                                                                                                              !! fan-out
  hypervisor.contract_registry                                                                                        ──                            ←1                                                                                         4                                                                                                                                                                                                                ←2                                hub
                        nl2uri                             2                                                           1                            ──                                                                                         1                                                           1                                                                                                                                                                                  ←1
             meta_agent.repair                             3                             1                                                                                        ──                                                                                                                                                                                                                                                                                                            
                uri3.resolvers                                                                                                                                                                                  ──                                                           6                                                                                                                                                     1                                                            
        hypervisor.domain_pack                                                                                         1                            ←1                                                                                        ──                                                                                                                                                                                                                                                  hub
            hypervisor.uri2llm                                                                                                                                                                                  ←6                                                          ──                                                                                                                                                                                                                    hub
               uri3.validators                                                                                                                      ←1                                                                                                                                                    ──                                                                                        ←2                             1                                                            
                    hypervisor                                                                                                                                                                                                                                                                                                          ──                             3                                                                                                                        
             hypervisor.config                                                                                                                                                                                                                                                                                                          ←3                            ──                                                                                                                        
                          uri3                                                                                                                                                                                                                                                                             2                                                                                        ──                                                                                          
                uri3.protocols                                                                                                                                                                                  ←1                                                                                        ←1                                                                                                                      ──                                                            
      hypervisor.compatibility                                                                                         2                                                                                                                                                                                                                                                                                                                                        ──                              
                hypervisor.uri                                                                                                                       1                                                                                                                                                                                                                                                                                                                                        ──
  CYCLES: 3
  HUB: generator/ (fan-in=12)
  HUB: hypervisor.domain_pack/ (fan-in=5)
  HUB: hypervisor.uri2llm/ (fan-in=6)
  HUB: hypervisor.contract_registry/ (fan-in=6)
  SMELL: meta_agent/ fan-out=10 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 3 groups | 115f 4208L | 2026-06-14

SUMMARY:
  files_scanned: 115
  total_lines:   4208
  dup_groups:    3
  dup_fragments: 8
  saved_lines:   101
  scan_ms:       2291

HOTSPOTS[3] (files with most duplication):
  hypervisor/domain_pack/templates.py  dup=76L  groups=1  frags=3  (1.8%)
  generator/header.py  dup=18L  groups=1  frags=3  (0.4%)
  uri3/resolvers/protocol_resolver.py  dup=6L  groups=1  frags=2  (0.1%)

DUPLICATES[3] (ranked by impact):
  [49d1d03e6ce392a1] ! STRU  weather_proto  L=43 N=3 saved=86 sim=1.00
      hypervisor/domain_pack/templates.py:36-78  (weather_proto)
      hypervisor/domain_pack/templates.py:81-106  (weather_handler)
      hypervisor/domain_pack/templates.py:109-115  (generic_handler)
  [277a3a34943f29ee]   STRU  python_file_header  L=6 N=3 saved=12 sim=1.00
      generator/header.py:23-28  (python_file_header)
      generator/header.py:31-36  (dockerfile_header)
      generator/header.py:39-44  (markdown_generated_banner)
  [bc6d855bfb035b8b]   STRU  resolve_a2a  L=3 N=2 saved=3 sim=1.00
      uri3/resolvers/protocol_resolver.py:10-12  (resolve_a2a)
      uri3/resolvers/protocol_resolver.py:15-17  (resolve_mcp)

REFACTOR[3] (ranked by priority):
  [1] ○ extract_function   → hypervisor/domain_pack/utils/weather_proto.py
      WHY: 3 occurrences of 43-line block across 1 files — saves 86 lines
      FILES: hypervisor/domain_pack/templates.py
  [2] ○ extract_function   → generator/utils/python_file_header.py
      WHY: 3 occurrences of 6-line block across 1 files — saves 12 lines
      FILES: generator/header.py
  [3] ○ extract_function   → uri3/resolvers/utils/resolve_a2a.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: uri3/resolvers/protocol_resolver.py

QUICK_WINS[2] (low risk, high savings — do first):
  [1] extract_function   saved=86L  → hypervisor/domain_pack/utils/weather_proto.py
      FILES: templates.py
  [2] extract_function   saved=12L  → generator/utils/python_file_header.py
      FILES: header.py

EFFORT_ESTIMATE (total ≈ 4.8h):
  hard   weather_proto                       saved=86L  ~258min
  easy   python_file_header                  saved=12L  ~24min
  easy   resolve_a2a                         saved=3L  ~6min

METRICS-TARGET:
  dup_groups:  3 → 0
  saved_lines: 101 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 220 func | 70f | 2026-06-14
# generated in 0.00s

NEXT[7] (ranked by impact):
  [1] !  SPLIT-FUNC      main  CC=16  fan=16
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 256

  [2] !  SPLIT-FUNC      main  CC=20  fan=11
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 220

  [3] !  SPLIT-FUNC      validate_config  CC=17  fan=11
      WHY: CC=17 exceeds 15
      EFFORT: ~1h  IMPACT: 187

  [4] !  SPLIT-FUNC      validate_registry  CC=20  fan=8
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 160

  [5] !  SPLIT-FUNC      validate_cross_references  CC=22  fan=3
      WHY: CC=22 exceeds 15
      EFFORT: ~1h  IMPACT: 66

  [6] !! SPLIT           planfile.yaml
      WHY: 1319L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0

  [7] !! SPLIT           goal.yaml
      WHY: 511L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[2]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          3.3 → ≤2.3
  max-CC:      22 → ≤11
  god-modules: 2 → 0
  high-CC(≥15): 5 → ≤2
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
  prev CC̄=3.5 → now CC̄=3.3
```

## Intent

WronAI resource agent monorepo — uri3, nl2uri, hypervisor, agent factory

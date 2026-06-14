# Resource Agent Meta-Factory v0.1

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `hypervisor`
- **version**: `0.1.0`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(3), app.doql.less, goal.yaml, .env.example, Dockerfile, docker-compose.yml, src(4 mod), project/(5 analysis files)

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

## Workflows

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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 141f 5112L | python:97,yaml:21,json:10,proto:3,txt:2,yml:1,toml:1,shell:1,j2:1 | 2026-06-14
# generated in 0.02s
# CC̅=3.8 | critical:6/145 | dups:0 | cycles:1

HEALTH[6]:
  🟡 CC    main CC=16 (limit:15)
  🟡 CC    load_config CC=16 (limit:15)
  🟡 CC    repair_agent_spec CC=26 (limit:15)
  🟡 CC    main CC=20 (limit:15)
  🟡 CC    validate_registry CC=20 (limit:15)
  🟡 CC    validate_cross_references CC=22 (limit:15)

REFACTOR[2]:
  1. split 6 high-CC methods  (CC>15)
  2. break 1 circular dependencies

PIPELINES[67]:
  [1] Src [validate]: validate → validate_uri → parse_uri
      PURITY: 100% pure
  [2] Src [validate_tree]: validate_tree → validate_uri_tree → load_yaml
      PURITY: 100% pure
  [3] Src [graph]: graph → build_graph_from_tree
      PURITY: 100% pure
  [4] Src [resolve]: resolve
      PURITY: 100% pure
  [5] Src [scan]: scan
      PURITY: 100% pure
  [6] Src [main]: main
      PURITY: 100% pure
  [7] Src [main]: main → iter_agent_specs
      PURITY: 100% pure
  [8] Src [scan]: scan → scan_http
      PURITY: 100% pure
  [9] Src [main]: main → verify_generated → verify_generated_agent → file_sha256
      PURITY: 100% pure
  [10] Src [normalize_uri]: normalize_uri → parse_uri
      PURITY: 100% pure
  [11] Src [main]: main → save_proposal_from_prompt → infer_intent → singularize
      PURITY: 100% pure
  [12] Src [resolve]: resolve
      PURITY: 100% pure
  [13] Src [__init__]: __init__
      PURITY: 100% pure
  [14] Src [resolve]: resolve → parse_uri
      PURITY: 100% pure
  [15] Src [call]: call → parse_uri
      PURITY: 100% pure
  [16] Src [resolve]: resolve → parse_uri
      PURITY: 100% pure
  [17] Src [call]: call
      PURITY: 100% pure
  [18] Src [resolve]: resolve → parse_uri
      PURITY: 100% pure
  [19] Src [scan]: scan
      PURITY: 100% pure
  [20] Src [resolve]: resolve
      PURITY: 100% pure
  [21] Src [main]: main
      PURITY: 100% pure
  [22] Src [get_config]: get_config → load_config → get_default_config → _load_yaml
      PURITY: 100% pure
  [23] Src [add_node]: add_node
      PURITY: 100% pure
  [24] Src [add_edge]: add_edge
      PURITY: 100% pure
  [25] Src [main]: main → load_contract_registry → _read_yaml
      PURITY: 100% pure
  [26] Src [evaluate_change]: evaluate_change
      PURITY: 100% pure
  [27] Src [main]: main → load_proposal
      PURITY: 100% pure
  [28] Src [__init__]: __init__
      PURITY: 100% pure
  [29] Src [resolve]: resolve
      PURITY: 100% pure
  [30] Src [graph]: graph → build_graph_from_tree
      PURITY: 100% pure
  [31] Src [nl2uri]: nl2uri → rule_based_plan → _slug
      PURITY: 100% pure
  [32] Src [main]: main → validate_contract_files → validate_file → _read_yaml
      PURITY: 100% pure
  [33] Src [resolve]: resolve → parse_uri
      PURITY: 100% pure
  [34] Src [export_json]: export_json → write_registry_manifest → build_registry_manifest → load_contract_registry → ...(1 more)
      PURITY: 100% pure
  [35] Src [generate]: generate → rule_based_plan → _slug
      PURITY: 100% pure
  [36] Src [main]: main
      PURITY: 100% pure
  [37] Src [_hash_file]: _hash_file
      PURITY: 100% pure
  [38] Src [classify_registry_change]: classify_registry_change → load_contract_registry → _read_yaml
      PURITY: 100% pure
  [39] Src [handler]: handler
      PURITY: 100% pure
  [40] Src [plan_domain_from_prompt]: plan_domain_from_prompt → _generic_plan → _slug
      PURITY: 100% pure
  [41] Src [generate]: generate → write_uri_tree
      PURITY: 100% pure
  [42] Src [main]: main
      PURITY: 100% pure
  [43] Src [__init__]: __init__
      PURITY: 100% pure
  [44] Src [read_resource]: read_resource
      PURITY: 100% pure
  [45] Src [dispatch_command]: dispatch_command
      PURITY: 100% pure
  [46] Src [__post_init__]: __post_init__
      PURITY: 100% pure
  [47] Src [from_config]: from_config → load_config → get_default_config → _load_yaml
      PURITY: 100% pure
  [48] Src [start]: start
      PURITY: 100% pure
  [49] Src [stop]: stop
      PURITY: 100% pure
  [50] Src [register_agent]: register_agent
      PURITY: 100% pure

LAYERS:
  generator/                      CC̄=5.1    ←in:10  →out:0
  │ model                       88L  2C    2m  CC=7      ←2
  │ agent_generator             84L  0C    4m  CC=5      ←1
  │ validate                    69L  0C    3m  CC=11     ←5
  │ verify                      65L  0C    3m  CC=9      ←3
  │ hashutil                     9L  0C    1m  CC=1      ←2
  │ Dockerfile.j2                6L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  meta_agent/                     CC̄=4.0    ←in:0  →out:10  !! split
  │ domain_pack_generator      248L  0C    8m  CC=11     ←0
  │ planner                    159L  0C    5m  CC=9      ←2
  │ llm_planner                141L  0C    7m  CC=6      ←0
  │ !! repair                     107L  0C    3m  CC=26     ←3
  │ !! cli                         93L  0C    1m  CC=16     ←0
  │ api                         83L  2C    7m  CC=2      ←0
  │ orchestrator                71L  0C    4m  CC=6      ←2
  │ models                      43L  3C    1m  CC=1      ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  hypervisor/                     CC̄=4.0    ←in:0  →out:0
  │ !! config                     108L  0C    4m  CC=16     ←1
  │ core                        86L  1C    7m  CC=3      ←0
  │ loader                      80L  0C    2m  CC=9      ←5
  │ !! cli                         77L  0C    1m  CC=20     ←0
  │ registry_builder            60L  0C    4m  CC=5      ←2
  │ !! cross_validator             56L  0C    4m  CC=22     ←1
  │ models                      56L  4C    3m  CC=4      ←0
  │ schema_validator            54L  1C    4m  CC=6      ←1
  │ router                      51L  1C    2m  CC=10     ←0
  │ !! validate                    50L  0C    1m  CC=20     ←2
  │ checker                     43L  0C    2m  CC=8      ←0
  │ cli                         33L  0C    1m  CC=10     ←0
  │ capability_tests            32L  0C    1m  CC=4      ←1
  │ models                      32L  1C    1m  CC=5      ←1
  │ registry_exporter           29L  0C    2m  CC=6      ←1
  │ cli                         28L  0C    1m  CC=5      ←0
  │ function_resolver           26L  0C    3m  CC=2      ←1
  │ gate                        26L  1C    1m  CC=5      ←0
  │ protocol_resolver           22L  0C    4m  CC=2      ←1
  │ _version                    20L  0C    0m  CC=0.0    ←0
  │ llm_resolver                18L  0C    1m  CC=5      ←1
  │ pypi_resolver               16L  0C    1m  CC=5      ←1
  │ validator                   16L  0C    1m  CC=6      ←1
  │ nlp2uri.yaml                15L  0C    0m  CC=0.0    ←0
  │ env_resolver                12L  0C    1m  CC=3      ←1
  │ cli                         10L  0C    3m  CC=2      ←0
  │ client                      10L  1C    5m  CC=1      ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  nl2uri/                         CC̄=3.3    ←in:4  →out:0
  │ planner                     32L  1C    2m  CC=8      ←4
  │ llm_planner                 18L  0C    1m  CC=4      ←2
  │ cli                         16L  0C    2m  CC=4      ←0
  │ writer                       7L  0C    1m  CC=1      ←2
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  domains/                        CC̄=3.0    ←in:0  →out:0
  │ weather_map.proto           41L  0C    0m  CC=0.0    ←0
  │ uri_tree.yaml               38L  0C    0m  CC=0.0    ←0
  │ generate_weather_map        24L  0C    1m  CC=3      ←0
  │ resources.yaml              23L  0C    0m  CC=0.0    ←0
  │ views.yaml                  11L  0C    0m  CC=0.0    ←0
  │ renderers.yaml              10L  0C    0m  CC=0.0    ←0
  │ domain.yaml                  8L  0C    0m  CC=0.0    ←0
  │ commands.yaml                8L  0C    0m  CC=0.0    ←0
  │ registry.fragment.yaml       2L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  uri3/                           CC̄=2.6    ←in:0  →out:3
  │ uri_graph                   51L  3C    3m  CC=10     ←2
  │ cli                         36L  0C    6m  CC=3      ←0
  │ router                      21L  1C    3m  CC=3      ←0
  │ uri_tree_validator          18L  0C    2m  CC=2      ←1
  │ parser                      17L  1C    1m  CC=2      ←7
  │ http_scanner                16L  0C    1m  CC=6      ←1
  │ python_resolver             14L  1C    2m  CC=2      ←0
  │ llm_resolver                14L  2C    1m  CC=1      ←0
  │ env_resolver                11L  1C    1m  CC=3      ←0
  │ uri_validator                9L  0C    1m  CC=2      ←1
  │ normalizer                   9L  0C    1m  CC=3      ←0
  │ scanner                      7L  0C    1m  CC=2      ←0
  │ http_resolver                7L  1C    1m  CC=2      ←0
  │ base                         7L  1C    0m  CC=0.0    ←0
  │ schemes                      4L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  runtime_client/                 CC̄=1.7    ←in:0  →out:0
  │ client                      47L  1C    3m  CC=2      ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  nl2a/                           CC̄=1.5    ←in:0  →out:3
  │ cli                         19L  0C    2m  CC=2      ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  511L  0C    0m  CC=0.0    ←0
  │ tree.txt                   240L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             120L  0C    0m  CC=0.0    ←0
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
  │ create_invoices_agent_prompt.txt     1L  0C    0m  CC=0.0    ←0
  │
  output/                         CC̄=0.0    ←in:0  →out:0
  │ contract_registry.resolved.json   174L  0C    0m  CC=0.0    ←0
  │
  evolution/                      CC̄=0.0    ←in:0  →out:0
  │ add_invoices_agent.yaml     18L  0C    0m  CC=0.0    ←0
  │ add_orders_agent.yaml       17L  0C    0m  CC=0.0    ←0
  │
  contracts/                      CC̄=0.0    ←in:0  →out:0
  │ weather.proto               41L  0C    0m  CC=0.0    ←0
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
  │ Dockerfile                   6L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   6L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     agents/__init__.py                        0L
     agents/custom/__init__.py                 0L
     agents/generated/__init__.py              0L
     domains/__init__.py                       0L
     domains/weather_map/__init__.py           0L
     domains/weather_map/handlers/__init__.py  0L
     generator/__init__.py                     0L
     hypervisor/__init__.py                    0L
     hypervisor/compatibility/__init__.py      0L
     hypervisor/contract_registry/__init__.py  0L
     hypervisor/deployment_registry/__init__.py  0L
     hypervisor/domain_pack/__init__.py        0L
     hypervisor/evolution/__init__.py          0L
     hypervisor/policy_gate/__init__.py        0L
     hypervisor/uri/__init__.py                0L
     hypervisor/verifier/__init__.py           0L
     nl2a/__init__.py                          0L
     nl2uri/__init__.py                        0L
     nl2uri/prompts/__init__.py                0L
     runtime_client/__init__.py                0L
     uri3/__init__.py                          0L
     uri3/discovery/__init__.py                0L
     uri3/graph/__init__.py                    0L
     uri3/protocols/__init__.py                0L
     uri3/resolvers/__init__.py                0L
     uri3/scanner/__init__.py                  0L
     uri3/validators/__init__.py               0L

COUPLING:
                                                   generator                    meta_agent                uri3.protocols                uri3.resolvers  hypervisor.contract_registry                        nl2uri                          nl2a                          uri3               uri3.validators      hypervisor.compatibility                hypervisor.uri           hypervisor.verifier                    uri3.graph                  uri3.scanner
                     generator                            ──                           ←10                                                                                                                                                                                                                                                                                                                                                                          hub
                    meta_agent                            10                            ──                                                                                                                                                                                                                                                                                                                                                                          !! fan-out
                uri3.protocols                                                                                        ──                            ←5                                                                                                                                                    ←1                                                                                                                                                    ←1  hub
                uri3.resolvers                                                                                         5                            ──                                                                                                                                                                                                                                                                                                            
  hypervisor.contract_registry                                                                                                                                                    ──                                                                                                                                                    ←2                                                          ←2                                                            
                        nl2uri                                                                                                                                                                                  ──                            ←3                                                                                                                      ←1                                                                                          
                          nl2a                                                                                                                                                                                   3                            ──                                                                                                                                                                                                                  
                          uri3                                                                                                                                                                                                                                              ──                             2                                                                                                                       1                              
               uri3.validators                                                                                         1                                                                                                                                                    ←2                            ──                                                                                                                                                      
      hypervisor.compatibility                                                                                                                                                     2                                                                                                                                                    ──                                                                                                                        
                hypervisor.uri                                                                                                                                                                                   1                                                                                                                                                    ──                                                           1                              
           hypervisor.verifier                                                                                                                                                     2                                                                                                                                                                                                                ──                                                            
                    uri3.graph                                                                                                                                                                                                                                              ←1                                                                                        ←1                                                          ──                              
                  uri3.scanner                                                                                         1                                                                                                                                                                                                                                                                                                                                        ──
  CYCLES: 1
  HUB: uri3.protocols/ (fan-in=7)
  HUB: generator/ (fan-in=10)
  SMELL: meta_agent/ fan-out=10 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 2 groups | 96f 3010L | 2026-06-14

SUMMARY:
  files_scanned: 96
  total_lines:   3010
  dup_groups:    2
  dup_fragments: 5
  saved_lines:   89
  scan_ms:       3511

HOTSPOTS[2] (files with most duplication):
  meta_agent/domain_planner/domain_pack_generator.py  dup=76L  groups=1  frags=3  (2.5%)
  hypervisor/uri2llm/protocol_resolver.py  dup=6L  groups=1  frags=2  (0.2%)

DUPLICATES[2] (ranked by impact):
  [49d1d03e6ce392a1] ! STRU  _weather_proto  L=43 N=3 saved=86 sim=1.00
      meta_agent/domain_planner/domain_pack_generator.py:49-91  (_weather_proto)
      meta_agent/domain_planner/domain_pack_generator.py:94-119  (_weather_handler)
      meta_agent/domain_planner/domain_pack_generator.py:122-128  (_generic_handler)
  [bc6d855bfb035b8b]   STRU  resolve_a2a  L=3 N=2 saved=3 sim=1.00
      hypervisor/uri2llm/protocol_resolver.py:10-12  (resolve_a2a)
      hypervisor/uri2llm/protocol_resolver.py:15-17  (resolve_mcp)

REFACTOR[2] (ranked by priority):
  [1] ○ extract_function   → meta_agent/domain_planner/utils/_weather_proto.py
      WHY: 3 occurrences of 43-line block across 1 files — saves 86 lines
      FILES: meta_agent/domain_planner/domain_pack_generator.py
  [2] ○ extract_function   → hypervisor/uri2llm/utils/resolve_a2a.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: hypervisor/uri2llm/protocol_resolver.py

QUICK_WINS[1] (low risk, high savings — do first):
  [1] extract_function   saved=86L  → meta_agent/domain_planner/utils/_weather_proto.py
      FILES: domain_pack_generator.py

EFFORT_ESTIMATE (total ≈ 4.4h):
  hard   _weather_proto                      saved=86L  ~258min
  easy   resolve_a2a                         saved=3L  ~6min

METRICS-TARGET:
  dup_groups:  2 → 0
  saved_lines: 89 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 145 func | 58f | 2026-06-14
# generated in 0.00s

NEXT[7] (ranked by impact):
  [1] !! SPLIT-FUNC      repair_agent_spec  CC=26  fan=21
      WHY: CC=26 exceeds 15
      EFFORT: ~1h  IMPACT: 546

  [2] !  SPLIT-FUNC      load_config  CC=16  fan=18
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 288

  [3] !  SPLIT-FUNC      main  CC=16  fan=16
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 256

  [4] !  SPLIT-FUNC      main  CC=20  fan=11
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 220

  [5] !  SPLIT-FUNC      validate_registry  CC=20  fan=8
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 160

  [6] !  SPLIT-FUNC      validate_cross_references  CC=22  fan=3
      WHY: CC=22 exceeds 15
      EFFORT: ~1h  IMPACT: 66

  [7] !! SPLIT           goal.yaml
      WHY: 511L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[1]:
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          3.8 → ≤2.7
  max-CC:      26 → ≤13
  god-modules: 1 → 0
  high-CC(≥15): 6 → ≤3
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
  (first run — no previous data)
```

## Intent

WronAI Hypervisor — orchestrator and control plane for AI desktop agents, NLP-to-URI resolution, koru drivers, and virtualized execution

# TellMesh v0.6

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

- **name**: `tellmesh`
- **version**: `0.5.28`
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

## Workflows

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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 641f 41770L | python:311,yaml:145,json:77,shell:40,javascript:17,toml:10,proto:10,txt:6,yml:4,mk:2,j2:1 | 2026-06-15
# generated in 0.14s
# CC̅=3.6 | critical:16/1723 | dups:0 | cycles:0

HEALTH[16]:
  🟡 CC    describe_agent CC=17 (limit:15)
  🟡 CC    _render_markdown CC=70 (limit:15)
  🟡 CC    resolve_contract_path CC=22 (limit:15)
  🟡 CC    fetch_agent_artifacts CC=21 (limit:15)
  🟡 CC    handle_contract_uri CC=21 (limit:15)
  🟡 CC    handle_schema_uri CC=20 (limit:15)
  🟡 CC    _validate_example CC=25 (limit:15)
  🟡 CC    _validate_deployments CC=26 (limit:15)
  🟡 CC    executorTurnFromCall CC=18 (limit:15)
  🟡 CC    rebuildNodes CC=19 (limit:15)
  🟡 CC    seen CC=19 (limit:15)
  🟡 CC    renderTurnHtml CC=17 (limit:15)
  🟡 CC    applyLanguage CC=24 (limit:15)
  🟡 CC    createVoiceController CC=29 (limit:15)
  🟡 CC    _applyOfficeCardCopy CC=15 (limit:15)
  🟡 CC    _capture_screenshot CC=26 (limit:15)

REFACTOR[1]:
  1. split 16 high-CC methods  (CC>15)

PIPELINES[611]:
  [1] Src [main]: main → iter_agent_specs
      PURITY: 100% pure
  [2] Src [main]: main → expand_paths
      PURITY: 100% pure
  [3] Src [main]: main → _agent_dirs
      PURITY: 100% pure
  [4] Src [health]: health
      PURITY: 100% pure
  [5] Src [capabilities]: capabilities
      PURITY: 100% pure
  [6] Src [well_known_agent_json]: well_known_agent_json
      PURITY: 100% pure
  [7] Src [well_known_agent_card_json]: well_known_agent_card_json
      PURITY: 100% pure
  [8] Src [read_resource]: read_resource → _uri_allowed
      PURITY: 100% pure
  [9] Src [dispatch_command]: dispatch_command
      PURITY: 100% pure
  [10] Src [skill_read_order]: skill_read_order
      PURITY: 100% pure
  [11] Src [skill_read_order_events]: skill_read_order_events
      PURITY: 100% pure
  [12] Src [health]: health
      PURITY: 100% pure
  [13] Src [capabilities]: capabilities
      PURITY: 100% pure
  [14] Src [well_known_agent_json]: well_known_agent_json
      PURITY: 100% pure
  [15] Src [well_known_agent_card_json]: well_known_agent_card_json
      PURITY: 100% pure
  [16] Src [read_resource]: read_resource → _uri_allowed
      PURITY: 100% pure
  [17] Src [dispatch_command]: dispatch_command
      PURITY: 100% pure
  [18] Src [skill_read_user]: skill_read_user
      PURITY: 100% pure
  [19] Src [skill_read_user_roles]: skill_read_user_roles
      PURITY: 100% pure
  [20] Src [skill_create_user]: skill_create_user
      PURITY: 100% pure
  [21] Src [skill_assign_user_role]: skill_assign_user_role
      PURITY: 100% pure
  [22] Src [main]: main → cmd_plan → save_proposal_from_prompt → infer_intent → ...(1 more)
      PURITY: 100% pure
  [23] Src [health]: health
      PURITY: 100% pure
  [24] Src [proposal_from_prompt]: proposal_from_prompt → save_proposal_from_prompt → infer_intent → singularize
      PURITY: 100% pure
  [25] Src [validate]: validate → validate_agent → load_agent_spec
      PURITY: 100% pure
  [26] Src [repair]: repair → repair_agent_spec → validate_agent → load_agent_spec
      PURITY: 100% pure
  [27] Src [generate]: generate → asdict_result
      PURITY: 100% pure
  [28] Src [pipeline]: pipeline → pipeline_from_prompt → save_proposal_from_prompt → infer_intent → ...(1 more)
      PURITY: 100% pure
  [29] Src [verify]: verify → verify_generated → _agent_dirs
      PURITY: 100% pure
  [30] Src [call]: call → _load_json_payload
      PURITY: 100% pure
  [31] Src [explain]: explain → _load_json_payload
      PURITY: 100% pure
  [32] Src [scan]: scan
      PURITY: 100% pure
  [33] Src [status]: status → echo_json
      PURITY: 100% pure
  [34] Src [config_cmd]: config_cmd → load_config → get_default_config → apply_builtin_defaults
      PURITY: 100% pure
  [35] Src [deployments_list]: deployments_list → registry_summary → load_deployment_registry → _read_yaml
      PURITY: 100% pure
  [36] Src [run_agent_cmd]: run_agent_cmd → run_local_agent → resolve_deployment → load_deployment_registry → ...(1 more)
      PURITY: 100% pure
  [37] Src [stop_agent_cmd]: stop_agent_cmd → echo_json
      PURITY: 100% pure
  [38] Src [restart_agent_cmd]: restart_agent_cmd → echo_json
      PURITY: 100% pure
  [39] Src [agent_status_cmd]: agent_status_cmd → echo_json
      PURITY: 100% pure
  [40] Src [inspect_agent_cmd]: inspect_agent_cmd → echo_json
      PURITY: 100% pure
  [41] Src [describe_agent_cmd]: describe_agent_cmd → describe_agent → resolve_deployment → load_deployment_registry → ...(1 more)
      PURITY: 100% pure
  [42] Src [supervise_cmd]: supervise_cmd → echo_json
      PURITY: 100% pure
  [43] Src [repair_diagnose_cmd]: repair_diagnose_cmd → echo_json
      PURITY: 100% pure
  [44] Src [repair_apply_cmd]: repair_apply_cmd → repair_apply → _repo_root → find_repo_root → ...(2 more)
      PURITY: 100% pure
  [45] Src [repair_heal_cmd]: repair_heal_cmd → run_uri_healer → supervise_with_repair → _repo_root → ...(3 more)
      PURITY: 100% pure
  [46] Src [repair_learn_cmd]: repair_learn_cmd → learn_from_incident → _repo_root → find_repo_root → ...(2 more)
      PURITY: 100% pure
  [47] Src [artifacts_check_cmd]: artifacts_check_cmd → find_repo_root → _walk_hypervisor_root → _is_hypervisor_root
      PURITY: 100% pure
  [48] Src [artifacts_schemas_cmd]: artifacts_schemas_cmd → check_schemas
      PURITY: 100% pure
  [49] Src [artifacts_lifecycle_cmd]: artifacts_lifecycle_cmd → check_lifecycle_coverage → _collect_lifecycle_results → _artifact_lifecycle_result → ...(1 more)
      PURITY: 100% pure
  [50] Src [ticket_import_cmd]: ticket_import_cmd → find_repo_root → _walk_hypervisor_root → _is_hypervisor_root
      PURITY: 100% pure

LAYERS:
  generator/                      CC̄=5.3    ←in:16  →out:4
  │ validate                     0L  0C    3m  CC=11     ←6
  │ hashutil                     0L  0C    1m  CC=1      ←3
  │ model                        0L  2C    2m  CC=7      ←3
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=4.3    ←in:0  →out:0
  │ effective_weather_playwright   466L  0C   17m  CC=14     ←0
  │ !! audit_agent_reports        427L  3C    6m  CC=26     ←0
  │ build_examples_docs        324L  0C   20m  CC=8      ←0
  │ build_landing_integrations   313L  0C   18m  CC=12     ←0
  │ split_packages             279L  0C    7m  CC=10     ←0
  │ checks_structure           278L  0C   17m  CC=11     ←1
  │ test_monitors.sh           179L  1C    2m  CC=0.0    ←0
  │ parsers                    170L  0C    3m  CC=12     ←1
  │ build_examples_manifest    164L  0C    8m  CC=11     ←0
  │ areas                      156L  0C    3m  CC=13     ←2
  │ install-cron.sh            150L  0C    4m  CC=0.0    ←0
  │ audit                      144L  0C    5m  CC=14     ←1
  │ checks_domain              142L  0C    6m  CC=9      ←1
  │ move_tests                 137L  0C    4m  CC=11     ←0
  │ monitor_landing            133L  0C    5m  CC=7      ←0
  │ fix_and_publish            129L  0C    7m  CC=6      ←0
  │ check_examples_links       106L  0C    6m  CC=12     ←0
  │ cli                         92L  0C    5m  CC=5      ←0
  │ monitor_notify              89L  0C    5m  CC=7      ←2
  │ render                      83L  0C    5m  CC=3      ←1
  │ monitor_url                 83L  0C    2m  CC=5      ←0
  │ site_nav                    77L  0C    4m  CC=5      ←1
  │ doql_host_preview.sh        74L  0C    0m  CC=0.0    ←0
  │ cli_fallback.sh             65L  0C    1m  CC=0.0    ←0
  │ run_uri3_workflow           58L  0C    1m  CC=4      ←0
  │ architecture_gate.sh        56L  0C    1m  CC=0.0    ←0
  │ about_parser                53L  0C    3m  CC=7      ←2
  │ models                      53L  5C    0m  CC=0.0    ←0
  │ md_html                     48L  0C    4m  CC=3      ←1
  │ run_monitors.sh             47L  0C    1m  CC=0.0    ←0
  │ verify_agents.sh            34L  0C    0m  CC=0.0    ←0
  │ architecture_responsibility_audit    28L  0C    0m  CC=0.0    ←0
  │ smoke.sh                    28L  0C    0m  CC=0.0    ←0
  │ __init__                    20L  0C    0m  CC=0.0    ←0
  │ ensure_editable_install.sh    19L  0C    0m  CC=0.0    ←0
  │ fix-generated-ownership.sh    18L  0C    0m  CC=0.0    ←0
  │ test-all-examples.sh         5L  0C    0m  CC=0.0    ←0
  │
  packages/                       CC̄=4.2    ←in:0  →out:0
  │ !! agent_describe             677L  1C   16m  CC=70     ←2
  │ !! cli                        563L  0C   31m  CC=8      ←13
  │ !! uri_resolver               562L  0C   19m  CC=22     ←2
  │ lifecycle                  423L  0C   15m  CC=7      ←5
  │ watch                      408L  0C   17m  CC=14     ←1
  │ supervisor                 381L  0C   10m  CC=11     ←4
  │ gate                       308L  2C   11m  CC=14     ←1
  │ !! system_handlers            305L  0C   13m  CC=20     ←1
  │ run_executor               304L  0C   14m  CC=10     ←2
  │ runtime_state              295L  0C   24m  CC=12     ←8
  │ stopper                    239L  0C   11m  CC=11     ←4
  │ pipeline                   231L  1C    6m  CC=13     ←1
  │ supervisor                 199L  0C    8m  CC=10     ←8
  │ status                     188L  0C   11m  CC=13     ←7
  │ incidents                  184L  0C    7m  CC=13     ←1
  │ incident                   181L  0C   11m  CC=8      ←1
  │ system_dispatch            175L  0C   19m  CC=5      ←1
  │ cli_commands               159L  0C    6m  CC=7      ←1
  │ probe                      148L  0C    6m  CC=13     ←1
  │ resolver                   147L  0C    6m  CC=14     ←3
  │ classifier                 138L  1C    5m  CC=7      ←1
  │ view_handlers              138L  1C    6m  CC=13     ←2
  │ policy                     137L  2C    5m  CC=13     ←2
  │ playbooks                  134L  0C   10m  CC=8      ←2
  │ agent_generator            132L  0C    5m  CC=5      ←2
  │ proposal_from_source       127L  0C    3m  CC=11     ←3
  │ process_discovery          124L  0C    7m  CC=9      ←2
  │ models                     124L  4C    6m  CC=7      ←0
  │ templates                  121L  0C    5m  CC=1      ←0
  │ local_targets              120L  0C    7m  CC=6      ←2
  │ ssh_run                    118L  0C    2m  CC=10     ←3
  │ resolver                   110L  1C   10m  CC=7      ←1
  │ plan_builder               108L  0C    6m  CC=11     ←1
  │ process                    104L  0C    5m  CC=8      ←2
  │ parser                      99L  1C    4m  CC=12     ←3
  │ loader                      96L  0C    5m  CC=6      ←2
  │ routes                      95L  1C   11m  CC=4      ←0
  │ ticket_mapper               95L  0C    5m  CC=10     ←1
  │ ssh_deploy                  95L  0C    2m  CC=7      ←2
  │ pack_writer                 93L  0C    1m  CC=8      ←1
  │ readiness                   92L  0C    3m  CC=9      ←1
  │ routes                      89L  1C    9m  CC=4      ←0
  │ loader                      87L  0C    7m  CC=7      ←12
  │ events                      86L  0C    3m  CC=6      ←4
  │ core                        84L  1C    7m  CC=3      ←0
  │ verify                      83L  0C    4m  CC=7      ←4
  │ expander                    81L  0C    4m  CC=11     ←3
  │ port_conflict               77L  0C    2m  CC=7      ←1
  │ docker_runner               76L  0C    6m  CC=9      ←4
  │ selector                    76L  0C    3m  CC=14     ←10
  │ generator                   75L  0C    2m  CC=2      ←0
  │ cli                         75L  0C    5m  CC=3      ←0
  │ explain                     74L  0C    2m  CC=6      ←1
  │ orchestrator                73L  0C    4m  CC=7      ←2
  │ client                      73L  1C    9m  CC=3      ←0
  │ dispatcher                  73L  0C    1m  CC=6      ←13
  │ policy                      71L  0C    3m  CC=2      ←2
  │ cli_commands                69L  0C    6m  CC=3      ←1
  │ capabilities                68L  0C    2m  CC=14     ←1
  │ registry_sync               68L  0C    4m  CC=2      ←3
  │ lifecycle_status            67L  0C    4m  CC=5      ←3
  │ health_uri                  66L  0C    7m  CC=8      ←6
  │ cli_commands                65L  0C    5m  CC=5      ←0
  │ __init__                    65L  0C    0m  CC=0.0    ←0
  │ validator                   64L  0C    3m  CC=11     ←1
  │ models                      63L  2C    2m  CC=2      ←0
  │ defaults                    63L  0C    4m  CC=4      ←1
  │ models                      63L  2C    3m  CC=3      ←0
  │ agent_card                  63L  0C    0m  CC=0.0    ←0
  │ port_utils                  62L  0C    6m  CC=4      ←8
  │ merge_helpers               61L  0C    3m  CC=6      ←1
  │ registry_builder            60L  0C    4m  CC=5      ←3
  │ capabilities                59L  0C    4m  CC=8      ←2
  │ registry_bridge             59L  0C    3m  CC=7      ←1
  │ registry                    58L  0C    5m  CC=10     ←1
  │ process                     57L  0C    4m  CC=5      ←1
  │ header                      56L  0C    5m  CC=3      ←1
  │ paths                       52L  0C    4m  CC=6      ←33
  │ cli                         51L  0C    1m  CC=7      ←0
  │ validator                   51L  0C    6m  CC=2      ←4
  │ config_checks               50L  0C    4m  CC=7      ←1
  │ system_request              50L  1C    4m  CC=4      ←4
  │ env                         50L  0C    3m  CC=9      ←4
  │ nlp2uri.yaml                50L  0C    0m  CC=0.0    ←0
  │ sandbox                     49L  0C    2m  CC=6      ←1
  │ agent_contract              48L  0C    1m  CC=2      ←1
  │ models                      47L  2C    1m  CC=11     ←0
  │ validator                   45L  0C    2m  CC=14     ←1
  │ cross_validator             42L  0C    2m  CC=5      ←3
  │ cli                         41L  0C    2m  CC=5      ←0
  │ uri_config                  40L  0C    2m  CC=10     ←1
  │ uri_flow.schema.json        40L  0C    0m  CC=0.0    ←0
  │ local_verify                39L  0C    1m  CC=8      ←1
  │ __init__                    39L  0C    0m  CC=0.0    ←0
  │ ssh_verify                  38L  0C    1m  CC=12     ←2
  │ utils                       38L  0C    4m  CC=5      ←1
  │ agent_card                  37L  0C    0m  CC=0.0    ←0
  │ runner                      37L  0C    0m  CC=0.0    ←0
  │ healer                      35L  0C    1m  CC=1      ←1
  │ proposal_builder            35L  0C    2m  CC=2      ←1
  │ aliases                     34L  0C    2m  CC=8      ←1
  │ validators                  33L  0C    2m  CC=5      ←1
  │ cli                         33L  0C    1m  CC=10     ←0
  │ run_plans                   33L  0C    1m  CC=5      ←4
  │ pyproject.toml              33L  0C    0m  CC=0.0    ←0
  │ env_merge                   31L  0C    2m  CC=6      ←1
  │ env_config                  28L  0C    3m  CC=2      ←1
  │ merger                      26L  0C    1m  CC=2      ←1
  │ resources                   26L  0C    2m  CC=7      ←1
  │ model                       25L  1C    1m  CC=1      ←0
  │ pyproject.toml              25L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              25L  0C    0m  CC=0.0    ←0
  │ resources                   24L  0C    1m  CC=2      ←1
  │ markpact_loader             23L  0C    0m  CC=0.0    ←0
  │ resources                   22L  0C    1m  CC=6      ←1
  │ __init__                    19L  0C    0m  CC=0.0    ←0
  │ commands                    18L  0C    1m  CC=2      ←1
  │ parser                      17L  0C    2m  CC=1      ←1
  │ __init__                    17L  0C    0m  CC=0.0    ←0
  │ views                       16L  0C    1m  CC=2      ←1
  │ proto_index                 16L  0C    2m  CC=2      ←3
  │ main                        16L  0C    0m  CC=0.0    ←0
  │ main                        16L  0C    0m  CC=0.0    ←0
  │ remote_runner               16L  0C    0m  CC=0.0    ←0
  │ __init__                    16L  0C    0m  CC=0.0    ←0
  │ renderers                   14L  0C    1m  CC=3      ←1
  │ ssh_helpers                 14L  0C    2m  CC=2      ←2
  │ validate                    13L  0C    1m  CC=1      ←3
  │ __init__                    13L  0C    0m  CC=0.0    ←0
  │ __init__                    13L  0C    0m  CC=0.0    ←0
  │ paths                       12L  0C    1m  CC=1      ←1
  │ writer                      11L  0C    1m  CC=1      ←2
  │ handlers                    10L  0C    1m  CC=3      ←1
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ __init__                     9L  0C    0m  CC=0.0    ←0
  │ proto                        8L  0C    1m  CC=2      ←1
  │ capability_tests             8L  0C    1m  CC=1      ←1
  │ Dockerfile.j2                7L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │ presentation                 0L  0C    4m  CC=7      ←1
  │ plan_runner                  0L  1C    5m  CC=12     ←1
  │ monitor_webhook              0L  0C    6m  CC=9      ←1
  │ models                       0L  3C    3m  CC=2      ←0
  │ dashboard.js                 0L  0C   11m  CC=6      ←0
  │ pyproject.toml               0L  0C    0m  CC=0.0    ←0
  │ agent_card                   0L  0C    0m  CC=0.0    ←0
  │ main                         0L  0C    0m  CC=0.0    ←0
  │
  meta_agent/                     CC̄=3.5    ←in:9  →out:8  !! split
  │ planner                      0L  0C    5m  CC=9      ←3
  │ api                          0L  2C    7m  CC=2      ←0
  │ models                       0L  3C    1m  CC=1      ←2
  │ loader                       0L  0C    2m  CC=2      ←1
  │ pipeline                     0L  0C    1m  CC=2      ←3
  │ rules                        0L  0C    6m  CC=8      ←1
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ domain_pack_generator        0L  0C    0m  CC=0.0    ←0
  │ llm_planner                  0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  hypervisor/                     CC̄=3.4    ←in:0  →out:0
  │ cli                          0L  0C    1m  CC=5      ←0
  │ gate                         0L  1C    1m  CC=5      ←0
  │ models                       0L  8C    9m  CC=4      ←0
  │ env                          0L  0C    4m  CC=9      ←1
  │ models                       0L  1C    1m  CC=5      ←1
  │ loader                       0L  0C    2m  CC=9      ←7
  │ registry_exporter            0L  0C    2m  CC=6      ←1
  │ schema_validator             0L  1C    4m  CC=6      ←3
  │ models                       0L  4C    3m  CC=4      ←0
  │ writer                       0L  0C    4m  CC=3      ←2
  │ checker                      0L  0C    2m  CC=8      ←0
  │ _version                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ function_resolver            0L  0C    0m  CC=0.0    ←0
  │ pypi_resolver                0L  0C    0m  CC=0.0    ←0
  │ protocol_resolver            0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ llm_resolver                 0L  0C    0m  CC=0.0    ←0
  │ router                       0L  0C    0m  CC=0.0    ←0
  │ env_resolver                 0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  www/                            CC̄=3.2    ←in:3  →out:0
  │ !! integrations-i18n.js      1143L  0C    0m  CC=0.0    ←0
  │ !! landing.js                 836L  0C  111m  CC=24     ←3
  │ !! app.js                     731L  0C   99m  CC=14     ←0
  │ !! landing-i18n.js            719L  0C    0m  CC=0.0    ←0
  │ examples-manifest.js       477L  0C    0m  CC=0.0    ←0
  │ !! office-cards-i18n.js       306L  0C   16m  CC=15     ←0
  │ !! chat-flow-view.js          273L  0C   25m  CC=19     ←0
  │ app.js                     260L  0C   30m  CC=8      ←5
  │ flow-chat.js               225L  0C   33m  CC=7      ←0
  │ api-client.js              215L  1C   22m  CC=13     ←0
  │ bridge                     199L  2C    8m  CC=11     ←0
  │ chat-uri.js                182L  0C   28m  CC=11     ←0
  │ !! chat-voice.js              157L  0C   22m  CC=29     ←0
  │ examples-gallery.js        144L  0C   24m  CC=7      ←0
  │ chat-markdown.js            80L  0C   10m  CC=5      ←0
  │ openapi.yaml                75L  0C    0m  CC=0.0    ←0
  │ docs-examples.js            59L  0C   12m  CC=9      ←0
  │ chat_ui_agent.yaml          55L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  39L  0C    0m  CC=0.0    ←0
  │ agent_contract.schema.json    36L  0C    0m  CC=0.0    ←0
  │ nl-commands.txt             33L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          22L  0C    0m  CC=0.0    ←0
  │ config.js                   13L  0C    0m  CC=0.0    ←0
  │ 06_orders_agent-fa8cebf95291599c.json     4L  0C    0m  CC=0.0    ←0
  │ 16_llm_graph_planner-159f06dd4832dbab.json     4L  0C    0m  CC=0.0    ←0
  │ 35_website_screenshot_schedule-e692fc863f4dfa33.json     4L  0C    0m  CC=0.0    ←0
  │ 32_ecommerce_integrations-ceb917a24dc426c7.json     4L  0C    0m  CC=0.0    ←0
  │ 32_ecommerce_integrations-57cc7abc3e46c709.json     4L  0C    0m  CC=0.0    ←0
  │ 05_meta_repair-829661dc35de8437.json     4L  0C    0m  CC=0.0    ←0
  │ 16_www_landing_monitor-f7bdca1db38212a5.json     4L  0C    0m  CC=0.0    ←0
  │ 18_llm_flow_planner-f9fd0a829937576e.json     4L  0C    0m  CC=0.0    ←0
  │ 35_website_screenshot_schedule-5d3d692bad14d211.json     4L  0C    0m  CC=0.0    ←0
  │ 33_office_workflows-3181e16d403bf94e.json     4L  0C    0m  CC=0.0    ←0
  │ 09_run_agent_hypervisor-1711dce8fea4b4bd.json     4L  0C    0m  CC=0.0    ←0
  │ 32_ecommerce_integrations-305e5c45f88421e7.json     4L  0C    0m  CC=0.0    ←0
  │ 12_android_operator-86a6aec1684d0822.json     4L  0C    0m  CC=0.0    ←0
  │ 32_ecommerce_integrations-6c89fbcb7026a6d6.json     4L  0C    0m  CC=0.0    ←0
  │ 32_ecommerce_integrations-824cdb1be9f48c5f.json     4L  0C    0m  CC=0.0    ←0
  │ 03_ssh_remote_agent-948fe4512a944461.json     4L  0C    0m  CC=0.0    ←0
  │ 15_compact_uri_flow-bfca62561aac316c.json     4L  0C    0m  CC=0.0    ←0
  │ 22_dashboard_agent-c59387bc332dc4f0.json     4L  0C    0m  CC=0.0    ←0
  │ 36_physical_ops-5999114d62a13a0c.json     4L  0C    0m  CC=0.0    ←0
  │ 21_touri_voice-dfb4ecf1dd749f23.json     4L  0C    0m  CC=0.0    ←0
  │ 20_touri_capabilities-44612b79959663b2.json     4L  0C    0m  CC=0.0    ←0
  │ 34_cron_uri-8caa86a1f0b567e7.json     4L  0C    0m  CC=0.0    ←0
  │ 32_ecommerce_integrations-232ba3159dae70e5.json     4L  0C    0m  CC=0.0    ←0
  │ 04_nl2a_weather_map-35dffafaa015f2b1.json     4L  0C    0m  CC=0.0    ←0
  │ 10_browser_operator-2dc37409a09018f3.json     4L  0C    0m  CC=0.0    ←0
  │ 32_ecommerce_integrations-ef973d98bef7911e.json     4L  0C    0m  CC=0.0    ←0
  │ 17_flow_vs_graph-315d5c344a908569.json     4L  0C    0m  CC=0.0    ←0
  │ 32_ecommerce_integrations-5a3ded5e1fc34441.json     4L  0C    0m  CC=0.0    ←0
  │ 31_office_day-e7c4d91a191e34ff.json     4L  0C    0m  CC=0.0    ←0
  │ 14_workflow_executor_mock-3c044d3a9015c567.json     4L  0C    0m  CC=0.0    ←0
  │ 11_playwright_browser-65f644b9333c4fad.json     4L  0C    0m  CC=0.0    ←0
  │ 35_website_screenshot_schedule-5f3f6f2bfa01f1f5.json     4L  0C    0m  CC=0.0    ←0
  │ 08_evolution-db22aad1f8844232.json     4L  0C    0m  CC=0.0    ←0
  │ 32_ecommerce_integrations-61c29dafb93b6890.json     4L  0C    0m  CC=0.0    ←0
  │ 13_pcwin_operator-73848739b38fa413.json     4L  0C    0m  CC=0.0    ←0
  │ 07_invoices_agent-5859648a80381c9c.json     4L  0C    0m  CC=0.0    ←0
  │ 22_markpact_weather-311b3b5c7edf84a8.json     4L  0C    0m  CC=0.0    ←0
  │ 33_office_workflows-16fbaee09a140a1e.json     4L  0C    0m  CC=0.0    ←0
  │ 02_uri3_scan_http-194cbbcfa8306eac.json     4L  0C    0m  CC=0.0    ←0
  │ 23_nl_to_agent_tutorial-2c28d4c71f717931.json     4L  0C    0m  CC=0.0    ←0
  │ 13_nl2uri_multi_uri_graph-def5bcd16af46627.json     4L  0C    0m  CC=0.0    ←0
  │ 32_ecommerce_integrations-a0f1de7dca1f671a.json     4L  0C    0m  CC=0.0    ←0
  │ 15_playwright_browser-a74b7e7795438fdb.json     4L  0C    0m  CC=0.0    ←0
  │ 14_uri2ops_serve-7b57cb5162c84c38.json     4L  0C    0m  CC=0.0    ←0
  │ 32_ecommerce_integrations-66ca0b9fc6eae707.json     4L  0C    0m  CC=0.0    ←0
  │ 01_quickstart_local-3ea5cbf71000635c.json     4L  0C    0m  CC=0.0    ←0
  │ 35_website_screenshot_schedule-390ed226ee85a7ff.json     4L  0C    0m  CC=0.0    ←0
  │ 30_golden_path-e898a3a7b7679ee7.json     4L  0C    0m  CC=0.0    ←0
  │
  agents/                         CC̄=3.2    ←in:0  →out:0
  │ routes                     416L  5C   22m  CC=13     ←0
  │ chat_format                387L  0C   24m  CC=14     ←4
  │ uri_client                 334L  1C   22m  CC=7      ←4
  │ browser_playwright         321L  1C   21m  CC=12     ←1
  │ events_service             285L  0C   19m  CC=13     ←1
  │ analysis                   265L  0C   11m  CC=14     ←1
  │ programmer                 184L  0C    7m  CC=14     ←1
  │ routes                     166L  1C   15m  CC=5      ←0
  │ routes                     165L  1C   16m  CC=5      ←0
  │ routes                     155L  1C   14m  CC=5      ←0
  │ routes                     152L  1C   13m  CC=5      ←0
  │ routes                     152L  1C   13m  CC=5      ←0
  │ routes                     150L  1C   14m  CC=5      ←0
  │ routes                     148L  1C   13m  CC=5      ←0
  │ routes                     146L  1C   13m  CC=5      ←0
  │ routes                     146L  1C   13m  CC=5      ←0
  │ routes                     146L  1C   13m  CC=5      ←0
  │ routes                     144L  1C   12m  CC=5      ←0
  │ android_adb                143L  0C    9m  CC=11     ←0
  │ !! screen_gnome               139L  0C    6m  CC=26     ←0
  │ routes                     138L  1C   11m  CC=5      ←0
  │ physical_mock              133L  0C    9m  CC=6      ←0
  │ pcwin_uia                   93L  0C    6m  CC=11     ←0
  │ deploy                      90L  0C    7m  CC=4      ←6
  │ browser_router              88L  0C   10m  CC=9      ←0
  │ browser_playwright_worker    85L  0C    2m  CC=11     ←0
  │ desktop_operator.yaml       82L  0C    0m  CC=0.0    ←0
  │ operation_registry.yaml     82L  0C    0m  CC=0.0    ←0
  │ routes                      80L  2C    7m  CC=1      ←0
  │ browser_mock                77L  0C    8m  CC=3      ←0
  │ operation_registry.yaml     77L  0C    0m  CC=0.0    ←0
  │ routes                      73L  3C    6m  CC=1      ←0
  │ device_robot_operator.yaml    73L  0C    0m  CC=0.0    ←0
  │ view_builder                70L  0C    5m  CC=12     ←0
  │ routes                      69L  1C    8m  CC=1      ←0
  │ agent_card                  67L  0C    0m  CC=0.0    ←0
  │ browser_operator.yaml       65L  0C    0m  CC=0.0    ←0
  │ agent_card                  61L  0C    0m  CC=0.0    ←0
  │ operation_registry.yaml     59L  0C    0m  CC=0.0    ←0
  │ android_mock                56L  0C    4m  CC=4      ←0
  │ agent_card                  55L  0C    0m  CC=0.0    ←0
  │ policy                      54L  1C    2m  CC=3      ←2
  │ android_router              54L  0C    6m  CC=8      ←0
  │ input_gnome                 51L  0C    2m  CC=10     ←0
  │ agent_card                  50L  0C    0m  CC=0.0    ←0
  │ pcwin_router                49L  0C    5m  CC=8      ←0
  │ pcwin_uri                   47L  0C    4m  CC=7      ←2
  │ agent_card                  47L  0C    0m  CC=0.0    ←0
  │ agent_card                  42L  0C    0m  CC=0.0    ←0
  │ agent_card                  42L  0C    0m  CC=0.0    ←0
  │ agent_card                  41L  0C    0m  CC=0.0    ←0
  │ agent_card                  41L  0C    0m  CC=0.0    ←0
  │ agent_card                  41L  0C    0m  CC=0.0    ←0
  │ agent_card                  40L  0C    0m  CC=0.0    ←0
  │ pcwin_mock                  38L  0C    3m  CC=4      ←0
  │ agent_card                  38L  0C    0m  CC=0.0    ←0
  │ input_router                36L  0C    3m  CC=8      ←0
  │ screen_router               36L  0C    3m  CC=8      ←0
  │ operator_runtime            33L  0C    3m  CC=1      ←0
  │ agent_card                  31L  0C    0m  CC=0.0    ←0
  │ agent_card                  28L  0C    0m  CC=0.0    ←0
  │ android_uri                 26L  0C    2m  CC=10     ←2
  │ main                        21L  0C    0m  CC=0.0    ←0
  │ main                        20L  0C    0m  CC=0.0    ←0
  │ agent_card                  20L  0C    0m  CC=0.0    ←0
  │ main                        20L  0C    0m  CC=0.0    ←0
  │ main                        19L  0C    0m  CC=0.0    ←0
  │ main                        19L  0C    0m  CC=0.0    ←0
  │ main                        19L  0C    0m  CC=0.0    ←0
  │ main                        19L  0C    0m  CC=0.0    ←0
  │ main                        19L  0C    0m  CC=0.0    ←0
  │ main                        19L  0C    0m  CC=0.0    ←0
  │ main                        19L  0C    0m  CC=0.0    ←0
  │ main                        19L  0C    0m  CC=0.0    ←0
  │ main                        19L  0C    0m  CC=0.0    ←0
  │ paths                       15L  0C    1m  CC=3      ←1
  │ pyproject.toml              13L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              13L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              13L  0C    0m  CC=0.0    ←0
  │ assertion                   12L  0C    1m  CC=2      ←0
  │ input_mock                  12L  0C    1m  CC=2      ←0
  │ main                        12L  0C    0m  CC=0.0    ←0
  │ main                        12L  0C    0m  CC=0.0    ←0
  │ main                        12L  0C    0m  CC=0.0    ←0
  │ main                        11L  0C    0m  CC=0.0    ←0
  │ main                        11L  0C    0m  CC=0.0    ←0
  │ main                        11L  0C    0m  CC=0.0    ←0
  │ screen_mock                 10L  0C    1m  CC=1      ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   9L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ .generated.yaml              7L  0C    0m  CC=0.0    ←0
  │ main                         7L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     2L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  testenv/                        CC̄=2.3    ←in:0  →out:0
  │ mock_agent_server           57L  1C    3m  CC=5      ←0
  │ Dockerfile                  20L  0C    0m  CC=0.0    ←0
  │ docker-compose.ssh.yml      10L  0C    0m  CC=0.0    ←0
  │ entrypoint.sh                7L  0C    0m  CC=0.0    ←0
  │
  domains/                        CC̄=1.8    ←in:0  →out:0
  │ scenario_registry.yaml     235L  0C    0m  CC=0.0    ←0
  │ scenario_registry.yaml     153L  0C    0m  CC=0.0    ←0
  │ scenario_registry.yaml     120L  0C    0m  CC=0.0    ←0
  │ scenario_registry.yaml      89L  0C    0m  CC=0.0    ←0
  │ uri_tree.yaml               85L  0C    0m  CC=0.0    ←0
  │ operator_registry.yaml      81L  0C    0m  CC=0.0    ←0
  │ operator_registry.yaml      78L  0C    0m  CC=0.0    ←0
  │ domain.yaml                 67L  0C    0m  CC=0.0    ←0
  │ planner                     61L  0C    2m  CC=2      ←0
  │ domain.yaml                 61L  0C    0m  CC=0.0    ←0
  │ uri_tree.yaml               57L  0C    0m  CC=0.0    ←0
  │ domain.yaml                 55L  0C    0m  CC=0.0    ←0
  │ operator_registry.yaml      45L  0C    0m  CC=0.0    ←0
  │ weather_map.proto           41L  0C    0m  CC=0.0    ←0
  │ generate_weather_map        30L  0C    1m  CC=3      ←0
  │ resources.yaml              23L  0C    0m  CC=0.0    ←0
  │ generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html.proto    23L  0C    0m  CC=0.0    ←0
  │ uri_tree.yaml               16L  0C    0m  CC=0.0    ←0
  │ resources.yaml              12L  0C    0m  CC=0.0    ←0
  │ views.yaml                  11L  0C    0m  CC=0.0    ←0
  │ registry.fragment.yaml      10L  0C    0m  CC=0.0    ←0
  │ renderers.yaml              10L  0C    0m  CC=0.0    ←0
  │ domain.yaml                  9L  0C    0m  CC=0.0    ←0
  │ commands.yaml                8L  0C    0m  CC=0.0    ←0
  │ commands.yaml                8L  0C    0m  CC=0.0    ←0
  │ domain.yaml                  7L  0C    0m  CC=0.0    ←0
  │ views.yaml                   6L  0C    0m  CC=0.0    ←0
  │ run                          5L  0C    1m  CC=1      ←0
  │ renderers.yaml               5L  0C    0m  CC=0.0    ←0
  │ domain.yaml                  4L  0C    0m  CC=0.0    ←0
  │ registry.fragment.yaml       2L  0C    0m  CC=0.0    ←0
  │
  runtime_client/                 CC̄=1.7    ←in:0  →out:0
  │ client                       0L  1C    3m  CC=2      ←0
  │
  examples/                       CC̄=0.0    ←in:0  →out:0
  │ run.sh                     204L  0C    3m  CC=0.0    ←0
  │ run.sh                      93L  0C    1m  CC=0.0    ←23
  │ run.sh                      86L  0C    1m  CC=0.0    ←0
  │ run.sh                      85L  1C    2m  CC=0.0    ←0
  │ workflow_graph.yaml         82L  0C    0m  CC=0.0    ←0
  │ run.sh                      76L  0C    2m  CC=0.0    ←0
  │ task_graph.yaml             72L  0C    0m  CC=0.0    ←0
  │ task_graph.yaml             72L  0C    0m  CC=0.0    ←0
  │ office_chains.yaml          71L  0C    0m  CC=0.0    ←0
  │ task_plan.yaml              60L  0C    0m  CC=0.0    ←0
  │ run.sh                      54L  0C    0m  CC=0.0    ←0
  │ task_graph.yaml             48L  0C    0m  CC=0.0    ←0
  │ stt_whisper.uri.capability.yaml    46L  0C    0m  CC=0.0    ←0
  │ run.sh                      45L  0C    0m  CC=0.0    ←0
  │ stt_mock.uri.capability.yaml    43L  0C    0m  CC=0.0    ←0
  │ tts_mock.uri.capability.yaml    43L  0C    0m  CC=0.0    ←0
  │ run.sh                      41L  0C    0m  CC=0.0    ←0
  │ weather_forecast.uri.capability.yaml    40L  0C    0m  CC=0.0    ←0
  │ task.device.yaml            40L  0C    0m  CC=0.0    ←0
  │ run.sh                      39L  0C    0m  CC=0.0    ←0
  │ expanded.expected.uri.graph.yaml    38L  0C    0m  CC=0.0    ←0
  │ task.robot.yaml             38L  0C    0m  CC=0.0    ←0
  │ run.sh                      37L  0C    0m  CC=0.0    ←0
  │ voice_command.uri.capability.yaml    36L  0C    0m  CC=0.0    ←0
  │ task.android.yaml           35L  0C    0m  CC=0.0    ←0
  │ bank_token.android.yaml     35L  0C    0m  CC=0.0    ←0
  │ run.sh                      34L  0C    0m  CC=0.0    ←0
  │ run.sh                      34L  0C    0m  CC=0.0    ←0
  │ portal_report.browser.yaml    30L  0C    0m  CC=0.0    ←0
  │ task_graph.yaml             28L  0C    0m  CC=0.0    ←0
  │ bank_batch_transfer.yaml    28L  0C    0m  CC=0.0    ←0
  │ portal_zus_form.yaml        28L  0C    0m  CC=0.0    ←0
  │ supplier_report_monthly.yaml    28L  0C    0m  CC=0.0    ←0
  │ task.health.yaml            28L  0C    0m  CC=0.0    ←0
  │ task.health.yaml            28L  0C    0m  CC=0.0    ←0
  │ invoice_review.pcwin.yaml    28L  0C    0m  CC=0.0    ←0
  │ task.pcwin.yaml             26L  0C    0m  CC=0.0    ←0
  │ run.sh                      26L  0C    0m  CC=0.0    ←0
  │ run.sh                      25L  0C    0m  CC=0.0    ←0
  │ browser_open_mock.uri.capability.yaml    24L  0C    0m  CC=0.0    ←0
  │ task_graph.yaml             24L  0C    0m  CC=0.0    ←0
  │ www_landing_monitor_cron.uri.capability.yaml    23L  0C    0m  CC=0.0    ←0
  │ website_screenshot_schedule.uri.capability.yaml    21L  0C    0m  CC=0.0    ←0
  │ website_screenshot_schedule_dry_run.uri.capability.yaml    21L  0C    0m  CC=0.0    ←0
  │ branching.uri.flow.yaml     20L  0C    0m  CC=0.0    ←0
  │ run.sh                      20L  0C    0m  CC=0.0    ←0
  │ office_day_marta.uri.capability.yaml    19L  0C    0m  CC=0.0    ←0
  │ check_health_graph.uri.capability.yaml    19L  0C    0m  CC=0.0    ←0
  │ weather_flow_dry_run.uri.capability.yaml    19L  0C    0m  CC=0.0    ←0
  │ order_woocommerce_to_erp_dry_run.uri.capability.yaml    19L  0C    0m  CC=0.0    ←0
  │ bank_batch_transfer.uri.capability.yaml    19L  0C    0m  CC=0.0    ←0
  │ bank_batch_transfer_dry_run.uri.capability.yaml    19L  0C    0m  CC=0.0    ←0
  │ portal_zus_form.uri.capability.yaml    19L  0C    0m  CC=0.0    ←0
  │ invoices_batch_dry_run.uri.capability.yaml    19L  0C    0m  CC=0.0    ←0
  │ office_supplier_report.uri.capability.yaml    19L  0C    0m  CC=0.0    ←0
  │ order_woocommerce_to_erp.uri.capability.yaml    19L  0C    0m  CC=0.0    ←0
  │ portal_zus_form_dry_run.uri.capability.yaml    19L  0C    0m  CC=0.0    ←0
  │ run.sh                      19L  0C    0m  CC=0.0    ←0
  │ run.sh                      19L  0C    0m  CC=0.0    ←0
  │ incident_explain.uri.capability.yaml    17L  0C    0m  CC=0.0    ←0
  │ repair_diagnose.uri.capability.yaml    17L  0C    0m  CC=0.0    ←0
  │ process_view.uri.capability.yaml    17L  0C    0m  CC=0.0    ←0
  │ run.sh                      17L  0C    0m  CC=0.0    ←0
  │ run.sh                      14L  0C    0m  CC=0.0    ←0
  │ mock_echo.uri.capability.yaml    12L  0C    0m  CC=0.0    ←0
  │ capture_www.uri.flow.yaml    11L  0C    0m  CC=0.0    ←0
  │ run.sh                      10L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          10L  0C    0m  CC=0.0    ←0
  │ weather.uri.flow.yaml        9L  0C    0m  CC=0.0    ←0
  │ weather.uri.flow.yaml        9L  0C    0m  CC=0.0    ←0
  │ dashboard_open.uri.flow.yaml     9L  0C    0m  CC=0.0    ←0
  │ run.sh                       8L  0C    0m  CC=0.0    ←0
  │ run.sh                       8L  0C    0m  CC=0.0    ←0
  │ run.sh                       8L  0C    0m  CC=0.0    ←0
  │ run.sh                       7L  0C    0m  CC=0.0    ←0
  │ run.sh                       7L  0C    0m  CC=0.0    ←0
  │ run.sh                       7L  0C    0m  CC=0.0    ←0
  │ stt                          7L  0C    0m  CC=0.0    ←0
  │ voice_command                5L  0C    0m  CC=0.0    ←0
  │ tts                          5L  0C    0m  CC=0.0    ←0
  │ run.sh                       5L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
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
  │ Makefile                   233L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             214L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                99L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ manifest.yaml               20L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          18L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  13L  0C    0m  CC=0.0    ←0
  │ nlp2uri.yaml                 8L  0C    0m  CC=0.0    ←0
  │
  schemas/                        CC̄=0.0    ←in:0  →out:0
  │ contract_registry.schema.json   129L  0C    0m  CC=0.0    ←0
  │ uri_exchange.schema.json   128L  0C    0m  CC=0.0    ←0
  │ runtime_environments.schema.json   123L  0C    0m  CC=0.0    ←0
  │ agent_contract.schema.json    79L  0C    0m  CC=0.0    ←0
  │ evolution_proposal.schema.json    79L  0C    0m  CC=0.0    ←0
  │ uri_tree.schema.json        78L  0C    0m  CC=0.0    ←0
  │ ticket.schema.json          74L  0C    0m  CC=0.0    ←0
  │ incident.schema.json        74L  0C    0m  CC=0.0    ←0
  │ workflow_graph.schema.json    69L  0C    0m  CC=0.0    ←0
  │ runtime_state.schema.json    62L  0C    0m  CC=0.0    ←0
  │ resources.schema.json       56L  0C    0m  CC=0.0    ←0
  │ apply_plan.schema.json      55L  0C    0m  CC=0.0    ←0
  │ views.schema.json           54L  0C    0m  CC=0.0    ←0
  │ deployment_registry.schema.json    54L  0C    0m  CC=0.0    ←0
  │ apply_result.schema.json    51L  0C    0m  CC=0.0    ←0
  │ workflow_artifact.schema.json    49L  0C    0m  CC=0.0    ←0
  │ log_event.schema.json       47L  0C    0m  CC=0.0    ←0
  │ command_contract.schema.json    43L  0C    0m  CC=0.0    ←0
  │ repair_plan.schema.json     37L  0C    0m  CC=0.0    ←0
  │ renderer_contract.schema.json    35L  0C    0m  CC=0.0    ←0
  │ agent_readiness.schema.json    35L  0C    0m  CC=0.0    ←0
  │ config_base.schema.json     34L  0C    0m  CC=0.0    ←0
  │ uri_graph.schema.json       31L  0C    0m  CC=0.0    ←0
  │ artifact_base.schema.json    30L  0C    0m  CC=0.0    ←0
  │ uri_shell_context.schema.json    29L  0C    0m  CC=0.0    ←0
  │ domain_pack.schema.json     20L  0C    0m  CC=0.0    ←0
  │ cli_shortcuts.schema.json    14L  0C    0m  CC=0.0    ←0
  │
  knowledge/                      CC̄=0.0    ←in:0  →out:0
  │ health_timeout_after_dynamic_port.yaml    28L  0C    0m  CC=0.0    ←0
  │
  evolution/                      CC̄=0.0    ←in:0  →out:0
  │ add_invoices_agent.yaml      0L  0C    0m  CC=0.0    ←0
  │ add_orders_agent.yaml        0L  0C    0m  CC=0.0    ←0
  │
  deployments/                    CC̄=0.0    ←in:0  →out:0
  │ agent_deployments.yaml     253L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-api-smoke.testql.toon.yaml    35L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    14L  0C    0m  CC=0.0    ←0
  │
  config/                         CC̄=0.0    ←in:0  →out:0
  │ runtime_environments.yaml   163L  0C    0m  CC=0.0    ←0
  │ flow_defaults.uri.yaml     141L  0C    0m  CC=0.0    ←0
  │ operator_policy.uri.yaml    74L  0C    0m  CC=0.0    ←0
  │ llm.uri.yaml                63L  0C    0m  CC=0.0    ←0
  │ cli_shortcuts.uri.yaml      54L  0C    0m  CC=0.0    ←0
  │ docker.uri.yaml             32L  0C    0m  CC=0.0    ←0
  │ deployments.uri.yaml        25L  0C    0m  CC=0.0    ←0
  │ uri3.uri.yaml               24L  0C    0m  CC=0.0    ←0
  │ ssh.uri.yaml                21L  0C    0m  CC=0.0    ←0
  │ touri.uri.yaml              20L  0C    0m  CC=0.0    ←0
  │ local-dev.yaml              19L  0C    0m  CC=0.0    ←0
  │ runtime.uri.yaml            18L  0C    0m  CC=0.0    ←0
  │ operator_registry.uri.yaml    17L  0C    0m  CC=0.0    ←0
  │ extra_operator_registry.yaml    11L  0C    0m  CC=0.0    ←0
  │
  contracts/                      CC̄=0.0    ←in:0  →out:0
  │ views.yaml                  92L  0C    0m  CC=0.0    ←0
  │ resources.yaml              78L  0C    0m  CC=0.0    ←0
  │ operator.proto              62L  0C    0m  CC=0.0    ←0
  │ hypervisor_dashboard_agent.yaml    55L  0C    0m  CC=0.0    ←0
  │ remote_deploy_agent.yaml    53L  0C    0m  CC=0.0    ←0
  │ deploy.proto                51L  0C    0m  CC=0.0    ←0
  │ screenshot_analysis_agent.yaml    42L  0C    0m  CC=0.0    ←0
  │ dashboard.proto             39L  0C    0m  CC=0.0    ←0
  │ user.proto                  39L  0C    0m  CC=0.0    ←0
  │ user_agent.yaml             38L  0C    0m  CC=0.0    ←0
  │ desktop.proto               37L  0C    0m  CC=0.0    ←0
  │ schema_collab_agent.yaml    36L  0C    0m  CC=0.0    ←0
  │ gnome_programmer_agent.yaml    35L  0C    0m  CC=0.0    ←0
  │ invoices.proto              32L  0C    0m  CC=0.0    ←0
  │ codex_uri_smoke_agent.yaml    30L  0C    0m  CC=0.0    ←0
  │ codex_nl_plan_agent.yaml    30L  0C    0m  CC=0.0    ←0
  │ screenshots.proto           29L  0C    0m  CC=0.0    ←0
  │ codex_nl_smoke_agent.yaml    29L  0C    0m  CC=0.0    ←0
  │ standards.yaml              28L  0C    0m  CC=0.0    ←0
  │ registry.yaml               28L  0C    0m  CC=0.0    ←0
  │ invoices_agent.yaml         28L  0C    0m  CC=0.0    ←0
  │ codex_uri_smoke.proto       24L  0C    0m  CC=0.0    ←0
  │ policy.yaml                 24L  0C    0m  CC=0.0    ←0
  │ weather_map_agent.yaml      22L  0C    0m  CC=0.0    ←0
  │ generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent.yaml    15L  0C    0m  CC=0.0    ←0
  │
  integration/                    CC̄=0.0    ←in:0  →out:0
  │ Makefile.optional.snippet.mk    11L  0C    0m  CC=0.0    ←0
  │ pyproject.optional.snippet.toml    10L  0C    0m  CC=0.0    ←0
  │ Makefile.optional.snippet.mk     9L  0C    0m  CC=0.0    ←0
  │ pyproject.optional.snippet.toml     5L  0C    0m  CC=0.0    ←0
  │
  docs/                           CC̄=0.0    ←in:0  →out:0
  │ PACKAGE_BOUNDARIES.yaml     67L  0C    0m  CC=0.0    ←0
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
     generator/validate.py                     0L
     hypervisor/__init__.py                    0L
     hypervisor/_version.py                    0L
     hypervisor/compatibility/checker.py       0L
     hypervisor/config/__init__.py             0L
     hypervisor/config/env.py                  0L
     hypervisor/config/models.py               0L
     hypervisor/contract_registry/loader.py    0L
     hypervisor/contract_registry/models.py    0L
     hypervisor/contract_registry/registry_exporter.py  0L
     hypervisor/contract_registry/schema_validator.py  0L
     hypervisor/deployment_registry/writer.py  0L
     hypervisor/domain_pack/__init__.py        0L
     hypervisor/evolution/models.py            0L
     hypervisor/policy_gate/gate.py            0L
     hypervisor/uri2llm/__init__.py            0L
     hypervisor/uri2llm/env_resolver.py        0L
     hypervisor/uri2llm/function_resolver.py   0L
     hypervisor/uri2llm/llm_resolver.py        0L
     hypervisor/uri2llm/protocol_resolver.py   0L
     hypervisor/uri2llm/pypi_resolver.py       0L
     hypervisor/uri2llm/router.py              0L
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
     packages/hypervisor-dashboard-agent/hypervisor_dashboard_agent/agent_card.py  0L
     packages/hypervisor-dashboard-agent/hypervisor_dashboard_agent/main.py  0L
     packages/hypervisor-dashboard-agent/hypervisor_dashboard_agent/models.py  0L
     packages/hypervisor-dashboard-agent/hypervisor_dashboard_agent/monitor_webhook.py  0L
     packages/hypervisor-dashboard-agent/hypervisor_dashboard_agent/plan_runner.py  0L
     packages/hypervisor-dashboard-agent/hypervisor_dashboard_agent/presentation.py  0L
     packages/hypervisor-dashboard-agent/hypervisor_dashboard_agent/static/dashboard.js  0L
     packages/hypervisor-dashboard-agent/pyproject.toml  0L
     runtime_client/client.py                  0L

COUPLING:
                                        packages.resource-agent-hypervisor        examples.38_autonomous_agents                     agents.generated                        agents.system                          scripts.www                            generator      packages.resource-agent-factory                     scripts.examples         hypervisor.contract_registry                           meta_agent                        agents.custom  packages.hypervisor-dashboard-agent                     scripts.tellmesh                    packages.uri2flow                    meta_agent.repair
   packages.resource-agent-hypervisor                                   ──                                   24                                  ←36                                  ←18                                                                         7                                    5                                   ←7                                   11                                    3                                    3                                                                                                                                                   2  hub
        examples.38_autonomous_agents                                  ←24                                   ──                                                                                                            ←21                                   ←4                                   ←6                                   ←9                                                                                                                                                                                      ←11                                   ←3                                       hub
                     agents.generated                                   36                                                                        ──                                                                                                                                                                                                                                                                                                                                                                                                                                                              !! fan-out
                        agents.system                                   18                                                                                                             ──                                                                                                                                                                                                                                                                                                       4                                                                                                                 hub
                          scripts.www                                                                        21                                                                                                             ──                                                                                                                                                                                                                                                                                                                                                                                    !! fan-out
                            generator                                   ←7                                    4                                                                                                                                                  ──                                   ←5                                                                                                             ←1                                                                                                                                                                                       ←3  hub
      packages.resource-agent-factory                                    3                                    6                                                                                                                                                   5                                   ──                                                                                                             ←1                                                                                                                                                                                           hub
                     scripts.examples                                    7                                    9                                                                                                                                                                                                                            ──                                    1                                    1                                                                                                                                                   1                                       !! fan-out
         hypervisor.contract_registry                                    2                                                                                                                                                                                                                                                                 ←1                                   ──                                                                                                                                                                                                                                hub
                           meta_agent                                    5                                                                                                                                                                                        1                                    1                                   ←1                                                                        ──                                                                                                                                                  ←4                                    1  hub
                        agents.custom                                   10                                                                                                                                                                                                                                                                                                                                                                                ──                                                                                                                                                      !! fan-out
  packages.hypervisor-dashboard-agent                                                                                                                                                   7                                                                                                                                                                                                                                                                                                      ──                                                                                                                 !! fan-out
                     scripts.tellmesh                                                                        11                                                                                                                                                                                                                                                                                                                                                                                                                     ──                                                                            !! fan-out
                    packages.uri2flow                                                                         3                                                                                                                                                                                                                            ←1                                                                         4                                                                                                                                                  ──                                     
                    meta_agent.repair                                   ←2                                                                                                                                                                                        3                                                                                                                                                   1                                                                                                                                                                                       ──
  CYCLES: none
  HUB: packages.resource-agent-hypervisor/ (fan-in=84)
  HUB: examples.38_autonomous_agents/ (fan-in=85)
  HUB: meta_agent/ (fan-in=9)
  HUB: packages.resource-agent-factory/ (fan-in=6)
  HUB: hypervisor.contract_registry/ (fan-in=15)
  HUB: generator/ (fan-in=16)
  HUB: www.assets/ (fan-in=5)
  HUB: agents.system/ (fan-in=8)
  SMELL: packages.resource-agent-hypervisor/ fan-out=64 → split needed
  SMELL: scripts.www/ fan-out=21 → split needed
  SMELL: scripts.examples/ fan-out=19 → split needed
  SMELL: scripts.tellmesh/ fan-out=11 → split needed
  SMELL: agents.custom/ fan-out=10 → split needed
  SMELL: meta_agent/ fan-out=8 → split needed
  SMELL: packages.resource-agent-factory/ fan-out=14 → split needed
  SMELL: agents.system/ fan-out=23 → split needed
  SMELL: agents.generated/ fan-out=36 → split needed
  SMELL: packages.hypervisor-dashboard-agent/ fan-out=8 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 54 groups | 336f 25859L | 2026-06-15

SUMMARY:
  files_scanned: 336
  total_lines:   25859
  dup_groups:    54
  dup_fragments: 233
  saved_lines:   1431
  scan_ms:       3341

HOTSPOTS[7] (files with most duplication):
  agents/generated/remote_deploy_agent/routes.py  dup=101L  groups=8  frags=12  (0.4%)
  agents/generated/hypervisor_dashboard_agent/routes.py  dup=99L  groups=9  frags=13  (0.4%)
  agents/generated/user_agent/routes.py  dup=91L  groups=9  frags=11  (0.4%)
  agents/generated/gnome_programmer_agent/routes.py  dup=89L  groups=8  frags=10  (0.3%)
  agents/generated/screenshot_analysis_agent/routes.py  dup=89L  groups=8  frags=10  (0.3%)
  agents/generated/schema_collab_agent/routes.py  dup=86L  groups=9  frags=11  (0.3%)
  agents/generated/invoices_agent/routes.py  dup=85L  groups=9  frags=10  (0.3%)

DUPLICATES[54] (ranked by impact):
  [f69a15dae6ad41f1] !! EXAC  _read_uri  L=17 N=12 saved=187 sim=1.00
      agents/generated/codex_nl_plan_agent/routes.py:109-125  (_read_uri)
      agents/generated/codex_nl_smoke_agent/routes.py:109-125  (_read_uri)
      agents/generated/codex_uri_smoke_agent/routes.py:109-125  (_read_uri)
      agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py:101-117  (_read_uri)
      agents/generated/gnome_programmer_agent/routes.py:115-131  (_read_uri)
      agents/generated/hypervisor_dashboard_agent/routes.py:128-144  (_read_uri)
      agents/generated/invoices_agent/routes.py:111-127  (_read_uri)
      agents/generated/remote_deploy_agent/routes.py:129-145  (_read_uri)
      agents/generated/schema_collab_agent/routes.py:113-129  (_read_uri)
      agents/generated/screenshot_analysis_agent/routes.py:115-131  (_read_uri)
      agents/generated/user_agent/routes.py:118-134  (_read_uri)
      agents/generated/weather_map_agent/routes.py:107-123  (_read_uri)
  [4dd812afaadbfdc8] !! EXAC  dispatch_command  L=13 N=12 saved=143 sim=1.00
      agents/generated/codex_nl_plan_agent/routes.py:66-78  (dispatch_command)
      agents/generated/codex_nl_smoke_agent/routes.py:66-78  (dispatch_command)
      agents/generated/codex_uri_smoke_agent/routes.py:66-78  (dispatch_command)
      agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py:66-78  (dispatch_command)
      agents/generated/gnome_programmer_agent/routes.py:66-78  (dispatch_command)
      agents/generated/hypervisor_dashboard_agent/routes.py:66-78  (dispatch_command)
      agents/generated/invoices_agent/routes.py:66-78  (dispatch_command)
      agents/generated/remote_deploy_agent/routes.py:66-78  (dispatch_command)
      agents/generated/schema_collab_agent/routes.py:66-78  (dispatch_command)
      agents/generated/screenshot_analysis_agent/routes.py:66-78  (dispatch_command)
      agents/generated/user_agent/routes.py:66-78  (dispatch_command)
      agents/generated/weather_map_agent/routes.py:66-78  (dispatch_command)
  [0697a8f50b5ddf36] !! EXAC  _dispatch_command  L=11 N=12 saved=121 sim=1.00
      agents/generated/codex_nl_plan_agent/routes.py:136-146  (_dispatch_command)
      agents/generated/codex_nl_smoke_agent/routes.py:136-146  (_dispatch_command)
      agents/generated/codex_uri_smoke_agent/routes.py:136-146  (_dispatch_command)
      agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py:128-138  (_dispatch_command)
      agents/generated/gnome_programmer_agent/routes.py:142-152  (_dispatch_command)
      agents/generated/hypervisor_dashboard_agent/routes.py:155-165  (_dispatch_command)
      agents/generated/invoices_agent/routes.py:138-148  (_dispatch_command)
      agents/generated/remote_deploy_agent/routes.py:156-166  (_dispatch_command)
      agents/generated/schema_collab_agent/routes.py:140-150  (_dispatch_command)
      agents/generated/screenshot_analysis_agent/routes.py:142-152  (_dispatch_command)
      agents/generated/user_agent/routes.py:145-155  (_dispatch_command)
      agents/generated/weather_map_agent/routes.py:134-144  (_dispatch_command)
  [84f9b4f57c2777f6] !! EXAC  _uri_allowed  L=8 N=14 saved=104 sim=1.00
      agents/generated/codex_nl_plan_agent/routes.py:99-106  (_uri_allowed)
      agents/generated/codex_nl_smoke_agent/routes.py:99-106  (_uri_allowed)
      agents/generated/codex_uri_smoke_agent/routes.py:99-106  (_uri_allowed)
      agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py:91-98  (_uri_allowed)
      agents/generated/gnome_programmer_agent/routes.py:105-112  (_uri_allowed)
      agents/generated/hypervisor_dashboard_agent/routes.py:118-125  (_uri_allowed)
      agents/generated/invoices_agent/routes.py:101-108  (_uri_allowed)
      agents/generated/remote_deploy_agent/routes.py:119-126  (_uri_allowed)
      agents/generated/schema_collab_agent/routes.py:103-110  (_uri_allowed)
      agents/generated/screenshot_analysis_agent/routes.py:105-112  (_uri_allowed)
      agents/generated/user_agent/routes.py:108-115  (_uri_allowed)
      agents/generated/weather_map_agent/routes.py:97-104  (_uri_allowed)
      packages/resource-agent-factory/agents/generated/orders_agent/routes.py:82-89  (_uri_allowed)
      packages/resource-agent-factory/agents/generated/user_agent/routes.py:88-95  (_uri_allowed)
  [a5eb0bba2cb3a4bd] ! EXAC  read_resource  L=9 N=12 saved=99 sim=1.00
      agents/generated/codex_nl_plan_agent/routes.py:54-62  (read_resource)
      agents/generated/codex_nl_smoke_agent/routes.py:54-62  (read_resource)
      agents/generated/codex_uri_smoke_agent/routes.py:54-62  (read_resource)
      agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py:54-62  (read_resource)
      agents/generated/gnome_programmer_agent/routes.py:54-62  (read_resource)
      agents/generated/hypervisor_dashboard_agent/routes.py:54-62  (read_resource)
      agents/generated/invoices_agent/routes.py:54-62  (read_resource)
      agents/generated/remote_deploy_agent/routes.py:54-62  (read_resource)
      agents/generated/schema_collab_agent/routes.py:54-62  (read_resource)
      agents/generated/screenshot_analysis_agent/routes.py:54-62  (read_resource)
      agents/generated/user_agent/routes.py:54-62  (read_resource)
      agents/generated/weather_map_agent/routes.py:54-62  (read_resource)
  [531e7609705ee56b] ! STRU  health  L=7 N=14 saved=91 sim=1.00
      agents/generated/codex_nl_plan_agent/routes.py:29-35  (health)
      agents/generated/codex_nl_smoke_agent/routes.py:29-35  (health)
      agents/generated/codex_uri_smoke_agent/routes.py:29-35  (health)
      agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py:29-35  (health)
      agents/generated/gnome_programmer_agent/routes.py:29-35  (health)
      agents/generated/hypervisor_dashboard_agent/routes.py:29-35  (health)
      agents/generated/invoices_agent/routes.py:29-35  (health)
      agents/generated/remote_deploy_agent/routes.py:29-35  (health)
      agents/generated/schema_collab_agent/routes.py:29-35  (health)
      agents/generated/screenshot_analysis_agent/routes.py:29-35  (health)
      agents/generated/user_agent/routes.py:29-35  (health)
      agents/generated/weather_map_agent/routes.py:29-35  (health)
      packages/resource-agent-factory/agents/generated/orders_agent/routes.py:29-35  (health)
      packages/resource-agent-factory/agents/generated/user_agent/routes.py:29-35  (health)
  [49d1d03e6ce392a1] ! STRU  weather_proto  L=43 N=3 saved=86 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py:36-78  (weather_proto)
      packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py:81-112  (weather_handler)
      packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py:115-121  (generic_handler)
  [30cfb10c039a4179] ! STRU  skill_run_cron_monitor  L=6 N=15 saved=84 sim=1.00
      agents/generated/codex_nl_plan_agent/routes.py:91-96  (skill_run_cron_monitor)
      agents/generated/gnome_programmer_agent/routes.py:83-88  (skill_observe_desktop)
      agents/generated/gnome_programmer_agent/routes.py:90-95  (skill_type_on_desktop)
      agents/generated/gnome_programmer_agent/routes.py:97-102  (skill_programmer_session)
      agents/generated/hypervisor_dashboard_agent/routes.py:103-108  (skill_repair_action)
      agents/generated/hypervisor_dashboard_agent/routes.py:110-115  (skill_uri_call)
      agents/generated/remote_deploy_agent/routes.py:83-88  (skill_plan_remote_deploy)
      agents/generated/remote_deploy_agent/routes.py:90-95  (skill_apply_remote_deploy)
      agents/generated/remote_deploy_agent/routes.py:97-102  (skill_verify_remote_agent)
      agents/generated/remote_deploy_agent/routes.py:104-109  (skill_start_remote_agent)
      agents/generated/remote_deploy_agent/routes.py:111-116  (skill_deploy_verify_start)
      agents/generated/schema_collab_agent/routes.py:95-100  (skill_run_cron_monitor)
      agents/generated/screenshot_analysis_agent/routes.py:83-88  (skill_analyze_screenshot)
      agents/generated/screenshot_analysis_agent/routes.py:90-95  (skill_capture_and_analyze)
      agents/generated/screenshot_analysis_agent/routes.py:97-102  (skill_scheduled_capture_analysis)
  [536dcae9aec4dd09] ! EXAC  _command_uri  L=6 N=12 saved=66 sim=1.00
      agents/generated/codex_nl_plan_agent/routes.py:128-133  (_command_uri)
      agents/generated/codex_nl_smoke_agent/routes.py:128-133  (_command_uri)
      agents/generated/codex_uri_smoke_agent/routes.py:128-133  (_command_uri)
      agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py:120-125  (_command_uri)
      agents/generated/gnome_programmer_agent/routes.py:134-139  (_command_uri)
      agents/generated/hypervisor_dashboard_agent/routes.py:147-152  (_command_uri)
      agents/generated/invoices_agent/routes.py:130-135  (_command_uri)
      agents/generated/remote_deploy_agent/routes.py:148-153  (_command_uri)
      agents/generated/schema_collab_agent/routes.py:132-137  (_command_uri)
      agents/generated/screenshot_analysis_agent/routes.py:134-139  (_command_uri)
      agents/generated/user_agent/routes.py:137-142  (_command_uri)
      agents/generated/weather_map_agent/routes.py:126-131  (_command_uri)
  [73f98c686f2885f8] ! STRU  skill_run_cron_monitor  L=6 N=7 saved=36 sim=1.00
      agents/generated/codex_nl_smoke_agent/routes.py:91-96  (skill_run_cron_monitor)
      agents/generated/codex_uri_smoke_agent/routes.py:91-96  (skill_run_cron_monitor)
      agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py:83-88  (skill_run)
      agents/generated/invoices_agent/routes.py:93-98  (skill_create_invoice)
      agents/generated/user_agent/routes.py:93-98  (skill_create_user)
      agents/generated/user_agent/routes.py:100-105  (skill_assign_user_role)
      agents/generated/weather_map_agent/routes.py:89-94  (skill_generate_weather_map)
  [b9f91dfd662b3f21]   STRU  skill_process_view  L=4 N=8 saved=28 sim=1.00
      agents/generated/hypervisor_dashboard_agent/routes.py:82-85  (skill_process_view)
      agents/generated/hypervisor_dashboard_agent/routes.py:87-90  (skill_workflow_timeline)
      agents/generated/hypervisor_dashboard_agent/routes.py:92-95  (skill_incident_explain)
      agents/generated/hypervisor_dashboard_agent/routes.py:97-100  (skill_repair_diagnose)
      agents/generated/invoices_agent/routes.py:82-85  (skill_read_invoice)
      agents/generated/invoices_agent/routes.py:87-90  (skill_read_invoice_events)
      agents/generated/user_agent/routes.py:82-85  (skill_read_user)
      agents/generated/user_agent/routes.py:87-90  (skill_read_user_roles)
  [c4637a2c18d6f5fb]   STRU  skill_read_markpact_source  L=3 N=9 saved=24 sim=1.00
      agents/generated/codex_nl_plan_agent/routes.py:82-84  (skill_read_markpact_source)
      agents/generated/codex_nl_plan_agent/routes.py:86-88  (skill_read_device_status)
      agents/generated/codex_nl_smoke_agent/routes.py:82-84  (skill_read_markpact_source)
      agents/generated/codex_nl_smoke_agent/routes.py:86-88  (skill_read_device_status)
      agents/generated/codex_uri_smoke_agent/routes.py:82-84  (skill_read_markpact_source)
      agents/generated/codex_uri_smoke_agent/routes.py:86-88  (skill_read_device_status)
      agents/generated/schema_collab_agent/routes.py:82-84  (skill_read_markpact_source)
      agents/generated/schema_collab_agent/routes.py:86-88  (skill_read_device_status)
      agents/generated/schema_collab_agent/routes.py:90-92  (skill_read_robot_state)
  [24079059ab354988]   EXAC  to_dict  L=11 N=3 saved=22 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/models.py:72-82  (to_dict)
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/models.py:71-81  (to_dict)
      packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py:24-34  (to_dict)
  [70e836b983bb39c1]   STRU  _playwright_ready  L=6 N=4 saved=18 sim=1.00
      agents/operators/browser_operator/adapters/browser_router.py:12-17  (_playwright_ready)
      agents/operators/desktop_operator/adapters/input_router.py:12-17  (_gnome_ready)
      agents/operators/desktop_operator/adapters/pcwin_router.py:12-17  (_uia_ready)
      agents/operators/desktop_operator/adapters/screen_router.py:12-17  (_gnome_ready)
  [d95815c02da96534]   EXAC  list_agent_deployments  L=15 N=2 saved=15 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py:53-67  (list_agent_deployments)
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/uri_client.py:30-44  (list_agent_deployments)
  [0d82fb96924f12d3]   STRU  _read_yaml  L=5 N=4 saved=15 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/agent_describe.py:300-304  (_read_yaml)
      packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py:17-21  (_read_yaml)
      packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py:84-88  (_read_yaml)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/aliases.py:10-14  (_read_yaml)
  [f56d9d07f4873f75]   STRU  _port_from_http_uri  L=5 N=4 saved=15 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py:23-27  (_port_from_http_uri)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py:28-32  (_port_from_uri)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py:54-58  (_port_from_uri)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_utils.py:34-38  (port_from_http_uri)
  [6435ce372a9eb625]   STRU  _uri_path_parts  L=7 N=3 saved=14 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/presentation.py:11-17  (_uri_path_parts)
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/uri_client.py:21-27  (_uri_path_parts)
      packages/resource-agent-hypervisor/hypervisor/routing/system_request.py:21-27  (uri_path_parts)
  [70c693fa623a6ad1]   EXAC  _task_context  L=3 N=5 saved=12 sim=1.00
      agents/operators/desktop_operator/adapters/android_adb.py:16-18  (_task_context)
      agents/operators/desktop_operator/adapters/android_mock.py:10-12  (_task_context)
      agents/operators/desktop_operator/adapters/pcwin_mock.py:10-12  (_task_context)
      agents/operators/desktop_operator/adapters/pcwin_uia.py:11-13  (_task_context)
      agents/operators/desktop_operator/adapters/screen_gnome.py:19-21  (_task_context)
  [8db5ce08e3f8bbcc]   EXAC  preview_action  L=12 N=2 saved=12 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/policy.py:43-54  (preview_action)
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/policy.py:41-52  (preview_action)
  [ce0bff36326d3cc1]   EXAC  _lifecycle_payload  L=4 N=4 saved=12 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py:39-42  (_lifecycle_payload)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle_status.py:14-17  (_lifecycle_payload)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py:27-30  (_lifecycle_payload)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py:19-22  (_lifecycle_payload)
  [277a3a34943f29ee]   STRU  python_file_header  L=6 N=3 saved=12 sim=1.00
      packages/resource-agent-factory/generator/header.py:21-26  (python_file_header)
      packages/resource-agent-factory/generator/header.py:29-34  (dockerfile_header)
      packages/resource-agent-factory/generator/header.py:37-42  (markdown_generated_banner)
  [3849203ed605ae1c]   STRU  _normalize_view_uri  L=11 N=2 saved=11 sim=1.00
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/uri_client.py:74-84  (_normalize_view_uri)
      packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py:52-62  (normalize_view_uri)
  [949c009dbb7bdf18]   STRU  port_from_http_uri  L=11 N=2 saved=11 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py:8-18  (port_from_http_uri)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py:25-35  (_port_from_http_uri)
  [84ff7d10372199a5]   STRU  resolve_adapter_mode  L=10 N=2 saved=10 sim=1.00
      agents/operators/desktop_operator/adapters/android_router.py:20-29  (resolve_adapter_mode)
      agents/operators/desktop_operator/adapters/input_router.py:20-29  (resolve_adapter_mode)
  [6086724a6eee5fd0]   STRU  _health_uri  L=5 N=3 saved=10 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py:52-56  (_health_uri)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py:66-70  (_command)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py:44-48  (_state_health_uri)
  [f8afc253eee4c414]   STRU  load_planfile_strategy  L=5 N=3 saved=10 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/integrations/planfile/ticket_mapper.py:50-54  (load_planfile_strategy)
      packages/resource-agent-hypervisor/hypervisor/repair/registry.py:22-26  (load_repair_case)
      packages/resource-agent-hypervisor/hypervisor/repair/validator.py:47-51  (read_yaml)
  [4bfbdb9093f84d8e]   STRU  skill_run_programmer_session  L=9 N=2 saved=9 sim=1.00
      agents/custom/gnome_programmer_agent/routes.py:65-73  (skill_run_programmer_session)
      agents/custom/screenshot_analysis_agent/routes.py:63-71  (skill_capture_and_analyze)
  [244e959beba3f97f]   STRU  _chat_request  L=9 N=2 saved=9 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py:197-205  (_chat_request)
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py:212-220  (_nl_request)
  [9d4dbbdcebf8dd41]   STRU  skill_read_order  L=3 N=4 saved=9 sim=1.00
      packages/resource-agent-factory/agents/generated/orders_agent/routes.py:70-72  (skill_read_order)
      packages/resource-agent-factory/agents/generated/orders_agent/routes.py:76-78  (skill_read_order_events)
      packages/resource-agent-factory/agents/generated/user_agent/routes.py:70-72  (skill_read_user)
      packages/resource-agent-factory/agents/generated/user_agent/routes.py:76-78  (skill_read_user_roles)
  [b87a5cae79cf60a4]   STRU  _local_health_uri  L=9 N=2 saved=9 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py:17-25  (_local_health_uri)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py:28-36  (_local_card_uri)
  [a3e37992ed9f572c]   STRU  validate_incident_dict  L=4 N=3 saved=8 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/repair/validator.py:21-24  (validate_incident_dict)
      packages/resource-agent-hypervisor/hypervisor/repair/validator.py:27-30  (validate_repair_plan_dict)
      packages/resource-agent-hypervisor/hypervisor/repair/validator.py:37-40  (validate_runtime_state_dict)
  [77e4969316a95224]   EXAC  to_dict  L=7 N=2 saved=7 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/models.py:14-20  (to_dict)
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/models.py:14-20  (to_dict)
  [7f5f67ab17f9683e]   EXAC  health  L=7 N=2 saved=7 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py:92-98  (health)
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/routes.py:28-34  (health)
  [8d177ac779710f41]   EXAC  ui_agents  L=7 N=2 saved=7 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py:122-128  (ui_agents)
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/routes.py:58-64  (ui_agents)
  [4e98482ed3705241]   EXAC  ui_agent_detail  L=7 N=2 saved=7 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py:132-138  (ui_agent_detail)
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/routes.py:68-74  (ui_agent_detail)
  [0e9dc2bdedc9fb73]   STRU  window_id_from_payload  L=7 N=2 saved=7 sim=1.00
      agents/operators/desktop_operator/adapters/pcwin_uri.py:32-38  (window_id_from_payload)
      agents/operators/desktop_operator/adapters/pcwin_uri.py:41-47  (automation_id_from_payload)
  [fc568deda0d56dd5]   EXAC  api_process_view  L=6 N=2 saved=6 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py:142-147  (api_process_view)
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/routes.py:78-83  (api_process_view)
  [9b56e35291cb990e]   EXAC  _import_markdown  L=6 N=2 saved=6 sim=1.00
      scripts/www/build_examples_docs.py:27-32  (_import_markdown)
      scripts/www/md_html.py:10-15  (_import_markdown)
  [99b6795376df94a2]   STRU  skill_start_remote_agent  L=6 N=2 saved=6 sim=1.00
      agents/custom/remote_deploy_agent/routes.py:55-60  (skill_start_remote_agent)
      agents/custom/remote_deploy_agent/routes.py:64-69  (skill_deploy_verify_start)
  [fdc7786ef049b370]   STRU  deploy_agent_cmd  L=6 N=2 saved=6 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/cli.py:504-509  (deploy_agent_cmd)
      packages/resource-agent-hypervisor/hypervisor/cli.py:522-529  (docker_cmd)
  [6955871a61c45e26]   STRU  _process_log_path  L=6 N=2 saved=6 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py:89-94  (_process_log_path)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py:97-102  (_process_log_uri)
  [a781900015fb2acd]   STRU  _incident_text  L=6 N=2 saved=6 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/repair/classifier.py:82-87  (_incident_text)
      packages/resource-agent-hypervisor/hypervisor/repair/classifier.py:90-95  (_warning_text)
  [c992a6059d580163]   EXAC  read_resource  L=5 N=2 saved=5 sim=1.00
      packages/resource-agent-factory/agents/generated/orders_agent/routes.py:54-58  (read_resource)
      packages/resource-agent-factory/agents/generated/user_agent/routes.py:54-58  (read_resource)
  [ce214caf504fbdb7]   EXAC  dispatch_command  L=5 N=2 saved=5 sim=1.00
      packages/resource-agent-factory/agents/generated/orders_agent/routes.py:62-66  (dispatch_command)
      packages/resource-agent-factory/agents/generated/user_agent/routes.py:62-66  (dispatch_command)
  [0ae5aa0932820a68]   STRU  playwright_import_error  L=5 N=2 saved=5 sim=1.00
      agents/operators/browser_operator/adapters/browser_playwright.py:34-38  (playwright_import_error)
      agents/operators/browser_operator/adapters/browser_playwright.py:41-45  (playwright_browsers_error)
  [2ea0b96f1eefaff8]   STRU  type_text  L=5 N=2 saved=5 sim=1.00
      agents/operators/desktop_operator/adapters/input_router.py:32-36  (type_text)
      agents/operators/desktop_operator/adapters/screen_router.py:32-36  (observe)
  [e9e2e5c84c119f1f]   STRU  _select_dashboard_uri_handler  L=5 N=2 saved=5 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py:272-276  (_select_dashboard_uri_handler)
      packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py:142-148  (_select_hypervisor_system_handler)
  [2ffd9c9c609cf61a]   STRU  port_from_command  L=5 N=2 saved=5 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py:21-25  (port_from_command)
      packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py:38-42  (_port_from_command)
  [3208596eddff8642]   STRU  root  L=4 N=2 saved=4 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py:78-81  (root)
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py:85-88  (chat_page_redirect)
  [be433a0e49bca3ee]   STRU  _html_request  L=4 N=2 saved=4 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py:78-81  (_html_request)
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py:84-87  (_markdown_request)
  [060fe645d32f78c5]   STRU  run_build_command  L=4 N=2 saved=4 sim=1.00
      packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py:33-36  (run_build_command)
      packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py:39-42  (run_export_md_command)
  [a77a54d6bf8c1257]   EXAC  render_process_html  L=3 N=2 saved=3 sim=1.00
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/view_builder.py:53-55  (render_process_html)
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/view_builder.py:79-81  (render_process_html)
  [541632e2c705e228]   EXAC  _human_title  L=3 N=2 saved=3 sim=1.00
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/view_builder.py:19-21  (_human_title)
      packages/resource-agent-hypervisor/hypervisor/routing/views/process.py:11-13  (_human_title)

REFACTOR[54] (ranked by priority):
  [1] ○ extract_function   → agents/generated/utils/_read_uri.py
      WHY: 12 occurrences of 17-line block across 12 files — saves 187 lines
      FILES: agents/generated/codex_nl_plan_agent/routes.py, agents/generated/codex_nl_smoke_agent/routes.py, agents/generated/codex_uri_smoke_agent/routes.py, agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py, agents/generated/gnome_programmer_agent/routes.py +7 more
  [2] ○ extract_function   → agents/generated/utils/dispatch_command.py
      WHY: 12 occurrences of 13-line block across 12 files — saves 143 lines
      FILES: agents/generated/codex_nl_plan_agent/routes.py, agents/generated/codex_nl_smoke_agent/routes.py, agents/generated/codex_uri_smoke_agent/routes.py, agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py, agents/generated/gnome_programmer_agent/routes.py +7 more
  [3] ○ extract_function   → agents/generated/utils/_dispatch_command.py
      WHY: 12 occurrences of 11-line block across 12 files — saves 121 lines
      FILES: agents/generated/codex_nl_plan_agent/routes.py, agents/generated/codex_nl_smoke_agent/routes.py, agents/generated/codex_uri_smoke_agent/routes.py, agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py, agents/generated/gnome_programmer_agent/routes.py +7 more
  [4] ○ extract_function   → utils/_uri_allowed.py
      WHY: 14 occurrences of 8-line block across 14 files — saves 104 lines
      FILES: agents/generated/codex_nl_plan_agent/routes.py, agents/generated/codex_nl_smoke_agent/routes.py, agents/generated/codex_uri_smoke_agent/routes.py, agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py, agents/generated/gnome_programmer_agent/routes.py +9 more
  [5] ○ extract_function   → agents/generated/utils/read_resource.py
      WHY: 12 occurrences of 9-line block across 12 files — saves 99 lines
      FILES: agents/generated/codex_nl_plan_agent/routes.py, agents/generated/codex_nl_smoke_agent/routes.py, agents/generated/codex_uri_smoke_agent/routes.py, agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py, agents/generated/gnome_programmer_agent/routes.py +7 more
  [6] ○ extract_function   → utils/health.py
      WHY: 14 occurrences of 7-line block across 14 files — saves 91 lines
      FILES: agents/generated/codex_nl_plan_agent/routes.py, agents/generated/codex_nl_smoke_agent/routes.py, agents/generated/codex_uri_smoke_agent/routes.py, agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py, agents/generated/gnome_programmer_agent/routes.py +9 more
  [7] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/domain_pack/utils/weather_proto.py
      WHY: 3 occurrences of 43-line block across 1 files — saves 86 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/domain_pack/templates.py
  [8] ○ extract_function   → agents/generated/utils/skill_run_cron_monitor.py
      WHY: 15 occurrences of 6-line block across 6 files — saves 84 lines
      FILES: agents/generated/codex_nl_plan_agent/routes.py, agents/generated/gnome_programmer_agent/routes.py, agents/generated/hypervisor_dashboard_agent/routes.py, agents/generated/remote_deploy_agent/routes.py, agents/generated/schema_collab_agent/routes.py +1 more
  [9] ○ extract_function   → agents/generated/utils/_command_uri.py
      WHY: 12 occurrences of 6-line block across 12 files — saves 66 lines
      FILES: agents/generated/codex_nl_plan_agent/routes.py, agents/generated/codex_nl_smoke_agent/routes.py, agents/generated/codex_uri_smoke_agent/routes.py, agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py, agents/generated/gnome_programmer_agent/routes.py +7 more
  [10] ○ extract_function   → agents/generated/utils/skill_run_cron_monitor.py
      WHY: 7 occurrences of 6-line block across 6 files — saves 36 lines
      FILES: agents/generated/codex_nl_smoke_agent/routes.py, agents/generated/codex_uri_smoke_agent/routes.py, agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py, agents/generated/invoices_agent/routes.py, agents/generated/user_agent/routes.py +1 more
  [11] ○ extract_function   → agents/generated/utils/skill_process_view.py
      WHY: 8 occurrences of 4-line block across 3 files — saves 28 lines
      FILES: agents/generated/hypervisor_dashboard_agent/routes.py, agents/generated/invoices_agent/routes.py, agents/generated/user_agent/routes.py
  [12] ○ extract_function   → agents/generated/utils/skill_read_markpact_source.py
      WHY: 9 occurrences of 3-line block across 4 files — saves 24 lines
      FILES: agents/generated/codex_nl_plan_agent/routes.py, agents/generated/codex_nl_smoke_agent/routes.py, agents/generated/codex_uri_smoke_agent/routes.py, agents/generated/schema_collab_agent/routes.py
  [13] ● extract_class      → utils/to_dict.py
      WHY: 3 occurrences of 11-line block across 3 files — saves 22 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/models.py, output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/models.py, packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py
  [14] ○ extract_function   → agents/operators/utils/_playwright_ready.py
      WHY: 4 occurrences of 6-line block across 4 files — saves 18 lines
      FILES: agents/operators/browser_operator/adapters/browser_router.py, agents/operators/desktop_operator/adapters/input_router.py, agents/operators/desktop_operator/adapters/pcwin_router.py, agents/operators/desktop_operator/adapters/screen_router.py
  [15] ○ extract_function   → utils/list_agent_deployments.py
      WHY: 2 occurrences of 15-line block across 2 files — saves 15 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py, output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/uri_client.py
  [16] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/utils/_read_yaml.py
      WHY: 4 occurrences of 5-line block across 4 files — saves 15 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/agent_describe.py, packages/resource-agent-hypervisor/hypervisor/contract_registry/loader.py, packages/resource-agent-hypervisor/hypervisor/contract_registry/uri_resolver.py, packages/resource-agent-hypervisor/hypervisor/deployment_registry/aliases.py
  [17] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/deployment_registry/utils/_port_from_http_uri.py
      WHY: 4 occurrences of 5-line block across 4 files — saves 15 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/deployment_registry/inspection/incidents.py, packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py, packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py, packages/resource-agent-hypervisor/hypervisor/deployment_registry/port_utils.py
  [18] ● extract_function   → utils/_uri_path_parts.py
      WHY: 3 occurrences of 7-line block across 3 files — saves 14 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/presentation.py, output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/uri_client.py, packages/resource-agent-hypervisor/hypervisor/routing/system_request.py
  [19] ○ extract_function   → agents/operators/desktop_operator/adapters/utils/_task_context.py
      WHY: 5 occurrences of 3-line block across 5 files — saves 12 lines
      FILES: agents/operators/desktop_operator/adapters/android_adb.py, agents/operators/desktop_operator/adapters/android_mock.py, agents/operators/desktop_operator/adapters/pcwin_mock.py, agents/operators/desktop_operator/adapters/pcwin_uia.py, agents/operators/desktop_operator/adapters/screen_gnome.py
  [20] ○ extract_function   → utils/preview_action.py
      WHY: 2 occurrences of 12-line block across 2 files — saves 12 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/policy.py, output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/policy.py
  [21] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/deployment_registry/utils/_lifecycle_payload.py
      WHY: 4 occurrences of 4-line block across 4 files — saves 12 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py, packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle_status.py, packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py, packages/resource-agent-hypervisor/hypervisor/deployment_registry/supervisor.py
  [22] ○ extract_function   → packages/resource-agent-factory/generator/utils/python_file_header.py
      WHY: 3 occurrences of 6-line block across 1 files — saves 12 lines
      FILES: packages/resource-agent-factory/generator/header.py
  [23] ○ extract_function   → utils/_normalize_view_uri.py
      WHY: 2 occurrences of 11-line block across 2 files — saves 11 lines
      FILES: output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/uri_client.py, packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py
  [24] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/deployment_registry/utils/port_from_http_uri.py
      WHY: 2 occurrences of 11-line block across 2 files — saves 11 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py, packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py
  [25] ○ extract_function   → agents/operators/desktop_operator/adapters/utils/resolve_adapter_mode.py
      WHY: 2 occurrences of 10-line block across 2 files — saves 10 lines
      FILES: agents/operators/desktop_operator/adapters/android_router.py, agents/operators/desktop_operator/adapters/input_router.py
  [26] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/deployment_registry/utils/_health_uri.py
      WHY: 3 occurrences of 5-line block across 2 files — saves 10 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py, packages/resource-agent-hypervisor/hypervisor/deployment_registry/stopper.py
  [27] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/utils/load_planfile_strategy.py
      WHY: 3 occurrences of 5-line block across 3 files — saves 10 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/integrations/planfile/ticket_mapper.py, packages/resource-agent-hypervisor/hypervisor/repair/registry.py, packages/resource-agent-hypervisor/hypervisor/repair/validator.py
  [28] ○ extract_function   → agents/custom/utils/skill_run_programmer_session.py
      WHY: 2 occurrences of 9-line block across 2 files — saves 9 lines
      FILES: agents/custom/gnome_programmer_agent/routes.py, agents/custom/screenshot_analysis_agent/routes.py
  [29] ○ extract_function   → agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/utils/_chat_request.py
      WHY: 2 occurrences of 9-line block across 1 files — saves 9 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py
  [30] ○ extract_function   → packages/resource-agent-factory/agents/generated/utils/skill_read_order.py
      WHY: 4 occurrences of 3-line block across 2 files — saves 9 lines
      FILES: packages/resource-agent-factory/agents/generated/orders_agent/routes.py, packages/resource-agent-factory/agents/generated/user_agent/routes.py
  [31] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/deployment_registry/utils/_local_health_uri.py
      WHY: 2 occurrences of 9-line block across 1 files — saves 9 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/deployment_registry/local_targets.py
  [32] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/repair/utils/validate_incident_dict.py
      WHY: 3 occurrences of 4-line block across 1 files — saves 8 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/repair/validator.py
  [33] ○ extract_class      → utils/to_dict.py
      WHY: 2 occurrences of 7-line block across 2 files — saves 7 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/models.py, output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/models.py
  [34] ○ extract_function   → utils/health.py
      WHY: 2 occurrences of 7-line block across 2 files — saves 7 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py, output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/routes.py
  [35] ○ extract_function   → utils/ui_agents.py
      WHY: 2 occurrences of 7-line block across 2 files — saves 7 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py, output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/routes.py
  [36] ○ extract_function   → utils/ui_agent_detail.py
      WHY: 2 occurrences of 7-line block across 2 files — saves 7 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py, output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/routes.py
  [37] ○ extract_function   → agents/operators/desktop_operator/adapters/utils/window_id_from_payload.py
      WHY: 2 occurrences of 7-line block across 1 files — saves 7 lines
      FILES: agents/operators/desktop_operator/adapters/pcwin_uri.py
  [38] ○ extract_function   → utils/api_process_view.py
      WHY: 2 occurrences of 6-line block across 2 files — saves 6 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py, output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/routes.py
  [39] ○ extract_function   → scripts/www/utils/_import_markdown.py
      WHY: 2 occurrences of 6-line block across 2 files — saves 6 lines
      FILES: scripts/www/build_examples_docs.py, scripts/www/md_html.py
  [40] ○ extract_function   → agents/custom/remote_deploy_agent/utils/skill_start_remote_agent.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: agents/custom/remote_deploy_agent/routes.py
  [41] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/utils/deploy_agent_cmd.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/cli.py
  [42] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/deployment_registry/utils/_process_log_path.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py
  [43] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/repair/utils/_incident_text.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/repair/classifier.py
  [44] ○ extract_function   → packages/resource-agent-factory/agents/generated/utils/read_resource.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: packages/resource-agent-factory/agents/generated/orders_agent/routes.py, packages/resource-agent-factory/agents/generated/user_agent/routes.py
  [45] ○ extract_function   → packages/resource-agent-factory/agents/generated/utils/dispatch_command.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: packages/resource-agent-factory/agents/generated/orders_agent/routes.py, packages/resource-agent-factory/agents/generated/user_agent/routes.py
  [46] ○ extract_function   → agents/operators/browser_operator/adapters/utils/playwright_import_error.py
      WHY: 2 occurrences of 5-line block across 1 files — saves 5 lines
      FILES: agents/operators/browser_operator/adapters/browser_playwright.py
  [47] ○ extract_function   → agents/operators/desktop_operator/adapters/utils/type_text.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: agents/operators/desktop_operator/adapters/input_router.py, agents/operators/desktop_operator/adapters/screen_router.py
  [48] ○ extract_function   → utils/_select_dashboard_uri_handler.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py, packages/resource-agent-hypervisor/hypervisor/routing/system_dispatch.py
  [49] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/deployment_registry/utils/port_from_command.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/deployment_registry/health_uri.py, packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py
  [50] ○ extract_function   → agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/utils/root.py
      WHY: 2 occurrences of 4-line block across 1 files — saves 4 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/routes.py
  [51] ○ extract_function   → agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/utils/_html_request.py
      WHY: 2 occurrences of 4-line block across 1 files — saves 4 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py
  [52] ○ extract_function   → packages/resource-agent-hypervisor/hypervisor/contract_registry/utils/run_build_command.py
      WHY: 2 occurrences of 4-line block across 1 files — saves 4 lines
      FILES: packages/resource-agent-hypervisor/hypervisor/contract_registry/cli_commands.py
  [53] ○ extract_function   → utils/render_process_html.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/view_builder.py, output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/view_builder.py
  [54] ○ extract_function   → utils/_human_title.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/view_builder.py, packages/resource-agent-hypervisor/hypervisor/routing/views/process.py

QUICK_WINS[41] (low risk, high savings — do first):
  [1] extract_function   saved=187L  → agents/generated/utils/_read_uri.py
      FILES: routes.py, routes.py, routes.py +9
  [2] extract_function   saved=143L  → agents/generated/utils/dispatch_command.py
      FILES: routes.py, routes.py, routes.py +9
  [3] extract_function   saved=121L  → agents/generated/utils/_dispatch_command.py
      FILES: routes.py, routes.py, routes.py +9
  [4] extract_function   saved=104L  → utils/_uri_allowed.py
      FILES: routes.py, routes.py, routes.py +11
  [5] extract_function   saved=99L  → agents/generated/utils/read_resource.py
      FILES: routes.py, routes.py, routes.py +9
  [6] extract_function   saved=91L  → utils/health.py
      FILES: routes.py, routes.py, routes.py +11
  [7] extract_function   saved=86L  → packages/resource-agent-hypervisor/hypervisor/domain_pack/utils/weather_proto.py
      FILES: templates.py
  [8] extract_function   saved=84L  → agents/generated/utils/skill_run_cron_monitor.py
      FILES: routes.py, routes.py, routes.py +3
  [9] extract_function   saved=66L  → agents/generated/utils/_command_uri.py
      FILES: routes.py, routes.py, routes.py +9
  [10] extract_function   saved=36L  → agents/generated/utils/skill_run_cron_monitor.py
      FILES: routes.py, routes.py, routes.py +3

DEPENDENCY_RISK[15] (duplicates spanning multiple packages):
  to_dict  packages=3  files=3
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/models.py
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/models.py
      packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py
  _uri_path_parts  packages=3  files=3
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/presentation.py
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/uri_client.py
      packages/resource-agent-hypervisor/hypervisor/routing/system_request.py
  _uri_allowed  packages=2  files=14
      agents/generated/codex_nl_plan_agent/routes.py
      agents/generated/codex_nl_smoke_agent/routes.py
      agents/generated/codex_uri_smoke_agent/routes.py
      agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py
      +10 more
  health  packages=2  files=14
      agents/generated/codex_nl_plan_agent/routes.py
      agents/generated/codex_nl_smoke_agent/routes.py
      agents/generated/codex_uri_smoke_agent/routes.py
      agents/generated/generuj_mape_pogody_dwa_tygodnie_do_przodu_w_html_agent/routes.py
      +10 more
  list_agent_deployments  packages=2  files=2
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/uri_client.py
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/uri_client.py
  preview_action  packages=2  files=2
      agents/system/hypervisor_dashboard/hypervisor_dashboard_agent/policy.py
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/policy.py
  _normalize_view_uri  packages=2  files=2
      output/ecosystems/hypervisor-dashboard/app/hypervisor_dashboard_agent/uri_client.py
      packages/resource-agent-hypervisor/hypervisor/routing/view_handlers.py

EFFORT_ESTIMATE (total ≈ 59.6h):
  hard   _read_uri                           saved=187L  ~374min
  hard   dispatch_command                    saved=143L  ~286min
  hard   _dispatch_command                   saved=121L  ~242min
  hard   _uri_allowed                        saved=104L  ~416min
  hard   read_resource                       saved=99L  ~198min
  hard   health                              saved=91L  ~364min
  hard   weather_proto                       saved=86L  ~258min
  hard   skill_run_cron_monitor              saved=84L  ~168min
  hard   _command_uri                        saved=66L  ~132min
  medium skill_run_cron_monitor              saved=36L  ~72min
  ... +44 more (~1066min)

METRICS-TARGET:
  dup_groups:  54 → 0
  saved_lines: 1431 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 1544 func | 205f | 2026-06-15
# generated in 0.01s

NEXT[10] (ranked by impact):
  [1] !! SPLIT           www/landing.js
      WHY: 836L, 0 classes, max CC=24
      EFFORT: ~4h  IMPACT: 20064

  [2] !! SPLIT           www/app.js
      WHY: 731L, 0 classes, max CC=14
      EFFORT: ~4h  IMPACT: 10234

  [3] !! SPLIT-FUNC      _render_markdown  CC=70  fan=25
      WHY: CC=70 exceeds 15
      EFFORT: ~1h  IMPACT: 1750

  [4] !! SPLIT-FUNC      createVoiceController  CC=29  fan=37
      WHY: CC=29 exceeds 15
      EFFORT: ~1h  IMPACT: 1073

  [5] !  SPLIT-FUNC      resolve_contract_path  CC=22  fan=21
      WHY: CC=22 exceeds 15
      EFFORT: ~1h  IMPACT: 462

  [6] !  SPLIT-FUNC      fetch_agent_artifacts  CC=21  fan=19
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 399

  [7] !  SPLIT-FUNC      describe_agent  CC=17  fan=21
      WHY: CC=17 exceeds 15
      EFFORT: ~1h  IMPACT: 357

  [8] !  SPLIT-FUNC      handle_contract_uri  CC=21  fan=17
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 357

  [9] !  SPLIT-FUNC      applyLanguage  CC=24  fan=14
      WHY: CC=24 exceeds 15
      EFFORT: ~1h  IMPACT: 336

  [10] !  SPLIT-FUNC      handle_schema_uri  CC=20  fan=14
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 280


RISKS[3]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting www/landing.js may break 111 import paths
  ⚠ Splitting www/app.js may break 99 import paths

METRICS-TARGET:
  CC̄:          3.6 → ≤2.5
  max-CC:      70 → ≤20
  god-modules: 8 → 0
  high-CC(≥15): 14 → ≤7
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
  prev CC̄=3.5 → now CC̄=3.6
```

## Intent

WronAI resource agent monorepo — uri3, nl2uri, uri2flow, uri2ops, touri, hypervisor, agent factory

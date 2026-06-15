# System Architecture Analysis
<!-- generated in 0.01s -->

## Overview

- **Project**: /home/tom/github/wronai/hypervisor
- **Primary Language**: python
- **Languages**: python: 554, yaml: 130, json: 80, shell: 40, toml: 17
- **Analysis Mode**: static
- **Total Functions**: 2612
- **Total Classes**: 145
- **Modules**: 875
- **Entry Points**: 885

## Architecture by Module

### www.landing
- **Functions**: 119
- **File**: `landing.js`

### www.app
- **Functions**: 99
- **File**: `app.js`

### packages.hypervisor-dashboard-agent.hypervisor_dashboard_agent.uri_client
- **Functions**: 52
- **Classes**: 1
- **File**: `uri_client.py`

### www.assets.app
- **Functions**: 38
- **File**: `app.js`

### www.chat-uri
- **Functions**: 31
- **File**: `chat-uri.js`

### packages.urish.urish.scenario_registry
- **Functions**: 30
- **File**: `scenario_registry.py`

### packages.resource-agent-hypervisor.hypervisor.cli
- **Functions**: 29
- **File**: `cli.py`

### www.assets.api-client
- **Functions**: 28
- **Classes**: 1
- **File**: `api-client.js`

### packages.nl2uri.nl2uri.graph_repair
- **Functions**: 27
- **File**: `graph_repair.py`

### www.examples-gallery
- **Functions**: 25
- **File**: `examples-gallery.js`

### packages.urish.urish.repl
- **Functions**: 24
- **Classes**: 1
- **File**: `repl.py`

### packages.resource-agent-hypervisor.hypervisor.deployment_registry.runtime_state
- **Functions**: 24
- **File**: `runtime_state.py`

### packages.hypervisor-dashboard-agent.hypervisor_dashboard_agent.chat_format
- **Functions**: 23
- **File**: `chat_format.py`

### www.chat-voice
- **Functions**: 23
- **File**: `chat-voice.js`

### packages.hypervisor-dashboard-agent.hypervisor_dashboard_agent.routes
- **Functions**: 21
- **Classes**: 5
- **File**: `routes.py`

### packages.urish.urish.backends.proof
- **Functions**: 20
- **Classes**: 1
- **File**: `proof.py`

### packages.uri3.uri3.results.envelope
- **Functions**: 20
- **File**: `envelope.py`

### packages.uri2run.uri2run.runner
- **Functions**: 20
- **File**: `runner.py`

### scripts.www.build_examples_docs
- **Functions**: 20
- **File**: `build_examples_docs.py`

### packages.urish.urish.cli
- **Functions**: 19
- **File**: `cli.py`

## Key Entry Points

Main execution flows into the system:

### packages.urish.urish.commands.agent_commands.register_agent_commands
- **Calls**: typer.Typer, agent_app.command, agent_app.command, agent_app.command, agent_app.command, agent_app.command, agent_app.command, agent_app.command

### packages.urish.urish.commands.ecosystem_commands.register_ecosystem_commands
- **Calls**: typer.Typer, ecosystem_app.command, ecosystem_app.command, ecosystem_app.command, ecosystem_app.command, ecosystem_app.command, app.add_typer, typer.Argument

### packages.urish.urish.commands.dashboard_commands.register_dashboard_commands
- **Calls**: typer.Typer, typer.Typer, dashboard_app.command, dashboard_app.command, www_app.command, www_app.command, www_app.command, app.add_typer

### packages.uri3.uri3.cli.commands.discovery.register
- **Calls**: app.command, app.command, app.command, app.command, typer.Option, typer.Option, packages.uri3.uri3.cli.helpers.list_payload, typer.echo

### www.chat-voice.createVoiceController
- **Calls**: www.chat-voice.trim, www.chat-voice.apiFetch, www.chat-voice.stringify, www.chat-voice.slice, www.chat-voice.Audio, www.chat-voice.play, www.chat-voice.speakText, www.chat-voice.String

### packages.uri2ops.uri2ops.cli.main
- **Calls**: argparse.ArgumentParser, parser.add_subparsers, sub.add_parser, ops.add_subparsers, ops_sub.add_parser, ops_sub.add_parser, desc.add_argument, desc.add_argument

### scripts.examples.audit_agent_reports.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.parse_args, out_dir.mkdir, packages.resource-agent-hypervisor.hypervisor.deployment_registry.loader.load_deployment_registry, AuditReport, audit.findings.extend

### scripts.examples.effective_weather_playwright.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.parse_args, workspace_env

### packages.uri2run.uri2run.runner.run_target
> Execute a concrete runtime URI target.
- **Calls**: target.startswith, target.startswith, target.startswith, target.startswith, target.startswith, target.startswith, target.startswith, target.startswith

### hypervisor.config.models.HypervisorConfig.from_dict
- **Calls**: cls, str, str, data.get, bool, str, LLMConfig.from_dict, Uri3Config.from_dict

### scripts.www.build_landing_integrations.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.parse_args, scripts.www.build_landing_integrations.collect_cards, scripts.www.build_landing_integrations.build_sections, fragment_path.parent.mkdir, scripts.www.build_landing_integrations.splice_index

### packages.uri3.uri3.protocols.schemes.spec_registry.build_scheme_registry
- **Calls**: log.spec, env.spec, python.spec, llm.spec, pypi.spec, http.spec, http.spec, a2a.spec

### packages.resource-agent-hypervisor.meta_agent.cli.main
- **Calls**: argparse.ArgumentParser, parser.add_subparsers, sub.add_parser, plan.add_argument, plan.add_argument, sub.add_parser, validate.add_argument, sub.add_parser

### www.api-bridge.bridge.call_uri
- **Calls**: app.post, uri.startswith, uri.startswith, www.api-bridge.bridge.run_cmd, www.api-bridge.bridge.envelope, uri.removeprefix, www.api-bridge.bridge.run_cmd, www.api-bridge.bridge.envelope

### packages.uri3.uri3.cli.commands.resolve.register
- **Calls**: app.command, app.command, app.command, app.command, uri3.validators.uri_validator.validate_uri, typer.echo, packages.uri3.uri3.validators.uri_tree_validator.validate_uri_tree, typer.echo

### scripts.www.monitor_landing.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.parse_args, scripts.www.monitor_landing.load_baseline

### packages.uri3.uri3.graph.adapters.browser_playwright.PlaywrightBrowserAdapter.execute
- **Calls**: packages.uri3.uri3.graph.adapters.browser_playwright._session_state, state.get, None.execute, urlparse, str, None.start, playwright.chromium.launch, browser.new_page

### packages.resource-agent-hypervisor.hypervisor.cli.supervise_cmd
> Run bounded health supervision or continuous watch mode.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option

### packages.resource-agent-hypervisor.hypervisor.repair.supervisor.repair_apply
- **Calls**: packages.resource-agent-hypervisor.hypervisor.repair.supervisor._repo_root, packages.resource-agent-hypervisor.hypervisor.repair.supervisor.diagnose_agent, packages.resource-agent-hypervisor.hypervisor.repair.supervisor._repair_playbook_candidates, packages.resource-agent-hypervisor.hypervisor.repair.supervisor._execute_repair_playbooks, packages.resource-agent-hypervisor.hypervisor.repair.supervisor._envelope, packages.resource-agent-hypervisor.hypervisor.events.emit_result_event, inspection.get, packages.resource-agent-hypervisor.hypervisor.repair.supervisor._healthy_repair_apply_body

### packages.uri3.uri3.cli.commands.workflow.register
- **Calls**: app.command, app.command, app.command, packages.uri3.uri3.graph.graph_validator.validate_workflow_graph, typer.echo, packages.uri3.uri3.graph.execution_plan.build_execution_plan, typer.echo, typer.Option

### packages.uri3.uri3.graph.adapters.registry.AssertionAdapter.execute
- **Calls**: payload.get, payload.get, payload.get, context.resolve_ref, node.uri.endswith, payload.get, payload.get, bool

### packages.uri3.uri3.doctor.checks.boundaries.check_runtime_transports
- **Calls**: frozenset, packages.uri3.uri3.doctor.checks._helpers.check_result, packages.uri2run.uri2run.runner.run_backend, result.to_dict, body.setdefault, body.setdefault, body.setdefault, set

### scripts.examples.run_uri3_workflow.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.parse_args, packages.uri3.uri3.graph.graph_validator.validate_workflow_graph, packages.uri3.uri3.graph.graph_validator.load_workflow_graph

### scripts.www.build_examples_docs.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.parse_args, scripts.www.build_examples_docs.list_example_dirs, scripts.www.build_examples_docs.build_overview_section, scripts.www.build_examples_docs.build_page, args.out.parent.mkdir

### packages.nl2uri.nl2uri.cli.flow
> Generate compact URI flow (*.uri.flow.yaml style).
- **Calls**: app.command, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option

### packages.uri3.uri3.resolvers.file_resolver.resolve_file
- **Calls**: packages.uri3.uri3.resolvers.file_resolver.path_from_file_uri, path.exists, str, path.exists, path.stat, data.update, mimetypes.guess_type, path.is_file

### packages.uri3.uri3.doctor.checks.verify.check_replay_failures
- **Calls**: sorted, packages.uri3.uri3.doctor.checks._helpers.check_result, logs_dir.is_dir, packages.uri3.uri3.doctor.checks._helpers.check_result, logs_dir.glob, packages.uri2verify.uri2verify.replay.replay_workflow_events, summary.get, summary.get

### www.app.handleSubmit
- **Calls**: www.app.preventDefault, www.app.trim, www.app.appendMessage, www.app.escapeHtml, www.app.looksLikeUri, www.app.extractUri, www.app.callUri, www.app.test

### uri2ops.operation_registry.models.OperationSpec.from_mapping
- **Calls**: cls, data.get, data.get, data.get, data.get, uri2ops.operation_registry.models.OperationRegistry.list, bool, bool

### packages.uri3.uri3.graph.models.GraphNode.from_dict
- **Calls**: cls, str, str, str, data.get, data.get, dict, uri2ops.operation_registry.models.OperationRegistry.list

## Process Flows

Key execution flows identified:

### Flow 1: register_agent_commands
```
register_agent_commands [packages.urish.urish.commands.agent_commands]
```

### Flow 2: register_ecosystem_commands
```
register_ecosystem_commands [packages.urish.urish.commands.ecosystem_commands]
```

### Flow 3: register_dashboard_commands
```
register_dashboard_commands [packages.urish.urish.commands.dashboard_commands]
```

### Flow 4: register
```
register [packages.uri3.uri3.cli.commands.discovery]
```

### Flow 5: createVoiceController
```
createVoiceController [www.chat-voice]
```

### Flow 6: main
```
main [packages.uri2ops.uri2ops.cli]
```

### Flow 7: run_target
```
run_target [packages.uri2run.uri2run.runner]
```

### Flow 8: from_dict
```
from_dict [hypervisor.config.models.HypervisorConfig]
```

### Flow 9: build_scheme_registry
```
build_scheme_registry [packages.uri3.uri3.protocols.schemes.spec_registry]
```

### Flow 10: call_uri
```
call_uri [www.api-bridge.bridge]
  └─> run_cmd
  └─> envelope
```

## Key Classes

### www.assets.api-client.TaskinityApiClient
- **Methods**: 28
- **Key Methods**: www.assets.api-client.TaskinityApiClient.setBaseUrl, www.assets.api-client.TaskinityApiClient.useMock, www.assets.api-client.TaskinityApiClient.isMock, www.assets.api-client.TaskinityApiClient.health, www.assets.api-client.TaskinityApiClient.res, www.assets.api-client.TaskinityApiClient.data, www.assets.api-client.TaskinityApiClient.call, www.assets.api-client.TaskinityApiClient.res, www.assets.api-client.TaskinityApiClient.data, www.assets.api-client.TaskinityApiClient.ask

### uri2ops.server.service.OperatorService
- **Methods**: 9
- **Key Methods**: uri2ops.server.service.OperatorService.__init__, uri2ops.server.service.OperatorService.registry, uri2ops.server.service.OperatorService.registry_export, uri2ops.server.service.OperatorService.list_operations, uri2ops.server.service.OperatorService.describe_operation, uri2ops.server.service.OperatorService.list_registry_sources, uri2ops.server.service.OperatorService.validate_task, uri2ops.server.service.OperatorService.plan_task, uri2ops.server.service.OperatorService.run_task

### packages.resource-agent-hypervisor.hypervisor.uri.client.Uri3Client
> Thin hypervisor adapter over uri3 routing, scanning and graph utilities.
- **Methods**: 8
- **Key Methods**: packages.resource-agent-hypervisor.hypervisor.uri.client.Uri3Client.__init__, packages.resource-agent-hypervisor.hypervisor.uri.client.Uri3Client.resolve, packages.resource-agent-hypervisor.hypervisor.uri.client.Uri3Client.call, packages.resource-agent-hypervisor.hypervisor.uri.client.Uri3Client.scan, packages.resource-agent-hypervisor.hypervisor.uri.client.Uri3Client.logs, packages.resource-agent-hypervisor.hypervisor.uri.client.Uri3Client.schema, packages.resource-agent-hypervisor.hypervisor.uri.client.Uri3Client.graph, packages.resource-agent-hypervisor.hypervisor.uri.client.Uri3Client.nl2uri

### packages.resource-agent-hypervisor.hypervisor.core.Hypervisor
> Main Hypervisor controller.

Example:
    from hypervisor import Hypervisor
    hv = Hypervisor()
  
- **Methods**: 7
- **Key Methods**: packages.resource-agent-hypervisor.hypervisor.core.Hypervisor.__post_init__, packages.resource-agent-hypervisor.hypervisor.core.Hypervisor.from_config, packages.resource-agent-hypervisor.hypervisor.core.Hypervisor.start, packages.resource-agent-hypervisor.hypervisor.core.Hypervisor.stop, packages.resource-agent-hypervisor.hypervisor.core.Hypervisor.register_agent, packages.resource-agent-hypervisor.hypervisor.core.Hypervisor.status, packages.resource-agent-hypervisor.hypervisor.core.Hypervisor.__repr__

### packages.nl2uri.nl2uri.domain_registry.DomainRegistryEntry
- **Methods**: 5
- **Key Methods**: packages.nl2uri.nl2uri.domain_registry.DomainRegistryEntry.flow_aliases, packages.nl2uri.nl2uri.domain_registry.DomainRegistryEntry.default_deployment_id, packages.nl2uri.nl2uri.domain_registry.DomainRegistryEntry.default_health_uri, packages.nl2uri.nl2uri.domain_registry.DomainRegistryEntry.default_card_uri, packages.nl2uri.nl2uri.domain_registry.DomainRegistryEntry.deployment_selector_aliases

### uri2ops.operation_registry.models.OperationRegistry
- **Methods**: 3
- **Key Methods**: uri2ops.operation_registry.models.OperationRegistry.get, uri2ops.operation_registry.models.OperationRegistry.require, uri2ops.operation_registry.models.OperationRegistry.list

### packages.uri3.uri3.results.service_result.ServiceResult
- **Methods**: 3
- **Key Methods**: packages.uri3.uri3.results.service_result.ServiceResult.finalize, packages.uri3.uri3.results.service_result.ServiceResult._default_error_source, packages.uri3.uri3.results.service_result.ServiceResult.to_dict

### packages.uri3.uri3.resolvers.router.Uri3Router
- **Methods**: 3
- **Key Methods**: packages.uri3.uri3.resolvers.router.Uri3Router.__init__, packages.uri3.uri3.resolvers.router.Uri3Router.resolve, packages.uri3.uri3.resolvers.router.Uri3Router.call

### hypervisor.contract_registry.models.ContractRegistry
- **Methods**: 3
- **Key Methods**: hypervisor.contract_registry.models.ContractRegistry.resource_by_uri, hypervisor.contract_registry.models.ContractRegistry.view_by_name, hypervisor.contract_registry.models.ContractRegistry.capability_by_name

### packages.resource-agent-hypervisor.hypervisor.deployment_registry.models.AgentDeployment
- **Methods**: 3
- **Key Methods**: packages.resource-agent-hypervisor.hypervisor.deployment_registry.models.AgentDeployment.declared_health_uri, packages.resource-agent-hypervisor.hypervisor.deployment_registry.models.AgentDeployment.effective_health_uri, packages.resource-agent-hypervisor.hypervisor.deployment_registry.models.AgentDeployment.to_dict

### runtime_client.client.ResourceRuntimeClient
> Small HTTP client used by generated thin agents.

Expected runtime API:
- GET  /resources/read?uri=r
- **Methods**: 3
- **Key Methods**: runtime_client.client.ResourceRuntimeClient.__init__, runtime_client.client.ResourceRuntimeClient.read_resource, runtime_client.client.ResourceRuntimeClient.dispatch_command

### testenv.ssh_agent_host.mock_agent_server.Handler
- **Methods**: 3
- **Key Methods**: testenv.ssh_agent_host.mock_agent_server.Handler._json, testenv.ssh_agent_host.mock_agent_server.Handler.do_GET, testenv.ssh_agent_host.mock_agent_server.Handler.log_message
- **Inherits**: BaseHTTPRequestHandler

### uri2ops.operation_registry.models.OperationSpec
- **Methods**: 2
- **Key Methods**: uri2ops.operation_registry.models.OperationSpec.from_mapping, uri2ops.operation_registry.models.OperationSpec.to_dict

### uri3.graph.uri_graph.UriGraph
- **Methods**: 2
- **Key Methods**: uri3.graph.uri_graph.UriGraph.add_node, uri3.graph.uri_graph.UriGraph.add_edge

### packages.uri3.uri3.graph.models.GraphNode
- **Methods**: 2
- **Key Methods**: packages.uri3.uri3.graph.models.GraphNode.from_dict, packages.uri3.uri3.graph.models.GraphNode.to_dict

### packages.uri3.uri3.graph.models.WorkflowGraph
- **Methods**: 2
- **Key Methods**: packages.uri3.uri3.graph.models.WorkflowGraph.add_node, packages.uri3.uri3.graph.models.WorkflowGraph.to_dict

### packages.uri3.uri3.graph.adapters.browser_router.BrowserRouterAdapter
> Deprecated: uri3 delegates operator schemes to uri2ops (see Uri2OpsAdapter).
- **Methods**: 2
- **Key Methods**: packages.uri3.uri3.graph.adapters.browser_router.BrowserRouterAdapter.__init__, packages.uri3.uri3.graph.adapters.browser_router.BrowserRouterAdapter.execute

### uri3.resolvers.http_resolver.HttpResolver
- **Methods**: 2
- **Key Methods**: uri3.resolvers.http_resolver.HttpResolver.resolve, uri3.resolvers.http_resolver.HttpResolver.fetch

### packages.uri3.uri3.resolvers.env_resolver.EnvResolver
- **Methods**: 2
- **Key Methods**: packages.uri3.uri3.resolvers.env_resolver.EnvResolver.resolve, packages.uri3.uri3.resolvers.env_resolver.EnvResolver.call

### uri3.resolvers.python_resolver.PythonResolver
- **Methods**: 2
- **Key Methods**: uri3.resolvers.python_resolver.PythonResolver.resolve, uri3.resolvers.python_resolver.PythonResolver.call

## Data Transformation Functions

Key functions that process and transform data:

### packages.urish.urish.repl.parse_repl_line
> Parse one REPL line into CLI argv, or None when handled as meta-command.
- **Output to**: line.strip, stripped.lower, _META_HANDLERS.get, packages.urish.urish.repl._handle_context_use, packages.urish.urish.repl._known_commands

### packages.urish.urish.backends.proof._format_proof_check_line
- **Output to**: check.get, check.get, check.get, check.get, check.get

### packages.urigen.urigen.cli.build_parser
- **Output to**: argparse.ArgumentParser, parser.add_subparsers, sub.add_parser, plan.add_argument, plan.add_argument

### packages.urigen.urigen.apply_validate.validate_apply_artifact
- **Output to**: Draft202012Validator, packages.urigen.urigen.apply_validate._load_schema, validator.iter_errors, None.join, str

### packages.uri2ops.uri2ops.cli.validate_cmd
- **Output to**: validate_task_file, packages.uri2ops.uri2ops.cli._print, packages.uri2ops.uri2ops.cli._print

### packages.uri2ops.uri2ops.operation_registry.validator.validate_registry_schema
- **Output to**: json.loads, None.read_text, sorted, uri2ops.operation_registry.loader.registry_schema_path, uri2ops.operation_registry.models.OperationRegistry.list

### packages.uri2ops.uri2ops.operation_registry.validator.validate_operation_registry
- **Output to**: registry.list, errors.append, spec.handler.startswith, errors.append, spec.handler.removeprefix

### uri2ops.server.service.OperatorService.validate_task
- **Output to**: validate_task_data, self.registry

### packages.uri3.uri3.logs.parsing.parse_json_entry
- **Output to**: line.strip, json.loads, isinstance, isinstance, data.get

### packages.uri3.uri3.logs.parsing.parse_text_entry
- **Output to**: line.strip, _TEXT_LOG_RE.match, match.groupdict, groups.get, None.upper

### packages.uri3.uri3.logs.parsing.parse_log_line
- **Output to**: line.strip, packages.uri3.uri3.logs.parsing.empty_entry, packages.uri3.uri3.logs.parsing.parse_json_entry, packages.uri3.uri3.logs.parsing.parse_text_entry, line.strip

### packages.uri3.uri3.logs.reader._parse_since
- **Output to**: value.strip, datetime.now, value.endswith, value.endswith, value.endswith

### packages.uri3.uri3.graph.graph_validator.validate_workflow_schema
- **Output to**: json.loads, Draft202012Validator, None.read_text, sorted, packages.uri3.uri3.graph.graph_validator._schema_path

### packages.uri3.uri3.graph.graph_validator.validate_workflow_graph
- **Output to**: packages.uri3.uri3.graph.graph_validator.load_workflow_graph, packages.uri3.uri3.graph.graph_validator.validate_workflow_schema, set, graph.nodes.values, packages.uri3.uri3.graph.dependency_graph.detect_cycles

### packages.uri3.uri3.graph.operation_registry.validate_node_operation
- **Output to**: packages.uri3.uri3.graph.operation_registry.scheme_from_uri, packages.uri3.uri3.graph.operation_registry.allowed_operations, None.join, sorted, packages.uri3.uri3.graph.operation_registry.allowed_operations

### uri3.validators.uri_validator.validate_uri
- **Output to**: uri3.protocols.parser.parse_uri, ValueError

### packages.uri3.uri3.validators.uri_tree_validator.validate_uri_tree
- **Output to**: packages.uri3.uri3.validators.uri_tree_validator.load_yaml, json.loads, Draft202012Validator, sorted, SCHEMA_PATH.read_text

### packages.uri3.uri3.artifacts.validator.validate_artifact
- **Output to**: packages.uri3.uri3.artifacts.validator.load_schema, Draft202012Validator, validator.iter_errors, None.join, map

### packages.uri3.uri3.artifacts.validator.validate_artifact_file
- **Output to**: path.read_text, packages.uri3.uri3.artifacts.validator.validate_artifact, json.loads, yaml.safe_load, isinstance

### packages.uri3.uri3.docker.actions.compose._parse_ps_stdout
- **Output to**: stdout.splitlines, line.strip, parsed.append, json.loads, parsed.append

### uri3.protocols.parser.parse_uri
- **Output to**: urlparse, ParsedURI, ValueError, parse_qs

### packages.uri3.uri3.protocols.schemes.instance_parser._parse_log
- **Output to**: None.to_dict, packages.uri3.uri3.resolvers.log_resolver.parse_log_uri

### packages.uri3.uri3.protocols.schemes.instance_parser._parse_env
- **Output to**: packages.uri3.uri3.resolvers.env_resolver.resolve_env

### packages.uri3.uri3.protocols.schemes.instance_parser._parse_python
- **Output to**: uri3.resolvers.python_resolver.resolve_python

### packages.uri3.uri3.protocols.schemes.instance_parser._parse_llm
- **Output to**: uri3.resolvers.llm_resolver.resolve_llm

## Behavioral Patterns

### recursion_load_payload
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: packages.urish.urish.payload.load_payload

### recursion_list
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: uri2ops.operation_registry.models.OperationRegistry.list

### recursion_plan_task
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: uri2ops.server.service.OperatorService.plan_task

### recursion_run_task
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: uri2ops.server.service.OperatorService.run_task

### recursion_resolve_uri_values
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: packages.uri3.uri3.config.uri_yaml.resolve_uri_values

### recursion_resolve
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: packages.uri3.uri3.resolvers.router.Uri3Router.resolve

### recursion_call
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: packages.uri3.uri3.resolvers.router.Uri3Router.call

### recursion_scan
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: packages.resource-agent-hypervisor.hypervisor.uri.client.Uri3Client.scan

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `packages.urish.urish.commands.agent_commands.register_agent_commands` - 71 calls
- `scripts.architecture_audit.parsers.parse_duplication` - 62 calls
- `packages.urish.urish.commands.ecosystem_commands.register_ecosystem_commands` - 56 calls
- `packages.urish.urish.commands.call_commands.register_call_commands` - 56 calls
- `packages.urish.urish.commands.dashboard_commands.register_dashboard_commands` - 54 calls
- `packages.uri3.uri3.cli.commands.discovery.register` - 47 calls
- `packages.resource-agent-hypervisor.hypervisor.contract_registry.uri_resolver.fetch_agent_artifacts` - 42 calls
- `packages.urigen.urigen.cli.build_parser` - 41 calls
- `packages.urigen.urigen.generator.generate_ecosystem` - 40 calls
- `scripts.architecture_audit.parsers.parse_map` - 40 calls
- `packages.urish.urish.backends.dashboard.create_dashboard` - 37 calls
- `www.chat-voice.createVoiceController` - 37 calls
- `packages.urish.urish.commands.ticket_commands.register_ticket_commands` - 35 calls
- `packages.resource-agent-hypervisor.hypervisor.domain_pack.pack_writer.write_domain_pack` - 34 calls
- `packages.uri2ops.uri2ops.cli.main` - 33 calls
- `packages.uri2ops.uri2ops.server.routes.mcp.mcp_router` - 33 calls
- `hypervisor.contract_registry.loader.load_contract_registry` - 33 calls
- `packages.uri3.uri3.config.llm_profiles.resolve_llm_profile` - 32 calls
- `scripts.architecture_audit.render.render_markdown` - 32 calls
- `packages.urish.urish.commands.evolution_commands.register_evolution_commands` - 31 calls
- `packages.nl2uri.nl2uri.flow_planner.plan_flow` - 30 calls
- `meta_agent.planner.infer_intent` - 30 calls
- `packages.urish.urish.commands.observe_commands.register_observe_commands` - 29 calls
- `agents.custom.screenshot_analysis_agent.analysis.analyze_artifact` - 29 calls
- `packages.resource-agent-hypervisor.hypervisor.contract_registry.uri_resolver.resolve_contract_path` - 29 calls
- `packages.resource-agent-hypervisor.hypervisor.contract_registry.uri_resolver.handle_contract_uri` - 29 calls
- `packages.urish.urish.commands.repair_commands.register_repair_commands` - 28 calls
- `packages.urigen.urigen.apply_planner.build_apply_plan` - 28 calls
- `uri3.graph.uri_graph.build_graph_from_tree` - 28 calls
- `packages.resource-agent-hypervisor.hypervisor.deployment_registry.watch.supervise_watch` - 28 calls
- `scripts.examples.audit_agent_reports.main` - 28 calls
- `scripts.examples.effective_weather_playwright.main` - 28 calls
- `packages.uri2run.uri2run.runner.run_target` - 27 calls
- `packages.urish.urish.scenario_registry.try_scenario_intent` - 26 calls
- `packages.resource-agent-hypervisor.hypervisor.agent_describe.describe_agent` - 26 calls
- `hypervisor.config.models.HypervisorConfig.from_dict` - 26 calls
- `scripts.www.build_landing_integrations.main` - 26 calls
- `packages.resource-agent-hypervisor.hypervisor.contract_registry.uri_resolver.generate_agent_contract` - 26 calls
- `packages.uri3.uri3.protocols.schemes.spec_registry.build_scheme_registry` - 25 calls
- `packages.resource-agent-hypervisor.meta_agent.cli.main` - 25 calls

## System Interactions

How components interact:

```mermaid
graph TD
    register_agent_comma --> Typer
    register_agent_comma --> command
    register_ecosystem_c --> Typer
    register_ecosystem_c --> command
    register_dashboard_c --> Typer
    register_dashboard_c --> command
    register --> command
    register --> Option
    createVoiceControlle --> trim
    createVoiceControlle --> apiFetch
    createVoiceControlle --> stringify
    createVoiceControlle --> slice
    createVoiceControlle --> Audio
    main --> ArgumentParser
    main --> add_subparsers
    main --> add_parser
    main --> add_argument
    main --> parse_args
    main --> mkdir
    run_target --> startswith
    from_dict --> cls
    from_dict --> str
    from_dict --> get
    from_dict --> bool
    main --> collect_cards
    build_scheme_registr --> spec
    call_uri --> post
    call_uri --> startswith
    call_uri --> run_cmd
    call_uri --> envelope
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.
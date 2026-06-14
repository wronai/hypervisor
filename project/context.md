# System Architecture Analysis
<!-- generated in 0.00s -->

## Overview

- **Project**: /home/tom/github/wronai/hypervisor
- **Primary Language**: python
- **Languages**: python: 267, yaml: 57, shell: 15, json: 15, toml: 10
- **Analysis Mode**: static
- **Total Functions**: 709
- **Total Classes**: 81
- **Modules**: 384
- **Entry Points**: 217

## Architecture by Module

### packages.nl2uri.nl2uri.cli
- **Functions**: 15
- **File**: `cli.py`

### packages.resource-agent-hypervisor.hypervisor.cli
- **Functions**: 15
- **File**: `cli.py`

### packages.uri3.uri3.protocols.schemes.instance_parser
- **Functions**: 13
- **File**: `instance_parser.py`

### packages.nl2uri.nl2uri.flow_repair
- **Functions**: 13
- **File**: `flow_repair.py`

### packages.nl2uri.nl2uri.graph_planner
- **Functions**: 11
- **File**: `graph_planner.py`

### packages.uri2flow.uri2flow.resolver
- **Functions**: 10
- **Classes**: 1
- **File**: `resolver.py`

### packages.resource-agent-hypervisor.hypervisor.deployment_registry.status
- **Functions**: 10
- **File**: `status.py`

### uri2ops.server.service
- **Functions**: 9
- **Classes**: 1
- **File**: `service.py`

### packages.uri3.uri3.graph.adapters.uri2ops_adapter
- **Functions**: 9
- **Classes**: 1
- **File**: `uri2ops_adapter.py`

### hypervisor.config.models
- **Functions**: 9
- **Classes**: 8
- **File**: `models.py`

### uri2ops.cli
- **Functions**: 8
- **File**: `cli.py`

### uri2ops.remote_registry.loader
- **Functions**: 8
- **File**: `loader.py`

### packages.uri3.uri3.docker.actions.compose
- **Functions**: 8
- **File**: `compose.py`

### packages.nl2uri.nl2uri.graph_repair
- **Functions**: 8
- **File**: `graph_repair.py`

### packages.resource-agent-hypervisor.hypervisor.uri.client
- **Functions**: 8
- **Classes**: 1
- **File**: `client.py`

### packages.resource-agent-hypervisor.hypervisor.deployment_registry.runtime_state
- **Functions**: 8
- **File**: `runtime_state.py`

### packages.uri3.uri3.resolvers.explain
- **Functions**: 8
- **File**: `explain.py`

### packages.uri3.uri3.logs.filters
- **Functions**: 7
- **File**: `filters.py`

### packages.uri3.uri3.config.ssh_auth
- **Functions**: 7
- **File**: `ssh_auth.py`

### packages.uri3.uri3.resolvers.ssh_resolver
- **Functions**: 7
- **File**: `ssh_resolver.py`

## Key Entry Points

Main execution flows into the system:

### packages.uri3.uri3.cli.commands.discovery.register
- **Calls**: app.command, app.command, app.command, app.command, typer.Option, typer.Option, packages.uri3.uri3.cli.helpers.list_payload, typer.echo

### uri2ops.cli.main
- **Calls**: argparse.ArgumentParser, parser.add_subparsers, sub.add_parser, ops.add_subparsers, ops_sub.add_parser, ops_sub.add_parser, desc.add_argument, desc.add_argument

### hypervisor.config.models.HypervisorConfig.from_dict
- **Calls**: cls, str, str, data.get, bool, str, LLMConfig.from_dict, Uri3Config.from_dict

### packages.uri3.uri3.protocols.schemes.spec_registry.build_scheme_registry
- **Calls**: log.spec, env.spec, python.spec, llm.spec, pypi.spec, http.spec, http.spec, a2a.spec

### packages.resource-agent-hypervisor.meta_agent.cli.main
- **Calls**: argparse.ArgumentParser, parser.add_subparsers, sub.add_parser, plan.add_argument, plan.add_argument, sub.add_parser, validate.add_argument, sub.add_parser

### packages.uri3.uri3.cli.commands.resolve.register
- **Calls**: app.command, app.command, app.command, app.command, uri3.validators.uri_validator.validate_uri, typer.echo, packages.uri3.uri3.validators.uri_tree_validator.validate_uri_tree, typer.echo

### packages.uri3.uri3.graph.adapters.browser_playwright.PlaywrightBrowserAdapter.execute
- **Calls**: packages.uri3.uri3.graph.adapters.browser_playwright._session_state, state.get, None.execute, urlparse, str, None.start, playwright.chromium.launch, browser.new_page

### packages.uri3.uri3.cli.commands.workflow.register
- **Calls**: app.command, app.command, app.command, packages.uri3.uri3.graph.graph_validator.validate_workflow_graph, typer.echo, packages.uri3.uri3.graph.graph_executor.build_execution_plan, typer.echo, typer.Option

### packages.uri3.uri3.graph.adapters.registry.AssertionAdapter.execute
- **Calls**: payload.get, payload.get, payload.get, context.resolve_ref, node.uri.endswith, payload.get, payload.get, bool

### packages.nl2uri.nl2uri.cli.flow
> Generate compact URI flow (*.uri.flow.yaml style).
- **Calls**: app.command, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option

### uri2ops.operation_registry.models.OperationSpec.from_mapping
- **Calls**: cls, data.get, data.get, data.get, data.get, uri2ops.operation_registry.models.OperationRegistry.list, bool, bool

### packages.uri3.uri3.graph.models.GraphNode.from_dict
- **Calls**: cls, str, str, str, data.get, data.get, dict, uri2ops.operation_registry.models.OperationRegistry.list

### packages.nl2uri.nl2uri.cli.task
- **Calls**: app.command, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, uri2ops.server.service.OperatorService.plan_task

### packages.nl2uri.nl2uri.cli.graph
- **Calls**: app.command, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, packages.nl2uri.nl2uri.graph_planner.plan_workflow_graph

### packages.nl2uri.nl2uri.cli.plan
> Classify prompt and generate the best matching URI plan.
- **Calls**: app.command, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, packages.nl2uri.nl2uri.graph_planner.plan_auto, packages.nl2uri.nl2uri.cli._emit

### packages.nl2uri.nl2uri.cli.tree
- **Calls**: app.command, typer.Option, typer.Option, typer.Option, typer.Option, packages.nl2uri.nl2uri.graph_planner.plan_tree, packages.nl2uri.nl2uri.cli._emit, nl2uri.writer.write_uri_tree

### packages.nl2uri.nl2uri.cli.generate
> Backward-compatible URI Tree generation.
- **Calls**: app.command, typer.Option, typer.Option, typer.Option, typer.Option, packages.nl2uri.nl2uri.domain_planner.plan_from_prompt, packages.nl2uri.nl2uri.cli._emit, nl2uri.writer.write_uri_tree

### packages.uri3.uri3.graph.adapters.uri2ops_adapter.Uri2OpsAdapter.execute
- **Calls**: packages.uri3.uri3.graph.adapters.uri2ops_adapter._registry_scheme, packages.uri3.uri3.graph.adapters.uri2ops_adapter._registry_operation, uri2ops.remote_registry.loader.resolve_operation_registry, registry.require, dict, payload.setdefault, payload.setdefault, packages.uri3.uri3.graph.adapters.uri2ops_adapter._runtime_context

### packages.uri3.uri3.protocols.schemes.log.spec
- **Calls**: SchemeSpec, QueryOption, QueryOption, QueryOption, QueryOption, QueryOption, QueryOption, QueryOption

### packages.resource-agent-hypervisor.hypervisor.contract_registry.cli_commands.run_check_command
- **Calls**: hypervisor.contract_registry.schema_validator.validate_contract_files, hypervisor.contract_registry.loader.load_contract_registry, packages.resource-agent-hypervisor.hypervisor.contract_registry.validate.validate_registry, packages.resource-agent-hypervisor.hypervisor.contract_registry.cross_validator.validate_root, hypervisor.contract_registry.registry_builder.write_registry_manifest, print, print, len

### uri2ops.cli.operations_cmd
- **Calls**: uri2ops.remote_registry.loader.resolve_operation_registry, SystemExit, uri2ops.cli._print, registry.require, uri2ops.cli._print, uri2ops.operation_registry.validator.validate_operation_registry, uri2ops.cli._print, spec.to_dict

### packages.uri3.uri3.cli.commands.flow.register
- **Calls**: app.command, app.command, typer.Option, typer.Option, packages.uri3.uri3.cli.commands.flow.expand_flow_cmd, typer.Option, typer.Option, typer.Option

### hypervisor.config.models.HypervisorSettings.from_dict
- **Calls**: data.get, cls, str, int, str, bool, str, data.get

### packages.resource-agent-hypervisor.hypervisor.evolution.cli.main
- **Calls**: print, print, sorted, hypervisor.evolution.models.load_proposal, hypervisor.evolution.validator.validate_proposal, print, None.glob, Path

### hypervisor.compatibility.checker.classify_registry_change
- **Calls**: Path, Path, hypervisor.contract_registry.loader.load_contract_registry, hypervisor.contract_registry.loader.load_contract_registry, sorted, sorted, sorted, sorted

### domains.weather_map.handlers.generate_weather_map.handler
- **Calls**: payload.get, int, None.hexdigest, payload.get, payload.get, payload.get, None.isoformat, hashlib.sha256

### generator.verify.main
- **Calls**: Path, generator.verify.verify_generated, print, root.exists, print, print, print, root.iterdir

### uri2ops.cli.registry_cmd
- **Calls**: SystemExit, uri2ops.cli._print, uri2ops.remote_registry.loader.resolve_operation_registry, uri2ops.operation_registry.validator.validate_operation_registry, uri2ops.cli._print, uri2ops.cli._print, uri2ops.remote_registry.loader.list_remote_sources, len

### generator.validate.main
- **Calls**: Path, generator.validate.iter_agent_specs, print, print, all_errors.extend, print, generator.validate.validate_agent, print

### hypervisor.policy_gate.gate.evaluate_change
- **Calls**: bool, change_report.get, change_report.get, bool, GateDecision, change_report.get, reasons.append, reasons.append

## Process Flows

Key execution flows identified:

### Flow 1: register
```
register [packages.uri3.uri3.cli.commands.discovery]
```

### Flow 2: main
```
main [uri2ops.cli]
```

### Flow 3: from_dict
```
from_dict [hypervisor.config.models.HypervisorConfig]
```

### Flow 4: build_scheme_registry
```
build_scheme_registry [packages.uri3.uri3.protocols.schemes.spec_registry]
```

### Flow 5: execute
```
execute [packages.uri3.uri3.graph.adapters.browser_playwright.PlaywrightBrowserAdapter]
  └─ →> _session_state
```

### Flow 6: flow
```
flow [packages.nl2uri.nl2uri.cli]
```

### Flow 7: from_mapping
```
from_mapping [uri2ops.operation_registry.models.OperationSpec]
```

### Flow 8: task
```
task [packages.nl2uri.nl2uri.cli]
```

### Flow 9: graph
```
graph [packages.nl2uri.nl2uri.cli]
```

### Flow 10: plan
```
plan [packages.nl2uri.nl2uri.cli]
```

## Key Classes

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

### uri2ops.operation_registry.models.OperationRegistry
- **Methods**: 3
- **Key Methods**: uri2ops.operation_registry.models.OperationRegistry.get, uri2ops.operation_registry.models.OperationRegistry.require, uri2ops.operation_registry.models.OperationRegistry.list

### packages.uri3.uri3.resolvers.router.Uri3Router
- **Methods**: 3
- **Key Methods**: packages.uri3.uri3.resolvers.router.Uri3Router.__init__, packages.uri3.uri3.resolvers.router.Uri3Router.resolve, packages.uri3.uri3.resolvers.router.Uri3Router.call

### hypervisor.contract_registry.models.ContractRegistry
- **Methods**: 3
- **Key Methods**: hypervisor.contract_registry.models.ContractRegistry.resource_by_uri, hypervisor.contract_registry.models.ContractRegistry.view_by_name, hypervisor.contract_registry.models.ContractRegistry.capability_by_name

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

### packages.uri3.uri3.results.service_result.ServiceResult
- **Methods**: 3
- **Key Methods**: packages.uri3.uri3.results.service_result.ServiceResult.finalize, packages.uri3.uri3.results.service_result.ServiceResult._default_error_source, packages.uri3.uri3.results.service_result.ServiceResult.to_dict

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

### packages.uri3.uri3.resolvers.log_resolver.LogResolver
- **Methods**: 2
- **Key Methods**: packages.uri3.uri3.resolvers.log_resolver.LogResolver.resolve, packages.uri3.uri3.resolvers.log_resolver.LogResolver.read

### hypervisor.config.models.HypervisorConfig
- **Methods**: 2
- **Key Methods**: hypervisor.config.models.HypervisorConfig.from_dict, hypervisor.config.models.HypervisorConfig.to_dict

### packages.resource-agent-hypervisor.hypervisor.deployment_registry.models.DeploymentRegistry
- **Methods**: 2
- **Key Methods**: packages.resource-agent-hypervisor.hypervisor.deployment_registry.models.DeploymentRegistry.by_id, packages.resource-agent-hypervisor.hypervisor.deployment_registry.models.DeploymentRegistry.by_agent_ref

## Data Transformation Functions

Key functions that process and transform data:

### uri2ops.cli.validate_cmd
- **Output to**: validate_task_file, uri2ops.cli._print, uri2ops.cli._print

### uri2ops.operation_registry.validator.validate_registry_schema
- **Output to**: json.loads, None.read_text, sorted, uri2ops.operation_registry.loader.registry_schema_path, uri2ops.operation_registry.models.OperationRegistry.list

### uri2ops.operation_registry.validator.validate_operation_registry
- **Output to**: registry.list, errors.append, spec.handler.startswith, errors.append, spec.handler.removeprefix

### uri2ops.server.service.OperatorService.validate_task
- **Output to**: validate_task_data, self.registry

### packages.uri3.uri3.logs.parsing.parse_json_entry
- **Output to**: line.strip, json.loads, isinstance, None.upper, data.get

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

### packages.uri3.uri3.protocols.schemes.instance_parser._parse_pypi
- **Output to**: hypervisor.uri2llm.pypi_resolver.resolve_pypi

### packages.uri3.uri3.protocols.schemes.instance_parser._parse_http
- **Output to**: packages.uri3.uri3.resolvers.protocol_resolver.resolve_http_like

### packages.uri3.uri3.protocols.schemes.instance_parser._parse_a2a
- **Output to**: packages.uri3.uri3.resolvers.protocol_resolver.resolve_a2a

### packages.uri3.uri3.protocols.schemes.instance_parser._parse_mcp
- **Output to**: packages.uri3.uri3.resolvers.protocol_resolver.resolve_mcp

### packages.uri3.uri3.protocols.schemes.instance_parser._parse_docker
- **Output to**: packages.uri3.uri3.resolvers.docker_resolver.resolve_docker

### packages.uri3.uri3.protocols.schemes.instance_parser._parse_ssh
- **Output to**: packages.uri3.uri3.resolvers.ssh_resolver.resolve_ssh

## Behavioral Patterns

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

- `uri2ops.server.app.create_app` - 62 calls
- `packages.uri3.uri3.cli.commands.discovery.register` - 47 calls
- `packages.touri.touri.loader.load_manifest` - 40 calls
- `packages.uri3.uri3.graph.graph_executor.run_workflow` - 39 calls
- `uri2ops.cli.main` - 33 calls
- `hypervisor.contract_registry.loader.load_contract_registry` - 33 calls
- `packages.uri3.uri3.config.llm_profiles.resolve_llm_profile` - 32 calls
- `packages.touri.touri.data_quality.apply_data_quality` - 31 calls
- `meta_agent.planner.infer_intent` - 30 calls
- `packages.resource-agent-hypervisor.hypervisor.domain_pack.pack_writer.write_domain_pack` - 30 calls
- `packages.nl2uri.nl2uri.flow_planner.plan_flow` - 29 calls
- `uri3.graph.uri_graph.build_graph_from_tree` - 28 calls
- `packages.nl2uri.nl2uri.flow_repair.extract_flow_payload` - 28 calls
- `hypervisor.config.models.HypervisorConfig.from_dict` - 26 calls
- `packages.uri3.uri3.protocols.schemes.spec_registry.build_scheme_registry` - 25 calls
- `packages.nl2uri.nl2uri.graph_repair.sanitize_node` - 25 calls
- `packages.nl2uri.nl2uri.graph_repair.repair_graph_body` - 25 calls
- `packages.resource-agent-hypervisor.meta_agent.cli.main` - 25 calls
- `packages.touri.touri.backends.python_backend.call_python_backend` - 25 calls
- `packages.uri3.uri3.graph.graph_serializer.normalize_graph_payload` - 24 calls
- `packages.uri3.uri3.cli.commands.resolve.register` - 24 calls
- `generator.model.load_agent_spec` - 24 calls
- `packages.nl2uri.nl2uri.flow_repair.sanitize_flow_step` - 24 calls
- `packages.uri3.uri3.graph.adapters.browser_playwright.PlaywrightBrowserAdapter.execute` - 23 calls
- `packages.uri3.uri3.resolvers.docker_resolver.parse_docker_uri` - 23 calls
- `packages.uri3.uri3.cli.commands.workflow.register` - 20 calls
- `packages.uri3.uri3.cli.commands.flow.run_flow_cmd` - 20 calls
- `uri2ops.remote_registry.loader.resolve_operation_registry` - 18 calls
- `packages.uri3.uri3.logs.reader.summarize_logs` - 18 calls
- `packages.uri3.uri3.graph.adapters.registry.AssertionAdapter.execute` - 18 calls
- `packages.uri3.uri3.resolvers.env_resolver.call_env` - 17 calls
- `packages.resource-agent-factory.generator.agent_generator.generate_agent` - 17 calls
- `packages.nl2uri.nl2uri.cli.flow` - 17 calls
- `packages.nl2uri.nl2uri.flow_repair.repair_flow_body` - 17 calls
- `packages.resource-agent-hypervisor.hypervisor.config.defaults.apply_builtin_defaults` - 17 calls
- `hypervisor.config.env.apply_structured_env_overrides` - 17 calls
- `packages.resource-agent-hypervisor.hypervisor.deployment_registry.lifecycle.stop_agent` - 17 calls
- `packages.resource-agent-hypervisor.hypervisor.deployment_registry.status.deployment_from_uri_tree` - 17 calls
- `packages.uri3.uri3.results.errors.normalize_error` - 17 calls
- `packages.uri3.uri3.resolvers.explain.explain_uri` - 17 calls

## System Interactions

How components interact:

```mermaid
graph TD
    register --> command
    register --> Option
    main --> ArgumentParser
    main --> add_subparsers
    main --> add_parser
    from_dict --> cls
    from_dict --> str
    from_dict --> get
    from_dict --> bool
    build_scheme_registr --> spec
    main --> add_argument
    register --> validate_uri
    execute --> _session_state
    execute --> get
    execute --> execute
    execute --> urlparse
    execute --> str
    register --> validate_workflow_gr
    register --> echo
    execute --> resolve_ref
    execute --> endswith
    flow --> command
    flow --> Option
    from_mapping --> cls
    from_mapping --> get
    task --> command
    task --> Option
    graph --> command
    graph --> Option
    plan --> command
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.
# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_uri_smoke_agent.yaml
# Contract hash: sha256:92e4d835ecacc5e7138946e5012d5948102fc79fd492458ffb981bd857372c38

# ruff: noqa: E501

AGENT_CARD = {'name': 'codex-uri-smoke-agent',
 'version': '0.1.0',
 'description': 'Smoke-test agent for file and physical-operation URI provenance.',
 'generated_from': {'contract': 'contracts/agents/codex_uri_smoke_agent.yaml',
                    'contract_hash': 'sha256:92e4d835ecacc5e7138946e5012d5948102fc79fd492458ffb981bd857372c38'},
 'capabilities': [{'name': 'read_markpact_source',
                   'type': 'resource_read',
                   'description': 'Read the generated agent README through a file URI.',
                   'uri': 'file:///home/tom/github/wronai/hypervisor/agents/generated/codex_uri_smoke_agent/README.md',
                   'output_schema': 'app.codex.v1.MarkpactSourceView',
                   'renderer': 'text',
                   'command': None,
                   'input_schema': None,
                   'emits': []},
                  {'name': 'read_device_status',
                   'type': 'resource_read',
                   'description': 'Read mock device status through uri2ops.',
                   'uri': 'device://device/sensor-1/status',
                   'output_schema': 'operator.device.v1.DeviceStatus',
                   'renderer': 'detail',
                   'command': None,
                   'input_schema': None,
                   'emits': []},
                  {'name': 'run_cron_monitor',
                   'type': 'command',
                   'description': 'Command placeholder for cron monitor integration.',
                   'uri': None,
                   'output_schema': None,
                   'renderer': None,
                   'command': 'RunCronMonitor',
                   'input_schema': 'app.codex.v1.RunCronMonitorCommand',
                   'emits': ['CronMonitorRequested']}]}

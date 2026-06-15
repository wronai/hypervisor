# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_nl_smoke_agent.yaml
# Contract hash: sha256:1e2da71bd316b85b830c1a1f69f333c7e5ac2b01e83258383005f0967dde488c

# ruff: noqa: E501

AGENT_CARD = {'name': 'codex-nl-smoke-agent',
 'version': '0.1.0',
 'description': 'Generated from NL prompt: stworz nowego agenta codex-nl-smoke-agent, '
                'ktory czyta file:// README, sprawdza device://device/sensor-1/status '
                'i ma komende cron monitor',
 'generated_from': {'contract': 'contracts/agents/codex_nl_smoke_agent.yaml',
                    'contract_hash': 'sha256:1e2da71bd316b85b830c1a1f69f333c7e5ac2b01e83258383005f0967dde488c'},
 'capabilities': [{'name': 'read_markpact_source',
                   'type': 'resource_read',
                   'description': 'Read generated agent README/provenance through '
                                  'file://.',
                   'uri': 'file:///home/tom/github/wronai/hypervisor/agents/generated/codex_nl_smoke_agent/README.md',
                   'output_schema': 'app.codex.v1.MarkpactSourceView',
                   'renderer': 'text',
                   'command': None,
                   'input_schema': None,
                   'emits': []},
                  {'name': 'read_device_status',
                   'type': 'resource_read',
                   'description': 'Read device status through uri2ops.',
                   'uri': 'device://device/sensor-1/status',
                   'output_schema': 'operator.device.v1.DeviceStatus',
                   'renderer': 'detail',
                   'command': None,
                   'input_schema': None,
                   'emits': []},
                  {'name': 'run_cron_monitor',
                   'type': 'command',
                   'description': 'Dispatch a scheduled monitor command.',
                   'uri': None,
                   'output_schema': None,
                   'renderer': None,
                   'command': 'RunCronMonitor',
                   'input_schema': 'app.codex.v1.RunCronMonitorCommand',
                   'emits': ['CronMonitorRequested']}]}

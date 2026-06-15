# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_nl_plan_agent.yaml
# Contract hash: sha256:2d9bc1c0b851ce7acae3b9134afc15449ddc5fe881c3fdb439c4077b9df4c699

# ruff: noqa: E501

AGENT_CARD = {'name': 'codex-nl-plan-agent',
 'version': '0.1.0',
 'description': 'Generated from NL prompt: stworz nowego agenta codex-nl-plan-agent, '
                'ktory czyta file:// README, sprawdza device://device/sensor-1/status '
                'i ma komende cron monitor',
 'generated_from': {'contract': 'contracts/agents/codex_nl_plan_agent.yaml',
                    'contract_hash': 'sha256:2d9bc1c0b851ce7acae3b9134afc15449ddc5fe881c3fdb439c4077b9df4c699'},
 'capabilities': [{'name': 'read_markpact_source',
                   'type': 'resource_read',
                   'description': 'Read generated agent README/provenance through '
                                  'file://.',
                   'uri': 'file:///app/agents/generated/codex_nl_plan_agent/README.md',
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
                   'description': 'Dispatch a scheduled monitor through cron:// URI.',
                   'uri': 'cron://www/monitor/landing',
                   'output_schema': None,
                   'renderer': None,
                   'command': 'RunCronMonitor',
                   'input_schema': 'app.codex.v1.RunCronMonitorCommand',
                   'emits': ['CronMonitorRequested']}]}

# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/schema_collab_agent.yaml
# Contract hash: sha256:17b3d806a8ebef60fa04b5234c2f32ccc2b94d7745234e05cbbd5c7e51bb4bd3

# ruff: noqa: E501

AGENT_CARD = {'name': 'schema-collab-agent',
 'version': '0.1.0',
 'description': 'Generated from NL prompt: stworz nowego agenta schema-collab-agent, '
                'ktory czyta file:// README, sprawdza device://device/sensor-1/status '
                'i robot://robot/amr-1/state oraz ma komende cron monitor',
 'generated_from': {'contract': 'contracts/agents/schema_collab_agent.yaml',
                    'contract_hash': 'sha256:17b3d806a8ebef60fa04b5234c2f32ccc2b94d7745234e05cbbd5c7e51bb4bd3'},
 'capabilities': [{'name': 'read_markpact_source',
                   'type': 'resource_read',
                   'description': 'Read generated agent README/provenance through '
                                  'file://.',
                   'uri': 'file://agents/generated/schema_collab_agent/README.md',
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
                  {'name': 'read_robot_state',
                   'type': 'resource_read',
                   'description': 'Read robot state through uri2ops.',
                   'uri': 'robot://robot/amr-1/state',
                   'output_schema': 'operator.robot.v1.RobotState',
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

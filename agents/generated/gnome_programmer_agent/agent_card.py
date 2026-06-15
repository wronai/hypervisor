# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/gnome_programmer_agent.yaml
# Contract hash: sha256:7b1bcba0139f125676c81df01f1bc3a4296937cf3a4ee3f06fcd7ff9efd0943e

# ruff: noqa: E501

AGENT_CARD = {'name': 'gnome-programmer-agent',
 'version': '0.1.0',
 'description': 'Observe and interact with Ubuntu GNOME desktop through '
                'desktop-operator.',
 'generated_from': {'contract': 'contracts/agents/gnome_programmer_agent.yaml',
                    'contract_hash': 'sha256:7b1bcba0139f125676c81df01f1bc3a4296937cf3a4ee3f06fcd7ff9efd0943e'},
 'capabilities': [{'name': 'observe_desktop',
                   'type': 'command',
                   'description': 'Capture GNOME desktop screenshot and window list '
                                  'via desktop-operator.',
                   'uri': 'screen://desktop/observe',
                   'output_schema': 'app.desktop.v1.DesktopObservation',
                   'renderer': 'detail',
                   'command': 'ObserveDesktop',
                   'input_schema': 'app.desktop.v1.ObserveDesktopCommand',
                   'emits': []},
                  {'name': 'type_on_desktop',
                   'type': 'command',
                   'description': 'Type text into focused GNOME window via '
                                  'ydotool/xdotool through desktop-operator.',
                   'uri': 'input://desktop/type',
                   'output_schema': 'app.desktop.v1.DesktopInputResult',
                   'renderer': 'detail',
                   'command': 'TypeOnDesktop',
                   'input_schema': 'app.desktop.v1.TypeOnDesktopCommand',
                   'emits': []},
                  {'name': 'programmer_session',
                   'type': 'command',
                   'description': 'Observe desktop, optionally type a command snippet, '
                                  'and persist session notes.',
                   'uri': 'workflow://desktop/programmer-session',
                   'output_schema': 'app.desktop.v1.ProgrammerSessionResult',
                   'renderer': 'detail',
                   'command': 'RunProgrammerSession',
                   'input_schema': 'app.desktop.v1.ProgrammerSessionCommand',
                   'emits': []}]}

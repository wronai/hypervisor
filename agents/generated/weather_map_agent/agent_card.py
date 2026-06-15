# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/weather_map_agent.yaml
# Contract hash: sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485

# ruff: noqa: E501

AGENT_CARD = {'name': 'weather-map-agent',
 'version': '0.1.0',
 'description': 'Generate forecast weather maps as HTML URL artifacts.',
 'generated_from': {'contract': 'contracts/agents/weather_map_agent.yaml',
                    'contract_hash': 'sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485'},
 'capabilities': [{'name': 'read_weather_map',
                   'type': 'resource_read',
                   'description': 'Read generated weather map HTML view for a location '
                                  'and forecast horizon.',
                   'uri': 'resource://weather/maps/{place}/forecast/{days}',
                   'output_schema': 'app.weather.v1.WeatherMapHtmlView',
                   'renderer': 'html',
                   'command': None,
                   'input_schema': None,
                   'emits': []},
                  {'name': 'generate_weather_map',
                   'type': 'command',
                   'description': 'Generate a weather map forecast HTML view for a '
                                  'location.',
                   'uri': None,
                   'output_schema': None,
                   'renderer': None,
                   'command': 'GenerateWeatherMap',
                   'input_schema': 'app.weather.v1.GenerateWeatherMapCommand',
                   'emits': ['WeatherMapGenerationRequested', 'WeatherMapGenerated']}]}

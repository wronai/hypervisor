<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/weather_map_agent.yaml -->
<!-- Contract hash: sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485 -->
# weather-map-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/weather_map_agent.yaml`
- Contract hash: `sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485`
- Generator: `resource-agent-factory`

## Run

```bash
uvicorn agents.generated.weather_map_agent.main:app --reload --port 8101
```

## Reproduce

```bash
PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/weather_map_agent.yaml
```

## Markpact provenance

```markpact:agent_generation weather-map-agent
agent:
  id: agent://weather-map-agent
  package: agents.generated.weather_map_agent
source:
  contract: contracts/agents/weather_map_agent.yaml
  contract_hash: sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485
generator:
  id: resource-agent-factory
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/weather_map_agent.yaml
runtime:
  default_run: uvicorn agents.generated.weather_map_agent.main:app --reload --port 8101
logs:
  hypervisor: log://hypervisor?grep=weather-map-agent.local
  process: log://file/output/logs/agents/weather-map-agent.local.process.log
```

```markpact:run_log weather-map-agent.local.latest
inspect:
  command: hypervisor inspect-agent weather-map-agent.local
  uri: view://process/agent/weather-map-agent.local/latest
logs:
  hypervisor: log://hypervisor?grep=weather-map-agent.local
  process: log://file/output/logs/agents/weather-map-agent.local.process.log
```

## Endpoints

```txt
GET /health
GET /capabilities
GET /.well-known/agent.json
GET /.well-known/agent-card.json
GET /resources/read?uri=...
POST /commands
```

## Capabilities

- `read_weather_map` — `resource_read`, URI: `resource://weather/maps/{place}/forecast/{days}`

- `generate_weather_map` — `command`, command: `GenerateWeatherMap`


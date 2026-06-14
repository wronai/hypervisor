<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/weather_map_agent.yaml -->
<!-- Contract hash: sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485 -->
# weather-map-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/weather_map_agent.yaml`
- Contract hash: `sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485`

## Run

```bash
uvicorn agents.generated.weather_map_agent.main:app --reload --port 8101
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

- `read_weather_map` — `resource_read`, URI: `resource://weather/maps/{place}/forecast/{days}`- `generate_weather_map` — `command`, command: `GenerateWeatherMap`
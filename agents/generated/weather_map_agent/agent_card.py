# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/weather_map_agent.yaml
# Contract hash: sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485

AGENT_CARD = {
  "capabilities": [
    {
      "command": null,
      "description": "Read generated weather map HTML view for a location and forecast horizon.",
      "emits": [],
      "input_schema": null,
      "name": "read_weather_map",
      "output_schema": "app.weather.v1.WeatherMapHtmlView",
      "renderer": "html",
      "type": "resource_read",
      "uri": "resource://weather/maps/{place}/forecast/{days}"
    },
    {
      "command": "GenerateWeatherMap",
      "description": "Generate a weather map forecast HTML view for a location.",
      "emits": [
        "WeatherMapGenerationRequested",
        "WeatherMapGenerated"
      ],
      "input_schema": "app.weather.v1.GenerateWeatherMapCommand",
      "name": "generate_weather_map",
      "output_schema": null,
      "renderer": null,
      "type": "command",
      "uri": null
    }
  ],
  "description": "Generate forecast weather maps as HTML URL artifacts.",
  "generated_from": {
    "contract": "contracts/agents/weather_map_agent.yaml",
    "contract_hash": "sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485"
  },
  "name": "weather-map-agent",
  "version": "0.1.0"
}
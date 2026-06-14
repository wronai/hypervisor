# uri2llm routing layer

`uri2llm` is the hypervisor routing layer that resolves typed URI addresses into models, secrets, protocols, functions, packages, resources and artifacts.

## Supported URI schemes

```txt
env://OPENROUTER_API_KEY
llm://openrouter/qwen/qwen3-coder-next
python://domains.weather_map.handlers.generate_weather_map:handler
pypi://httpx
resource://weather/maps/{place}/forecast/{days}
domain://weather-map
a2a://weather-map-agent/.well-known/agent-card.json
mcp://weather-map-agent/resources/read
artifact://weather-map/Gdansk/forecast/14/index.html
```

## Rules

- LLM may reference `env://...` but must not read or print secret values.
- LLM may propose `pypi://...` dependencies, but policy gate decides whether they are allowed.
- Generated handlers should be referenced by `python://...` and called through `uri2llm.call`.
- A2A/MCP endpoints are protocol addresses, not core domain logic.

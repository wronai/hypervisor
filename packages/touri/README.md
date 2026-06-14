# touri

`touri` maps new URI schemes/templates to reusable capabilities without creating a new library for every URI.

Core idea:

```txt
URI -> capability manifest -> backend -> service result
```

Example:

```yaml
version: 1
capability:
  id: weather.forecast.html
  scheme: weather
  uri_template: weather://forecast/{place}/{days}/html
  operation: generate
  kind: command
backend:
  type: python
  target: python://examples.hello_weather:handler
```

Run:

```bash
pip install -e packages/touri
touri validate examples/20_touri_capabilities/weather_forecast.uri.capability.yaml
touri list examples/20_touri_capabilities
touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities
```

`touri` does not replace `uri3`, `uri2flow`, `uri2ops`, or hypervisor. It is the generic capability layer used when a URI should be backed by an existing function, shell script, HTTP service, Docker action, MCP tool, A2A skill, flow, or graph.

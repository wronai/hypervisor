# Example 20: touri capabilities

`touri` lets you create new URI capabilities by manifest, reusing existing code or services.

```bash
pip install -e packages/touri
touri validate examples/20_touri_capabilities/weather_forecast.uri.capability.yaml
touri list examples/20_touri_capabilities
touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities
touri call echo://Adam --registry examples/20_touri_capabilities
```

This example creates `weather://forecast/{place}/{days}/html` backed by an existing Python handler.

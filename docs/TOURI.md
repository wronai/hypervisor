# touri

`touri` is a generic URI-to-capability layer.

It solves this problem:

> Do not create a new library for every new URI. Create a capability manifest that maps the URI to an existing function, script, service, flow, graph, MCP tool, A2A skill, Docker action, or HTTP endpoint.

## Role in the architecture

```txt
nl2uri      -> prompt -> flow/tree/graph
uri2flow    -> compact flow -> workflow graph
uri3        -> URI validation, routing, graph execution
uri2ops     -> OS/UI/browser operations
touri       -> generic new URI -> reusable capability backend
hypervisor  -> lifecycle, policy, deployment, registry
```

## Manifest naming

Use:

```txt
*.uri.capability.yaml
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
  target: python://touri_examples.weather:handler
```

## Backends

MVP supports:

- `python`
- `mock`
- `shell`

Planned:

- `http`, `docker`, `mcp`, `a2a`, `uri_flow`, `uri_graph`, `uri2ops`

## Data quality

Capability manifests may declare validation policy:

```yaml
data_quality:
  relevance_required: true
  min_confidence: 0.75
  failure_code: PRICE_RESULT_NOT_RELEVANT
  validators:
    - python://validators.price:validate_relevance
```

Results use the shared [`ServiceResult`](./SERVICE_RESULT.md) envelope with three status levels. See [`ANTI_TELLM.md`](./ANTI_TELLM.md).

## URI resolution

```bash
uri3 explain weather://forecast/Gdansk/14/html
```

Resolution order: uri3 → touri → uri2ops → hypervisor → denied (`config/touri.uri.yaml`).

## Security

Secrets should be referenced by URI, not embedded directly:

```yaml
api_key: env://OPENROUTER_API_KEY
```

`touri` should return structured service results and avoid logging secret payloads.

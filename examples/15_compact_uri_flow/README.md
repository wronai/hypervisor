# Example 15 — Compact URI Flow

Preferowany format dla autorów (human/LLM) — krótki zapis oparty na URI:

```yaml
flow:
  id: weather-agent-local-health

do:
  - agent://weather-generator
  - hypervisor://local/weather-agent/run
  - browser://chrome/page/open:
      url: http://localhost:8101/health
```

`uri2flow` rozwija ten zapis do pełnego `workflow_graph`, który waliduje i wykonuje `uri3`. **`uri2flow` nic nie wykonuje** — tylko kompilacja.

## Komendy

```bash
uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml
uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
uri2flow print examples/15_compact_uri_flow/weather.uri.flow.yaml

# dalej uri3
uri3 validate-workflow output/weather.uri.graph.yaml
uri3 plan-workflow output/weather.uri.graph.yaml
uri3 run-workflow output/weather.uri.graph.yaml --approve --browser mock
```

Makefile:

```bash
make uri2flow-validate uri2flow-expand
```

## Gałęzie (`id` + `after`)

Zobacz [`branching.uri.flow.yaml`](./branching.uri.flow.yaml):

```yaml
do:
  - id: run_agent
    uri: hypervisor://local/weather-agent/run

  - id: check_health
    uri: http://localhost:8101/health
    after: run_agent
```

## Demo

```bash
bash examples/15_compact_uri_flow/run.sh
```

## Port drift

Flow YAML may hardcode `localhost:8101` while hypervisor rebinds the agent to another port (e.g. `8118`).
`health://agent/weather-map-agent.local` uses the **effective** port from inspect.
See [`docs/CHAT_AND_WORKFLOWS.md`](../../docs/CHAT_AND_WORKFLOWS.md#agent-ports-and-health-uri-drift).

## Pipeline

```txt
nl2uri (optional) -> compact *.uri.flow.yaml -> uri2flow expand -> uri3 run-workflow -> uri2ops
```

Dokumentacja: [`docs/URI2FLOW.md`](../../docs/URI2FLOW.md) · [`packages/uri2flow/docs/FLOW_FORMAT.md`](../../packages/uri2flow/docs/FLOW_FORMAT.md)

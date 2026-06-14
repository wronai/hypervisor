# uri2flow

`uri2flow` to lekki kompilator **compact URI flow → expanded workflow graph** dla pipeline `nl2uri → uri3`.

Nie wykonuje workflow — tylko parsuje, normalizuje i rozwija krótki format YAML do pełnego `workflow_graph`, który przejmuje `uri3` (validate/plan/run) lub dalej `uri2ops`.

## Rola w systemie

```txt
nl2uri    → natural language → compact URI flow / URI graph
uri2flow  → compact URI flow → expanded workflow graph
uri3      → validate, plan, route, run-workflow
uri2ops   → execute UI/OS/browser operations
hypervisor → lifecycle, deployment, policy
```

## Format wejściowy

```yaml
flow:
  id: weather-agent-local-health

do:
  - agent://weather-generator
  - hypervisor://local/weather-agent/run
  - browser://chrome/page/open:
      url: http://localhost:8101/health
```

Gałęzie przez `id` + `after`:

```yaml
do:
  - id: run_agent
    uri: hypervisor://local/weather-agent/run
  - id: check_health
    uri: http://localhost:8101/health
    after: run_agent
```

Pełna specyfikacja: [`packages/uri2flow/docs/FLOW_FORMAT.md`](../packages/uri2flow/docs/FLOW_FORMAT.md).

## CLI

```bash
uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml
uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
uri2flow print examples/15_compact_uri_flow/weather.uri.flow.yaml
```

Makefile:

```bash
make uri2flow-validate
make uri2flow-expand
make uri2flow-test
```

## Pipeline z uri3

```bash
uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
uri3 validate-workflow output/weather.uri.graph.yaml
uri3 plan-workflow output/weather.uri.graph.yaml
uri3 run-workflow output/weather.uri.graph.yaml --approve --browser mock
```

## Instalacja

Z root repo (entry point w root `pyproject.toml`):

```bash
pip install -e '.[dev]'
```

Osobno:

```bash
pip install -e packages/uri2flow
```

## Powiązane

- [`packages/uri2flow/README.md`](../packages/uri2flow/README.md)
- [`examples/15_compact_uri_flow/`](../examples/15_compact_uri_flow/README.md)
- [`docs/URI3.md`](./URI3.md) — workflow executor
- [`docs/NL2URI.md`](./NL2URI.md) — generowanie planów z NL

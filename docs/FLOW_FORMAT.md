# Compact URI Flow Format

Preferowany format wejściowy dla autorów (human/LLM). Pełny `workflow_graph` jest formatem pośrednim/maszynowym.

## Konwencja plików

| Rozszerzenie | Rola |
|--------------|------|
| `*.uri.flow.yaml` | format wejściowy (compact) |
| `*.uri.graph.yaml` | rozwinięty workflow graph (build artifact) |

## Linear flow

```yaml
flow:
  id: weather-agent-health

do:
  - agent://weather-generator
  - hypervisor://local/weather-agent/run
  - browser://chrome/page/open:
      url: http://localhost:8101/health
```

Oznacza sekwencję: `A → B → C`.

## URI step z payload

```yaml
do:
  - browser://chrome/page/open:
      url: http://localhost:8101/health
```

## Gałęzie (`id` + `after`)

```yaml
do:
  - id: run_agent
    uri: hypervisor://local/weather-agent/run

  - id: check_health
    uri: http://localhost:8101/health
    after: run_agent

  - id: read_card
    uri: http://localhost:8101/.well-known/agent-card.json
    after: run_agent
```

## Warunki (`if`)

```yaml
  - id: logs_if_failed
    uri: log://weather-map-agent.local?limit=100
    after: check_health
    if: check_health.ok == false
```

## Pipeline

```txt
nl2uri flow -p "..."     → compact flow YAML
uri2flow expand          → workflow_graph
uri3 validate-workflow   → walidacja graph
uri3 run-workflow        → wykonanie (mock/playwright)
```

Skróty:

```bash
nl2uri flow -p "wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome"
nl2uri flow -p "..." --llm --validate --expand
uri3 expand-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
uri3 run-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --dry-run
uri3 run-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --approve --browser mock
```

## Defaults operacji

Mapowanie `URI → operation/kind` pochodzi wyłącznie z [`config/flow_defaults.uri.yaml`](../config/flow_defaults.uri.yaml) (scheme defaults, patterns, fallback). Nie wpisuj `operation`/`kind` ręcznie w compact flow, chyba że chcesz nadpisać domyślne zachowanie.

LLM compact flow (`nl2uri flow --llm`) przechodzi przez `flow_repair` (normalizacja kroków, `after`/`if`, ids) i `validate_expanded_flow` (parse → expand → uri3 validate).

## Powiązane

- [`docs/URI2FLOW.md`](URI2FLOW.md)
- [`docs/NL2URI.md`](NL2URI.md)
- [`packages/uri2flow/docs/FLOW_FORMAT.md`](../packages/uri2flow/docs/FLOW_FORMAT.md)

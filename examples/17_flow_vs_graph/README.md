# Example 17 — Flow vs Graph

Porównanie **compact URI flow** (format wejściowy) i **expanded workflow graph** (artefakt maszynowy).

## Pliki

| Plik | Opis |
|------|------|
| [`weather.uri.flow.yaml`](weather.uri.flow.yaml) | compact flow (human/LLM) |
| [`expanded.expected.uri.graph.yaml`](expanded.expected.uri.graph.yaml) | oczekiwany wynik `uri2flow expand` |

## Pipeline

```bash
# 1. NL → compact flow
nl2uri flow -p "wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome"

# 2. expand → graph
uri3 expand-flow examples/17_flow_vs_graph/weather.uri.flow.yaml \
  --out output/weather.uri.graph.yaml

# 3. dry-run plan
uri3 run-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --dry-run

# 4. mock execute
uri3 run-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --approve --browser mock
```

## Demo

```bash
bash examples/17_flow_vs_graph/run.sh
```

## Zasada

```txt
*.uri.flow.yaml  = format wejściowy
*.uri.graph.yaml = format pośredni (nie pisz ręcznie nodes/depends_on/kind)
```

Dokumentacja: [`docs/FLOW_FORMAT.md`](../../docs/FLOW_FORMAT.md)

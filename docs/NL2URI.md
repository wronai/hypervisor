# nl2uri

`nl2uri` tłumaczy query w języku naturalnym na plany URI — od pojedynczego adresu po graf workflow z warunkami.

## CLI — tryby wyjścia

| Komenda | `kind` | Kiedy używać |
|---------|--------|--------------|
| `nl2uri single` | `single_uri` | jeden zasób (status, health) |
| `nl2uri list` | `uri_list` | kilka niezależnych odczytów |
| `nl2uri tree` | `uri_tree` | hierarchia domeny (Domain Pack) |
| `nl2uri task` | `task_graph` | liniowy proces (Chrome → DOM → assertion) |
| `nl2uri flow` | `uri_flow` | compact flow (*.uri.flow.yaml) — preferowany dla sekwencji |
| `nl2uri graph` | `workflow_graph` | workflow z warunkami i gałęziami |
| `nl2uri plan` | auto | klasyfikuje prompt i wybiera tryb |
| `nl2uri classify` | — | tylko klasyfikacja (`kind`) bez generacji |
| `nl2uri generate` | `uri_tree` | wsteczna kompatybilność (URI Tree + `--out`) |

```bash
# auto — klasyfikuje i generuje najlepszy plan
nl2uri plan -p "otwórz Chrome i sprawdź localhost:8101/health"

# jawne tryby
nl2uri single -p "pokaż status agenta pogodowego"
nl2uri list   -p "sprawdź health agenta i pokaż agent card"
nl2uri tree   -p "wygeneruj domenę weather map" --no-llm --out domains/weather_map/uri_tree.yaml
nl2uri task   -p "otwórz Chrome i sprawdź localhost:8101/health" --validate --dry-run
nl2uri flow   -p "wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome" --validate
nl2uri graph  -p "wygeneruj agenta, uruchom go, sprawdź health" --llm --validate

# klasyfikacja bez generacji
nl2uri classify -p "otwórz Chrome i sprawdź health"
```

Bez `--out` wypisuje YAML/JSON na stdout (`--json` dla JSON).

### Walidacja i dry-run

Dla `flow`, `task` i `graph`:

```bash
nl2uri flow -p "..." --validate          # uri2flow validate + expand + uri3 validate-workflow
nl2uri flow -p "..." --llm --validate  # LLM compact flow + repair + validate
nl2uri flow -p "..." --repair            # normalizacja compact flow (after/if, ids)
nl2uri task -p "..." --validate          # uri3 validate-workflow
nl2uri graph -p "..." --validate --dry-run   # + plan wykonania uri3
```

### LLM vs deterministyczny planner

| Tryb | Źródło |
|------|--------|
| `--no-llm` | deterministyczny szablon / graph planner regułowy |
| `--llm` | LLM planner: `flow` → compact flow + repair; `task`/`graph` → workflow graph + repair |
| domyślnie | `NL2URI_USE_LLM` / `NL2A_USE_LLM` env (domyślnie off) |

Dla promptów pogodowych (`pogod`, `weather`, `forecast`, `map`) LLM **nie może zastąpić** uproszczonym drzewem list URI — planner użyje kanonicznego szablonu `weather_map` i doda `planner_warning`.

Bez `--no-llm` i z włączonym LLM wymagany jest `OPENROUTER_API_KEY` (lub fallback deterministyczny przy błędzie API).

## Pipeline z uri3

```bash
nl2uri graph -p "$(cat prompt.txt)" --validate > workflow.yaml
uri3 validate-workflow workflow.yaml
uri3 plan-workflow workflow.yaml
uri3 run-workflow workflow.yaml --approve --browser mock
```

Alternatywnie operator runtime:

```bash
uri2ops validate task.yaml
uri2ops run task.yaml --adapter auto --approve
```

## Compact URI flow (uri2flow)

Dla autorów (human/LLM) preferowany jest krótki format `*.uri.flow.yaml`:

```yaml
flow:
  id: weather-agent-local-health

do:
  - agent://weather-generator
  - hypervisor://local/weather-agent/run
  - browser://chrome/page/open:
      url: http://localhost:8101/health
```

```bash
nl2uri flow -p "wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome" --validate
uri3 run-flow output/weather.uri.flow.yaml --dry-run
uri3 run-flow output/weather.uri.flow.yaml --approve --browser mock
```

Alternatywnie ręczny expand:

```bash
uri2flow expand flow.yaml --out workflow.yaml
uri3 validate-workflow workflow.yaml
uri3 run-workflow workflow.yaml --approve
```

Zobacz [`docs/URI2FLOW.md`](./URI2FLOW.md) · [`examples/15_compact_uri_flow/`](../examples/15_compact_uri_flow/README.md).

## Powiązane

- [`docs/URI3.md`](./URI3.md) — workflow executor
- [`docs/URI2OPS.md`](./URI2OPS.md) — operator runtime
- [`docs/NL2A_DOMAIN_PACKS.md`](./NL2A_DOMAIN_PACKS.md) — pełny pipeline z Domain Pack
- [`examples/13_nl2uri_multi_uri_graph/`](../examples/13_nl2uri_multi_uri_graph/README.md)
- [`examples/16_llm_graph_planner/`](../examples/16_llm_graph_planner/README.md)
- [`examples/04_nl2a_weather_map/`](../examples/04_nl2a_weather_map/README.md)

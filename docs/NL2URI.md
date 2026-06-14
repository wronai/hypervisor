# nl2uri

`nl2uri` tłumaczy query w języku naturalnym na `URI Tree`.

## CLI

```bash
nl2uri --no-llm -p "generuj mape pogody dwa tygodnie do przodu w html" \
  --out domains/weather_map/uri_tree.yaml
```

Bez `--out` wypisuje YAML/JSON na stdout.

### LLM vs deterministyczny planner

`nl2uri` i `nl2a` używają tego samego `domain_planner.plan_from_prompt()`:

| Tryb | Źródło |
|------|--------|
| `--no-llm` | deterministyczny szablon (weather_map ma pełny URI Tree) |
| z LLM | OpenRouter, ale wynik jest **walidowany** |

Dla promptów pogodowych (`pogod`, `weather`, `forecast`, `map`) LLM **nie może zastąpić** uproszczonym drzewem list URI — jeśli zwróci np.:

```yaml
domain: domain://weather
commands:
  - command://...
```

to planner automatycznie użyje kanonicznego szablonu `weather_map` i doda `planner_warning`.

Bez `--no-llm` wymagany jest `OPENROUTER_API_KEY` (lub fallback deterministyczny przy błędzie API).

## Zachowanie

- domyślnie próbuje LLM (OpenRouter przez `.env`),
- z `--no-llm` używa plannera regułowego (reprodukowalne testy),
- wynik waliduj przez `uri3 validate-tree`.

## Powiązane

- [`docs/NL2A_DOMAIN_PACKS.md`](./NL2A_DOMAIN_PACKS.md) — pełny pipeline z Domain Pack
- [`examples/04_nl2a_weather_map/`](../examples/04_nl2a_weather_map/README.md)
- [`examples/01_quickstart_local/`](../examples/01_quickstart_local/README.md)

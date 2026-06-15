# 13 — nl2uri multi-URI output (single / list / tree / task / graph)

Ten przykład pokazuje, że **jedno zdanie naturalne** może mapować się na różne struktury URI — nie tylko na pojedynczy adres.

## Podział odpowiedzialności

```txt
nl2uri  = rozumie prompt i produkuje plan (single, list, tree, task, graph)
uri3    = waliduje graf, sortuje zależności, buduje plan wykonania (dry-run)
hypervisor = lifecycle deploymentów, policy gate (w przyszłości: wykonanie command nodes)
```

## Tryby nl2uri

| Tryb | Kiedy | Przykład |
|------|-------|----------|
| `single` | jeden zasób | status agenta |
| `list` | kilka niezależnych odczytów | health + agent card |
| `tree` | hierarchia domeny | domain pack / URI Tree |
| `task` | liniowy proces | Chrome → DOM → assertion |
| `graph` | workflow z warunkami | generate → run → check → logs if failed |

## Szybki start

```bash
pip install -e '.[dev]'

# auto — klasyfikuje prompt i wybiera tryb
nl2uri plan -p "$(cat examples/13_nl2uri_multi_uri_graph/prompt.txt)"

# jawne tryby
nl2uri single -p "pokaż status agenta pogodowego"
nl2uri list   -p "sprawdź health agenta pogodowego i pokaż jego agent card"
nl2uri tree   -p "wygeneruj domenę weather map z agentem" --no-llm
nl2uri task   -p "otwórz Chrome i sprawdź localhost:8101/health" --validate --dry-run
nl2uri graph  -p "$(cat examples/13_nl2uri_multi_uri_graph/prompt.txt)" --validate

# uri3 — walidacja i plan wykonania
uri3 validate-workflow examples/13_nl2uri_multi_uri_graph/workflow_graph.yaml
uri3 plan-workflow examples/13_nl2uri_multi_uri_graph/workflow_graph.yaml
```

## Pełny demo skrypt

```bash
bash examples/13_nl2uri_multi_uri_graph/run.sh
```

Generuje m.in.:

- `output/examples/13_nl2uri_multi_uri_graph/workflow_graph.yaml` — workflow z node'ami `generate_*`, `run_*`, `open_health`, `verify_ok`, `read_logs_if_failed`
- `output/examples/13_nl2uri_multi_uri_graph/task_plan.yaml` — dry-run plan z uri3 (`nl2uri task --dry-run`)

Statyczne pliki `workflow_graph.yaml` i `task_plan.yaml` w katalogu przykładu są referencją
dla dokumentacji; skrypt demo ich nie nadpisuje.

## Schematy

- `schemas/workflow_graph.schema.json` — nodes, depends_on, condition
- `schemas/uri_graph.schema.json` — manifest `uri_graph:` do wykonania w uri3

## Nowe scheme URI (workflow)

`browser://`, `dom://`, `screen://`, `assertion://`, `hypervisor://` — zarejestrowane w uri3 jako scheme workflow (routing/discovery; adaptery wykonawcze w kolejnych wersjach).

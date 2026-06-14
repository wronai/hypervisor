# URI Operation Registry

Rejestr operacji mapuje schematy URI i nazwy operacji na handlery, semantykę CQRS i schematy wejścia/wyjścia.

- **Scheme registry** (uri3): „Czy `browser://…` jest poprawnym URI?”
- **Operation registry** (uri2ops): „Co mogę zrobić z `browser://…`, jaki schema waliduje payload i jaki handler to wykonuje?”

## Lokalizacja plików

```txt
uri2ops/operation_registry/registry.yaml     # kanoniczny registry pakietu (packages/uri2ops/uri2ops/...)
config/operator_registry.uri.yaml            # merge dla serve / remote
config/extra_operator_registry.yaml          # rozszerzenia projektu
schemas/operator_registry.schema.json        # JSON Schema walidacji
```

## Przykład wpisu

```yaml
browser:
  operations:
    open:
      kind: command
      handler: python://uri2ops.operator.adapters.browser_mock:open_page
      input_schema: operator.browser.v1.BrowserPageOpenCommand
      side_effects: true
      requires_policy: true
    extract_dom:
      kind: query
      handler: python://uri2ops.operator.adapters.browser_mock:extract_dom
      input_schema: operator.browser.v1.BrowserPageQuery
      side_effects: false
```

Handlery real backendów są w routerach (`browser_router`, `android_router`, `pcwin_router`) — wybór mock vs real przez `--adapter auto`.

## Semantyka CQRS

| `kind` | Mutacja | Policy |
|--------|---------|--------|
| `query` | tylko odczyt | domyślnie bez approve |
| `command` | może mutować stan zewnętrzny | `requires_policy: true` → `--approve` |

## Remote registry (v0.5)

`uri2ops serve` i `resolve_operation_registry()` ładują merge:

1. `packages/uri2ops/uri2ops/operation_registry/registry.yaml`
2. `config/operator_registry.uri.yaml`
3. `config/extra_operator_registry.yaml`

```bash
uri2ops registry list
uri2ops registry validate
curl http://127.0.0.1:8791/registry
```

## Protobuf / JSON Schema

Kontrakty operatora: [`contracts/proto/operator/`](../contracts/proto/operator/)

- `browser.proto`, `android.proto`, `common.proto`, `events.proto`, …

## Zasady

- `query` nie mutuje stanu zewnętrznego.
- `command` wymaga polityki approve (chyba że jawnie wyłączone w policy).
- Duże wyniki → `artifact://`, nie payload eventu.
- Sekrety nigdy w event log (redaction w `uri2ops/operator/redaction.py`).

## Powiązane

- [`docs/URI2OPS.md`](./URI2OPS.md)
- [`docs/OPERATOR_RUNTIME.md`](./OPERATOR_RUNTIME.md)
- [`docs/OPERATOR_SECURITY.md`](./OPERATOR_SECURITY.md)
- [`config/operator_policy.uri.yaml`](../config/operator_policy.uri.yaml)

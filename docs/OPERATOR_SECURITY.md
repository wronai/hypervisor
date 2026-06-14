# Operator Security

Wykonanie operatora może kontrolować przeglądarkę, urządzenia mobilne, okna systemowe i input. Traktuj to jak **automatyzację wysokiego ryzyka**.

## Zasady domyślne

- Operacje `command` ze `side_effects: true` wymagają `--approve` (CLI) lub jawnej polityki w [`config/operator_policy.uri.yaml`](../config/operator_policy.uri.yaml).
- Nie przekazuj sekretów w query string URI.
- Nie loguj wartości oznaczonych `secret: true` — redaction w `uri2ops/operator/redaction.py`.
- Screenshoty, DOM i dump UI → `artifact://`, nie body eventu JSONL.
- Event log zawiera metadane, hashe i URI artefaktów.

## Poziomy ryzyka (suggested)

| Poziom | Przykłady |
|--------|-----------|
| `observe` | screenshot, odczyt DOM, dump UI |
| `navigate` | otwarcie URL / aplikacji |
| `input` | kliknięcie, tap, focus |
| `submit` | potwierdzenie, wysłanie formularza |
| `system` | shell, instalator, zmiany systemowe |

Mapowanie risk → approve w `config/operator_policy.uri.yaml`.

## uri2ops serve

- Domyślnie bind `127.0.0.1` — nie wystawiaj na publiczny interfejs bez TLS i auth.
- MCP/A2A endpointy delegują do tego samego policy gate co CLI.
- Remote registry merge nie powinien nadpisywać handlerów bez review (extra registry w repo).

## uri3 run-workflow (MVP)

- `--approve` wymagane dla węzłów `command`.
- `--dry-run` omija policy blocks — tylko do planowania.
- Playwright E2E: uruchamiaj w izolowanym środowisku testowym.

## Powiązane

- [`docs/OPERATOR_RUNTIME.md`](./OPERATOR_RUNTIME.md)
- [`docs/URI_OPERATION_REGISTRY.md`](./URI_OPERATION_REGISTRY.md)
- [`docs/URI2OPS.md`](./URI2OPS.md)

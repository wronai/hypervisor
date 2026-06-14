# Operator Runtime

`uri2ops` wykonuje grafy zadań URI przez adaptery operatora. Hypervisor nie wykonuje akcji OS — deleguje do `uri2ops` (lub w MVP do uri3 `run-workflow`).

## Przepływ

```txt
URI task/workflow graph
  → validate (schema + registry)
  → topological sort (depends_on)
  → policy check (config/operator_policy.uri.yaml)
  → dispatch operation (registry lookup)
  → adapter execution (mock | playwright | adb | uia)
  → event JSONL + artifact:// URIs
```

## CLI

```bash
uri2ops validate task.yaml
uri2ops plan task.yaml
uri2ops run task.yaml --adapter mock --approve
uri2ops run task.yaml --adapter auto --approve
uri2ops serve --host 127.0.0.1 --port 8791
```

| Flaga | Opis |
|-------|------|
| `--adapter mock\|playwright\|adb\|uia\|auto` | Backend wykonania |
| `--approve` | Zezwolenie na operacje `command` ze side effects |
| `--dry-run` | Tylko plan (bez dispatch) |

## Adaptery (v0.1–v0.4)

| Adapter | Schemat | Real backend |
|---------|---------|--------------|
| Mock browser | `browser://` | Zawsze dostępny (testy) |
| Playwright | `browser://` | `pip install -e '.[browser]'` |
| Android | `android://device/{id}/…` | ADB + UI Automator |
| Windows UIA | `pcwin://window\|control/…` | `pip install -e '.[windows]'` |
| Assertion | `assertion://` | Mock check |

Sesja taska jest współdzielona między krokami (np. ta sama strona Playwright, to samo okno UIA).

## HTTP daemon (v0.5)

```bash
uri2ops serve --port 8791
```

Endpointy: `/health`, `/registry`, `/validate`, `/plan`, `/run`, A2A (`/.well-known/agent-card.json`, `/a2a/tasks`), MCP (`/mcp/tools`).

Przykład: [`examples/14_uri2ops_serve/`](../examples/14_uri2ops_serve/README.md).

## Relacja uri3 vs uri2ops

| Warstwa | Rola dziś |
|---------|-----------|
| uri3 `run-workflow` | MVP executor w monorepo (mock + Playwright browser) |
| uri2ops `run` | Pełny operator runtime (wszystkie adaptery, policy, serve) |

Docelowo uri3 `run-workflow` powinien delegować do uri2ops jako wspólnego backendu (patrz [`TODO.md`](../TODO.md)).

## Artefakty i eventy

- Event log: `output/events/operator/{task_id}.jsonl`
- Artefakty: `artifact://operator/workflows/{task_id}/{run_id}/{step_id}/…`
- Duże payloady (screenshot, DOM) → artifact URI, nie event body

## Powiązane

- [`docs/URI2OPS.md`](./URI2OPS.md)
- [`docs/URI_OPERATION_REGISTRY.md`](./URI_OPERATION_REGISTRY.md)
- [`docs/OPERATOR_SECURITY.md`](./OPERATOR_SECURITY.md)
- [`packages/uri2ops/README.md`](../packages/uri2ops/README.md)

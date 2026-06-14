# uri2ops

`uri2ops` to samodzielny pakiet **URI Operation Registry + Operator Runtime** w katalogu repo [`uri2ops/`](../uri2ops/).

Hypervisor **nie klika, nie pisze i nie steruje OS** — wykonanie operatora należy do `uri2ops`.

## Architektura

```txt
nl2uri  → URI task/workflow graph (single, list, tree, task, graph)
uri3    → parsing, validation, uri3 run-workflow (MVP executor)
uri2ops → operation registry + adapters + policy + artifacts + serve
hypervisor → deployment, lifecycle, audit, approval gate (future)
```

Pełna dokumentacja pakietu: [`packages/uri2ops/README.md`](../packages/uri2ops/README.md).

## CLI

```bash
uri2ops operations list
uri2ops operations describe browser open
uri2ops validate examples/10_browser_operator/task.health.yaml
uri2ops plan examples/10_browser_operator/task.health.yaml
uri2ops run examples/10_browser_operator/task.health.yaml --adapter mock --approve
uri2ops run examples/10_browser_operator/task.health.yaml --adapter playwright --approve
uri2ops run examples/10_browser_operator/task.health.yaml --adapter auto --approve
uri2ops serve --host 127.0.0.1 --port 8791
uri2ops registry list
uri2ops registry validate
```

### Adaptery (`--adapter`)

| Wartość | Opis |
|---------|------|
| `mock` | Deterministyczne mocki (testy, CI) |
| `playwright` | Prawdziwa przeglądarka (extra `[browser]`) |
| `adb` | Android przez ADB + UI Automator |
| `uia` | Windows UI Automation (extra `[windows]`) |
| `auto` | Wybór real backend gdy dostępny, inaczej mock |

## Schematy URI operatora

```txt
browser://chrome/page/open
browser://chrome/page/active
android://device/{id}/screenshot|dump_ui|tap
pcwin://window/{id}/focus
pcwin://control/{automation_id}/click
assertion://contains
artifact://operator/workflows/{task_id}/{run_id}/{step_id}/...
```

## Konfiguracja

| Plik | Rola |
|------|------|
| [`config/operator_policy.uri.yaml`](../config/operator_policy.uri.yaml) | Polityka approve/risk |
| [`config/operator_registry.uri.yaml`](../config/operator_registry.uri.yaml) | Bazowy rejestr operacji |
| [`config/extra_operator_registry.yaml`](../config/extra_operator_registry.yaml) | Rozszerzenia (merge) |
| [`packages/uri2ops/uri2ops/operation_registry/registry.yaml`](../packages/uri2ops/uri2ops/operation_registry/registry.yaml) | Kanoniczny registry pakietu |

## HTTP daemon (v0.5)

```bash
uri2ops serve --port 8791
curl http://127.0.0.1:8791/health
curl http://127.0.0.1:8791/registry
curl -X POST http://127.0.0.1:8791/run -H 'Content-Type: application/json' -d @task.json
```

A2A: `/.well-known/agent-card.json`, `POST /a2a/tasks`  
MCP: `GET /mcp/tools`, `POST /mcp/tools/call`

Przykład: [`examples/14_uri2ops_serve/`](../examples/14_uri2ops_serve/README.md).

## Przykłady

| # | Katalog | Temat |
|---|---------|-------|
| 10 | [`examples/10_browser_operator/`](../examples/10_browser_operator/) | Mock browser + assertion |
| 11 | [`examples/11_playwright_browser/`](../examples/11_playwright_browser/) | Playwright |
| 12 | [`examples/12_android_operator/`](../examples/12_android_operator/) | Android ADB |
| 13 | [`examples/13_pcwin_operator/`](../examples/13_pcwin_operator/) | Windows UIA |
| 14 | [`examples/14_uri2ops_serve/`](../examples/14_uri2ops_serve/) | HTTP daemon |

## Powiązane dokumenty

- [`docs/OPERATOR_RUNTIME.md`](./OPERATOR_RUNTIME.md) — przepływ wykonania
- [`docs/URI_OPERATION_REGISTRY.md`](./URI_OPERATION_REGISTRY.md) — format registry
- [`docs/OPERATOR_SECURITY.md`](./OPERATOR_SECURITY.md) — zasady bezpieczeństwa
- [`packages/uri2ops/CHANGELOG.md`](../packages/uri2ops/CHANGELOG.md) · [`packages/uri2ops/TODO.md`](../packages/uri2ops/TODO.md)

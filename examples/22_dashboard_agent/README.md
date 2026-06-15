# Example 22 — dashboard-agent capabilities

Manifesty touri/uri2flow dla agenta **hypervisor-dashboard** (chat, widok procesów, repair).

## Pliki

| Plik | Opis |
|------|------|
| [`dashboard_open.uri.flow.yaml`](dashboard_open.uri.flow.yaml) | Otwarcie UI w przeglądarce po diagnose |
| [`process_view.uri.capability.yaml`](process_view.uri.capability.yaml) | Widok procesu agenta |
| [`repair_diagnose.uri.capability.yaml`](repair_diagnose.uri.capability.yaml) | Diagnoza repair |
| [`incident_explain.uri.capability.yaml`](incident_explain.uri.capability.yaml) | Wyjaśnienie incydentu |

## Użycie

```bash
touri validate examples/22_dashboard_agent/process_view.uri.capability.yaml
touri list examples/22_dashboard_agent
```

Dashboard działa po `make start` → http://localhost:8788/www/chat.html

## Powiązane

- [`packages/hypervisor-dashboard-agent/README.md`](../../packages/hypervisor-dashboard-agent/README.md)
- [`docs/DASHBOARD.md`](../../docs/DASHBOARD.md)
- [`09_run_agent_hypervisor`](../09_run_agent_hypervisor/)

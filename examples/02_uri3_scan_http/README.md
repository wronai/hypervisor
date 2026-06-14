# Example 02 — skanowanie HTTP/A2A-like

Skan działającego agenta HTTP przez `uri3`. **Najpierw uruchom agenta** (jedna z opcji poniżej).

## Wymagania

Agent nasłuchujący na porcie HTTP (domyślnie `8101`):

| Źródło | Jak uruchomić |
|--------|----------------|
| Docker testenv | [`../03_ssh_remote_agent/`](../03_ssh_remote_agent/) → `make docker-testenv-up` |
| Lokalny agent | [`../09_run_agent_hypervisor/`](../09_run_agent_hypervisor/) → `hypervisor run-agent weather-map-agent.local` |
| Makefile | `make run-user-agent` (inny agent, port 8101) |

> **Port zajęty?** Sprawdź faktyczne mapowanie: `docker port hypervisor-ssh-agent-host 8101`  
> Jeśli host ma np. `8102`, skanuj: `uri3 scan http://localhost:8102`

## Skanowanie

```bash
uri3 scan http
# lub pełny URI:
uri3 scan http://localhost:8101
hypervisor scan http://localhost:8101
make scan-http
```

Oczekiwany wynik (gdy agent działa): `"kind": "health", "status": "ok"`.

Sprawdzane endpointy:

```txt
/health
/capabilities
/.well-known/agent-card.json
/.well-known/agent.json
```

## Introspection

```bash
uri3 schema 'http://'
uri3 resolve http://localhost:8101/health
```

## Stop agenta

| Źródło | Komenda |
|--------|---------|
| hypervisor (local) | `hypervisor stop-agent weather-map-agent.local` |
| Docker testenv | `make docker-testenv-down` |
| Makefile uvicorn | `Ctrl+C` w terminalu z `make run-user-agent` |

## Powiązane

- [`../03_ssh_remote_agent/`](../03_ssh_remote_agent/) — mock HTTP + SSH w Dockerze
- [`../09_run_agent_hypervisor/`](../09_run_agent_hypervisor/) — lokalny lifecycle

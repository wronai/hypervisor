# Example 02 — skanowanie HTTP/A2A-like

Ten przykład zakłada, że działa mock agent z przykładu `03_ssh_remote_agent` albo inny agent HTTP.

```bash
uri3 scan http://localhost:8101
```

Oczekiwane punkty sprawdzane przez skaner:

```txt
/health
/capabilities
/.well-known/agent-card.json
/.well-known/agent.json
```

To jest celowo w paczce `uri3`, a nie w hypervisorze. `uri3` odkrywa fakty, hypervisor później podejmuje decyzje o rejestracji, aktualizacji albo oznaczeniu agenta jako stale.

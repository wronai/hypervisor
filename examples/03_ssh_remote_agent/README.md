# Example 03 — remote agent host przez Docker + SSH

Ten przykład uruchamia kontener, który udaje zewnętrzną maszynę do wdrażania agentów.
Kontener wystawia:

- SSH: `ssh://deploy@localhost:2222/opt/agents`
- mock Agent Card: `http://localhost:8101/.well-known/agent-card.json`
- health: `http://localhost:8101/health`
- resources/read: `http://localhost:8101/resources/read?uri=...`

## Start

```bash
docker compose up --build -d
```

## Test SSH

Hasło użytkownika `deploy`: `deploy`.

```bash
ssh -p 2222 deploy@localhost 'ls -la /opt/agents'
```

## Skanowanie HTTP przez uri3

```bash
uri3 scan http://localhost:8101
```

## Skanowanie SSH przez uri3

```bash
uri3 scan ssh://deploy@localhost:2222/opt/agents
```

## Stop

```bash
docker compose down -v
```

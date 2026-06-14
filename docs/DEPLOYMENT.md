# Wdrożenie

## Lokalnie

```bash
pip install -e '.[dev]'
make validate generate verify test
make run-user-agent
```

Agent user-agent:

```bash
uvicorn agents.generated.user_agent.main:app --reload --port 8101
```

## Pipeline nl2a

```bash
nl2a --no-llm -p "generuj mape pogody dwa tygodnie do przodu w html"
make verify
make test
```

Zobacz [`examples/04_nl2a_weather_map/`](../examples/04_nl2a_weather_map/README.md).

## Docker dla wygenerowanego agenta

Po wygenerowaniu:

```bash
docker build -f agents/generated/user_agent/Dockerfile -t user-agent:0.1.0 .
docker run -p 8101:8101 -e RESOURCE_RUNTIME_URL=http://host.docker.internal:8000 user-agent:0.1.0
```

## Docker + SSH testenv

Symulacja zewnętrznej maszyny do skanowania/wdrożeń:

```bash
make docker-ssh-up
make scan-http
ssh -p 2222 deploy@localhost 'ls -la /opt/agents'   # hasło: deploy
make docker-ssh-down
```

Szczegóły: [`examples/03_ssh_remote_agent/`](../examples/03_ssh_remote_agent/README.md).

> Automatyczny deploy przez `ssh://` w pipeline nie jest jeszcze zaimplementowany. Registry przechowuje targety (`deployments/agent_deployments.yaml`), ale synchronizacja kończy się na wpisie `planned` / `generated`.

## Deployment registry

```txt
deployments/agent_deployments.yaml
```

### Uruchomienie agenta przez hypervisor

```bash
hypervisor deployments
hypervisor run-agent weather-map-agent.local --dry-run
hypervisor run-agent weather-map-agent.local --detach --if-running reuse
hypervisor run-agent weather-map-agent.local --detach --wait-healthy --supervise-repair auto
make run-weather-agent
hypervisor agent-status weather-map-agent.local
hypervisor inspect-agent weather-map-agent.local
hypervisor supervise weather-map-agent.local
hypervisor supervise weather-map-agent.local --repair auto
hypervisor scan http://localhost:8101/health
```

`run-agent --if-running reuse|restart|fail` jawnie steruje zachowaniem przy
istniejącym procesie, a `--wait-healthy --supervise-repair auto` po starcie
wykonuje ograniczoną pętlę inspekcji i naprawy. `inspect-agent` raportuje
`process`, `health`, `card`, `log_errors`, `incidents` i `service_status`, więc
`running` nie jest mylone ze zdrową usługą. `supervise --repair auto` wykonuje
ograniczony cykl: inspekcja, sync runtime `health_uri` albo restart, i ponowna
inspekcja.

Przykład krok po kroku: [`examples/09_run_agent_hypervisor/`](../examples/09_run_agent_hypervisor/README.md).

Przykładowe targety:

```txt
local://agents/generated/weather_map_agent
ssh://deploy@localhost:2222/opt/agents/weather-map-agent
```

Walidacja evolution proposals:

```bash
make evolution-check
```

Pliki: [`examples/08_evolution/proposals/`](../examples/08_evolution/proposals/).

## Zmienne środowiskowe

```txt
RESOURCE_RUNTIME_URL=http://localhost:8000
OPENROUTER_API_KEY=...
LLM_MODEL=openrouter/qwen/qwen3-coder-next
NL2A_USE_LLM=0
```

## Integracja z Resource Runtime

Agent oczekuje endpointów runtime:

```txt
GET  /resources/read?uri=resource://...
POST /commands
```

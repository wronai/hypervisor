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

## Kontrola całego systemu wyłącznie przez `urish` (shell)

Używaj tylko komendy `urish` (lub `uri` fallback) do wdrażania, weryfikacji i kontroli agentów z examples:

```bash
# Plan + apply ekosystemu agenta z examples (np. orders, invoices via profile agent/dashboard-agent)
urish ecosystem plan examples/06_orders_agent --profile agent > /tmp/proposal.yaml
urish ecosystem apply /tmp/proposal.yaml --approve

# Deploy/run istniejących (z generated/ lub deployments)
urish agent run weather-map-agent.local --dry-run   # lub bez dry-run + approve w real
urish agent run hypervisor-dashboard.local

# Weryfikacja: czy poprawnie wyodrębniani (separation/domain boundaries)
urish doctor --strict
urish explain agent://weather-map-agent
urish explain health://agent/weather-map-agent.local

# Czy procesy poprawnie realizowane (runtime, health, card, repair loops)
urish agent health weather-map-agent.local
urish agent status desktop-operator.local
urish repair diagnose weather-map-agent.local
urish watch health://agent/weather-map-agent.local
urish call http://localhost:8105/health   # lub health_uri z status

# Natural language control całego systemu
urish nl "deploy and verify orders agent from examples using agent profile"
urish nl "check health and repair loop for all running agents"
```

Aktualne agenty z examples (weather_map_agent, orders/invoices plans, dashboard, desktop-operator, capabilities z examples/20_touri_capabilities):

- **Wyodrębnianie**: Poprawnie – agenty w `agents/generated/*` (z contracts/ + domains/), capabilities/flows w `examples/20_touri_capabilities` (touri registry), nie zanieczyszczają core packages. `urish doctor` pokazuje registry z examples/, explain via uri3 bez domain vocab w generic. Card payload zawiera "generated_from": contract hash.

- **Procesy**: Poprawnie realizowane. `urish agent health/status` pokazuje: pid running, uvicorn command (z generated lub packages/), effective health/card 200 + capabilities z contract, runtime_state (z centralized accessors), readiness ok (minor HEALTH_URI_DRIFT – znany), log_errors=0, repair diagnose clean (no incidents, recommended=none). Watch/call potwierdzają observation. Lifecycle pod spodem (po refaktorach) zachowuje detached run, plans, state.

Existing (weather-map-agent.local, hypervisor-dashboard.local, desktop-operator.local) healthy/running via urish. Plans dla nowych (orders, invoices) generują poprawne proposals z domains/agents/caps/flows/deployments.

Pełna autonomia: repair loops (urish repair), monitory (via watch/nl flows), detached (run), verifiable wyłącznie przez urish shell.

Zobacz też: `urish --help`, `urish agent --help`, `urish ecosystem --help`, `urish repair --help`, `urish doctor`, examples/ README.

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
hypervisor supervise weather-map-agent.local --watch --repair auto --interval 15
hypervisor supervise weather-map-agent.local --watch --repair auto --count 2 --interval 0
hypervisor scan http://localhost:8101/health
```

`run-agent --if-running reuse|restart|fail` jawnie steruje zachowaniem przy
istniejącym procesie, a `--wait-healthy --supervise-repair auto` po starcie
wykonuje ograniczoną pętlę inspekcji i naprawy. `inspect-agent` raportuje
`process`, `health`, `card`, `log_errors`, `incidents` i `service_status`, więc
`running` nie jest mylone ze zdrową usługą. `supervise --repair auto` wykonuje
ograniczony cykl: inspekcja, sync runtime `health_uri` albo restart, i ponowna
inspekcja.

### Port zajęty i HEALTH_URI_DRIFT

Gdy preferowany port jest zajęty (np. `8101`, `8103` przez inną usługę), hypervisor
uruchamia agenta na wolnym porcie i zapisuje **effective health URI** w runtime state.

```bash
hypervisor inspect-agent invoices-agent.local
# declared: http://localhost:8103/health  effective: http://localhost:8110/health

hypervisor repair apply invoices-agent.local --playbook sync_health_uri
```

Po udanym starcie z `port_rebound` rejestr `deployments/agent_deployments.yaml` jest
aktualizowany automatycznie. Playbook `sync_health_uri` służy do ręcznej synchronizacji
gdy agent już działa na innym porcie.

`health://agent/{deployment}` używa inspekcji (effective port), nie tylko wpisu z rejestru.

Zależność runtime: `pip install 'uvicorn>=0.27'` w venv hypervisora przed `run-agent`.

Więcej: [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md) · [`AGENTS_AND_MONITORING.md`](./AGENTS_AND_MONITORING.md).

### Wiele agentów równolegle

Każdy wpis w `deployments/agent_deployments.yaml` ma własny port i stan runtime.
Hypervisor uruchamia ich wiele niezależnie:

```bash
hypervisor run-agent weather-map-agent.local --detach --if-running reuse
hypervisor run-agent invoices-agent.local --detach --if-running reuse
hypervisor inspect-agent weather-map-agent.local
hypervisor inspect-agent invoices-agent.local
```

Monitoring floty: `hypervisor deployments` + `inspect-agent` + dashboard `/api/events`
(incydenty, monitory WWW, logi JSONL, health agentów). Szczegóły: [`AGENTS_AND_MONITORING.pl.md`](./AGENTS_AND_MONITORING.pl.md).

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

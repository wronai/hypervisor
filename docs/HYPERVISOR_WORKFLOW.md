# Hypervisor workflow — generacja i uruchomienie agenta

Pełny przepływ od promptu do działającego agenta HTTP.

## 1. Konfiguracja

```txt
config/llm.uri.yaml     # profile LLM jako URI (bez sufiksów _uri w polach)
hypervisor.yaml         # opcjonalny override lokalny
.env                    # tylko sekrety, np. OPENROUTER_API_KEY
```

Profil LLM:

```bash
export DEFAULT_LLM_PROFILE=domain_planner
```

Zasady `*.uri.yaml`: [`docs/CONFIG_URI_YAML.md`](./CONFIG_URI_YAML.md).

## 2. Generacja agenta

```bash
nl2a --no-llm -p "generuj mape pogody dwa tygodnie do przodu w html"
make verify
```

Artefakty:

```txt
domains/weather_map/uri_tree.yaml
contracts/agents/weather_map_agent.yaml
agents/generated/weather_map_agent/
deployments/agent_deployments.yaml   # wpis weather-map-agent.local
output/logs/nl2a.log                 # wpisy pipeline
output/logs/hypervisor.log
```

Przykład: [`examples/04_nl2a_weather_map/`](../examples/04_nl2a_weather_map/).

## 3. Rejestr deploymentów (hypervisor)

```bash
hypervisor deployments
hypervisor agent-status weather-map-agent.local --no-health
```

Hypervisor **nie generuje** agenta — synchronizuje registry po nl2a i później zarządza lifecycle.

## 4. Uruchomienie agenta

```bash
hypervisor run-agent weather-map-agent.local --dry-run
make run-weather-agent
```

W drugim terminalu:

```bash
hypervisor agent-status weather-map-agent.local
hypervisor scan http://localhost:8101/health
curl http://localhost:8101/.well-known/agent-card.json
```

Przykład: [`examples/09_run_agent_hypervisor/`](../examples/09_run_agent_hypervisor/).

## 5. Logi przez uri3

Po pipeline nl2a pliki logów powstają w `output/logs/`:

```bash
uri3 logs 'log://hypervisor?limit=20'
uri3 logs 'log://nl2a?grep=pipeline' --summary
uri3 logs 'log://hypervisor?level=ERROR&limit=50'
```

Jeśli plik nie istnieje, `uri3 logs` zwraca JSON z `exists: false`, `path` i `hint` — nie pustą tablicę `[]`.

## 6. Meta-agent (alternatywna ścieżka)

```bash
make meta-pipeline
make meta-repair
```

Bez Domain Pack — bezpośrednio `contracts/agents/*.yaml` → generator.

## 7. Zdalny agent przez SSH (v0.6)

Testenv Docker: [`examples/03_ssh_remote_agent/`](../examples/03_ssh_remote_agent/)

```bash
make docker-ssh-up
export HYPERVISOR_SSH_PASSWORD=deploy   # opcjonalnie, gdy masz sshpass
hypervisor deploy-agent weather-map-agent.ssh-dev
hypervisor deploy-agent weather-map-agent.ssh-dev --apply
hypervisor run-agent weather-map-agent.ssh-dev --dry-run
hypervisor verify-agent weather-map-agent.ssh-dev
uri3 scan ssh://deploy@localhost:2222/opt/agents/weather-map-agent
```

`run-agent` dla `ssh://` zwraca tylko plan (`--dry-run`). Start procesu na hoście zdalnym wymaga ręcznego wykonania `remote_command` lub przyszłego `remote detach`.

## Podział odpowiedzialności

```txt
nl2a       = generuje URI Tree, Domain Pack, agent, wpis w registry
hypervisor = registry, run-agent (local:// + ssh dry-run), deploy-agent, verify-agent, status, scan
uri3       = log://, schema, resolve, scan HTTP/SSH
generator  = kod z YAML (deterministyczny)
```

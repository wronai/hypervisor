# Example 09 — uruchomienie agenta przez hypervisor

Hypervisor **interpretuje deployment registry** i uruchamia lokalny target `local://…` przez uvicorn.

## Wymagania

```bash
pip install -e '.[dev]'
make nl2a-weather
make verify
```

Agent musi istnieć:

```txt
agents/generated/weather_map_agent/
deployments/agent_deployments.yaml  →  id: weather-map-agent.local
```

## 1. Lista deploymentów

```bash
hypervisor deployments
```

## 2. Podgląd komendy (dry-run)

```bash
hypervisor run-agent weather-map-agent.local --dry-run
```

Przykładowe pole `command`:

```txt
python -m uvicorn agents.generated.weather_map_agent.main:app --host 0.0.0.0 --port 8101
```

## 3. Start agenta

```bash
hypervisor run-agent weather-map-agent.local --detach
# foreground + reload:
hypervisor run-agent weather-map-agent.local --reload
make run-weather-agent
```

Po `--detach` stan w:

```txt
output/runtime/agents/weather-map-agent.local/state.json
```

## 4. Status i health

```bash
hypervisor agent-status weather-map-agent.local
uri3 scan http
hypervisor scan http://localhost:8101
curl http://localhost:8101/.well-known/agent-card.json
```

## 5. Logi

**Pliki aplikacji** (`output/logs/`):

```bash
uri3 logs 'log://hypervisor?limit=20'
uri3 logs 'log://nl2a?grep=pipeline'
uri3 logs 'log://hypervisor?level=ERROR&limit=50' --summary
```

**Logi powiązane z deploymentem** (hypervisor → log:// URI):

```bash
hypervisor logs weather-map-agent.local
hypervisor logs weather-map-agent.local --limit 100
```

Gdy plik logu nie istnieje, `uri3 logs` zwraca `exists: false` i `hint` — uruchom najpierw `make nl2a-weather`.

## 6. Stop / restart

```bash
hypervisor stop-agent weather-map-agent.local
hypervisor restart-agent weather-map-agent.local
hypervisor agent-status weather-map-agent.local
```

## 7. Zmienne środowiskowe

Z registry i `config/deployments.uri.yaml`:

```yaml
env:
  RESOURCE_RUNTIME_URL: http://localhost:8000
  OPENROUTER_API_KEY: env://OPENROUTER_API_KEY
```

Ustawienie sekretu przez uri3:

```bash
uri3 call 'env://OPENROUTER_API_KEY?action=set&value=sk-or-...&persist=1'
```

## Ograniczenia targetów

| Target | Uruchomienie |
|--------|----------------|
| `local://…` | `hypervisor run-agent` |
| `ssh://…` | `deploy-agent` / `verify-agent`; `run-agent --dry-run` |
| `docker://…` | `deploy-agent --apply` / `verify-agent` |

Zdalny testenv: [`../03_ssh_remote_agent/`](../03_ssh_remote_agent/).

## Powiązane

- [`../04_nl2a_weather_map/`](../04_nl2a_weather_map/) — generacja agenta
- [`../02_uri3_scan_http/`](../02_uri3_scan_http/) — skan HTTP

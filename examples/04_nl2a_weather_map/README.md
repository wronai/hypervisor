# Example 04 — prompt do weather-map Domain Pack

Generacja Domain Pack i agenta `weather_map` z promptu NL.

## Wymagania

```bash
pip install -e '.[dev]'
```

## Generacja (bez LLM)

Krótko przez Makefile:

```bash
make nl2a-weather
```

Pełny prompt (jak w docs):

```bash
nl2a --no-llm -p "generuj mape pogody dwa tygodnie do przodu w oparciu o miejscowosc i odpowiedni model przewidujacy pogode, generuj widok w formie html pod adresem url"
```

Artefakty:

```txt
domains/weather_map/uri_tree.yaml
agents/generated/weather_map_agent/
deployments/agent_deployments.yaml   # wpis weather-map-agent.local
```

## Sprawdzenie

```bash
make verify
uri3 validate-tree domains/weather_map/uri_tree.yaml
uri3 graph domains/weather_map/uri_tree.yaml
hypervisor deployments
```

## Uruchomienie agenta

```bash
hypervisor run-agent weather-map-agent.local --dry-run
hypervisor run-agent weather-map-agent.local --detach
hypervisor agent-status weather-map-agent.local
hypervisor stop-agent weather-map-agent.local
make run-weather-agent    # foreground + reload
```

Szczegóły lifecycle: [`../09_run_agent_hypervisor/README.md`](../09_run_agent_hypervisor/README.md).

## Logi pipeline

```bash
uri3 logs 'log://nl2a?limit=20'
uri3 logs 'log://hypervisor?level=ERROR&limit=50'
```

## Następny krok

- skan HTTP: [`../02_uri3_scan_http/`](../02_uri3_scan_http/)
- deploy SSH: [`../03_ssh_remote_agent/`](../03_ssh_remote_agent/)

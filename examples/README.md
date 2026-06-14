# Examples

Przykłady są uporządkowane według schematu `examples/*/*` — każdy katalog ma własny `README.md`.

**Wymagania wspólne** (z katalogu repo):

```bash
pip install -e '.[dev]'
```

## Przegląd

| # | Katalog | Typ | Start / stop / logi |
|---|---------|-----|---------------------|
| 01 | [`01_quickstart_local`](./01_quickstart_local/) | pipeline | `make uri-tree` → `make test` (bez runtime) |
| 02 | [`02_uri3_scan_http`](./02_uri3_scan_http/) | skan HTTP | wymaga działającego agenta → [`03`](./03_ssh_remote_agent/) lub [`09`](./09_run_agent_hypervisor/) |
| 03 | [`03_ssh_remote_agent`](./03_ssh_remote_agent/) | Docker + SSH | `make docker-testenv-up` / `down`, `uri3 scan`, `uri3 call … logs` |
| 04 | [`04_nl2a_weather_map`](./04_nl2a_weather_map/) | generacja | `make nl2a-weather` → [`09`](./09_run_agent_hypervisor/) |
| 05 | [`05_meta_repair`](./05_meta_repair/) | naprawa kontraktu | `make meta-repair` |
| 06 | [`06_orders_agent`](./06_orders_agent/) | wzorzec YAML | walidacja kontraktu (bez runtime) |
| 07 | [`07_invoices_agent`](./07_invoices_agent/) | prompt NL | `meta_agent plan` / `pipeline` |
| 08 | [`08_evolution`](./08_evolution/) | propozycje | `make evolution-check` |
| 09 | [`09_run_agent_hypervisor`](./09_run_agent_hypervisor/) | lifecycle | `run-agent` / `stop-agent` / `logs` / `agent-status` |

## Szybki start (pełny stack testenv)

```bash
# 1. Hasło SSH (raz, przez uri3)
uri3 call 'env://HYPERVISOR_SSH_PASSWORD?action=set&value=deploy&persist=1'

# 2. Docker + SSH testenv
make docker-testenv-up

# 3. Sprawdzenie
uri3 scan --all
hypervisor verify-agent weather-map-agent.ssh-dev

# 4. Logi kontenera
uri3 call 'docker://stack/ssh-testenv?action=logs&tail=50'

# 5. Stop
make docker-testenv-down
```

## Zasada architektury

```txt
uri3 = skanowanie, routing, discovery, logi plikowe, docker:// call
hypervisor = registry, policy, lifecycle agentów (run/stop/deploy/verify)
nl2uri = natural language -> URI Tree
nl2a = pipeline prompt -> URI Tree -> Domain Pack -> agent
```

## Najczęstsze komendy

```bash
uri3 list
uri3 scan http
uri3 scan ssh
uri3 scan docker
make uri-tree
make nl2a-weather
make meta-repair
make evolution-check
hypervisor deployments
hypervisor run-agent weather-map-agent.local --dry-run
hypervisor run-agent weather-map-agent.local --detach
hypervisor stop-agent weather-map-agent.local
hypervisor logs weather-map-agent.local
```

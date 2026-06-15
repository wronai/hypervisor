# Prawdziwi agenci, komunikacja, ewolucja i monitoring wielu agentów

Stan zweryfikowany 2026-06-14 na bieżącym repo.

## Krótkie odpowiedzi

| Pytanie | Odpowiedź |
|---------|-----------|
| Czy można tworzyć **prawdziwych** agentów? | **Tak** — agenci HTTP contract-first przez `nl2a`, `urigen` / `uri ecosystem` lub evolution proposals. Artefakty: `contracts/agents/`, `agents/generated/`, `deployments/agent_deployments.yaml`. |
| Czy jest **komunikacja** z agentami? | **Tak** — `/health`, `/.well-known/agent-card.json`, trasy zasobów. Hypervisor i dashboard wołają je przez URI (`health://`, `repair://`, `view://`) i sondy HTTP. |
| Czy agentów można **ulepszać**? | **Tak, kontrolowanie** — diagnoza → naprawa → incydent → propozycja ewolucji → regeneracja → weryfikacja → apply. Bez zgody nie ma mutacji kodu produkcyjnego. |
| Czy **kilka agentów naraz**? | **Tak** — osobny port/PID/stan runtime na deployment. Np. `weather-map-agent.local` na `:8118` i `invoices-agent.local` na `:8123` równolegle. |
| Jakie **oprogramowanie monitoruje** wielu agentów? | **`hypervisor`** (rejestr, inspect, supervise), **`hypervisor-dashboard-agent`** (WWW + `/api/events`), **`uri3`** (`logs`, `scan`, `doctor`, `watch`), artefakty w `output/logs/`, `output/incidents/`, `output/monitoring/`. |

## Tworzenie agentów

1. **`nl2a`** — Domain Pack → kontrakt → `agents/generated/` (np. weather-map)
2. **`uri ecosystem`** — izolowany pakiet ekosystemu (`minimal`, `voice`, `dashboard-agent`)
3. **Evolution** — `examples/08_evolution/`, `uri evolve from-incident`

Nie edytuj ręcznie `agents/generated/`.

## Komunikacja

- HTTP: `curl http://localhost:8118/health`
- URI: `health://agent/weather-map-agent.local`, `repair://agent/…/auto`
- Dashboard: `POST /api/uri/call`, `POST /api/plan/run` (dry-run domyślnie, auto-repair przy błędzie kroku)
- Logi: `uri3 logs 'log://hypervisor?grep=…'`
- Widok procesu: `view://process/agent/{deployment}/latest`

Chat i CLI używają tych samych backendów.

## Ulepszanie (repair + evolution)

```text
observe → diagnose → repair → incident → evolution → regenerate → verify → apply
```

- `hypervisor supervise --repair auto` — ograniczona pętla naprawy
- `POST /api/plan/run` z `auto_repair: true` — naprawa + retry w planie z czatu
- `uri evolve from-incident` / `from-ticket` — propozycja, nie bezpośrednia edycja kodu

Brakuje jeszcze: pełnej pętli uri-healer dla wszystkich klas błędów. Watch mode jest dostępny: `hypervisor supervise … --watch --repair auto`.

## Wiele agentów równolegle

```bash
hypervisor run-agent weather-map-agent.local --detach --if-running reuse
hypervisor run-agent invoices-agent.local --detach --if-running reuse
hypervisor inspect-agent weather-map-agent.local
hypervisor inspect-agent invoices-agent.local
```

Przy zajętym porcie hypervisor rebindinguje port i zapisuje effective health URI.

## Monitoring — co używać

| Warstwa | Narzędzie | Do czego |
|---------|-----------|----------|
| Rejestr + lifecycle | `hypervisor deployments`, `inspect-agent`, `supervise` | stan procesu, health, incydenty |
| WWW | `/ui/agents`, `/www/chat.html`, `/api/events`, SSE | lista agentów, zdarzenia na żywo |
| Logi | `uri3 logs`, `output/logs/*.jsonl` | błędy pipeline i agentów (`log.event` w `/api/events`) |
| Monitory WWW | `make www-monitor`, `scripts/www/monitor_landing.py` | snapshoty w `output/monitoring/` |
| Zadania OS/www | `uri2ops` | operacje browser/Android/Windows — nie flota agentów |

## Szybka weryfikacja

```bash
hypervisor deployments
hypervisor run-agent weather-map-agent.local --detach --if-running reuse
hypervisor run-agent invoices-agent.local --detach --if-running reuse
curl -s http://localhost:8118/health
curl -s http://localhost:8123/health
curl -s http://localhost:8788/api/events?limit=10
```

Pełna wersja EN: [`AGENTS_AND_MONITORING.md`](./AGENTS_AND_MONITORING.md)

Tutorial krok po kroku (3 agenci + czat + markpact): [`TUTORIAL_THREE_AGENTS.pl.md`](./TUTORIAL_THREE_AGENTS.pl.md)

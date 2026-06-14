# uri3

`uri3` to niezależna paczka do pracy z URI: parser, normalizer, resolvery, skanery, graf zależności, walidacja URI Tree, logi (`log://`) i introspection schematów.

Hypervisor korzysta z `uri3` przez cienki adapter (`hypervisor.uri.client.Uri3Client`), ale `uri3` nie zależy od hypervisora.

## CLI

Bez argumentów lub przez `uri3 list` — szybka ściągawka ze skrótami:

```bash
uri3
uri3 list
uri3 list --json
uri3 list --schemes
```

Skanowanie po nazwie skrótu (z `config/uri3.uri.yaml`) lub pełnym URI:

```bash
uri3 scan http
uri3 scan ssh
uri3 scan docker
uri3 scan --all
uri3 scan http://localhost:8101
```

Pozostałe komendy:

```bash
uri3 validate <uri>
uri3 validate-tree domains/weather_map/uri_tree.yaml
uri3 graph domains/weather_map/uri_tree.yaml
uri3 resolve <uri>
uri3 call 'docker://stack/ssh-testenv?action=up'
uri3 logs 'log://hypervisor?level=ERROR&grep=deployment&limit=100'
uri3 logs 'log://hypervisor' --summary
uri3 schema 'log://'
uri3 schema 'log://hypervisor?level=ERROR'
uri3 schema --list
```

## Obsługiwane schematy

```txt
env llm log python pypi http https a2a mcp
resource artifact domain agent local input command event
ssh docker git
```

Pełna lista i opcje query: `uri3 schema --list` oraz `uri3 schema '<scheme>://'`.

## log://

Domyślne strumienie mapują na `output/logs/{stream}.log`:

```bash
uri3 logs 'log://hypervisor?level=ERROR&since=1h&limit=50'
uri3 logs 'log://file/output/logs/hypervisor.log'
```

Filtry: `level`, `grep`, `logger`, `since`, `until`, `limit`, `offset`, `tail`.

## Skanowanie

Skaner HTTP sprawdza m.in.:

```txt
/health
/capabilities
/.well-known/agent-card.json
/.well-known/agent.json
```

Skaner `log://` zwraca metadane pliku i liczbę dopasowanych wpisów.

Skaner `ssh://` sprawdza connectivity i katalog zdalny. Skaner `docker://` zwraca status stacka compose lub kontenera.

## docker://

Sterowanie Dockerem (generowanie compose, up/down, start/stop, ps, logs):

```bash
uri3 call 'docker://generate/weather-map-agent?action=generate'
uri3 call 'docker://stack/ssh-testenv?action=up'
uri3 call 'docker://stack/ssh-testenv?action=down&remove_volumes=1'
uri3 scan docker://stack/ssh-testenv
```

Profile stacków: `config/docker.uri.yaml`. Hypervisor: `hypervisor docker 'docker://...'`, `hypervisor deploy-agent weather-map-agent.docker --apply`.

Szczegóły SSH/Docker testenv: [`examples/03_ssh_remote_agent/`](../examples/03_ssh_remote_agent/README.md).

## Python API

```python
from uri3.resolvers.router import resolve, call
from uri3.logs.reader import read_logs, summarize_logs
from uri3.protocols.scheme_registry import get_scheme_schema, analyze_uri, describe_uri
```

## Powiązane dokumenty

- [`docs/ARCHITECTURE_V0_5.md`](./ARCHITECTURE_V0_5.md)
- [`docs/URI2LLM.md`](./URI2LLM.md) — historyczna warstwa routing (dziś `uri3.resolvers`)
- [`examples/02_uri3_scan_http/`](../examples/02_uri3_scan_http/README.md)

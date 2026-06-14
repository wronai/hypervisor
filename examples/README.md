# Examples

Przykłady są uporządkowane tak, żeby pokazać praktyczny start projektu:

1. [`01_quickstart_local`](./01_quickstart_local/) — lokalny przepływ `prompt -> URI Tree`.
2. [`02_uri3_scan_http`](./02_uri3_scan_http/) — skanowanie HTTP/A2A-like przez `uri3`.
3. [`03_ssh_remote_agent`](./03_ssh_remote_agent/) — kontener Docker udający zewnętrzną maszynę z SSH i mock agentem.
4. [`04_nl2a_weather_map`](./04_nl2a_weather_map/) — przykład promptu generującego domenę weather-map.

Zasada architektury:

```txt
uri3 = skanowanie, routing, discovery i graf URI
hypervisor = registry, policy, lifecycle i decyzje
nl2uri = natural language -> URI Tree
nl2a = pipeline prompt -> URI Tree -> Domain Pack -> agent
```

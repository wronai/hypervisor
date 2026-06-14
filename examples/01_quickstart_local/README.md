# Example 01 — lokalny quickstart

Minimalny przepływ bez Dockera i bez LLM. **Brak runtime agenta** — tylko generacja i walidacja URI Tree.

## Wymagania

```bash
cd /path/to/hypervisor   # katalog repo
pip install -e '.[dev]'
```

## Uruchomienie

```bash
make uri-tree
make validate
make graph
make test
```

Lub skrypt (robi to samo + `pip install`):

```bash
./examples/01_quickstart_local/run.sh
```

## Wynik

```txt
domains/weather_map/uri_tree.yaml
```

## Sprawdzenie

```bash
uri3 validate-tree domains/weather_map/uri_tree.yaml
uri3 graph domains/weather_map/uri_tree.yaml
```

## Łańcuch

```txt
prompt -> nl2uri -> URI Tree -> uri3 validate/graph
```

## Następny krok

- generacja agenta: [`../04_nl2a_weather_map/`](../04_nl2a_weather_map/)
- uruchomienie agenta: [`../09_run_agent_hypervisor/`](../09_run_agent_hypervisor/)

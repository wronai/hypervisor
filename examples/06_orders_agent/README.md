# Example 06 — kontrakt agenta zamówień

**Wzorzec kontraktu** (reference) — agent nie jest generowany ani uruchamiany w tym przykładzie.

## Plik

```txt
examples/06_orders_agent/create_orders_agent.yaml
```

Capabilities: `read_order`, `read_order_events`, `create_order`.

## Walidacja kontraktu

```bash
python -m generator.validate examples/06_orders_agent
```

Oczekiwany wynik: `Validated 1 agent spec(s).`

## Użycie

- wzorzec przy ręcznym tworzeniu `contracts/agents/*.yaml`
- punkt odniesienia dla evolution proposal [`../08_evolution/proposals/add_orders_agent.yaml`](../08_evolution/proposals/add_orders_agent.yaml)

## Sprawdzenie proposal

```bash
make evolution-check
```

## Runtime

Ten przykład **nie zawiera** start/stop/logów — to tylko YAML.  
Pełny lifecycle agenta: [`../09_run_agent_hypervisor/`](../09_run_agent_hypervisor/).

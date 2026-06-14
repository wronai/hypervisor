# Example 08 — evolution proposals

Walidacja propozycji autoewolucji agentów przez `hypervisor.evolution`.

## Pliki

```txt
examples/08_evolution/proposals/add_orders_agent.yaml
examples/08_evolution/proposals/add_invoices_agent.yaml
```

## Uruchomienie

```bash
make evolution-check
```

Równoważnie:

```bash
python -m hypervisor.evolution.cli \
  examples/08_evolution/proposals/add_orders_agent.yaml \
  examples/08_evolution/proposals/add_invoices_agent.yaml
```

## Oczekiwany wynik

```txt
Valid proposal: add-orders-agent
Valid proposal: add-invoices-agent
```

## Powiązane przykłady

| Proposal | Źródło |
|----------|--------|
| `add_orders_agent` | [`../06_orders_agent/`](../06_orders_agent/) |
| `add_invoices_agent` | [`../07_invoices_agent/`](../07_invoices_agent/) |

Brak runtime — tylko **walidacja propozycji**, nie deploy agentów.

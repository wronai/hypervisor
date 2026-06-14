# Autoewolucja agentów

## Zasada

Agent nie powinien samodzielnie zmieniać kodu produkcyjnego. Przygotowuje **Evolution Proposal**, który jest walidowany, generowany, testowany i zatwierdzany.

## Pipeline

```txt
1. Evolution Proposal
2. Contract patch
3. Generator
4. Contract tests
5. Compatibility report
6. Approval gate
7. Deploy
```

## Przykłady w repo

Propozycje znajdują się w:

```txt
examples/08_evolution/proposals/
  add_orders_agent.yaml
  add_invoices_agent.yaml
```

Walidacja:

```bash
make evolution-check
# lub
python -m hypervisor.evolution.cli examples/08_evolution/proposals/add_orders_agent.yaml examples/08_evolution/proposals/add_invoices_agent.yaml
```

Zobacz [`examples/08_evolution/README.md`](../examples/08_evolution/README.md).

## Przykład proposal

```yaml
proposal_id: add-orders-agent
type: new_agent
reason: Potrzebny osobny cienki agent do obsługi zamówień.
adds:
  agents:
    - contracts/agents/orders_agent.yaml
  resources:
    - resource://orders/{order_id}
    - resource://orders/{order_id}/events
  capabilities:
    - read_order
    - read_order_events
    - create_order
compatibility:
  breaking_change: false
  requires_approval: false
  migration_required: true
```

Powiązane przykłady:

- [`examples/06_orders_agent/`](../examples/06_orders_agent/) — kontrakt orders
- [`examples/07_invoices_agent/`](../examples/07_invoices_agent/) — prompt invoices

## Reguły

- Agent może proponować zmianę.
- Generator tworzy kod.
- Testy sprawdzają zgodność.
- Człowiek albo policy gate zatwierdza zmianę.
- Produkcja nie jest modyfikowana bez przejścia testów.

## Minimalne testy evolution

```txt
validate-contracts
generate-agents
verify-generated
contract-tests
runtime-smoke-tests
```

## Powiązane dokumenty

- [`docs/AUTO_EVOLUTION_PIPELINE.md`](./AUTO_EVOLUTION_PIPELINE.md)
- [`docs/STANDARDS.md`](./STANDARDS.md)

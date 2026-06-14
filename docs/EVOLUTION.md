# Autoewolucja agentów

## Zasada

Agent nie powinien samodzielnie zmieniać kodu produkcyjnego. Agent może przygotować **Evolution Proposal**, który jest później walidowany, generowany, testowany i zatwierdzany.

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

## Przykład proposal

```yaml
proposal_id: add-orders-agent
kind: new_agent
reason: Potrzebny osobny agent do obsługi zamówień.

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

checks:
  breaking_change: false
  requires_migration: true
  requires_new_projection: true
```

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

# Example 07 — prompt agenta faktur

Przykładowy prompt naturalny do wygenerowania agenta faktur przez `meta_agent`.

## Plik

```txt
examples/07_invoices_agent/create_invoices_agent_prompt.txt
```

## Plan (bez generacji kodu)

```bash
python -m meta_agent.cli plan "$(cat examples/07_invoices_agent/create_invoices_agent_prompt.txt)"
```

Wypisuje ścieżkę kontraktu, np. `contracts/agents/invoices_agent.yaml`.

## Pełny pipeline

```bash
python -m meta_agent.cli pipeline "$(cat examples/07_invoices_agent/create_invoices_agent_prompt.txt)"
make meta-plan    # inny przykładowy prompt (orders)
```

## Walidacja wyniku

```bash
python -m generator.validate contracts/agents/invoices_agent.yaml
```

## Powiązane

- evolution proposal: [`../08_evolution/proposals/add_invoices_agent.yaml`](../08_evolution/proposals/add_invoices_agent.yaml)
- lifecycle uruchomionego agenta: [`../09_run_agent_hypervisor/`](../09_run_agent_hypervisor/)

Brak własnego runtime w tym katalogu — to **prompt + kontrakt**, nie deployment.

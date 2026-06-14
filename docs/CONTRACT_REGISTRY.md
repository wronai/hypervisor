# Contract Registry

`contracts/registry.yaml` wskazuje pliki kontraktów, a moduł `hypervisor/contract_registry` buduje z nich indeks.

## Pliki wejściowe

```txt
contracts/registry.yaml
contracts/resources.yaml
contracts/views.yaml
contracts/agents/*.yaml
contracts/proto/*.proto
contracts/compatibility/policy.yaml
```

## Walidacja

```bash
make registry
```

Walidacja sprawdza między innymi:

- czy URI zaczyna się od `resource://`,
- czy zasób wskazuje istniejącą projekcję/widok,
- czy capability `resource_read` wskazuje istniejący URI,
- czy `output_schema` i `renderer` capability zgadzają się z zasobem,
- czy capability command ma `command` i `input_schema`.

## Model odpowiedzialności

Contract Registry jest centrum prawdy. `Agent Factory`, `Meta-Agent`, `Verifier` i `Policy Gate` korzystają z niego zamiast czytać luźne pliki na własną rękę.

# Contract Registry Schema

v0.3 introduces formal schemas for the contract registry layer.

## Files

```txt
schemas/
  contract_registry.schema.json
  resources.schema.json
  views.schema.json
  agent_contract.schema.json
  evolution_proposal.schema.json
```

## Validation layers

There are two validation layers:

1. **JSON Schema validation** — checks field names, types, required fields, enum values and URI pattern.
2. **Cross-reference validation** — checks whether references are real and consistent:
   - capability agent exists in agent contracts,
   - resource URI used by a capability exists in `resources.yaml`,
   - projection/view exists in `views.yaml`,
   - renderer is known,
   - referenced Protobuf messages exist in `contracts/proto/*.proto`.

## Commands

```bash
make registry-schema
make registry-cross
make registry-build
make registry-export-md
make hypervisor-check
```

`registry-build` writes a resolved manifest to:

```txt
output/contract_registry.resolved.json
```

`registry-export-md` writes a human-readable export to:

```txt
output/contract_registry.md
```

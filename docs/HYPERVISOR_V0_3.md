# Resource Agent Hypervisor v0.3

v0.3 formalizes the contract registry as the source of truth for the whole system.

## Added in v0.3

- JSON Schema 2020-12 schemas for registry files.
- Schema validator for YAML/JSON contract files.
- Cross-reference validator.
- Registry builder that produces a resolved registry JSON artifact.
- Registry Markdown exporter.
- `contracts/standards.yaml` describing adopted standards.
- Additional tests for schema validation, cross validation and registry build/export.

## Runtime model

The runtime remains shared. Generated agents are still thin adapters. They do not get their own CQRS/Event Store/Projection stack by default.

```txt
Contract Registry
      ↓
Shared Resource Runtime
      ↓
Generated Thin Agents
```

## Recommended flow

```bash
make validate
make registry-schema
make registry-cross
make registry-build
make generate
make verify
make capability-tests
make evolution-check
make test
```

or simply:

```bash
make hypervisor-check
```

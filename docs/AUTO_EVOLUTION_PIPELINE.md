# Controlled auto-evolution pipeline

The project supports controlled auto-evolution, not uncontrolled self-modifying code.

Recommended pipeline:

```text
1. Observe missing capability
2. Create Evolution Proposal
3. Generate or update agent YAML
4. Validate YAML
5. Repair safe mistakes
6. Generate agent code
7. Verify contract hash
8. Run tests
9. Human/policy approval
10. Deploy
```

## Evolution proposal

Example:

```yaml
proposal_id: add-invoices-agent
type: new_agent
reason: Potrzebny agent do obsługi faktur.
input_prompt: >
  Stwórz agenta do obsługi faktur. Ma odczytywać fakturę, historię faktury i umożliwiać utworzenie faktury.
checks:
  - validate_agent_spec
  - auto_repair_if_safe
  - generate_agent
  - verify_contract_hash
  - run_tests
approval:
  required: true
```

## Why approval is still required

The meta-agent can generate and repair contracts, but contract changes may introduce:

- new public capabilities,
- new commands,
- new event types,
- new URI semantics,
- new data exposure paths.

Therefore production deployment should require human review or a strict policy gate.

## Good rule

```text
Agent proposes.
Generator writes.
Tests verify.
Policy approves.
Runtime executes.
```

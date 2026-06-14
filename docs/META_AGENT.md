# Meta-agent: generator, validator and repairer of agents

This package adds a **meta-agent layer** on top of `resource-agent-factory`.

The meta-agent does not write arbitrary production code. It follows a safer rule:

```text
LLM / user prompt -> agent YAML proposal -> validation -> safe repair -> generator -> verification -> tests
```

The generated agent remains a thin adapter to the shared Resource Runtime.

## Responsibilities

The meta-agent can:

1. create a draft agent contract from a natural-language prompt,
2. validate an existing `contracts/agents/*.yaml` file,
3. repair common non-semantic errors,
4. run the agent generator,
5. verify generated code against `contract_hash`,
6. expose the same workflow as FastAPI endpoints.

It should not:

- directly edit generated files in `agents/generated/`,
- invent critical domain behavior without review,
- deploy agents automatically without tests and approval,
- bypass compatibility checks.

## Main components

```text
meta_agent/
  planner.py        prompt -> normalized intent -> YAML spec
  repair.py         safe YAML repair rules
  orchestrator.py   pipeline coordination
  api.py            FastAPI service
  cli.py            command line interface
```

## Safety model

The system separates creative and deterministic parts:

```text
creative layer:      prompt interpretation / proposal
controlled layer:    YAML contract
 deterministic layer: generator + tests + verification
```

This avoids uncontrolled code generation.

## CLI examples

Create a YAML proposal:

```bash
python -m meta_agent.cli plan "Stwórz agenta do obsługi zamówień z odczytem, historią i tworzeniem"
```

Run full pipeline:

```bash
python -m meta_agent.cli pipeline "Stwórz agenta do obsługi faktur z odczytem, historią i tworzeniem"
```

Validate a contract:

```bash
python -m meta_agent.cli validate contracts/agents/user_agent.yaml
```

Repair a broken contract:

```bash
python -m meta_agent.cli repair examples/broken_agent.yaml --write
```

Verify generated agents:

```bash
python -m meta_agent.cli verify
```

## API examples

Run the meta-agent service:

```bash
make run-meta-agent
```

Create a proposal:

```bash
curl -X POST http://localhost:8200/proposals/from-prompt \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Stwórz agenta do obsługi zamówień z odczytem, historią i tworzeniem"}'
```

Run the whole pipeline:

```bash
curl -X POST http://localhost:8200/pipeline/from-prompt \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Stwórz agenta do obsługi faktur z odczytem, historią i tworzeniem"}'
```

## Repair policy

The repairer can safely fix:

- missing `agent.python_package`,
- missing `agent.version`,
- duplicate capability names,
- missing `renderer` for resource reads,
- missing `output_schema` when URI domain is available,
- missing `input_schema` for commands,
- missing command name when capability name exists.

The repairer should not guess complex business rules. For example, it should not decide whether an invoice should emit `InvoiceApproved` or `InvoicePaid` unless that is explicitly in the proposal.

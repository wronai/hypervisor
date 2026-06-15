<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/invoices_agent.yaml -->
<!-- Contract hash: sha256:a536397207b68bed66eefb1defcfb80529b8d2aa4fe82645f2ffa38069c60960 -->
# invoices-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/invoices_agent.yaml`
- Contract hash: `sha256:a536397207b68bed66eefb1defcfb80529b8d2aa4fe82645f2ffa38069c60960`
- Generator: `resource-agent-factory`

## Run

```bash
uvicorn agents.generated.invoices_agent.main:app --reload --port 8101
```

## Reproduce

```bash
PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/invoices_agent.yaml
```

## Markpact provenance

```markpact:agent_generation invoices-agent
agent:
  id: agent://invoices-agent
  package: agents.generated.invoices_agent
source:
  contract: contracts/agents/invoices_agent.yaml
  contract_hash: sha256:a536397207b68bed66eefb1defcfb80529b8d2aa4fe82645f2ffa38069c60960
generator:
  id: resource-agent-factory
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/invoices_agent.yaml
runtime:
  default_run: uvicorn agents.generated.invoices_agent.main:app --reload --port 8101
logs:
  hypervisor: log://hypervisor?grep=invoices-agent.local
  process: log://file/output/logs/agents/invoices-agent.local.process.log
```

```markpact:run_log invoices-agent.local.latest
inspect:
  command: hypervisor inspect-agent invoices-agent.local
  uri: view://process/agent/invoices-agent.local/latest
logs:
  hypervisor: log://hypervisor?grep=invoices-agent.local
  process: log://file/output/logs/agents/invoices-agent.local.process.log
```

## Endpoints

```txt
GET /health
GET /capabilities
GET /.well-known/agent.json
GET /.well-known/agent-card.json
GET /resources/read?uri=...
POST /commands
```

## Capabilities

- `read_invoice` — `resource_read`, URI: `resource://invoices/{invoice_id}`- `read_invoice_events` — `resource_read`, URI: `resource://invoices/{invoice_id}/events`- `create_invoice` — `command`, command: `CreateInvoice`

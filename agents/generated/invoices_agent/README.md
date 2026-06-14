<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/invoices_agent.yaml -->
<!-- Contract hash: sha256:a536397207b68bed66eefb1defcfb80529b8d2aa4fe82645f2ffa38069c60960 -->
# invoices-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/invoices_agent.yaml`
- Contract hash: `sha256:a536397207b68bed66eefb1defcfb80529b8d2aa4fe82645f2ffa38069c60960`

## Run

```bash
uvicorn agents.generated.invoices_agent.main:app --reload --port 8101
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
# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/invoices_agent.yaml
# Contract hash: sha256:a536397207b68bed66eefb1defcfb80529b8d2aa4fe82645f2ffa38069c60960

# ruff: noqa: E501

AGENT_CARD = {'name': 'invoices-agent',
 'version': '0.1.0',
 'description': 'Generated thin agent for invoices resources.',
 'generated_from': {'contract': 'contracts/agents/invoices_agent.yaml',
                    'contract_hash': 'sha256:a536397207b68bed66eefb1defcfb80529b8d2aa4fe82645f2ffa38069c60960'},
 'capabilities': [{'name': 'read_invoice',
                   'type': 'resource_read',
                   'description': 'Read resource://invoices/{invoice_id} from the '
                                  'shared Resource Runtime.',
                   'uri': 'resource://invoices/{invoice_id}',
                   'output_schema': 'app.invoices.v1.InvoiceView',
                   'renderer': 'detail',
                   'command': None,
                   'input_schema': None,
                   'emits': []},
                  {'name': 'read_invoice_events',
                   'type': 'resource_read',
                   'description': 'Read resource://invoices/{invoice_id}/events from '
                                  'the shared Resource Runtime.',
                   'uri': 'resource://invoices/{invoice_id}/events',
                   'output_schema': 'app.invoices.v1.InvoiceEventsView',
                   'renderer': 'timeline',
                   'command': None,
                   'input_schema': None,
                   'emits': []},
                  {'name': 'create_invoice',
                   'type': 'command',
                   'description': 'Execute CreateInvoice through the shared Resource '
                                  'Runtime.',
                   'uri': None,
                   'output_schema': None,
                   'renderer': None,
                   'command': 'CreateInvoice',
                   'input_schema': 'app.invoices.v1.CreateInvoiceCommand',
                   'emits': ['CreateInvoiceRequested']}]}

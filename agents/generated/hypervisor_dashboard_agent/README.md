<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/hypervisor_dashboard_agent.yaml -->
<!-- Contract hash: sha256:e4ec619a25955f0c7cfe29270e603cf7256c7840417f77ca63fd48173bda14b5 -->
# hypervisor-dashboard

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/hypervisor_dashboard_agent.yaml`
- Contract hash: `sha256:e4ec619a25955f0c7cfe29270e603cf7256c7840417f77ca63fd48173bda14b5`
- Generator: `resource-agent-factory`

## Run

```bash
uvicorn agents.generated.hypervisor_dashboard_agent.main:app --reload --port 8789
```

## Reproduce

```bash
PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/hypervisor_dashboard_agent.yaml
```

## Markpact provenance

```markpact:agent_generation hypervisor-dashboard
agent:
  id: agent://hypervisor-dashboard
  package: agents.generated.hypervisor_dashboard_agent
source:
  contract: contracts/agents/hypervisor_dashboard_agent.yaml
  contract_hash: sha256:e4ec619a25955f0c7cfe29270e603cf7256c7840417f77ca63fd48173bda14b5
generator:
  id: resource-agent-factory
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/hypervisor_dashboard_agent.yaml
runtime:
  default_run: uvicorn agents.generated.hypervisor_dashboard_agent.main:app --reload --port 8789
logs:
  hypervisor: log://hypervisor?grep=hypervisor-dashboard.local
  process: log://file/output/logs/agents/hypervisor-dashboard.local.process.log
```

```markpact:run_log hypervisor-dashboard.local.latest
inspect:
  command: hypervisor inspect-agent hypervisor-dashboard.local
  uri: view://process/agent/hypervisor-dashboard.local/latest
logs:
  hypervisor: log://hypervisor?grep=hypervisor-dashboard.local
  process: log://file/output/logs/agents/hypervisor-dashboard.local.process.log
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

- `process_view` — `resource_read`, URI: `resource://dashboard/process/agent/{agent_id}/latest`

- `workflow_timeline` — `resource_read`, URI: `resource://dashboard/workflow/{workflow_id}/timeline`

- `incident_explain` — `resource_read`, URI: `resource://dashboard/incident/{incident_id}/explain`

- `repair_diagnose` — `resource_read`, URI: `resource://dashboard/repair/agent/{agent_id}/diagnosis`

- `repair_action` — `command`, URI: `repair://agent/{agent_id}/apply`, command: `ApplySafeRepair`

- `uri_call` — `command`, URI: `hypervisor://dashboard/uri/call`, command: `UriCall`


<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/schema_collab_agent.yaml -->
<!-- Contract hash: sha256:17b3d806a8ebef60fa04b5234c2f32ccc2b94d7745234e05cbbd5c7e51bb4bd3 -->
# schema-collab-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/schema_collab_agent.yaml`
- Contract hash: `sha256:17b3d806a8ebef60fa04b5234c2f32ccc2b94d7745234e05cbbd5c7e51bb4bd3`
- Generator: `resource-agent-factory`

## Run

```bash
uvicorn agents.generated.schema_collab_agent.main:app --reload --port 8131
```

## Reproduce

```bash
PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/schema_collab_agent.yaml
```

## Markpact provenance

```markpact:agent_generation schema-collab-agent
agent:
  id: agent://schema-collab-agent
  package: agents.generated.schema_collab_agent
source:
  contract: contracts/agents/schema_collab_agent.yaml
  contract_hash: sha256:17b3d806a8ebef60fa04b5234c2f32ccc2b94d7745234e05cbbd5c7e51bb4bd3
generator:
  id: resource-agent-factory
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/schema_collab_agent.yaml
runtime:
  default_run: uvicorn agents.generated.schema_collab_agent.main:app --reload --port 8131
logs:
  hypervisor: log://hypervisor?grep=schema-collab-agent.local
  process: log://file/output/logs/agents/schema-collab-agent.local.process.log
```

```markpact:run_log schema-collab-agent.local.latest
inspect:
  command: hypervisor inspect-agent schema-collab-agent.local
  uri: view://process/agent/schema-collab-agent.local/latest
logs:
  hypervisor: log://hypervisor?grep=schema-collab-agent.local
  process: log://file/output/logs/agents/schema-collab-agent.local.process.log
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

- `read_markpact_source` — `resource_read`, URI: `file://agents/generated/schema_collab_agent/README.md`

- `read_device_status` — `resource_read`, URI: `device://device/sensor-1/status`

- `read_robot_state` — `resource_read`, URI: `robot://robot/amr-1/state`

- `run_cron_monitor` — `command`, URI: `cron://www/monitor/landing`, command: `RunCronMonitor`


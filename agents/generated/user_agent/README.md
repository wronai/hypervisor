<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/user_agent.yaml -->
<!-- Contract hash: sha256:740801960691f1c4aefee04d0cc5a7e27aa3a9915ef2eb73a729f9226a10ce45 -->
# user-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/user_agent.yaml`
- Contract hash: `sha256:740801960691f1c4aefee04d0cc5a7e27aa3a9915ef2eb73a729f9226a10ce45`
- Generator: `resource-agent-factory`

## Run

```bash
uvicorn agents.generated.user_agent.main:app --reload --port 8102
```

## Reproduce

```bash
PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/user_agent.yaml
```

## Markpact provenance

```markpact:agent_generation user-agent
agent:
  id: agent://user-agent
  package: agents.generated.user_agent
source:
  contract: contracts/agents/user_agent.yaml
  contract_hash: sha256:740801960691f1c4aefee04d0cc5a7e27aa3a9915ef2eb73a729f9226a10ce45
generator:
  id: resource-agent-factory
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/user_agent.yaml
runtime:
  default_run: uvicorn agents.generated.user_agent.main:app --reload --port 8102
logs:
  hypervisor: log://hypervisor?grep=user-agent.local
  process: log://file/output/logs/agents/user-agent.local.process.log
```

```markpact:run_log user-agent.local.latest
inspect:
  command: hypervisor inspect-agent user-agent.local
  uri: view://process/agent/user-agent.local/latest
logs:
  hypervisor: log://hypervisor?grep=user-agent.local
  process: log://file/output/logs/agents/user-agent.local.process.log
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

- `read_user` — `resource_read`, URI: `resource://users/{user_id}`

- `read_user_roles` — `resource_read`, URI: `resource://users/{user_id}/roles`

- `create_user` — `command`, command: `CreateUser`

- `assign_user_role` — `command`, command: `AssignUserRole`


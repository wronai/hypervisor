<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/remote_deploy_agent.yaml -->
<!-- Contract hash: sha256:cb604273489ae8add7f97a4cad7786e18f628fcb1528369b992e7e437be6846e -->
# remote-deploy-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/remote_deploy_agent.yaml`
- Contract hash: `sha256:cb604273489ae8add7f97a4cad7786e18f628fcb1528369b992e7e437be6846e`
- Generator: `resource-agent-factory`

## Run

```bash
uvicorn agents.generated.remote_deploy_agent.main:app --reload --port 8135
```

## Reproduce

```bash
PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/remote_deploy_agent.yaml
```

## Markpact provenance

```markpact:agent_generation remote-deploy-agent
agent:
  id: agent://remote-deploy-agent
  package: agents.generated.remote_deploy_agent
source:
  contract: contracts/agents/remote_deploy_agent.yaml
  contract_hash: sha256:cb604273489ae8add7f97a4cad7786e18f628fcb1528369b992e7e437be6846e
generator:
  id: resource-agent-factory
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/remote_deploy_agent.yaml
runtime:
  default_run: uvicorn agents.generated.remote_deploy_agent.main:app --reload --port 8135
logs:
  hypervisor: log://hypervisor?grep=remote-deploy-agent.local
  process: log://file/output/logs/agents/remote-deploy-agent.local.process.log
```

```markpact:run_log remote-deploy-agent.local.latest
inspect:
  command: hypervisor inspect-agent remote-deploy-agent.local
  uri: view://process/agent/remote-deploy-agent.local/latest
logs:
  hypervisor: log://hypervisor?grep=remote-deploy-agent.local
  process: log://file/output/logs/agents/remote-deploy-agent.local.process.log
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

- `plan_remote_deploy` — `command`, URI: `deploy://agents/plan`, command: `PlanRemoteDeploy`

- `apply_remote_deploy` — `command`, URI: `deploy://agents/apply`, command: `ApplyRemoteDeploy`

- `verify_remote_agent` — `command`, URI: `deploy://agents/verify`, command: `VerifyRemoteAgent`

- `start_remote_agent` — `command`, URI: `deploy://agents/start`, command: `StartRemoteAgent`

- `deploy_verify_start` — `command`, URI: `workflow://agents/deploy-verify-start`, command: `DeployVerifyStart`


<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/codex_nl_plan_agent.yaml -->
<!-- Contract hash: sha256:2d9bc1c0b851ce7acae3b9134afc15449ddc5fe881c3fdb439c4077b9df4c699 -->
# codex-nl-plan-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/codex_nl_plan_agent.yaml`
- Contract hash: `sha256:2d9bc1c0b851ce7acae3b9134afc15449ddc5fe881c3fdb439c4077b9df4c699`
- Generator: `resource-agent-factory`

## Run

```bash
uvicorn agents.generated.codex_nl_plan_agent.main:app --reload --port 8132
```

## Reproduce

```bash
PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/codex_nl_plan_agent.yaml
```

## Markpact provenance

```markpact:agent_generation codex-nl-plan-agent
agent:
  id: agent://codex-nl-plan-agent
  package: agents.generated.codex_nl_plan_agent
source:
  contract: contracts/agents/codex_nl_plan_agent.yaml
  contract_hash: sha256:2d9bc1c0b851ce7acae3b9134afc15449ddc5fe881c3fdb439c4077b9df4c699
generator:
  id: resource-agent-factory
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/codex_nl_plan_agent.yaml
runtime:
  default_run: uvicorn agents.generated.codex_nl_plan_agent.main:app --reload --port 8132
logs:
  hypervisor: log://hypervisor?grep=codex-nl-plan-agent.local
  process: log://file/output/logs/agents/codex-nl-plan-agent.local.process.log
```

```markpact:run_log codex-nl-plan-agent.local.latest
inspect:
  command: hypervisor inspect-agent codex-nl-plan-agent.local
  uri: view://process/agent/codex-nl-plan-agent.local/latest
logs:
  hypervisor: log://hypervisor?grep=codex-nl-plan-agent.local
  process: log://file/output/logs/agents/codex-nl-plan-agent.local.process.log
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

- `read_markpact_source` — `resource_read`, URI: `file:///app/agents/generated/codex_nl_plan_agent/README.md`

- `read_device_status` — `resource_read`, URI: `device://device/sensor-1/status`

- `run_cron_monitor` — `command`, URI: `cron://www/monitor/landing`, command: `RunCronMonitor`


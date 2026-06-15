<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/codex_nl_smoke_agent.yaml -->
<!-- Contract hash: sha256:1e2da71bd316b85b830c1a1f69f333c7e5ac2b01e83258383005f0967dde488c -->
# codex-nl-smoke-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/codex_nl_smoke_agent.yaml`
- Contract hash: `sha256:1e2da71bd316b85b830c1a1f69f333c7e5ac2b01e83258383005f0967dde488c`
- Generator: `resource-agent-factory`

## Run

```bash
uvicorn agents.generated.codex_nl_smoke_agent.main:app --reload --port 8130
```

## Reproduce

```bash
PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/codex_nl_smoke_agent.yaml
```

## Markpact provenance

```markpact:agent_generation codex-nl-smoke-agent
agent:
  id: agent://codex-nl-smoke-agent
  package: agents.generated.codex_nl_smoke_agent
source:
  contract: contracts/agents/codex_nl_smoke_agent.yaml
  contract_hash: sha256:1e2da71bd316b85b830c1a1f69f333c7e5ac2b01e83258383005f0967dde488c
generator:
  id: resource-agent-factory
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/codex_nl_smoke_agent.yaml
runtime:
  default_run: uvicorn agents.generated.codex_nl_smoke_agent.main:app --reload --port 8130
logs:
  hypervisor: log://hypervisor?grep=codex-nl-smoke-agent.local
  process: log://file/output/logs/agents/codex-nl-smoke-agent.local.process.log
```

```markpact:run_log codex-nl-smoke-agent.local.latest
inspect:
  command: hypervisor inspect-agent codex-nl-smoke-agent.local
  uri: view://process/agent/codex-nl-smoke-agent.local/latest
logs:
  hypervisor: log://hypervisor?grep=codex-nl-smoke-agent.local
  process: log://file/output/logs/agents/codex-nl-smoke-agent.local.process.log
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

- `read_markpact_source` — `resource_read`, URI: `file:///home/tom/github/wronai/hypervisor/agents/generated/codex_nl_smoke_agent/README.md`

- `read_device_status` — `resource_read`, URI: `device://device/sensor-1/status`

- `run_cron_monitor` — `command`, command: `RunCronMonitor`


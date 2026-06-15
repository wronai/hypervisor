<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/codex_uri_smoke_agent.yaml -->
<!-- Contract hash: sha256:92e4d835ecacc5e7138946e5012d5948102fc79fd492458ffb981bd857372c38 -->
# codex-uri-smoke-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/codex_uri_smoke_agent.yaml`
- Contract hash: `sha256:92e4d835ecacc5e7138946e5012d5948102fc79fd492458ffb981bd857372c38`
- Generator: `resource-agent-factory`

## Run

```bash
uvicorn agents.generated.codex_uri_smoke_agent.main:app --reload --port 8101
```

## Reproduce

```bash
PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/codex_uri_smoke_agent.yaml
```

## Markpact provenance

```markpact:agent_generation codex-uri-smoke-agent
agent:
  id: agent://codex-uri-smoke-agent
  package: agents.generated.codex_uri_smoke_agent
source:
  contract: contracts/agents/codex_uri_smoke_agent.yaml
  contract_hash: sha256:92e4d835ecacc5e7138946e5012d5948102fc79fd492458ffb981bd857372c38
generator:
  id: resource-agent-factory
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/codex_uri_smoke_agent.yaml
runtime:
  default_run: uvicorn agents.generated.codex_uri_smoke_agent.main:app --reload --port 8101
logs:
  hypervisor: log://hypervisor?grep=codex-uri-smoke-agent.local
  process: log://file/output/logs/agents/codex-uri-smoke-agent.local.process.log
```

```markpact:run_log codex-uri-smoke-agent.local.latest
inspect:
  command: hypervisor inspect-agent codex-uri-smoke-agent.local
  uri: view://process/agent/codex-uri-smoke-agent.local/latest
logs:
  hypervisor: log://hypervisor?grep=codex-uri-smoke-agent.local
  process: log://file/output/logs/agents/codex-uri-smoke-agent.local.process.log
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

- `read_markpact_source` — `resource_read`, URI: `file:///home/tom/github/wronai/hypervisor/agents/generated/codex_uri_smoke_agent/README.md`

- `read_device_status` — `resource_read`, URI: `device://device/sensor-1/status`

- `run_cron_monitor` — `command`, command: `RunCronMonitor`


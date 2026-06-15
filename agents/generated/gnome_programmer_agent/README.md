<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/gnome_programmer_agent.yaml -->
<!-- Contract hash: sha256:7b1bcba0139f125676c81df01f1bc3a4296937cf3a4ee3f06fcd7ff9efd0943e -->
# gnome-programmer-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/gnome_programmer_agent.yaml`
- Contract hash: `sha256:7b1bcba0139f125676c81df01f1bc3a4296937cf3a4ee3f06fcd7ff9efd0943e`
- Generator: `resource-agent-factory`

## Run

```bash
uvicorn agents.generated.gnome_programmer_agent.main:app --reload --port 8136
```

## Reproduce

```bash
PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/gnome_programmer_agent.yaml
```

## Markpact provenance

```markpact:agent_generation gnome-programmer-agent
agent:
  id: agent://gnome-programmer-agent
  package: agents.generated.gnome_programmer_agent
source:
  contract: contracts/agents/gnome_programmer_agent.yaml
  contract_hash: sha256:7b1bcba0139f125676c81df01f1bc3a4296937cf3a4ee3f06fcd7ff9efd0943e
generator:
  id: resource-agent-factory
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/gnome_programmer_agent.yaml
runtime:
  default_run: uvicorn agents.generated.gnome_programmer_agent.main:app --reload --port 8136
logs:
  hypervisor: log://hypervisor?grep=gnome-programmer-agent.local
  process: log://file/output/logs/agents/gnome-programmer-agent.local.process.log
```

```markpact:run_log gnome-programmer-agent.local.latest
inspect:
  command: hypervisor inspect-agent gnome-programmer-agent.local
  uri: view://process/agent/gnome-programmer-agent.local/latest
logs:
  hypervisor: log://hypervisor?grep=gnome-programmer-agent.local
  process: log://file/output/logs/agents/gnome-programmer-agent.local.process.log
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

- `observe_desktop` — `command`, URI: `screen://desktop/observe`, command: `ObserveDesktop`

- `type_on_desktop` — `command`, URI: `input://desktop/type`, command: `TypeOnDesktop`

- `programmer_session` — `command`, URI: `workflow://desktop/programmer-session`, command: `RunProgrammerSession`


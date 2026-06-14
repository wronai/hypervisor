# Artifact standard

Every YAML/JSON lifecycle file uses **one envelope**:

```yaml
$schema: schemas/...
apiVersion: uri3.io/v1
kind: ...

metadata:
  id: ...
  created_at: ...
  created_by: ...

uri:
  self: ...
  # optional links: agent, deployment, source, subject

spec:
  # intent, configuration, expected state

status:
  # runtime observations (when applicable)
```

## Canonical status vocabulary

Lifecycle (ecosystem, apply, deployment):

```text
planned → generated → verified → applied → running
healthy | degraded | failed | stale
repaired | rolled_back
```

ServiceResult envelope (CLI output):

```text
workflow_status
execution_status
service_result_status
data_quality_status
verification_status
```

UI-friendly mapping:

| Technical | Human |
|-----------|-------|
| `healthy` | działa |
| `degraded` | wymaga uwagi |
| `failed` | nie działa |
| `stale` | stan nieaktualny |
| `planned` | zaplanowane |
| `verified` | sprawdzone |
| `applied` | wdrożone |

## Schema index

| Kind | Schema |
|------|--------|
| RuntimeState | `schemas/runtime_state.schema.json` |
| Incident | `schemas/incident.schema.json` |
| RepairPlan | `schemas/repair_plan.schema.json` |
| Ticket | `schemas/ticket.schema.json` |
| EvolutionProposal | `schemas/evolution_proposal.schema.json` |
| ApplyPlan / ApplyResult | `schemas/apply_plan.schema.json`, `apply_result.schema.json` |
| Ecosystem / Proposal | `schemas/ecosystem.schema.json`, `ecosystem_proposal.schema.json` |
| AgentReadiness | `schemas/agent_readiness.schema.json` |
| Workflow artifact | `schemas/workflow_artifact.schema.json` |
| Config | `schemas/config/config_base.schema.json` |

## Example: runtime state

```yaml
$schema: schemas/runtime_state.schema.json
apiVersion: uri3.io/v1
kind: RuntimeState

metadata:
  id: weather-map-agent.local

uri:
  self: runtime://agent/weather-map-agent.local/state
  agent: agent://weather-map-agent
  deployment: hypervisor://local/weather-map-agent.local

spec:
  expected_health_uri: http://localhost:8101/health

status:
  process_status: running
  health_status: failed
  service_result_status: failed
```

## Validation

```bash
hypervisor artifacts schemas
hypervisor artifacts check
hypervisor artifacts lifecycle
uri doctor --strict
```

See also [`CONFIG_URI_YAML.md`](./CONFIG_URI_YAML.md) for `config/*.uri.yaml`.

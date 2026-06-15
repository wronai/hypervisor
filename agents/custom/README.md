# Custom agents

Hand-maintained agent packages live here. They are **not** overwritten by
`resource-agent-factory`.

## When to use custom vs generated

| Use **generated** (`agents/generated/`) | Use **custom** (`agents/custom/`) |
|----------------------------------------|-----------------------------------|
| Thin HTTP wrapper over Resource Runtime | Direct FastAPI implementation |
| Domain handlers in `domains/*/handlers` | Agent-to-agent orchestration, bespoke logic |
| Markpact README provenance from generator | No generator/Markpact README (contract YAML only) |

## Create a custom agent

1. **Contract** — add `contracts/agents/<name>.yaml` (same schema as generated agents).
2. **Package** — create `agents/custom/<python_package>/`:
   - `main.py` — FastAPI app
   - `routes.py` — `/health`, `/.well-known/agent-card.json`, `/skills/*`
   - `agent_card.py` — capabilities aligned with the contract
   - optional modules for business logic (e.g. `analysis.py`)
3. **Deployment** — register in `deployments/agent_deployments.yaml`:

   ```yaml
   - id: my-agent.local
     agent_ref: agent://my-agent
     target_uri: local://agents/custom/my_agent
     metadata:
       source: custom_agent
       contract: contracts/agents/my_agent.yaml
   ```

4. **Run** — `hypervisor run-agent my-agent.local --detach --wait-healthy`

Hypervisor resolves `local://agents/custom/...` to
`agents.custom.<package>.main:app` (see `local_targets.py`).

## Markpact / pactown

Custom agents do **not** use Markpact README blocks or the external `pactown`
runtime. The contract YAML is the source of truth; capabilities are exposed
via hand-written routes. Generated agents under `agents/generated/` embed
Markpact provenance in README for audit and `uri2pact` import.

## Existing custom agents

| Agent | Port | Role |
|-------|------|------|
| `screenshot-analysis-agent.local` | 8134 | Capture + analyze via `desktop-operator` |
| `remote-deploy-agent.local` | 8135 | SSH deploy / verify / start orchestration |
| `gnome-programmer-agent.local` | 8136 | GNOME desktop observe + type via uri2ops |

See [`examples/38_autonomous_agents`](../../examples/38_autonomous_agents/) for multi-agent collaboration.

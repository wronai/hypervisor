# Example 38 — autonomous multi-agent collaboration

Three custom orchestrators collaborate with `desktop-operator`:

| Agent | Port | Role |
|-------|------|------|
| `remote-deploy-agent.local` | 8135 | SSH deploy / verify / start plans |
| `gnome-programmer-agent.local` | 8136 | GNOME desktop observe + type via uri2ops |
| `screenshot-analysis-agent.local` | 8134 | Capture + analyze via desktop-operator |

## Run

```bash
bash examples/38_autonomous_agents/run.sh
ADAPTER=gnome bash examples/38_autonomous_agents/run.sh   # real GNOME tools when available
```

## Outputs

- `output/reports/examples-audit/` — describe-agent reports
- `output/analysis/remote-deploy/` — remote deploy orchestration logs
- `output/analysis/gnome-programmer/` — desktop session notes
- `output/analysis/screenshots/` — screenshot analysis JSONL/MD

## Remote host (optional)

With Docker testenv (`make docker-testenv-up`):

```bash
hypervisor deploy-agent weather-map-agent.ssh-dev --apply
curl -X POST http://localhost:8135/skills/deploy_verify_start \
  -H 'Content-Type: application/json' \
  -d '{"deployment_id":"weather-map-agent.ssh-dev","wait_healthy":true}'
```

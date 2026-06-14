# URI cookbook

Quick recipes. Prefer **`uri`** shortcuts where listed; full URIs work everywhere.

## Agents and health

| I want to… | Command / URI |
|------------|----------------|
| Agent status | `uri agent status weather-map-agent.local` |
| Agent health | `uri agent health weather-map-agent.local` or `uri hwa` |
| Run agent | `uri agent run weather-map-agent.local --wait-healthy --approve` |
| Inspect readiness | `hypervisor inspect-agent weather-map-agent.local` |
| Health URI | `health://agent/weather-map-agent.local` |

## Logs and observation

| I want to… | Command / URI |
|------------|----------------|
| Hypervisor logs | `uri logs log://hypervisor?grep=weather-map-agent.local` |
| Watch health | `uri watch health://agent/weather-map-agent.local --count 5` |
| Explain URI | `uri explain weather://forecast/Gdansk/14/html` |

## Repair and autonomy

| I want to… | Command / URI |
|------------|----------------|
| Diagnose | `uri repair diagnose weather-map-agent.local` or `uri rwa` |
| Dry-run repair | `uri repair apply weather-map-agent.local --dry-run` |
| Apply repair | `uri repair apply weather-map-agent.local --approve` |
| Repair URI | `repair://agent/weather-map-agent.local/diagnose` |

## Tickets and evolution

| I want to… | Command / URI |
|------------|----------------|
| List tickets | `uri ticket list` |
| Show ticket | `uri ticket show ticket://feature/PL-1` |
| Proposal from ticket | `uri evolve from-ticket ticket://feature/PL-1` |
| Verify proposal | `uri proposal verify evolution/proposals/proposal_from_ticket_PL-1.yaml` |
| Sandbox apply | `uri proposal apply … --sandbox` |

## Ecosystem (create agents)

| I want to… | Command |
|------------|---------|
| Natural language plan | `uri ask "stwórz agenta pogodowego"` |
| Plan ecosystem | `uri ecosystem plan "…" --profile minimal --out output/proposals/weather.yaml` |
| Generate artifacts | `uri ecosystem generate output/proposals/weather.yaml --out output/ecosystems/weather` |
| Verify | `uri ecosystem verify output/ecosystems/weather/ecosystem.yaml` |
| Apply plan | `uri ecosystem apply …/ecosystem.yaml --plan` |
| Apply for real | `uri ecosystem apply …/ecosystem.yaml --approve` |

## Dashboard (Web UI agent)

| I want to… | Command / URI |
|------------|----------------|
| Plan dashboard | `uri ask "stwórz web UI hypervisor-dashboard"` |
| Create (plan only) | `uri dashboard create hypervisor-dashboard --plan-only` |
| Run dashboard | `uri agent run hypervisor-dashboard.local --wait-healthy --approve` |
| Open UI | `uri dashboard open` or `uri dashboard-ui --approve` |
| Process view | `view://process/agent/weather-map-agent.local/latest` |
| Incident explain | `view://incident/{incident_id}/explain` |

## Shortcuts (`config/cli_shortcuts.uri.yaml`)

| Shortcut | URI |
|----------|-----|
| `uri hwa` | `health://agent/weather-map-agent.local` |
| `uri rwa` | `repair://agent/weather-map-agent.local/diagnose` |
| `uri wh` | `weather://forecast/Gdansk/14/html` |
| `uri weather-status` | same as `hwa` |
| `uri weather-process` | process view for weather agent |
| `uri dashboard-ui --approve` | open dashboard UI with payload from config |

## Policy reminders

```bash
uri call repair://agent/demo/apply              # blocked without --approve
uri call repair://agent/demo/apply --dry-run    # show plan only
uri call repair://agent/demo/apply --approve    # execute
```

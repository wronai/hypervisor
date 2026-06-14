# Hypervisor Dashboard Agent

System agent `agent://hypervisor-dashboard` — observer, renderer, and controlled action launcher over URI.

## Role

- Reads system URIs (`view://`, `runtime://`, `health://`, `log://`, `incident://`, `repair://`)
- Renders process views in the browser
- Launches mutating actions only with explicit approval

## Run locally

```bash
uv run uvicorn hypervisor_dashboard_agent.main:app --host 0.0.0.0 --port 8788
```

Or via hypervisor deployment:

```bash
hypervisor run-agent hypervisor-dashboard.local --detach
```

## Endpoints

| Path | Maps to |
|------|---------|
| `GET /ui/agents` | agent list |
| `GET /ui/agents/{id}` | `view://process/agent/{id}/latest` |
| `GET /api/view/process/agent/{id}` | JSON view envelope |
| `POST /api/uri/call` | policy-gated URI execution |

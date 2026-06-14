# user-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/user_agent.yaml`
- Contract hash: `sha256:740801960691f1c4aefee04d0cc5a7e27aa3a9915ef2eb73a729f9226a10ce45`

## Run

```bash
uvicorn agents.generated.user_agent.main:app --reload --port 8101
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

- `read_user` — `resource_read`, URI: `resource://users/{user_id}`- `read_user_roles` — `resource_read`, URI: `resource://users/{user_id}/roles`- `create_user` — `command`, command: `CreateUser`- `assign_user_role` — `command`, command: `AssignUserRole`
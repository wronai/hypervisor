# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/user_agent.yaml
# Contract hash: sha256:740801960691f1c4aefee04d0cc5a7e27aa3a9915ef2eb73a729f9226a10ce45

AGENT_CARD = {
  "capabilities": [
    {
      "command": null,
      "description": "Read a single user view by user_id.",
      "emits": [],
      "input_schema": null,
      "name": "read_user",
      "output_schema": "app.users.v1.UserView",
      "renderer": "detail",
      "type": "resource_read",
      "uri": "resource://users/{user_id}"
    },
    {
      "command": null,
      "description": "Read roles assigned to a user.",
      "emits": [],
      "input_schema": null,
      "name": "read_user_roles",
      "output_schema": "app.users.v1.UserRolesView",
      "renderer": "table",
      "type": "resource_read",
      "uri": "resource://users/{user_id}/roles"
    },
    {
      "command": "CreateUser",
      "description": "Create a user by emitting UserCreated.",
      "emits": [
        "UserCreated"
      ],
      "input_schema": "app.users.v1.CreateUserCommand",
      "name": "create_user",
      "output_schema": null,
      "renderer": null,
      "type": "command",
      "uri": null
    },
    {
      "command": "AssignUserRole",
      "description": "Assign a role to a user.",
      "emits": [
        "UserRoleAssigned"
      ],
      "input_schema": "app.users.v1.AssignUserRoleCommand",
      "name": "assign_user_role",
      "output_schema": null,
      "renderer": null,
      "type": "command",
      "uri": null
    }
  ],
  "description": "Thin generated agent for reading users and dispatching user commands.",
  "generated_from": {
    "contract": "contracts/agents/user_agent.yaml",
    "contract_hash": "sha256:740801960691f1c4aefee04d0cc5a7e27aa3a9915ef2eb73a729f9226a10ce45"
  },
  "name": "user-agent",
  "version": "0.1.0"
}
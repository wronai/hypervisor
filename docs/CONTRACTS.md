# Kontrakty agentów

## Minimalny kontrakt

```yaml
agent:
  name: user-agent
  python_package: user_agent
  version: 0.1.0
  description: Thin generated agent for users.
  runtime_url_env: RESOURCE_RUNTIME_URL
  runtime_url_default: http://localhost:8000

capabilities:
  - name: read_user
    type: resource_read
    uri: resource://users/{user_id}
    output_schema: app.users.v1.UserView
    renderer: detail

  - name: create_user
    type: command
    command: CreateUser
    input_schema: app.users.v1.CreateUserCommand
    emits:
      - UserCreated
```

## Capability: resource_read

Służy do odczytu danych z Resource Runtime przez URI.

```yaml
- name: read_user_roles
  type: resource_read
  uri: resource://users/{user_id}/roles
  output_schema: app.users.v1.UserRolesView
  renderer: table
```

## Capability: command

Służy do wysyłania komend do Resource Runtime.

```yaml
- name: assign_user_role
  type: command
  command: AssignUserRole
  input_schema: app.users.v1.AssignUserRoleCommand
  emits:
    - UserRoleAssigned
```

## Dobre praktyki

- Nazwa capability powinna być stabilna.
- URI powinno być semantyczne, nie techniczne.
- Nie wiąż URI z nazwą tabeli SQL.
- Capability powinno mieć test kontraktowy.
- Breaking change wymaga nowej wersji capability albo nowego URI.

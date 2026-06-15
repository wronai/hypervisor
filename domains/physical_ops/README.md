# Physical Ops domain

Canonical YAML registry: [`scenario_registry.yaml`](./scenario_registry.yaml)

This domain pack describes generic physical-operation routing for robots,
sensors, actuators, PLC-like devices and field equipment. It does not execute
device actions directly. Execution stays in `uri2ops`, lifecycle stays in
`hypervisor`, and the generic operator contract stays in
[`agents/operators/device_robot_operator.yaml`](../../agents/operators/device_robot_operator.yaml).

## URI design

Use `robot://` when the target has autonomy, motion, pose or mission state:

| Intent | URI |
|--------|-----|
| Read robot state | `robot://robot/{id}/state` |
| Move robot | `robot://robot/{id}/move` |
| Stop robot | `robot://robot/{id}/stop` |
| Start mission | `robot://robot/{id}/mission/{mission_id}/start` |

Use `device://` when the target is a sensor, actuator, PLC register, relay,
camera, scale, printer or another field device:

| Intent | URI |
|--------|-----|
| Read device status | `device://device/{id}/status` |
| Read value/register | `device://device/{id}/read` |
| Write value/register | `device://device/{id}/write` |

Mutating physical actions should include a human/safety gate in plans:

```text
robot://robot/amr-1/state
human://operator/safety/approve
robot://robot/amr-1/move
```

## Files

| File | Purpose |
|------|---------|
| [`domain.yaml`](./domain.yaml) | Boundary and ownership contract |
| [`operator_registry.yaml`](./operator_registry.yaml) | Robot and device capability cards |
| [`scenario_registry.yaml`](./scenario_registry.yaml) | NL routing to physical-operation URIs |

## Load from markpact

```markpact:scenario_registry physical-ops
include: domains/physical_ops/scenario_registry.yaml
kind: urish.scenario_registry
metadata:
  id: physical-ops
  markpact_readme: domains/physical_ops/README.md
```

## Exportable scenarios

```markpact:scenario robot_status
scenario:
  id: robot_status
  subtype: robot_status
  chat_prompt: Sprawdz stan robota amr-1 i pokaz baterie oraz pozycje.
  planned_uris:
    - robot://robot/amr-1/state
  human_in_the_loop: false
```

```markpact:scenario robot_move_with_approval
scenario:
  id: robot_move_with_approval
  subtype: robot_move
  chat_prompt: Przesun robota amr-1 do punktu kontrolnego po zatwierdzeniu operatora.
  planned_uris:
    - robot://robot/amr-1/state
    - human://operator/safety/approve
    - robot://robot/amr-1/move
  human_in_the_loop: true
```

```markpact:scenario device_read
scenario:
  id: device_read
  subtype: device_read
  chat_prompt: Odczytaj temperature z czujnika sensor-1.
  planned_uris:
    - device://device/sensor-1/status
    - device://device/sensor-1/read
  human_in_the_loop: false
```

```markpact:scenario device_write_with_approval
scenario:
  id: device_write_with_approval
  subtype: device_write
  chat_prompt: Wlacz przekaznik relay-1 po zatwierdzeniu operatora.
  planned_uris:
    - device://device/relay-1/status
    - human://operator/safety/approve
    - device://device/relay-1/write
  human_in_the_loop: true
```

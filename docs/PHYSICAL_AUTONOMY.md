# Physical Autonomy

Physical autonomy covers robots, sensors, actuators, PLC-like devices and field
equipment. It is implemented as a controlled `uri2ops` capability layer, not as
hidden hardware logic inside the hypervisor.

```text
NL/domain prompt
  -> domains/physical_ops scenario
  -> URI task graph
  -> agent://device-robot-operator
  -> uri2ops operation registry
  -> robot/device adapter
  -> artifacts, logs, validation and approval gates
```

## Best URI Schemes

Use two top-level schemes:

| Scheme | Use for | Examples |
|--------|---------|----------|
| `robot://` | actors with motion, pose, autonomy, missions or safety state | AMR, AGV, cobot, robotic arm |
| `device://` | sensors, actuators, PLC registers and field devices | relay, camera, scale, printer, meter |

Do not encode a customer workflow into the scheme. Keep workflows in
`domains/<domain>/` and use the physical URIs as execution capabilities.

## Robot URIs

| Intent | URI | Approval |
|--------|-----|----------|
| Read state | `robot://robot/{id}/state` | no |
| Move | `robot://robot/{id}/move` | yes |
| Stop | `robot://robot/{id}/stop` | yes |
| Start mission | `robot://robot/{id}/mission/{mission_id}/start` | yes |

Preferred plan shape:

```text
robot://robot/amr-1/state
human://operator/safety/approve
robot://robot/amr-1/move
```

## Device URIs

| Intent | URI | Approval |
|--------|-----|----------|
| Read status | `device://device/{id}/status` | no |
| Read value/register | `device://device/{id}/read` | no |
| Write value/register | `device://device/{id}/write` | yes |

Preferred plan shape:

```text
device://device/relay-1/status
human://operator/safety/approve
device://device/relay-1/write
```

## Separation Rule

| Layer | Owns | Must not own |
|-------|------|--------------|
| `domains/physical_ops` | Generic physical routing vocabulary and safety boundaries | Hardware adapter implementation |
| `agents/operators/` | Capability-agent contracts | Factory/warehouse process data |
| `packages/uri2ops` | Operation registry, adapters, task execution, A2A/MCP serve runtime | Business workflows |
| `hypervisor` | Deployment, policy, events, incidents, approval | Direct device control |

The capability contract is
[`agents/operators/device_robot_operator.yaml`](../agents/operators/device_robot_operator.yaml).
The generic routing/domain pack is
[`domains/physical_ops/`](../domains/physical_ops/).

## Running The Mock Operator

```bash
hypervisor run-agent device-robot-operator.local --detach --wait-healthy
curl -s http://127.0.0.1:8792/health
curl -s http://127.0.0.1:8792/.well-known/agent-card.json
```

Or run task examples directly:

```bash
python -m uri2ops.cli validate examples/36_physical_ops/task.robot.yaml
python -m uri2ops.cli run examples/36_physical_ops/task.robot.yaml --adapter mock --approve
python -m uri2ops.cli validate examples/36_physical_ops/task.device.yaml
python -m uri2ops.cli run examples/36_physical_ops/task.device.yaml --adapter mock --approve
```

## Adapter Roadmap

Current implementation is mock-only. Real adapters should be added behind the
same URI contracts:

| Adapter | Likely use |
|---------|------------|
| `ros2` | robot state, movement and missions |
| `mqtt` | IoT sensors/actuators and lightweight robots |
| `modbus` | PLC/register style device access |
| `opcua` | industrial device telemetry/control |
| `vendor_sdk` | proprietary robot or device APIs |

Real adapters must require explicit selection and policy approval for physical
mutations. They should never run implicitly from generic NL prompts.

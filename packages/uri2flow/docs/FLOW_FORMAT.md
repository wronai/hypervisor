# Compact URI Flow Format

The compact flow format is the preferred authoring format for humans and LLMs.

## Linear flow

```yaml
do:
  - A
  - B
  - C
```

means:

```text
A -> B -> C
```

## URI step with payload

```yaml
do:
  - browser://chrome/page/open:
      url: http://localhost:8101/health
```

## Explicit id and branching

```yaml
do:
  - id: run_agent
    uri: hypervisor://local/weather-agent/run

  - id: check_health
    uri: http://localhost:8101/health
    after: run_agent

  - id: read_card
    uri: http://localhost:8101/.well-known/agent-card.json
    after: run_agent
```

## Expanded graph

The expanded graph contains explicit node IDs, operations, kind, dependencies and edges. It should be treated as an intermediate machine format.

# Architecture: Resource Agent Meta-Factory

The project has three layers.

## 1. Shared Resource Runtime

The runtime owns the actual business execution:

```text
Event Store -> Projections -> URI Resolver -> Renderer
```

Generated agents call this runtime instead of implementing their own business logic.

## 2. Agent Factory

The factory turns YAML contracts into thin FastAPI agents:

```text
contracts/agents/*.yaml -> generator -> agents/generated/*
```

Generated agents expose:

- health endpoint,
- capabilities endpoint,
- Agent Card,
- resource reads,
- command forwarding.

## 3. Meta-agent

The meta-agent manages the factory:

```text
prompt -> proposal YAML -> validation -> repair -> generation -> verification
```

It is an orchestration and governance layer.

## Recommended deployment

For local development:

```text
Resource Runtime: localhost:8000
Meta-Agent:       localhost:8200
Generated Agent:  localhost:8101+
```

For Docker deployment:

```text
resource-runtime
meta-agent
user-agent
orders-agent
invoices-agent
postgres
```

## Thin vs thick agents

This package generates thin agents. They do not own state. They forward reads and commands to the shared runtime.

Use thick agents only later, when each domain needs separate storage, scaling and deployment.

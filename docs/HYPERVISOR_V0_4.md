# Resource Agent Hypervisor v0.4

v0.4 adds natural-language-to-domain-pack generation and URI routing.

## New features

- `nl2a -p` CLI.
- LLM-configurable domain planner using `.env` and OpenRouter-compatible chat completions.
- Deterministic fallback planner for reproducible generation.
- URI Tree schema.
- Domain Pack generator.
- `uri2llm` resolver for env, llm, python functions, PyPI, A2A, MCP and resource/artifact URIs.
- Weather map domain generation example.

## Design decision

The domain layer is generated as a Domain Pack. It is not part of the hypervisor core.

The hypervisor owns:

```txt
Contract Registry
Compatibility
Policy Gate
Verifier
Agent Factory
URI Router
Evolution Pipeline
```

A generated Domain Pack owns:

```txt
proto
resources
views
commands
renderers
handlers
templates
tests
```

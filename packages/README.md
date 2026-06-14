# Monorepo packages (v0.5.6)

Physical Python packages live under `packages/`:

| Directory | Distribution | Modules |
|---|---|---|
| `packages/uri3/` | `uri3` | `uri3` |
| `packages/nl2uri/` | `nl2uri` | `nl2uri`, `nl2a` |
| `packages/resource-agent-hypervisor/` | `resource-agent-hypervisor` | `hypervisor`, `meta_agent`, `runtime_client` |
| `packages/resource-agent-factory/` | `resource-agent-factory` | `generator` |

Shared repo assets remain at the repository root:

```txt
contracts/ schemas/ domains/ agents/ deployments/ output/ tests/
```

Install editable workspace from repo root:

```bash
uv sync
```

Or a single legacy editable install still works via root `pyproject.toml`.

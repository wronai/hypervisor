# Generated agents

This directory contains **build output** from `resource-agent-factory` (`generator/`).

- Do **not** edit files here manually.
- Regenerate from contract YAML under `contracts/agents/`.
- Keep custom extensions in `agents/custom/`.

Each agent directory includes:

- Python sources with `# AUTO-GENERATED FILE. DO NOT EDIT.`
- `.generated.yaml` marker with source contract and hash

Regenerate:

```bash
python -m generator.agent_generator contracts/agents/*.yaml
```

# Resource Agent Meta-Factory v0.1


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.1-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.43-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-2.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.4309 (2 commits)
- 👤 **Human dev:** ~$200 (2.0h @ $100/h, 30min dedup)

Generated on 2026-06-14 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---



Generator, validator and repairer for contract-first thin agents.

This package extends the earlier `resource-agent-factory` with a **meta-agent** that can create agent specifications from prompts, validate them, repair common mistakes and generate working FastAPI agents.

## Core idea

```text
Prompt / request
      ↓
Meta-agent
      ↓
contracts/agents/*.yaml
      ↓
Validator + safe repair
      ↓
Agent Factory
      ↓
agents/generated/<agent>/
      ↓
Tests + contract hash verification
```

The LLM or user creates the **contract proposal**. The deterministic generator creates the code.

## Quick start

Install dependencies:

```bash
pip install -e '.[dev]'
```

Validate existing contracts:

```bash
make validate
```

Generate agents:

```bash
make generate
```

Verify generated agents:

```bash
make verify
```

Run tests:

```bash
make test
```

## Meta-agent workflow

Create a new agent from a prompt:

```bash
python -m meta_agent.cli pipeline "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia"
```

Run the meta-agent HTTP API:

```bash
make run-meta-agent
```

Then call:

```bash
curl -X POST http://localhost:8200/pipeline/from-prompt \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Stwórz agenta do obsługi faktur z odczytem faktury, historią i tworzeniem faktury"}'
```

## Important rule

Do not edit `agents/generated/` manually.

Change:

```text
contracts/agents/*.yaml
```

Then regenerate.

## Documentation

- `docs/META_AGENT.md` — meta-agent usage.
- `docs/ARCHITECTURE_META_FACTORY.md` — architecture.
- `docs/AUTO_EVOLUTION_PIPELINE.md` — controlled auto-evolution.
- `docs/CONTRACTS.md` — YAML contract format.
- `docs/GENERATOR.md` — generator details.
- `docs/DEPLOYMENT.md` — deployment notes.


## License

Licensed under Apache-2.0.

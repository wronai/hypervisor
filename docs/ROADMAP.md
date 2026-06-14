# Roadmap

## v0.1

- YAML agent spec
- generator FastAPI agent
- Agent Card
- runtime client
- contract hash verify
- basic tests

## v0.2

- generator MCP adapter
- generator OpenAPI docs
- better URI template matching
- contract schema JSON Schema

## v0.3

- A2A transport adapter
- capability test runner
- sample multi-agent setup

## v0.4

- Evolution Proposal format
- proposal validator
- compatibility report

## v0.5

- agent-assisted proposal creation
- approval gate
- CI template
- uri3 / nl2uri / hypervisor split (monorepo packages)

## v0.6 (done)

### uri3 workflow

- [x] `validate-workflow`, `plan-workflow`, `run-workflow`
- [x] Mock + Playwright browser adapters w executorze MVP
- [x] Event JSONL w `output/events/workflows/`

### nl2uri multi-output

- [x] CLI: `single`, `list`, `tree`, `task`, `graph`, `plan`, `classify`
- [x] LLM graph planner (`--llm`) + graph repair + registry injection
- [x] Integracja walidacji uri3 (`--validate`, `--dry-run`)

### uri2ops v0.1–v0.5

- [x] Operation registry + mock adapters + policy + artifacts
- [x] Playwright, Android ADB, Windows UIA adapters
- [x] `uri2ops serve` (FastAPI), A2A/MCP, remote registry merge

### uri2flow v0.1

- [x] Compact URI flow format (`*.uri.flow.yaml`)
- [x] `uri2flow validate|expand|print` → expanded `workflow_graph`
- [x] Przykład `15_compact_uri_flow`, testy `tests/uri2flow/`

### Przykłady

- [x] `10_browser_operator` … `16_llm_graph_planner`

## v0.7 (planned)

- [ ] uri3 `run-workflow` → uri2ops jako wspólny backend
- [ ] Hypervisor policy gate + audit trail dla operator runs
- [ ] `hypervisor run-workflow` z deployment registry
- [ ] TLS/auth dla `uri2ops serve` w produkcji
- [ ] Real shell/SSH adapter w uri2ops

Szczegóły: [`TODO.md`](../TODO.md) · [`packages/uri2ops/TODO.md`](../packages/uri2ops/TODO.md)

<!-- AUTO-GENERATED FILE. DO NOT EDIT. -->
<!-- Source: contracts/agents/screenshot_analysis_agent.yaml -->
<!-- Contract hash: sha256:a541c061b26d8303d14f931b3ad48dea9ada37990cc1a9426d2c1c0a13fbc77e -->
# screenshot-analysis-agent

Generated thin resource agent.

- Version: `0.1.0`
- Source: `contracts/agents/screenshot_analysis_agent.yaml`
- Contract hash: `sha256:a541c061b26d8303d14f931b3ad48dea9ada37990cc1a9426d2c1c0a13fbc77e`
- Generator: `resource-agent-factory`

## Run

```bash
uvicorn agents.generated.screenshot_analysis_agent.main:app --reload --port 8134
```

## Reproduce

```bash
PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/screenshot_analysis_agent.yaml
```

## Markpact provenance

```markpact:agent_generation screenshot-analysis-agent
agent:
  id: agent://screenshot-analysis-agent
  package: agents.generated.screenshot_analysis_agent
source:
  contract: contracts/agents/screenshot_analysis_agent.yaml
  contract_hash: sha256:a541c061b26d8303d14f931b3ad48dea9ada37990cc1a9426d2c1c0a13fbc77e
generator:
  id: resource-agent-factory
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator contracts/agents/screenshot_analysis_agent.yaml
runtime:
  default_run: uvicorn agents.generated.screenshot_analysis_agent.main:app --reload --port 8134
logs:
  hypervisor: log://hypervisor?grep=screenshot-analysis-agent.local
  process: log://file/output/logs/agents/screenshot-analysis-agent.local.process.log
```

```markpact:run_log screenshot-analysis-agent.local.latest
inspect:
  command: hypervisor inspect-agent screenshot-analysis-agent.local
  uri: view://process/agent/screenshot-analysis-agent.local/latest
logs:
  hypervisor: log://hypervisor?grep=screenshot-analysis-agent.local
  process: log://file/output/logs/agents/screenshot-analysis-agent.local.process.log
```

## Endpoints

```txt
GET /health
GET /capabilities
GET /.well-known/agent.json
GET /.well-known/agent-card.json
GET /resources/read?uri=...
POST /commands
```

## Capabilities

- `analyze_screenshot` — `command`, URI: `analysis://screenshots/analyze`, command: `AnalyzeScreenshot`

- `capture_and_analyze` — `command`, URI: `workflow://screenshots/capture-and-analyze`, command: `CaptureAndAnalyze`

- `scheduled_capture_analysis` — `command`, URI: `cron://screenshots/capture-analysis/every-5-min`, command: `RunScheduledCaptureAnalysis`


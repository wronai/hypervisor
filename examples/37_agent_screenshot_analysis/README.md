# Example 37 — two agents: screenshot capture + screenshot analysis

This example verifies agent-to-agent work:

```text
screenshot-analysis-agent
  -> calls desktop-operator /run
  -> desktop-operator opens a page and captures a screenshot artifact
  -> screenshot-analysis-agent reads the returned artifact URI
  -> writes observations to output/analysis/screenshots/
```

The production schedule URI for running this every five minutes is:

```text
cron://screenshots/capture-analysis/every-5-min
```

The smoke script runs two ticks immediately instead of waiting five minutes.

## Run

```bash
bash examples/37_agent_screenshot_analysis/run.sh
```

The default run uses the deterministic `mock` adapter. To capture and analyze
a real PNG screenshot through Playwright, use the same script with:

```bash
ADAPTER=playwright bash examples/37_agent_screenshot_analysis/run.sh
```

## Useful URIs

```bash
uri call schema://agent/desktop-operator.local --json
uri call schema://agent/screenshot-analysis-agent.local --json
uri call health://agent/desktop-operator.local --json
uri call health://agent/screenshot-analysis-agent.local --json
```

Analysis output:

```text
output/analysis/screenshots/screenshot-analysis.jsonl
output/analysis/screenshots/screenshot-analysis.md
```

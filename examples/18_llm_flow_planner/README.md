# Example 18 — LLM Compact Flow Planner (v0.6.4)

Rule-based compact flow (no API key):

```bash
nl2uri flow -p "$(cat prompt.txt)" --validate
```

LLM compact flow with repair + validate:

```bash
export OPENROUTER_API_KEY=...
nl2uri flow -p "$(cat prompt.txt)" --llm --validate
```

Expand and execute via uri3:

```bash
nl2uri flow -p "$(cat prompt.txt)" --validate > /tmp/weather.uri.flow.yaml
uri3 expand-flow /tmp/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
uri3 run-flow /tmp/weather.uri.flow.yaml --dry-run
uri3 run-flow /tmp/weather.uri.flow.yaml --approve --browser mock
```

One-liner with expand output:

```bash
nl2uri flow -p "$(cat prompt.txt)" --validate --expand
```

If the LLM returns graph nodes or invalid schemes, `flow_repair` normalizes to compact `do:` steps and falls back to the rule-based planner when validation still fails.

Compare with example 16 (full `workflow_graph`) and example 17 (hand-authored compact flow).

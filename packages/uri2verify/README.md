# uri2verify

Shared verification layer for the URI stack:

```txt
data_quality     — confidence, validators, relevance gates
replay           — workflow event log analysis + regression test generation
capability_plan  — contract registry capability test plans
result_checks    — data_quality_status, verification_status, technical vs business ok
```

Used by `touri`, `uri3`, and `hypervisor` (thin wrappers — logic lives here).

## CLI

```bash
uri2verify replay check-agent-health
uri2verify replay output/events/workflows/check-agent-health.jsonl --timeline
uri2verify replay demo --create-test tests/regression/test_replay_demo.py

uri2verify capability-plan .

uri2verify data-quality examples/20_touri_capabilities weather://forecast/Gdansk/14/html
```

Equivalent facades:

```bash
uri3 replay check-agent-health
uri3 doctor --capability-plan
uri3 doctor --replay-failures
hypervisor replay-failure check-agent-health --create-test tests/replay/test_check_agent_health.py
```

## Library

```python
from uri2verify import apply_data_quality, replay_workflow_events, build_capability_test_plan
from uri2verify.result_checks import enrich_result_dict, technical_vs_business_ok
```

See [`docs/PACKAGE_BOUNDARIES.md`](../../docs/PACKAGE_BOUNDARIES.md) · [`docs/SERVICE_RESULT.md`](../../docs/SERVICE_RESULT.md).

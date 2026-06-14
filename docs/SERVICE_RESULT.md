# ServiceResult envelope

Canonical result format for `touri`, `uri3`, `uri2ops`, and hypervisor workflow layers.

## Module

```python
from uri3.results import ErrorEnvelope, ServiceResult, service_result
```

Location: `packages/uri3/uri3/results/`

## Fields

| Field | Description |
|-------|-------------|
| `ok` | top-level pass/fail shortcut |
| `workflow_status` | `completed`, `completed_with_service_error`, `failed` |
| `execution_status` | `completed`, `failed` |
| `service_result_status` | `succeeded`, `failed` |
| `result_type` | `data`, `artifact`, `mock`, `error`, … |
| `uri`, `capability`, `backend` | routing context |
| `data`, `artifact_uri` | payload |
| `errors` | list of `ErrorEnvelope` |
| `warnings`, `meta` | diagnostics |

## ErrorEnvelope

```json
{
  "code": "PRICE_RESULT_NOT_RELEVANT",
  "source": "touri://capability/price.search",
  "recoverable": true,
  "detail": "…",
  "data_quality": {}
}
```

Do not use bare strings in `errors` for new code — use structured envelopes.

## Usage

```python
result = service_result(
    ok=False,
    result_type="error",
    uri="price://search/cukier",
    capability="price.search",
    errors=[{"code": "PRICE_RESULT_NOT_RELEVANT", "recoverable": True, "detail": "…"}],
)
payload = result.to_dict()
```

`touri call` and future `uri3`/`uri2ops` adapters should return this shape.

## Migration

| Layer | Status |
|-------|--------|
| `touri` | uses shared envelope + data_quality |
| `uri3 graph_executor` | planned |
| `uri2ops run_task` | planned |
| `hypervisor lifecycle` | planned |

See [`ANTI_TELLM.md`](./ANTI_TELLM.md) for rationale.

# Anti-tellm safeguards

Shared result envelope and LLM boundaries to avoid repeating `tellm` failure modes in hypervisor capability/provider layers.

## Problem (tellm)

```txt
LLM + provider + naive parser + ok=true  →  false confidence in bad data
```

## Hypervisor defense

```txt
nl2uri      → intent only (flow/graph/proposal)
touri       → URI -> capability manifest -> backend
uri3        → validation, routing, graph execution
uri2ops     → operator/browser/OS actions
hypervisor  → lifecycle, deployment, policy
```

LLM must **not** produce final business truth or runtime providers without contracts and tests.

## Shared envelope

All layers should converge on [`uri3.results.ServiceResult`](../packages/uri3/uri3/results/service_result.py):

```json
{
  "ok": false,
  "workflow_status": "completed_with_service_error",
  "execution_status": "completed",
  "service_result_status": "failed",
  "result_type": "artifact",
  "uri": "price://search/cukier",
  "capability": "price.search",
  "errors": [
    {
      "code": "PRICE_RESULT_NOT_RELEVANT",
      "source": "touri://capability/price.search",
      "recoverable": true,
      "detail": "Visible prices found, but not for requested product"
    }
  ]
}
```

Three status levels:

| Field | Meaning |
|-------|---------|
| `workflow_status` | graph/workflow finished? |
| `execution_status` | backend call ran? |
| `service_result_status` | business/data outcome OK? |

## URI resolution order

Configured in [`config/touri.uri.yaml`](../config/touri.uri.yaml):

```txt
1. uri3 built-in schemes
2. touri capability registry
3. uri2ops operator registry
4. hypervisor deployment registry
5. denied
```

Diagnostic:

```bash
uri3 explain weather://forecast/Gdansk/14/html
uri3 explain browser://chrome/page/open
uri3 explain http://localhost:8101/health
```

## Data quality (touri)

Capability manifests may declare:

```yaml
data_quality:
  relevance_required: true
  min_confidence: 0.75
  failure_code: PRICE_RESULT_NOT_RELEVANT
  validators:
    - python://validators.price:validate_relevance
```

`touri call` runs validators after backend execution and sets `service_result_status=failed` when quality checks fail.

## Provider testing checklist

For each external-data capability:

```txt
tests/capabilities/<id>/
  fixtures/good.html
  fixtures/irrelevant.html
  test_success.py
  test_irrelevant_result.py
  test_provider_blocked.py
  test_fallback.py
```

Use fixture HTML → parser → `ServiceResult`, not live internet in unit tests.

## LLM boundaries

LLM **may** produce:

- prompt classification
- `uri_flow` / `workflow_graph`
- capability **proposal**
- repair suggestion

LLM **must not** produce:

- final scraped/provider data as truth
- `service_result.ok=true` without validation
- runtime code merged without tests

See also [`SERVICE_RESULT.md`](./SERVICE_RESULT.md) and [`TOURI.md`](./TOURI.md).

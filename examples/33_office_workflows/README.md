# 33 — Office workflow URIs (landing cards)

Mock task graphs and Touri capabilities aligned with the six **office-use cards** on
[`www/index.html`](../../www/index.html) and quick prompts in [`www/chat.html`](../../www/chat.html).

Each landing quote maps to `urish ask` → planned URIs via
[`agents/scenarios/office_automation.yaml`](../../agents/scenarios/office_automation.yaml).
The `urish` package only loads this registry; it does not hardcode office scenarios.

## Graphs

| File | Workflow URI | Landing card |
|------|----------------|--------------|
| `supplier_report_monthly.yaml` | `workflow://office/supplier-report/monthly` | WWW · CSV report |
| `portal_zus_form.yaml` | `workflow://portal/zus-form/dry-run` · `--approve` | Portal · ZUS form |
| `bank_batch_transfer.yaml` | `workflow://bank/batch-transfer/dry-run` | Bank · batch transfer |

Related capabilities (no separate graph in this folder):

- `workflow://invoices/batch/dry-run` → `examples/31_office_day/task_graph.yaml`
- `pcwin://…` · `android://…` → `examples/31_office_day/*.yaml` + uri2ops operators

## Run

```bash
bash examples/33_office_workflows/run.sh
```

Or step by step:

```bash
uri ask "Wystaw faktury za zamówienia z WooCommerce, pokaż listę do akceptacji i wyślij tylko zatwierdzone."
uri run workflow://office/supplier-report/monthly --dry-run
uri run workflow://portal/zus-form/dry-run
uri run workflow://bank/batch-transfer/dry-run
```

## Chat

Click any office card on the landing page → prompt is prefilled in chat (`taskinity.chatPrompt`).

Tests: `tests/urish/test_office_scenarios.py`

Docs: `www/docs/examples.html#ex-33_office_workflows`

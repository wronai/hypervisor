# Example 16 — monitor landing WWW

Workflow uri3 sprawdzający dostępność strony Taskinity i obecność cen w ofercie.

## Plik

[`task_graph.yaml`](task_graph.yaml) — otwiera `http://localhost:8788/www/` i weryfikuje tekst „Taskinity”, ceny audytu i pilota.

## Uruchomienie

Wymaga działającego serwera WWW (`make start` lub `urish www serve`):

```bash
uri3 validate-workflow examples/16_www_landing_monitor/task_graph.yaml
uri3 run-workflow examples/16_www_landing_monitor/task_graph.yaml --dry-run
uri3 run-workflow examples/16_www_landing_monitor/task_graph.yaml --approve --browser mock
```

Z Playwright (prawdziwa przeglądarka, serwer na :8788):

```bash
pip install -e '.[browser]'
playwright install chromium
uri3 run-workflow examples/16_www_landing_monitor/task_graph.yaml --approve --browser playwright
```

## Monitory cron

Skrypt hosta (bez workflow):

```bash
python scripts/www/monitor_landing.py --url http://localhost:8788/www/
bash scripts/www/run_monitors.sh
```

## Powiązane

- [`www/README.md`](../../www/README.md)
- [`scripts/www/monitor_landing.py`](../../scripts/www/monitor_landing.py)
- [`14_workflow_executor_mock`](../14_workflow_executor_mock/)

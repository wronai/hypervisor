.PHONY: validate generate verify test clean run-user-agent run-meta-agent meta-plan meta-pipeline meta-repair
.PHONY: uri-tree graph nl2a-weather docker-ssh-up docker-ssh-down scan-http scan-ssh docker-testenv-up docker-testenv-down evolution-check examples run-weather-agent
.PHONY: uri2flow-test uri2flow-validate uri2flow-expand uri3-flow-dry-run nl2uri-flow-validate example-18 touri-test touri-demo voice-test voice-demo
.PHONY: architecture-test architecture-responsibility-audit doctor architecture-gate ci-gate examples-test examples-comprehensive examples-real-report
.PHONY: start start-agents start-full stop uri-shell ensure-dev agent-health www-test www-smoke www-logs www-monitor www-monitor-reset www-monitor-test www-docs www-docs-check examples-shell examples-playwright-proof

WWW_PORT ?= 8788
WWW_COMPOSE = docker compose -f www/docker-compose.yml
WWW_BASE = http://localhost:$(WWW_PORT)

# Prefer repo .venv so start-agents works outside an activated shell (conda base often lacks uvicorn).
PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else command -v python3; fi)
HYPERVISOR := $(PYTHON) -m hypervisor.cli

WEATHER_PROMPT = generuj mape pogody dwa tygodnie do przodu w html

validate:
	python -m generator.validate contracts

generate:
	python -m generator.agent_generator contracts/agents/*.yaml

verify:
	python -m generator.verify agents/generated

test:
	pytest -q

architecture-test:
	pytest tests/architecture -q

architecture-responsibility-audit:
	python3 scripts/architecture_responsibility_audit.py --top 30

doctor:
	uri3 doctor --json

architecture-gate:
	bash scripts/ci/architecture_gate.sh

ci-gate: architecture-gate test examples-test

examples-test:
	pytest tests/examples -q

examples-comprehensive:
	python3 scripts/examples/comprehensive_test.py

examples-real-report:
	python3 scripts/examples/comprehensive_test.py --real-only

doql-registry:
	bash scripts/examples/doql_host_preview.sh

examples-comprehensive-mock:
	python3 scripts/examples/comprehensive_test.py --mock-only

examples-playwright-proof:
	python3 scripts/examples/effective_weather_playwright.py
	python3 scripts/examples/effective_weather_playwright.py --legacy-screenshot

uri2flow-test:
	pytest tests/uri2flow -q

uri2flow-validate:
	uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml

uri2flow-expand:
	mkdir -p output
	uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml

uri3-flow-dry-run:
	uri3 run-flow examples/17_flow_vs_graph/weather.uri.flow.yaml --dry-run

nl2uri-flow-validate:
	nl2uri flow -p "wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome" --validate

example-18:
	bash examples/18_llm_flow_planner/run.sh

touri-test:
	pytest tests/touri -q

touri-demo:
	touri validate examples/20_touri_capabilities/weather_forecast.uri.capability.yaml
	touri list examples/20_touri_capabilities
	touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities
	touri call echo://Adam --registry examples/20_touri_capabilities

voice-test:
	pytest tests/touri/test_voice_capabilities.py -q

voice-demo:
	touri validate examples/21_touri_voice/stt_mock.uri.capability.yaml
	touri list examples/21_touri_voice
	touri call stt://mock/transcribe --registry examples/21_touri_voice --payload '{"text":"otwórz Chrome i sprawdź health"}'
	touri call voice://command/from-text --registry examples/21_touri_voice --payload '{"text":"wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome"}'
	touri call tts://mock/speak --registry examples/21_touri_voice --payload '{"text":"Agent działa poprawnie"}'

uri-tree:
	python -m nl2uri.cli tree --no-llm -p "$(WEATHER_PROMPT)" --out domains/weather_map/uri_tree.yaml

graph:
	uri3 graph domains/weather_map/uri_tree.yaml

nl2a-weather:
	python -m nl2a.cli --no-llm -p "$(WEATHER_PROMPT)"

run-user-agent:
	uvicorn agents.generated.user_agent.main:app --reload --port 8101

run-meta-agent:
	uvicorn meta_agent.api:app --reload --port 8200

meta-plan:
	python -m meta_agent.cli plan "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia"

meta-pipeline:
	python -m meta_agent.cli pipeline "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia"

meta-repair:
	python -m meta_agent.cli repair examples/05_meta_repair/broken_agent.yaml --write

docker-ssh-up:
	python -m hypervisor.cli call 'docker://stack/ssh-testenv?action=up&build=1'

docker-ssh-down:
	python -m hypervisor.cli call 'docker://stack/ssh-testenv?action=down&remove_volumes=1'

docker-testenv-up: docker-ssh-up

docker-testenv-down: docker-ssh-down

scan-http:
	python -m uri3.cli scan http

scan-ssh:
	HYPERVISOR_SSH_PASSWORD=$${HYPERVISOR_SSH_PASSWORD:-deploy} python -m uri3.cli scan ssh

scan-all:
	HYPERVISOR_SSH_PASSWORD=$${HYPERVISOR_SSH_PASSWORD:-deploy} python -m uri3.cli scan --all

evolution-check:
	python -m hypervisor.evolution.cli examples/08_evolution/proposals/add_orders_agent.yaml examples/08_evolution/proposals/add_invoices_agent.yaml

examples:
	@echo "See examples/README.md for the full catalog (01–09)."

run-weather-agent:
	python -m hypervisor.cli run-agent weather-map-agent.local

clean:
	rm -rf agents/generated/* output/* .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

ensure-dev:
	@$(PYTHON) -c "import uvicorn" 2>/dev/null || { \
		echo "Installing dev deps into project Python…"; \
		$(PYTHON) -m pip install -q -e ".[dev]"; \
	}
	@$(PYTHON) -c "import sys, uvicorn; import typer._click.decorators; print('ok: uvicorn + typer', typer.__version__, 'via', sys.executable)" 2>/dev/null || { \
		echo "Repairing typer (need >=0.26.7 with bundled click)…"; \
		$(PYTHON) -m pip install -q 'typer>=0.26.7'; \
	}
	@$(PYTHON) -c "import sys, uvicorn, typer; import typer._click.decorators; print('ok: uvicorn + typer', typer.__version__, 'via', sys.executable)"

agent-health:
	@echo "Agents:"
	@for id in weather-map-agent.local invoices-agent.local user-agent.local; do \
		uri=$$($(HYPERVISOR) inspect-agent $$id 2>/dev/null | $(PYTHON) -c "import json,sys; print(json.load(sys.stdin).get('effective_health_uri',''))" 2>/dev/null || true); \
		if [ -n "$$uri" ]; then \
			echo "  $$id -> $$uri"; \
			curl -fsS "$$uri" 2>/dev/null | $(PYTHON) -m json.tool || echo "    (unreachable)"; \
		fi; \
	done

start:
	$(WWW_COMPOSE) up -d --build
	@echo "Waiting for www chat health on $(WWW_BASE)…"
	@for i in $$(seq 1 30); do \
		if curl -fsS "$(WWW_BASE)/health" >/dev/null 2>&1; then break; fi; \
		if [ "$$i" -eq 30 ]; then echo "timeout waiting for health"; exit 1; fi; \
		sleep 1; \
	done
	@curl -fsS "$(WWW_BASE)/health" | python3 -m json.tool
	@echo "Chat UI: $(WWW_BASE)/www/"
	@echo "Tip: run local agents with: make start-agents"

start-agents: ensure-dev
	$(HYPERVISOR) run-agent weather-map-agent.local --detach --if-running reuse --wait-healthy
	$(HYPERVISOR) run-agent invoices-agent.local --detach --if-running reuse --wait-healthy
	$(HYPERVISOR) run-agent user-agent.local --detach --if-running reuse --wait-healthy
	@$(MAKE) agent-health

start-full: start start-agents

uri-shell:
	urish

stop:
	$(WWW_COMPOSE) down

www-test:
	pytest tests/hypervisor/test_chat_www.py -q

www-docs:
	python3 scripts/www/build_examples_docs.py
	python3 scripts/www/build_landing_integrations.py
	python3 scripts/www/build_examples_manifest.py

www-docs-check:
	python3 scripts/www/build_examples_docs.py --check
	python3 scripts/www/build_landing_integrations.py --check
	python3 scripts/www/build_examples_manifest.py --check
	python3 scripts/www/check_examples_links.py

examples-shell:
	python3 tests/examples/shell_runner.py

www-smoke:
	bash scripts/www/smoke.sh "$(WWW_BASE)"

www-monitor:
	bash scripts/www/run_monitors.sh

www-monitor-reset:
	python3 scripts/www/monitor_landing.py --url "$(WWW_BASE)/www/" --reset-baseline

www-monitor-test:
	bash scripts/www/test_monitors.sh

www-logs:
	$(WWW_COMPOSE) logs -f --tail=100

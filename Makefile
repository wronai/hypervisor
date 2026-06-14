.PHONY: validate generate verify test clean run-user-agent run-meta-agent meta-plan meta-pipeline meta-repair
.PHONY: uri-tree graph nl2a-weather docker-ssh-up docker-ssh-down scan-http scan-ssh docker-testenv-up docker-testenv-down evolution-check examples run-weather-agent
.PHONY: uri2flow-test uri2flow-validate uri2flow-expand uri3-flow-dry-run nl2uri-flow-validate example-18 touri-test touri-demo voice-test voice-demo
.PHONY: architecture-test doctor architecture-gate ci-gate

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

doctor:
	uri3 doctor --json

architecture-gate:
	bash scripts/ci/architecture_gate.sh

ci-gate: architecture-gate test

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
	python -m nl2a.cli generate --no-llm -p "$(WEATHER_PROMPT)"

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

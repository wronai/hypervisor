.PHONY: validate generate verify test clean run-user-agent run-meta-agent meta-plan meta-pipeline meta-repair
.PHONY: uri-tree graph nl2a-weather docker-ssh-up docker-ssh-down scan-http scan-ssh docker-testenv-up docker-testenv-down evolution-check examples run-weather-agent

WEATHER_PROMPT = generuj mape pogody dwa tygodnie do przodu w html

validate:
	python -m generator.validate contracts

generate:
	python -m generator.agent_generator contracts/agents/*.yaml

verify:
	python -m generator.verify agents/generated

test:
	pytest -q

uri-tree:
	python -m nl2uri.cli --no-llm -p "$(WEATHER_PROMPT)" --out domains/weather_map/uri_tree.yaml

graph:
	python -m uri3.cli graph domains/weather_map/uri_tree.yaml

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

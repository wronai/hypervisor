.PHONY: validate generate verify test clean run-user-agent run-meta-agent meta-plan meta-pipeline meta-repair

validate:
	python -m generator.validate contracts

generate:
	python -m generator.agent_generator contracts/agents/*.yaml

verify:
	python -m generator.verify agents/generated

test:
	pytest -q

run-user-agent:
	uvicorn agents.generated.user_agent.main:app --reload --port 8101

run-meta-agent:
	uvicorn meta_agent.api:app --reload --port 8200

meta-plan:
	python -m meta_agent.cli plan "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia"

meta-pipeline:
	python -m meta_agent.cli pipeline "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia"

meta-repair:
	python -m meta_agent.cli repair examples/broken_agent.yaml --write

clean:
	rm -rf agents/generated/* output/* .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_nl_smoke_agent.yaml
# Contract hash: sha256:1e2da71bd316b85b830c1a1f69f333c7e5ac2b01e83258383005f0967dde488c
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8130
CMD ["uvicorn", "agents.generated.codex_nl_smoke_agent.main:app", "--host", "0.0.0.0", "--port", "8130"]

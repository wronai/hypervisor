# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_nl_plan_agent.yaml
# Contract hash: sha256:2d9bc1c0b851ce7acae3b9134afc15449ddc5fe881c3fdb439c4077b9df4c699
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8132
CMD ["uvicorn", "agents.generated.codex_nl_plan_agent.main:app", "--host", "0.0.0.0", "--port", "8132"]

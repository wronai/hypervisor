# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_uri_smoke_agent.yaml
# Contract hash: sha256:92e4d835ecacc5e7138946e5012d5948102fc79fd492458ffb981bd857372c38
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8101
CMD ["uvicorn", "agents.generated.codex_uri_smoke_agent.main:app", "--host", "0.0.0.0", "--port", "8101"]

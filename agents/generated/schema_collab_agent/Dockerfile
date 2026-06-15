# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/schema_collab_agent.yaml
# Contract hash: sha256:17b3d806a8ebef60fa04b5234c2f32ccc2b94d7745234e05cbbd5c7e51bb4bd3
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8131
CMD ["uvicorn", "agents.generated.schema_collab_agent.main:app", "--host", "0.0.0.0", "--port", "8131"]

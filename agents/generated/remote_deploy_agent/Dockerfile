# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/remote_deploy_agent.yaml
# Contract hash: sha256:cb604273489ae8add7f97a4cad7786e18f628fcb1528369b992e7e437be6846e
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8135
CMD ["uvicorn", "agents.generated.remote_deploy_agent.main:app", "--host", "0.0.0.0", "--port", "8135"]

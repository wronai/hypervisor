# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/hypervisor_dashboard_agent.yaml
# Contract hash: sha256:e4ec619a25955f0c7cfe29270e603cf7256c7840417f77ca63fd48173bda14b5
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8789
CMD ["uvicorn", "agents.generated.hypervisor_dashboard_agent.main:app", "--host", "0.0.0.0", "--port", "8789"]

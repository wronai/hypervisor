# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/user_agent.yaml
# Contract hash: sha256:740801960691f1c4aefee04d0cc5a7e27aa3a9915ef2eb73a729f9226a10ce45
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8101
CMD ["uvicorn", "agents.generated.user_agent.main:app", "--host", "0.0.0.0", "--port", "8101"]
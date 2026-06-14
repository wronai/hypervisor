# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/invoices_agent.yaml
# Contract hash: sha256:a536397207b68bed66eefb1defcfb80529b8d2aa4fe82645f2ffa38069c60960
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8101
CMD ["uvicorn", "agents.generated.invoices_agent.main:app", "--host", "0.0.0.0", "--port", "8101"]
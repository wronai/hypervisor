FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY generator ./generator
COPY runtime_client ./runtime_client
COPY meta_agent ./meta_agent
COPY agents ./agents
COPY contracts ./contracts
COPY docs ./docs
RUN pip install --no-cache-dir -e .

CMD ["uvicorn", "meta_agent.api:app", "--host", "0.0.0.0", "--port", "8200"]

# www chat — hypervisor-dashboard-agent + static UI
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY packages ./packages
COPY www ./www
COPY contracts ./contracts
COPY schemas ./schemas
COPY deployments ./deployments
COPY config ./config
COPY domains ./domains

RUN pip install --no-cache-dir -e ".[server]"

ENV PYTHONUNBUFFERED=1
EXPOSE 8788

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=5 \
  CMD curl -fsS http://127.0.0.1:8788/health >/dev/null || exit 1

CMD ["uvicorn", "hypervisor_dashboard_agent.main:app", "--host", "0.0.0.0", "--port", "8788"]

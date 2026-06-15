# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/screenshot_analysis_agent.yaml
# Contract hash: sha256:a541c061b26d8303d14f931b3ad48dea9ada37990cc1a9426d2c1c0a13fbc77e
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8134
CMD ["uvicorn", "agents.generated.screenshot_analysis_agent.main:app", "--host", "0.0.0.0", "--port", "8134"]

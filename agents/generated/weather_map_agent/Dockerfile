# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/weather_map_agent.yaml
# Contract hash: sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8101
CMD ["uvicorn", "agents.generated.weather_map_agent.main:app", "--host", "0.0.0.0", "--port", "8101"]

# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/gnome_programmer_agent.yaml
# Contract hash: sha256:7b1bcba0139f125676c81df01f1bc3a4296937cf3a4ee3f06fcd7ff9efd0943e
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8136
CMD ["uvicorn", "agents.generated.gnome_programmer_agent.main:app", "--host", "0.0.0.0", "--port", "8136"]

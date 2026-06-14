FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8101
CMD ["uvicorn", "agents.generated.user_agent.main:app", "--host", "0.0.0.0", "--port", "8101"]
FROM python:3.11-slim

WORKDIR /app
COPY ../../../.. /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8003

CMD ["uvicorn", "backend.agents.retrieval_agent.main:app", "--host", "0.0.0.0", "--port", "8003"] 
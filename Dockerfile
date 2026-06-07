FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src
COPY knowledge_base /app/knowledge_base
COPY samples /app/samples

RUN pip install --no-cache-dir -e .[api]

EXPOSE 8000
CMD ["uvicorn", "eda_log_ai.api:app", "--host", "0.0.0.0", "--port", "8000"]

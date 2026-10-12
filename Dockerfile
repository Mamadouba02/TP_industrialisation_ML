# syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --timeout 120 --retries 10 -r requirements.txt
COPY . .
RUN python -m src.generate_data && python -m src.train && useradd --uid 1000 --create-home churn && mkdir -p /app/logs && chown -R churn:churn /app
USER churn
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

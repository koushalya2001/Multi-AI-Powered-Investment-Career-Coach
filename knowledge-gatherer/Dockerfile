FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# Sets the entrypoint to your orchestrator script
CMD ["python", "-m", "src.ingestion.run_pipeline"]
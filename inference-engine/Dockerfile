FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose the port Cloud Run expects
EXPOSE 8080

# Run Streamlit on port 8080 and bind to 0.0.0.0 so Cloud Run can route traffic to it
CMD ["streamlit", "run", "src/inference/app.py", "--server.port=8080", "--server.address=0.0.0.0"]
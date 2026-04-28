FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create and set working directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/cache/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# .dockerignore should prevent local .venv and __pycache__ from being copied
COPY . .

# Cloud Run expects this port
EXPOSE 8080

# Use gunicorn for production. It handles the PORT env var automatically
# if we bind to 0.0.0.0:$PORT.
# We use exec to ensure signals are passed to the process.
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0 app.main:app
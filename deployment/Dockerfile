# Bazzite Gaming Optimizer - Docker Image
# Production-ready containerized deployment

FROM python:3.11-slim

LABEL maintainer="bazzite-optimizer"
LABEL description="Bazzite Gaming Optimizer with ML/AI capabilities"
LABEL version="1.5.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/models

# Expose ports
EXPOSE 8080 8081

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV ML_MODELS_DIR=/app/models
ENV DATA_DIR=/app/data
ENV LOG_DIR=/app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/api/v1/health || exit 1

# Run FastAPI server
CMD ["uvicorn", "ml_engine.cloud_api.api_server:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]

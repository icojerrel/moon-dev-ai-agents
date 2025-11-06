# Moon Dev AI Trading Agents - Production Dockerfile
# Multi-stage build for optimized image size

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    g++ \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/src/data /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 moondev && \
    chown -R moondev:moondev /app

# Switch to non-root user
USER moondev

# Expose ports if needed (uncomment and adjust as needed)
# EXPOSE 8000

# Health check - verifies that main.py process is actually running
HEALTHCHECK --interval=5m --timeout=30s --start-period=1m --retries=3 \
    CMD python /app/healthcheck.py

# Default command (can be overridden)
CMD ["python", "src/main.py"]

# 🌙 Moon Dev AI Trading System - Production Dockerfile
# Multi-stage build for optimized image size and performance

# ============================================
# Stage 1: Rust Builder
# ============================================
FROM rust:1.70-slim as rust-builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Rust workspace
COPY rust_core/ ./rust_core/

# Build Rust core
WORKDIR /build/rust_core
RUN cargo build --release

# ============================================
# Stage 2: Python Builder
# ============================================
FROM python:3.10-slim as python-builder

WORKDIR /build

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies to a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install maturin for Rust-Python bindings
RUN pip install --no-cache-dir maturin

# ============================================
# Stage 3: Runtime
# ============================================
FROM python:3.10-slim

LABEL maintainer="Moon Dev <moondev@example.com>"
LABEL description="Moon Dev AI Trading System - Hybrid Python+Rust Architecture"
LABEL version="2.0"

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libssl3 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=python-builder /opt/venv /opt/venv

# Copy Rust artifacts from builder
COPY --from=rust-builder /build/rust_core/target/release/*.so /app/rust_core/target/release/ || true

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY .env_example ./.env_example

# Create necessary directories
RUN mkdir -p \
    src/data \
    logs \
    benchmarks \
    && chmod -R 755 src/data logs benchmarks

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '.'); from src import config; print('healthy')" || exit 1

# Non-root user for security
RUN useradd -m -u 1000 moondev && \
    chown -R moondev:moondev /app
USER moondev

# Default command
CMD ["python", "src/agents/async_orchestrator.py"]

# Alternative commands (override with docker run --entrypoint):
# CMD ["python", "src/services/monitoring_dashboard.py"]  # Dashboard
# CMD ["python", "scripts/test_system.py"]  # Tests
# CMD ["python", "scripts/benchmark_performance.py"]  # Benchmarks

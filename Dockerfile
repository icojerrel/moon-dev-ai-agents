FROM python:3.11-slim

# Set Moon Dev working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies that might be missing
RUN pip install --no-cache-dir \
    groq \
    pandas \
    numpy \
    youtube-transcript-api \
    PyPDF2

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p src/data/rbi

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_BASE_URL=http://ollama:11434

# Default command (can be overridden)
CMD ["python", "src/main.py"]

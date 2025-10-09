# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WORDUP_HOST=0.0.0.0 \
    WORDUP_PORT=5000 \
    FLASK_DEBUG=false

# Set work directory
WORKDIR /app

# Install system dependencies (minimal set needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install uv (modern Python package manager)
RUN pip install --upgrade pip && pip install uv

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Copy the rest of the project files
COPY . /app/

# Create directories and set permissions
RUN mkdir -p /app/data /app/instance && \
    chmod 755 /app/data /app/instance

# Create volume for SQLite database (both locations)
VOLUME ["/app/data", "/app/instance"]

# Expose port
EXPOSE 5000

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash wordup && \
    chown -R wordup:wordup /app
USER wordup

# Health check (using curl which is simpler than importing requests)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000')" || exit 1

# Default command
CMD ["python", "main.py"]

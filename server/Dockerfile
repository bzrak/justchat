# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

# Prevent Python from writing bytecode and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# -----------------------------
# Dependencies stage
# -----------------------------
FROM base AS dependencies

# Install build dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first (layer caching optimization)
COPY requirements.txt ./

# Install production dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Development stage
# -----------------------------
FROM dependencies AS development

# Install dev dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER appuser

# Source code will be mounted as volume in dev
# Default command for development (with hot reload)
CMD ["uvicorn", "chat_server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# -----------------------------
# Production stage
# -----------------------------
FROM base AS production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy source code
COPY --chown=appuser:appgroup src/ ./src/

# Switch to non-root user
USER appuser

# Production command (no reload, multiple workers)
CMD ["uvicorn", "chat_server.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

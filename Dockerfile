# OpenGlaze Dockerfile
# Multi-stage build for optimized image size

# =============================================================================
# BUILDER STAGE
# =============================================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# =============================================================================
# PRODUCTION STAGE
# =============================================================================
FROM python:3.11-slim as production

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash openglaze

# Copy application code
COPY --chown=openglaze:openglaze . .

# Switch to non-root user
USER openglaze

# Expose port
EXPOSE 8768

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8768/health || exit 1

# Run application
CMD ["python", "server.py"]

# =============================================================================
# DEVELOPMENT STAGE
# =============================================================================
FROM production as development

# Switch back to root for dev tools
USER root

# Install development dependencies
RUN pip install --no-cache-dir \
    watchfiles \
    debugpy

# Switch back to openglaze user
USER openglaze

# Run with auto-reload
CMD ["watchfiles", "python server.py"]

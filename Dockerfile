# Dockerfile - Agent-Commerce Container
# Multi-stage build for optimized image size

# ============================================================
# Stage 1: Builder
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi
RUN if [ -f requirements-dev.txt ]; then pip install --no-cache-dir -r requirements-dev.txt; fi


# ============================================================
# Stage 2: Runtime
# ============================================================
FROM python:3.11-slim AS runtime

# Security: Run as non-root user
RUN groupadd --gid 1000 agent && \
    useradd --uid 1000 --gid agent --shell /bin/bash --create-home agent

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application
COPY --chown=agent:agent . /workspace/agent

# Set working directory
WORKDIR /workspace/agent

# Environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV AGENT_HOME=/workspace/agent

# Expose ports
EXPOSE 8000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import asyncio; from surrealdb_layer import SurrealDBLayer; print('OK')" || exit 1

# Switch to non-root user
USER agent

# Default command
CMD ["python3", "-m", "uvicorn", "ucp_agent:app", "--host", "0.0.0.0", "--port", "8000"]


# ============================================================
# Multi-Architecture Build
# ============================================================
# Build for multiple architectures:
# docker buildx build --platform linux/amd64,linux/arm64 -t agent-commerce:latest .


# ============================================================
# Docker Compose for Development
# ============================================================
# docker-compose up -d
# docker-compose exec agent python3 test_e2e.py
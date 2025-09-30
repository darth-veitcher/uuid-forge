# syntax=docker/dockerfile:1
# Multi-stage, multi-architecture Dockerfile for UUID-Forge

# Stage 1: Builder
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1

WORKDIR /build

# Install system dependencies including git for version detection
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ src/
COPY .git/ .git/

# Set fallback version if git detection fails
ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.1.0.dev0

# Install dependencies and build wheel
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system build && \
    python -m build

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1

# Set labels
LABEL org.opencontainers.image.title="UUID-Forge"
LABEL org.opencontainers.image.description="Deterministic UUID generation for cross-system coordination"
LABEL org.opencontainers.image.authors="your.email@example.com"
LABEL org.opencontainers.image.source="https://github.com/yourusername/uuid-forge"
LABEL org.opencontainers.image.licenses="MIT"

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Install uv for runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy wheel from builder
COPY --from=builder /build/dist/*.whl /tmp/

# Install the package
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system /tmp/*.whl && \
    rm /tmp/*.whl

# Switch to non-root user
USER appuser
WORKDIR /home/appuser

# Set up entrypoint
ENTRYPOINT ["uuid-forge"]
CMD ["--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD uuid-forge info || exit 1

# Stage 3: Development
FROM runtime AS development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1 \
    UV_PROJECT_ENVIRONMENT="/usr/local/"

USER root

# Install development dependencies and git
RUN apt-get update && \
    apt-get install -y --no-install-recommends git vim && \
    rm -rf /var/lib/apt/lists/*

# Copy source code for development (including uv.lock)
COPY --chown=appuser:appuser . /app
WORKDIR /app

# Install all dependency groups using uv sync (as root to avoid cache permission issues)
# Remove the .python-version file if it exists to avoid conflicts with the system Python
RUN rm .python-version
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-groups

USER appuser

# Development entrypoint - flexible for both interactive and command use
ENTRYPOINT []
CMD ["/bin/bash"]

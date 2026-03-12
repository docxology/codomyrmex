# ── Stage 1: Build ────────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /build

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for cache efficiency
COPY pyproject.toml uv.lock ./
COPY src/ src/

# Sync dependencies (frozen lockfile, no dev deps)
RUN uv sync --frozen --no-dev --no-editable

# ── Stage 2: Runtime ──────────────────────────────────────────────
FROM python:3.13-slim AS runtime

LABEL maintainer="docxology"
LABEL org.opencontainers.image.source="https://github.com/docxology/codomyrmex"
LABEL org.opencontainers.image.description="Codomyrmex — Modular Coding Workspace"

# Security: non-root user
RUN groupadd --gid 1000 codo && \
    useradd --uid 1000 --gid 1000 --create-home codo

WORKDIR /app

# Copy uv and virtualenv from builder
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv
COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/src /app/src

# Copy project config
COPY pyproject.toml ./

# Ensure venv is on PATH
ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "from codomyrmex.cli import main; print('ok')" || exit 1

# Switch to non-root user
USER codo

EXPOSE 8787 8888

ENTRYPOINT ["python", "-m", "codomyrmex.cli"]
CMD ["--help"]

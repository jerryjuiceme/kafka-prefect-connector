FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.8.21 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Use a slim Python image for the final application
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy application code
COPY --from=builder /app /app

# Copy already built virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PREFECT_LOGGING_LEVEL=INFO

# Expose the port that the application will run on
EXPOSE 8000

ENTRYPOINT ["gunicorn", "src.main:app", "--workers" , "4", "--worker-class", "uvicorn.workers.UvicornWorker",  "--bind=0.0.0.0:8000", "--worker-connections", "1000"]
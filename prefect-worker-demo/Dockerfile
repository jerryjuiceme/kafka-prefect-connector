FROM prefecthq/prefect:3-latest AS builder

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY flows ./flows

# Install uv
RUN pip install uv

# Create isolated environment in .venv
RUN uv sync --frozen --no-dev

COPY ./deploy.py ./

FROM python:3.12-slim

WORKDIR /app

# Copy application code
COPY --from=builder /app /app

# Copy already built virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PREFECT_LOGGING_LEVEL=INFO

# Entry point: seed credentials, deploy, and start worker
CMD bash -c "prefect work-pool create 'basic-pipe' --type process --overwrite   && python deploy.py && prefect worker start --pool 'basic-pipe'"

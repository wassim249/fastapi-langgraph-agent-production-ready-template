FROM python:3.13.2-slim

# Set working directory
WORKDIR /app

# Set non-sensitive environment variables
ARG APP_ENV=production

ENV APP_ENV=${APP_ENV} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && pip install --upgrade pip \
    && pip install uv \
    && rm -rf /var/lib/apt/lists/*

# Install locked dependencies first (cached unless pyproject.toml / uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy the application and install the project itself against the locked deps
COPY . .
RUN uv sync --frozen

# Make entrypoint script executable - do this before changing user
RUN chmod +x /app/scripts/docker-entrypoint.sh

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Create log directory
RUN mkdir -p /app/logs

# Default port
EXPOSE 8000

# Log the environment we're using
RUN echo "Using ${APP_ENV} environment"

# Command to run the application
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

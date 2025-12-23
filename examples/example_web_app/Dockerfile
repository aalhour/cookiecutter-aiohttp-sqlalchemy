# Build stage
FROM python:3.12-slim AS builder

# Set build arguments
ARG DB_HOST="postgres"
ARG DB_PORT=5432
ARG DB_USER="admin"
ARG DB_NAME="example_db"
ARG DB_SCHEMA="public"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies (asyncpg requires no system libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Copy application code
COPY . .

# Install the application
RUN pip install --user .


# Production stage
FROM python:3.12-slim AS production

LABEL maintainer="me@aalhour.com"

# Set environment variables
ARG SERVER_HOST="0.0.0.0"
ARG SERVER_PORT=9999
ARG DB_HOST="postgres"
ARG DB_PORT=5432
ARG DB_USER="admin"
ARG DB_NAME="example_db"
ARG DB_SCHEMA="public"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    PATH="/home/app/.local/bin:$PATH" \
    SERVER_HOST=${SERVER_HOST} \
    SERVER_PORT=${SERVER_PORT} \
    DB_HOST=${DB_HOST} \
    DB_PORT=${DB_PORT} \
    DB_NAME=${DB_NAME} \
    DB_USER=${DB_USER} \
    DB_SCHEMA=${DB_SCHEMA}

# Create non-root user (asyncpg requires no system libs at runtime)
RUN useradd --create-home --shell /bin/bash app

# Switch to non-root user
USER app
WORKDIR /home/app

# Copy installed packages from builder
COPY --from=builder --chown=app:app /root/.local /home/app/.local

# Copy application code
COPY --chown=app:app . /home/app/app

WORKDIR /home/app/app

# Expose the application port
EXPOSE ${SERVER_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${SERVER_PORT}/api/-/health')" || exit 1

# Run the application (use CMD so docker-compose can override with migrations)
CMD ["python", "-m", "example_web_app.app"]

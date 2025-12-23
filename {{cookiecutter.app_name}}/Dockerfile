# Build stage
FROM python:3.12-slim AS builder

# Set build arguments
ARG DB_HOST="{{cookiecutter.db_host}}"
ARG DB_PORT={{cookiecutter.db_port}}
ARG DB_USER="{{cookiecutter.db_user}}"
ARG DB_NAME="{{cookiecutter.db_name}}"
ARG DB_SCHEMA="{{cookiecutter.db_schema}}"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
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

LABEL maintainer="{{cookiecutter.author_email}}"

# Set environment variables
ARG SERVER_HOST="{{cookiecutter.server_host}}"
ARG SERVER_PORT={{cookiecutter.server_port}}
ARG DB_HOST="{{cookiecutter.db_host}}"
ARG DB_PORT={{cookiecutter.db_port}}
ARG DB_USER="{{cookiecutter.db_user}}"
ARG DB_NAME="{{cookiecutter.db_name}}"
ARG DB_SCHEMA="{{cookiecutter.db_schema}}"

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

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash app

# Switch to non-root user
USER app
WORKDIR /home/app

# Copy installed packages from builder
COPY --from=builder --chown=app:app /root/.local /home/app/.local

# Copy application code
COPY --chown=app:app . /home/app/app

# Setup config file
RUN mkdir -p /home/app/.config && \
    cp /home/app/app/config/default.conf /home/app/.config/{{cookiecutter.app_name}}.conf

WORKDIR /home/app/app

# Expose the application port
EXPOSE ${SERVER_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${SERVER_PORT}/api/-/health')" || exit 1

# Run the application
ENTRYPOINT ["python", "-m", "{{cookiecutter.app_name}}.app"]

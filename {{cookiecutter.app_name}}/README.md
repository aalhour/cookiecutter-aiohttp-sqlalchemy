# {{cookiecutter.project_name}}

A modern async Python web API built with Aiohttp and SQLAlchemy 2.0.

## Features

- **Async Everything** - Native async/await with SQLAlchemy 2.0 and asyncpg
- **Request Validation** - Pydantic schemas for type-safe request/response handling
- **Observability** - Prometheus metrics, structured logging, OpenTelemetry tracing
- **Caching & Rate Limiting** - Redis-based caching and rate limiting
- **Background Tasks** - arq task queue for async job processing
- **WebSocket Support** - Real-time bidirectional communication
- **Docker Ready** - Multi-stage Dockerfile with docker-compose
- **Kubernetes Ready** - Full K8s manifests with HPA, PDB, and health checks
- **API Documentation** - Swagger/OpenAPI docs at `/api/v1.0/docs`

## Quick Start

### Docker (Recommended)

```bash
# Start the application with PostgreSQL and Redis
docker compose up -d

# View logs
docker compose logs -f {{cookiecutter.app_name}}

# Stop everything
docker compose down
```

The API will be available at `http://localhost:{{cookiecutter.server_port}}`.

### Local Development

```bash
# Install dependencies
make install-dev

# Set up environment
cp env.example .env

# Run database migrations
make migrate-up

# Start development server (with auto-reload)
make dev-server
```

## API Endpoints

### Health & Monitoring

| Endpoint | Description |
|----------|-------------|
| `GET /api/-/health` | Health check (liveness) |
| `GET /api/-/ready` | Readiness check (with dependency health) |
| `GET /api/-/live` | Simple liveness probe |
| `GET /metrics` | Prometheus metrics |
| `GET /api/v1.0/docs` | Swagger UI documentation |

### Example CRUD API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1.0/examples` | List all examples |
| `POST` | `/api/v1.0/examples` | Create a new example |
| `GET` | `/api/v1.0/examples/{id}` | Get example by ID |
| `PUT` | `/api/v1.0/examples/{id}` | Update example |
| `DELETE` | `/api/v1.0/examples/{id}` | Delete example |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `WS /api/v1.0/ws/echo` | Echo messages back to sender |
| `WS /api/v1.0/ws/broadcast` | Broadcast to all connected clients |

## Project Structure

```
{{cookiecutter.app_name}}/
├── {{cookiecutter.app_name}}/         # Application package
│   ├── app.py                         # Application factory
│   ├── config.py                      # Pydantic Settings configuration
│   ├── database.py                    # SQLAlchemy 2.0 async setup
│   ├── redis.py                       # Redis client
│   ├── cache.py                       # Caching decorator
│   ├── rate_limit.py                  # Rate limiting middleware
│   ├── metrics.py                     # Prometheus metrics
│   ├── telemetry.py                   # OpenTelemetry tracing
│   ├── websocket.py                   # WebSocket support
│   ├── logger.py                      # Structlog configuration
│   ├── routes.py                      # URL routing
│   ├── middlewares.py                 # Aiohttp middlewares
│   ├── controllers/                   # API controllers
│   ├── models/                        # SQLAlchemy ORM models
│   ├── schemas/                       # Pydantic schemas
│   ├── tasks/                         # Background tasks (arq)
│   └── docs/                          # Swagger/OpenAPI specs
├── alembic/                           # Database migrations
├── tests/                             # Test suite
├── k8s/                               # Kubernetes manifests
├── docker-compose.yaml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── env.example
```

## Configuration

Configuration is managed via environment variables (Pydantic Settings).

Copy `env.example` to `.env` and customize:

```bash
cp env.example .env
```

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_PORT` | `{{cookiecutter.server_port}}` | Server port |
| `DB_HOST` | `{{cookiecutter.db_host}}` | PostgreSQL host |
| `DB_PASSWORD` | | Database password |
| `REDIS_HOST` | `localhost` | Redis host |
| `REDIS_ENABLED` | `true` | Enable Redis features |
| `RATELIMIT_ENABLED` | `true` | Enable rate limiting |
| `OTEL_ENABLED` | `false` | Enable OpenTelemetry |
| `SENTRY_DSN` | | Sentry error tracking DSN |

## Development

### Database Migrations

```bash
# Create a new migration
make migrate-create msg="add users table"

# Apply migrations
make migrate-up

# Rollback last migration
make migrate-down

# Show migration history
make migrate-history
```

### Background Tasks

Start the worker to process background jobs:

```bash
# Using arq directly
arq {{cookiecutter.app_name}}.tasks.worker.WorkerSettings

# Or with Docker Compose
docker compose --profile worker up -d
```

Enqueue tasks from your code:

```python
from {{cookiecutter.app_name}}.tasks import enqueue

# Enqueue a task
await enqueue("send_notification", user_id=123, message="Hello!")

# Enqueue with delay
await enqueue("example_task", name="test", _defer_by=60)
```

### Testing

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test file
pytest tests/test_unit/test_controllers/test_example_api.py -v
```

### Linting & Formatting

```bash
# Run linting
make lint

# Run formatting
make format

# Type checking
make typecheck
```

## Deployment

### Docker

```bash
# Build production image
make docker-build

# Run the container
make docker-run
```

### Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -k k8s/

# Or apply individually
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

See `k8s/README.md` for detailed Kubernetes deployment instructions.

## Author

{{cookiecutter.author_name}} <{{cookiecutter.author_email}}>

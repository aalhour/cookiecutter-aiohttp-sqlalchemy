# 🍪 cookiecutter-aiohttp-sqlalchemy

A modern, opinionated [Cookiecutter](https://cookiecutter.readthedocs.io/) template for building **async Python web APIs** powered by Aiohttp, SQLAlchemy 2.0, and PostgreSQL.

Generate a production-ready async REST API in seconds with database migrations, structured logging, Docker support, and CI/CD workflows—all pre-configured.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Aiohttp](https://img.shields.io/badge/aiohttp-3.13+-green.svg)](https://docs.aiohttp.org/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/sqlalchemy-2.0+-orange.svg)](https://www.sqlalchemy.org/)


## ✨ What You Get

| Feature | Description |
|---------|-------------|
| **SQLAlchemy 2.0 Async** | Native async/await with `asyncpg` driver—no thread pools needed |
| **Alembic Migrations** | Database schema management with auto-generated migrations |
| **Pydantic Validation** | Type-safe request/response schemas with automatic validation |
| **Pydantic Settings** | Type-safe configuration via environment variables |
| **Redis Integration** | Caching, rate limiting, and pub/sub support |
| **Rate Limiting** | Redis-based sliding window rate limiter |
| **Background Tasks** | arq task queue for async job processing |
| **WebSocket Support** | Real-time bidirectional communication |
| **Prometheus Metrics** | `/metrics` endpoint for monitoring |
| **OpenTelemetry Tracing** | Distributed tracing with OTLP export |
| **Structured Logging** | JSON logs in production, colorful console in development (structlog) |
| **Full CRUD Example** | Working Create, Read, Update, Delete API out of the box |
| **Docker Ready** | Multi-stage Dockerfile + docker-compose with PostgreSQL & Redis |
| **Kubernetes Ready** | Full K8s manifests with HPA, PDB, Ingress, and health checks |
| **GitHub Actions CI** | Linting, type checking, testing, and Docker builds |
| **Pre-commit Hooks** | Ruff linting and formatting on every commit |
| **Swagger/OpenAPI** | Auto-generated API documentation at `/api/v1.0/docs` |
| **Sentry Integration** | Error tracking ready to configure |

## Examples

**[View the Example App →](examples/example_web_app/)**

## Quick Start

### 1. Generate Your Project

```bash
pip install cookiecutter
cookiecutter gh:aalhour/cookiecutter-aiohttp-sqlalchemy
```

Answer the prompts (or accept defaults):

```
app_name [example_web_app]: my_api
project_name [Example Web App]: My API
author_name [Your Name]: Jane Doe
...
```

### 2. Run with Docker (Recommended)

```bash
cd my_api
docker compose up -d
```

That's it! Your API is running at `http://localhost:9999` with:
- PostgreSQL database
- Alembic migrations applied automatically
- Health check endpoint ready

### 3. Test the API

```bash
# Health check
curl http://localhost:9999/api/-/health

# Create an item
curl -X POST http://localhost:9999/api/v1.0/examples \
  -H "Content-Type: application/json" \
  -d '{"name": "My Item", "description": "A test item", "price": 29.99}'

# List all items
curl http://localhost:9999/api/v1.0/examples

# Swagger docs
open http://localhost:9999/api/v1.0/docs
```


## Generated Project Structure

```
my_api/
├── my_api/                    # Application package
│   ├── app.py                 # Application factory
│   ├── config.py              # Pydantic Settings configuration
│   ├── database.py            # SQLAlchemy 2.0 async setup
│   ├── logger.py              # Structlog configuration
│   ├── routes.py              # URL routing
│   ├── middlewares.py         # Aiohttp middlewares
│   ├── controllers/           # API controllers (CRUD endpoints)
│   ├── models/                # SQLAlchemy ORM models
│   └── docs/                  # Swagger/OpenAPI YAML specs
├── alembic/                   # Database migrations
│   ├── env.py                 # Async migration environment
│   └── versions/              # Migration scripts
├── tests/                     # Pytest test suite
├── .github/workflows/         # GitHub Actions CI
├── docker-compose.yaml        # Docker Compose (app + PostgreSQL)
├── Dockerfile                 # Multi-stage production build
├── Makefile                   # Development commands
├── pyproject.toml             # Project metadata & tools config
└── env.example                # Environment variables template
```


## Development Workflow

```bash
cd my_api

# Install development environment
make install-dev

# Run tests
make test

# Start development server (with auto-reload)
make dev-server

# Run linting
make lint

# Run type checking
make typecheck

# Format code
make format

# Create a database migration
make migrate-create msg="add users table"

# Apply migrations
make migrate-up
```


## Configuration

The generated app uses **environment variables** for configuration (via Pydantic Settings).

Copy `env.example` to `.env` and customize:

```bash
cp env.example .env
```

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `9999` | Server port |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `example_db` | Database name |
| `DB_USER` | `example` | Database user |
| `DB_PASSWORD` | | Database password |
| `SENTRY_DSN` | | Sentry error tracking DSN |


## Code Example

Here's what the generated async API code looks like:

**Controller** (`controllers/example_api.py`):

```python
class ExampleApiController(BaseJsonApiController):
    async def get(self, request: web.Request) -> web.Response:
        """GET /api/v1.0/examples - List all examples"""
        async with transactional_session() as session:
            examples = await Example.get_all(session)
            return self.json_response([e.serialized for e in examples])

    async def create(self, request: web.Request) -> web.Response:
        """POST /api/v1.0/examples - Create a new example"""
        data = await request.json()
        async with transactional_session() as session:
            example = await Example.create(
                session=session,
                name=data["name"],
                description=data.get("description"),
                price=data.get("price"),
            )
            return self.json_response(example.serialized, status=201)
```

**Model** (`models/example.py`):

```python
class Example(Base):
    __tablename__ = "example"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list["Example"]:
        result = await session.execute(select(cls))
        return list(result.scalars().all())

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> "Example":
        example = cls(**kwargs)
        session.add(example)
        await session.flush()
        return example
```


## Tech Stack

| Component | Technology |
|-----------|------------|
| Web Framework | [Aiohttp 3.13+](https://docs.aiohttp.org/) |
| ORM | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (native async) |
| Database Driver | [asyncpg](https://github.com/MagicStack/asyncpg) |
| Database | [PostgreSQL 16](https://www.postgresql.org/) |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) |
| Cache / Queue | [Redis](https://redis.io/) |
| Task Queue | [arq](https://arq-docs.helpmanual.io/) |
| Validation | [Pydantic](https://docs.pydantic.dev/) |
| Configuration | [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| Logging | [structlog](https://www.structlog.org/) |
| Metrics | [prometheus-client](https://prometheus.io/) |
| Tracing | [OpenTelemetry](https://opentelemetry.io/) |
| Linting | [Ruff](https://docs.astral.sh/ruff/) |
| Type Checking | [mypy](https://mypy.readthedocs.io/) |
| Testing | [pytest](https://pytest.org/) + pytest-aiohttp |
| Error Tracking | [Sentry](https://sentry.io/) |
| Event Loop | [uvloop](https://github.com/MagicStack/uvloop) |


## Requirements

- Python 3.12+ (tested with 3.12 and 3.13)
- Docker & Docker Compose (for containerized deployment)
- PostgreSQL 14+ (or use Docker)


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


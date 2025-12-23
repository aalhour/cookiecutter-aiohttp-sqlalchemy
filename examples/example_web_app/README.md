# Example Web App

An Example Web API project powered by Aiohttp and SQLAlchemy

## ✨ Features

- **Modern Python** - Built with Python 3.10+ and fully async
- **SQLAlchemy 2.0** - Native async support with `asyncpg` driver
- **Type Safety** - Full type hints with mypy support
- **Auto Migrations** - Database migrations with Alembic
- **API Documentation** - Swagger/OpenAPI docs included
- **Structured Logging** - JSON logging with structlog
- **Docker Ready** - Production-ready Docker Compose setup
- **Code Quality** - Pre-commit hooks, Ruff linting, formatting
- **CI/CD** - GitHub Actions workflow included
- **Error Tracking** - Sentry integration built-in


## 🚀 Quick Start

### With Docker (Recommended)

```bash
# Start all services (app + PostgreSQL)
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f example_web_app

# Stop everything
docker compose down -v
```

The API is available at `http://localhost:9999`

### Test the API

```bash
# Health check
curl http://localhost:9999/api/-/health

# List all examples
curl http://localhost:9999/api/v1.0/examples

# Create a new example
curl -X POST http://localhost:9999/api/v1.0/examples \
  -H "Content-Type: application/json" \
  -d '{"name": "My Example", "description": "A test item", "price": 19.99}'

# Get example by ID
curl http://localhost:9999/api/v1.0/examples/1

# Update an example
curl -X PUT http://localhost:9999/api/v1.0/examples/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Example", "price": 29.99}'

# Delete an example
curl -X DELETE http://localhost:9999/api/v1.0/examples/1
```


## 📚 Documentation

| Resource | URL |
|----------|-----|
| Swagger UI | http://localhost:9999/api/v1.0/docs |
| Health Check | http://localhost:9999/api/-/health |
| OpenAPI Spec | `example_web_app/docs/swagger-v1.0.yaml` |


## 🛠️ Development Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 14+ (or Docker)
- Make

### Local Development

```bash
# Install development dependencies
make install-dev

# Start development server with auto-reload
make dev-server
```

### Available Make Commands

Run `make help` to see all available commands:

```
Setup & Installation:
  make install          Install the application
  make install-dev      Install in development mode with dev dependencies

Development:
  make dev-server       Start development server with auto-reload

Code Quality:
  make lint             Run ruff linting
  make format           Format code with ruff
  make typecheck        Run mypy type checking
  make pre-commit-run   Run all pre-commit hooks

Testing:
  make test             Install dev deps and run all tests
  make coverage         Generate test coverage report

Database Migrations:
  make migrate-up       Apply all pending migrations
  make migrate-down     Rollback the last migration
  make migrate-create   Create a new migration (msg='description')

Docker:
  make docker-compose-up    Start all services
  make docker-compose-down  Stop all services
```


## 🗄️ Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations.

```bash
# Create a new migration
make migrate-create msg="add users table"

# Apply all pending migrations
make migrate-up

# Rollback the last migration
make migrate-down

# View migration history
make migrate-history
```

**Note:** When running with Docker, migrations are automatically applied on startup.


## ⚙️ Configuration

Configuration is managed via environment variables. Copy `env.example` to `.env`:

```bash
cp env.example .env
# Edit .env with your values
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `9999` | Server port |
| `DB_HOST` | `postgres` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `example_db` | Database name |
| `DB_USER` | `admin` | Database user |
| `DB_PASSWORD` | | Database password |
| `DB_SCHEMA` | `public` | Database schema |
| `SENTRY_DSN` | | Sentry DSN for error tracking |
| `LOGGING_LEVEL` | `DEBUG` | Logging level |


## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage report
make coverage

# Run specific test types
make test-unit
make test-integration
```


## 📦 Project Structure

```
example_web_app/
├── example_web_app/           # Application package
│   ├── app.py                           # Application factory
│   ├── config.py                        # Pydantic settings
│   ├── database.py                      # SQLAlchemy async setup
│   ├── routes.py                        # URL routing
│   ├── logger.py                        # Structured logging
│   ├── middlewares.py                   # Aiohttp middlewares
│   ├── controllers/                     # API controllers
│   │   ├── base.py                      # Base controller class
│   │   ├── example_api.py               # Example CRUD controller
│   │   └── health_api.py                # Health check endpoint
│   ├── models/                          # SQLAlchemy models
│   │   ├── base.py                      # Base model mixin
│   │   └── example.py                   # Example model
│   └── docs/                            # OpenAPI/Swagger specs
├── alembic/                             # Database migrations
│   ├── env.py                           # Alembic configuration
│   └── versions/                        # Migration scripts
├── tests/                               # Test suite
│   ├── fixtures/                        # Test fixtures
│   └── test_unit/                       # Unit tests
├── config/                              # Configuration templates
├── .github/workflows/                   # CI/CD workflows
├── docker-compose.yaml                  # Docker Compose setup
├── Dockerfile                           # Multi-stage Docker build
├── Makefile                             # Development commands
├── pyproject.toml                       # Project metadata
└── requirements.txt                     # Python dependencies
```


## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| Web Framework | [aiohttp](https://docs.aiohttp.org/) |
| ORM | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) |
| Database Driver | [asyncpg](https://github.com/MagicStack/asyncpg) |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) |
| Configuration | [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| Logging | [structlog](https://www.structlog.org/) |
| Error Tracking | [Sentry](https://sentry.io/) |
| Linting | [Ruff](https://docs.astral.sh/ruff/) |
| Type Checking | [mypy](https://mypy.readthedocs.io/) |


## 📝 License

This project is licensed under the ISC License - see the [LICENSE](LICENSE) file for details.


## 👤 Author

**Ahmad Alhour** - [me@aalhour.com](mailto:me@aalhour.com)

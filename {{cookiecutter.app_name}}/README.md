# {{cookiecutter.app_name}}

{{cookiecutter.project_short_description}}


## Contents

  * [Synopsis](#synopsis)
  * [Dependencies](#dependencies)
  * [API](#api)
  * [How To Guides](#how-to-guides)
    + [Quick Start with Docker](#quick-start-with-docker)
    + [Local Setup](#local-setup)
    + [Development](#development)
    + [Testing](#testing)
    + [Packaging](#packaging)
  * [Configuration](#configuration)


## Synopsis

```bash
# Using Docker (recommended)
docker compose up

# Or run locally
bin/service {start|stop|status|restart}
```


## Dependencies

 * Python 3.10+
 * PostgreSQL 14+
 * See `requirements.txt` for Python dependencies
 * See `requirements_dev.txt` for development/testing dependencies


## API

 * Health Check: `http://{{cookiecutter.server_host}}:{{cookiecutter.server_port}}/api/-/health`
 * Swagger UI: `http://{{cookiecutter.server_host}}:{{cookiecutter.server_port}}/api/v1.0/docs`
 * OpenAPI Schema: `{{cookiecutter.app_name}}/docs/swagger-v1.0.yaml`


## How To Guides

### Quick Start with Docker

The fastest way to get started:

```bash
# Start the application with PostgreSQL
docker compose up

# Or run in detached mode
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop everything
docker compose down
```

The API will be available at `http://localhost:{{cookiecutter.server_port}}`.

### Local Setup

1. Copy the configuration file:
```bash
cp config/default.conf ~/.config/{{cookiecutter.app_name}}.conf
```

2. Install the application:
```bash
make clean install
```

3. Make sure PostgreSQL is running and update your config with database credentials.

4. Start the application:
```bash
bin/service start
```

### Development

Start the development server with hot-reload:

```bash
make dev-server
```

### Testing

Run the test suite:

```bash
make test
```

Run with coverage:

```bash
make coverage
```

### Packaging

Build a distributable wheel:

```bash
make package
```

The wheel will be created in the `dist/` directory.


## Configuration

Configuration is managed via INI files located at `~/.config/{{cookiecutter.app_name}}.conf`.

For Docker deployments, you can use environment variables. Copy `env.template` to `.env` and customize:

```bash
cp env.template .env
# Edit .env with your values
docker compose up
```

### Configuration Options

| Section | Option | Description |
|---------|--------|-------------|
| `server` | `host` | Server bind address (default: 0.0.0.0) |
| `server` | `port` | Server port (default: {{cookiecutter.server_port}}) |
| `db` | `host` | PostgreSQL host |
| `db` | `port` | PostgreSQL port (default: 5432) |
| `db` | `name` | Database name |
| `db` | `user` | Database user |
| `db` | `schema` | Database schema (default: public) |
| `sentry` | `dsn` | Sentry DSN for error tracking (optional) |

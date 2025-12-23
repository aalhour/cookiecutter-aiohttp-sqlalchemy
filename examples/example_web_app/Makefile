#############################################
#                                           #
#  Example Web App Makefile   #
#                                           #
#  A comprehensive management CLI for       #
#  development, testing, and deployment     #
#                                           #
#############################################

# Shell and Python configuration
SHELL := /bin/bash
PYTHON := python3

# Directory configuration
VENV_DIR := .venv
TEST_VENV_DIR := .testing-venv

# Development server command
DEV_SERVER_CMD := adev runserver -v example_web_app/app.py --app-factory create_app -p 8137

# Colors for terminal output (if supported)
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m  # No Color

#############################################
#  PHONY TARGETS                            #
#############################################
# Auto-generated from target definitions
.PHONY: help \
        clean clean-venv clean-temp-files \
        venv venv-app venv-test \
        install install-dev \
        package \
        dev-server dev-upgrade-deps \
        test pytest test-unit test-integration test-end-to-end \
        coverage \
        lint format format-check typecheck \
        pre-commit-install pre-commit-run \
        migrate-init migrate-create migrate-up migrate-down migrate-history \
        docker-build docker-run docker-compose-up docker-compose-down


#############################################
#  HELP                                     #
#############################################

help:
	@echo ""
	@echo "$(BLUE)Example Web App - Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup & Installation:$(NC)"
	@echo "  make install          Install the application"
	@echo "  make install-dev      Install in development mode with dev dependencies"
	@echo "  make venv             Create virtual environment"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make dev-server       Start development server with auto-reload"
	@echo "  make dev-upgrade-deps Upgrade all dependencies to latest versions"
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@echo "  make lint             Run ruff linting"
	@echo "  make format           Format code with ruff"
	@echo "  make format-check     Check code formatting"
	@echo "  make typecheck        Run mypy type checking"
	@echo "  make pre-commit-run   Run all pre-commit hooks"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  make test             Install dev deps and run all tests"
	@echo "  make pytest           Run all tests (requires install-dev first)"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make coverage         Generate test coverage report"
	@echo ""
	@echo "$(GREEN)Database Migrations:$(NC)"
	@echo "  make migrate-up       Apply all pending migrations"
	@echo "  make migrate-down     Rollback the last migration"
	@echo "  make migrate-create   Create a new migration (msg='description')"
	@echo "  make migrate-history  Show migration history"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  make docker-build      Build the Docker image"
	@echo "  make docker-run        Run the Docker container"
	@echo "  make docker-compose-up Start all services with Docker Compose"
	@echo "  make docker-compose-down Stop all services"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  make clean            Clean all temporary files and venvs"
	@echo "  make clean-venv       Remove virtual environments"
	@echo "  make clean-temp-files Remove cache and build artifacts"
	@echo ""
	@echo "$(GREEN)Packaging:$(NC)"
	@echo "  make package          Create a wheel package for deployment"
	@echo ""


#############################################
#  CLEANUP                                  #
#############################################

clean-venv:
	@echo ">>> Cleaning virtual environments..."
	@rm -rf $(VENV_DIR) $(TEST_VENV_DIR) venv
	@echo "Done!"

clean-temp-files:
	@echo ">>> Cleaning temporary files..."
	@rm -rf build dist *.egg-info .tox htmlcov .cache .pytest_cache .mypy_cache .ruff_cache
	@find . -name "*.*,cover" -delete 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Done!"

clean: clean-venv clean-temp-files


#############################################
#  VIRTUAL ENVIRONMENT                      #
#############################################

log-py-version:
	@echo -n "Using Python: "
	@$(PYTHON) -c 'import sys; v = sys.version_info; print(f"{v.major}.{v.minor}.{v.micro}")'

venv-app: log-py-version
	@echo ">>> Creating application virtual environment..."
	@test -d $(VENV_DIR) || $(PYTHON) -m venv $(VENV_DIR)
	@echo "Done! Activate with: source $(VENV_DIR)/bin/activate"

venv-test: log-py-version
	@echo ">>> Creating test virtual environment..."
	@test -d $(TEST_VENV_DIR) || $(PYTHON) -m venv $(TEST_VENV_DIR)
	@echo "Done!"

venv: venv-app


#############################################
#  INSTALLATION                             #
#############################################

install: venv-app
	@echo ">>> Installing application..."
	@. $(VENV_DIR)/bin/activate && \
		pip install -U pip && \
		pip install -r requirements.txt && \
		pip install -e .
	@echo "Done!"

install-dev: venv-test
	@echo ">>> Installing development environment..."
	@. $(TEST_VENV_DIR)/bin/activate && \
		pip install -U pip && \
		pip install -r requirements.txt -r requirements_dev.txt && \
		pip install -e .
	@echo "Done!"


#############################################
#  PACKAGING                                #
#############################################

package: venv-app
	@echo ">>> Creating deployment package..."
	@rm -rf dist
	@. $(VENV_DIR)/bin/activate && \
		pip install -U build && \
		$(PYTHON) -m build --wheel --outdir dist
	@echo "Done! Package available in dist/"


#############################################
#  DEVELOPMENT TOOLS                        #
#############################################

dev-upgrade-deps: clean install
	@echo ">>> Upgrading dependencies..."
	@. $(VENV_DIR)/bin/activate && \
		pip install -U -r requirements_floating.txt && \
		pip freeze | grep -v example_web_app > requirements.txt
	@echo "Updated requirements.txt:"
	@git diff requirements.txt || true

dev-server:
	@echo ">>> Starting development server..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && $(DEV_SERVER_CMD)


#############################################
#  TESTING                                  #
#############################################

VERBOSITY := vq
PYTEST_ARGS :=

pytest:
	@echo ">>> Running tests..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && pytest --cache-clear -$(VERBOSITY) $(PYTEST_ARGS)

test: install-dev pytest

test-unit:
	@$(MAKE) -s pytest PYTEST_ARGS="tests/test_unit"

test-integration:
	@$(MAKE) -s pytest PYTEST_ARGS="tests/test_integration"

test-end-to-end:
	@$(MAKE) -s pytest PYTEST_ARGS="tests/test_end_to_end"

coverage:
	@echo ">>> Generating coverage report..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && \
		coverage run --source example_web_app/ -m pytest --cache-clear -$(VERBOSITY) tests/test_unit && \
		coverage report && \
		coverage html
	@echo "Coverage report: htmlcov/index.html"


#############################################
#  CODE QUALITY                             #
#############################################

lint:
	@echo ">>> Linting with ruff..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && ruff check example_web_app/ tests/

format:
	@echo ">>> Formatting with ruff..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && ruff format example_web_app/ tests/

format-check:
	@echo ">>> Checking format with ruff..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && ruff format --check example_web_app/ tests/

typecheck:
	@echo ">>> Type checking with mypy..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && mypy example_web_app/


#############################################
#  PRE-COMMIT                               #
#############################################

pre-commit-install:
	@echo ">>> Installing pre-commit hooks..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && pre-commit install
	@echo "Done!"

pre-commit-run:
	@echo ">>> Running pre-commit hooks..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && pre-commit run --all-files


#############################################
#  DATABASE MIGRATIONS                      #
#############################################

migrate-init:
	@echo ">>> Initializing Alembic..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && alembic init alembic
	@echo "Done!"

migrate-create:
	@echo ">>> Creating migration: $(msg)..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@test -n "$(msg)" || { echo "Usage: make migrate-create msg='migration description'"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && alembic revision --autogenerate -m "$(msg)"
	@echo "Done!"

migrate-up:
	@echo ">>> Applying migrations..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && alembic upgrade head
	@echo "Done!"

migrate-down:
	@echo ">>> Rolling back migration..."
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && alembic downgrade -1
	@echo "Done!"

migrate-history:
	@echo ">>> Migration history:"
	@test -d $(TEST_VENV_DIR) || { echo "Run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && alembic history --verbose


#############################################
#  DOCKER                                   #
#############################################

docker-build:
	@echo ">>> Building Docker image..."
	@docker build -t example_web_app:latest .
	@echo "Done!"

docker-run:
	@echo ">>> Running Docker container..."
	@docker run --rm -it -p 9999:9999 example_web_app:latest

docker-compose-up:
	@echo ">>> Starting services with Docker Compose..."
	@docker compose up -d
	@echo "Services started. View logs with: docker compose logs -f"

docker-compose-down:
	@echo ">>> Stopping services..."
	@docker compose down -v
	@echo "Done!"

# cookiecutter-aiohttp-sqlalchemy

Fat and opinionated cookiecutter template for building async Web Apps powered by Aiohttp, SQLAlchemy and Swagger.

Check out the [Features](#features) section below for a short description of what this box packs for you. The [Code Examples](#code-examples) section showcases a code example of an async API using an SQLAlchemy Base Model.

If you want to see a **working example web app** generated using this cookiecutter-template, then please head over to [/examples](https://github.com/aalhour/cookiecutter-aiohttp-sqlalchemy/tree/master/examples) directory.

## Contents
 
  * [Features](#features)
  * [Requirements](#requirements)
  * [Quick Start](#quick-start)
  * [Code Examples](#code-examples)
 
## Features

 - [x] SQLALchemy Support:
   - [x] `asyncio`-compatible: use `async/await` to execute db queries
   - [x] Request-scoped DB Sessions via `contextvars`
   - [x] Executor-based queries execution
   - [x] Managed transactional support via contextmanager interface
 - [x] Swagger Support:
   - [x] Separate Swagger YAML file
   - [x] Auto-generation of Swagger UI
   - [x] Docs served at: `/api/v1.0/docs`
   - [x] Swagger JSON Schema served at: `/api/v1.0/docs/swagger.json`
 - [x] Development Server:
   - [x] `make dev-server` starts an Aiohttp Dev Server (file-watch enabled)
 - [x] Docker Support:
   - [x] Multi-stage `Dockerfile` with Python 3.12
   - [x] `docker-compose.yaml` with PostgreSQL 16 and health checks
   - [x] `make docker-build`: to build the image
   - [x] `make docker-run`: to run the image
   - [x] `make docker-build-run`: a shorthand for two of the above
 - [x] Independent Test Env:
   - [x] `make install-dev` creates a separate virtualenv with all dev requirements
   - [x] `make pytest` runs the `tests/` package from the testing virtualenv
   - [x] `make coverage` runs test coverage analysis from the testing virtualenv
   - [x] `make test` runs `make install-dev` and then `make pytest`
 - [x] Configuration Management:
   - [x] Ini-file based configuration, see: `config/default.conf`
   - [x] Environment variable support via `env.template`
 - [x] Management CLI:
   - [x] `make install` to create a virtualenv and install the project
   - [x] `make test` to run the tests
   - [x] `make clean` to remove cached and built artifacts
   - [x] `make help` to display more awesome commands
   - [x] `make dev-upgrade-deps` upgrades all high-level dependencies
 - [x] Python packaging:
   - [x] Auto-generated `setup.py` with project info
   - [x] `make package` builds a distributable `wheel` of the project
 - [x] Error Tracking:
   - [x] Sentry integration via `sentry-sdk`
 - [x] Docs:
   - [x] README.md (see: [example](examples/example_web_app/README.md))

## Requirements

 * Python 3.10+ (tested with Python 3.12 and 3.14)
 * Aiohttp 3.13+
 * Aiohttp-Swagger
 * Psycopg2-binary
 * SQLAlchemy 1.4+
 * UVLoop
 * uJSON
 * Sentry-SDK

## Quick Start

First, grab cookiecutter if you don't have it and start the generation process:
```bash
pip install cookiecutter
cookiecutter https://github.com/aalhour/cookiecutter-aiohttp-sqlalchemy
```

### Option 1: Docker (Recommended)

Run everything with Docker Compose, which spins up PostgreSQL automatically:
```bash
cd <your-app-name>
docker compose up
```

The API will be available at `http://localhost:9999` (or your configured port).

### Option 2: Local Installation

Install via the Makefile:
```bash
make install
```

Copy the config file to your home directory:
```bash
cp config/default.conf ~/.config/<your-app-name>.conf
```

Customize the config file with your database details:
```ini
[db]
host = localhost
port = 5432
name = <database_name>
schema = <schema_name>
user = <database_user>
```

Start the application:
```bash
venv/bin/run_<your-app-name>
```

## Code Examples

The following is an example API code that tries to query the database using an SQLAlchemy Declarative Model:

```python
class UsersApi:
    async def get_user_by_id(self, request):
        """
        GET /api/v1.0/users/<id>
        """
        user_id = request.match_info.get('id')
        
        async with transactional_session() as db:
            # `User` is an SQLAlchemy declarative class
            user = await User.get_by_id(user_id, db)
            
            return self.json_response(user.serialized)
```

```python
class User(db.BaseModel):
    """
    Data model for the User database table.
    """
    __tablename__ = 'user'

    id = Column(INTEGER, primary_key=True, autoincrement=True)

    def __init__(self, id_=None, name=None):
        self.id = id_

    @classmethod
    async def get_by_id(cls, id_: int, session: Session) -> "User":
        """
        Get user by ID from the database
        
        :param id_: User ID
        :param session: Database session object
        :return: User instance if user exists; otherwise, None
        """
        # Run the SQLAlchemy session.query(Example).get() function in the background
        return await run_async(session.query(cls).get, (id_,))
```

The template comes with pre-packaged asyncio utility functions and classes to aid querying the database via SQLALchemy declarative models in the background, the above mentioned `transactional_session` context-manager, `run_async` function and `db.BaseModel` class will be generated for you as part of the cookiecutter template. 

If you want to see a **working example web app** generated using this cookiecutter-template, then please head over to [/examples](https://github.com/aalhour/cookiecutter-aiohttp-sqlalchemy/tree/master/examples) directory.

# cookiecutter-aiohttp-sqlalchemy

Fat and opinionated cookiecutter template for building async Web Apps powered by Aiohttp, SQLAlchemy and Swagger.

Check out the [features](#features) section below for a short description of what this box packs for you.

## Contents
 
  * [Features](#features)
  * [Requirements](#requirements)
  * [Usage](#usage)
  * [Examples](#examples)
 
## Features

 - [x] SQLALchemy Support:
   - [x] `asyncio`-compatible: use `async/await` to execute db queries
   - [x] Request-scoped DB Sessions
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
   - [x] `Dockerfile`: configurable arguments for DB Access
   - [x] `docker-compose.yml`: Spins up `PostgreSQL` for development
   - [x] `make docker-build`: to build the image
   - [x] `make docker-run`: to run the image
   - [x] `make docker-build-run`: a shorthand for two of the above
 - [x] Independent Test Env:
   - [x] `make install-dev` creates a separate virtualenv with all dev requirements
   - [x] `make pytest` runs the `tests/` package from the testing virtualenv
   - [x] `make coverage` runs test coverage analysis from the testing virtualenv
   - [x] `make test` runs `make install-dev` and then `make pyest`
 - [ ] Configuration Management:
   - [x] Ini-filed based configuration, see: `config/default.conf`
   - [ ] Support configuration via `.env` file
 - [x] Management CLI:
   - [x] `make install` to create a virtualenv and install the project
   - [x] `make test` to run the tests
   - [x] `make clean` to remove cached and built artifacts
   - [x] `make help` to display more awesome commands
   - [x] `make dev-upgrade-deps` upgrades all high-level dependencies
 - [x] Python packaging:
   - [x] Auto-generated `setup.py` with project info
   - [x] `make package` builds a distributable `wheel` of the project

## Requirements

 * Python 3.6+ (tested with Python 3.8)
 * Aiohttp
 * Aiohttp-Swagger
 * Psycopg2
 * SQLAlchemy
 * UVLoop
 * uJSON

## Usage

First, grab cookiecutter if you don't have it and start the generation process:
```
$ pip install cookiecutter
$ cookiecutter https://github.com/aalhour/cookiecutter-aiohttp-sqlalchemy
```

Either run everything with Docker and Docker-compose, which will also spin-up a PostgreSQL side-car instance, as follows:
```
$ docker-compose up
```

Or, go the manual way and install everything locally via the Makefile:
```
$ make install
```

Once installed manually, copy the config file template over to `~/.config/<your-app-name>.conf`. It is important that the file name matches the application name you entered in the cookiecutter generation process:
```
$ cp config/example.conf ~/.config/<your-app-name>.conf
```

Next thing is, you need to customize your config file and enter your database details under the `[db]` section, please follow the config file:
```
$ cat ~/.config/<your-app-name>.conf

[db]
host = localhost
port = 5432
name = <database_name>
schema = <schema_name>
user = <database_user>
```

Lastly, start the application using the Pythonic entry point:
```
$ venv/bin/run_<your-app-name>
```

## Examples

The following is an example API code that tries to query the database using an SQLAlchemy Declarative Model:

```python
class UsersApi:
    async def get_user_by_id(self, request):
        user_id = request.match_info.get('id')
        
        async with transactional_session() as db:
            # `User` is an SQLAlchemy declarative class
            user = await User.get_by_id(user_id, db)
            
            return self.json_response(user.serialized)
```

If you want to see a **working example web app** generated using this cookiecutter-template, then please head over to [/examples](https://github.com/aalhour/cookiecutter-aiohttp-sqlalchemy/tree/master/examples) directory.

# cookiecutter-aiohttp-sqlalchemy

Fat and opinionated cookiecutter template for building async Web Apps powered by Aiohttp, SQLAlchemy and Swagger.

Check out the [features](#features) section below for a short description of what this box packs for you.

## Contents
 
  * [Features](#features)
  * [Requirements](#requirements)
  * [Usage](#usage)
  * [Examples](#examples)
 
## Features

 * SQLAlchemy Declarative Data Models with async/await class methods
 * Run SQLAlchemy declarative queries *asynchronously* inside Aiohttp's awaitable request handlers
   + Asynchronicity is emulated using an ThreadPoolExecutor in the background, managed by the I/O Loop
   + You can use a simple utility function out-of-the box which manages all the details for you
 * Database Sessions are scoped for every request
   + The request context is emulated using asyncio's Task interface, inspired by this [blog post by by SkyScanner](https://medium.com/@SkyscannerEng/from-flask-to-aiohttp-22f1ddc5dd5e)
 * Manage transactional database sessions using the context manager interface with your data models
 * Packaging included - `setup.py` and `Makefile` already implemented for you
   + Type in `make help` to get more info about the CLI features
 * Nicely separated interfaces for the Application factory and the URL routes registration
 * Swagger-UI integration
 * Configuration is offloaded to a flat text file (not the best option, I know! :/)
 * Simple to use CLI made with make. Type in `make help` to display all available commands
 * Two separated Python virtualenvs for 1) hosting the application requirements, and 2) running tests
   + Easily managed via the CLI interface, so no need for you to remember this detail
   + Comes in handy when running tests post-deployment on the same machine without affecting the app virtualenv
   + `make install` command: creates the app virtualenv and resolves its dependencies
   + `make install-dev`: creates the testing virtualenv and resolves its dev-dependencies, i.e.: pytest ... etc

## Requirements

 * Python 3.6+ (tested with Python 3.6.6)
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

Second, setup virtual environment and install requirements:
```
$ make install
```

Third, copy the config file template over to `~/.config/<your-app-name>.conf`. It is important that the file name matches the application name you entered in the cookiecutter generation process:
```
$ cp config/example.conf ~/.config/<your-app-name>.conf
```

Next thing is, you need to customize your config file and enter your database details under the `[db]` section, please follow the config file:
```
$ cat ~/.config/example_web_app.conf

[db]
host = localhost
port = 5432
name = <database_name>
schema = <schema_name>
user = <database_user>
```

Fourth and last step, start the application using the Pythonic entry point:
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

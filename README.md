# cookiecutter-aiohttp-sqlalchemy

Cookiecutter template for boilerplate async Web Apps powered by Aiohttp and SQLAlchemy.

## Contents
 
  * [Features](#features)
  * [Usage](#usage)
  * [Code Snippet](#code-snippet)
  * [Working Examples](#working-examples)

## Features:

 * SQLAlchemy Declarative Data Models with async/await class methods
 * Run custom SQLAlchemy declarative queries asynchronously inside Aiohttp's awaitable request handlers
 * Database Sessions are scoped for every request
   + The request context is emulated using asyncio's Task interface, inspired by this [blog post by by SkyScanner](https://medium.com/@SkyscannerEng/from-flask-to-aiohttp-22f1ddc5dd5e)
 * Manage transactional database sessions using the context manager interface with your data models
 * Packaging included - `setup.py` and `Makefile` already implemented for you
   + Type in `make help` to get more info about the CLI features
 * Nicely separated interfaces for the Application factory and the URL routes registeration
 * Configuration is offloaded to a flat text file (not the best option, I know! :/)
 * Swagger-UI integration

## Usage:

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
$ cp config/example.conf ~/.config/config/example_web_app.conf
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

## Code Snippet:

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

## Working Examples:

If you want to see working examples of this cookiecutter-template, then please head over to [/examples](https://github.com/aalhour/cookiecutter-aiohttp-sqlalchemy/tree/master/examples).

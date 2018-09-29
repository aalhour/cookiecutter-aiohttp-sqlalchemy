# cookiecutter-aiohttp-sqlalchemy

Cookiecutter template for boilerplate async Web Apps powered by Aiohttp and SQLAlchemy.

## Features:

 * SQLAlchemy Declarative Data Models with async/await class methods
 * Run custom SQLAlchemy declarative queries asynchronously inside Aiohttp request handlers
 * Database sessions are scoped for every request
   + The request context is emulated using asyncio's Task interface, inspired by this [blog post by by SkyScanner](https://medium.com/@SkyscannerEng/from-flask-to-aiohttp-22f1ddc5dd5e)
 * Nicely separated interfaces for the Application factory and the URL routes registeration
 * Configuration is offloaded to a flat text file (not the best option, I know! :/)
 * Swagger-UI integration

## Code Snippets:

The following is an example API code that tries to query the database using an SQLAlchemy Declarative Model:

```python
class UsersApi:
    async def get_user_by_id(self, request):
        user_id = request.match_info.get('id')
        
        async with transactional_session() as db_session:
            # User class is an SQLAlchemy declarative model
            user = await User.get_by_id(user_id, db_session)
            
            return self.json_response(user.serialized)
```

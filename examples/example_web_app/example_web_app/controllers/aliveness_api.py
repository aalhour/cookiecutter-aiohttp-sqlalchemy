from aiohttp import web

from example_web_app.controllers.base import BaseJsonApiController
from example_web_app.logger import get_logger


_logger = get_logger()


class AlivenessApiController(BaseJsonApiController):
    async def get(self, request: web.Request) -> web.Response:
        """
        Returns an HTTP 200 OK JSON message for clients to know the service is alive!

        :param request: A request that contains query params
        :return: JSON response with `{message: 'I'm alive and kicking!!!'}
        """
        return self.json_response(body={
            "message": "I'm alive and kicking!!!"
        })

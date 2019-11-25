from aiohttp import web

from {{cookiecutter.app_name}}.controllers.base import BaseJsonApiController
from {{cookiecutter.app_name}}.models.health import HealthStatus
from {{cookiecutter.app_name}}.logger import get_logger


_logger = get_logger()


class HealthApiController(BaseJsonApiController):
    async def get(self, request: web.Request) -> web.Response:
        """
        Returns an HTTP 200 OK JSON message for clients to know the service is healthy

        Inspired by: https://tools.ietf.org/id/draft-inadarei-api-health-check-01.html

        :param request: A request that contains query params
        :return: JSON response with `{message: 'I'm alive and kicking!!!'}
        """
        # TODO: Try connecting to the database before returning "200 OK: Pass" Response
        return self.json_response(body={
            "status": HealthStatus.Pass.value
        })

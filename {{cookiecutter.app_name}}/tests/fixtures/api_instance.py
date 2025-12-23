from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from bravado_core.spec import Spec

from {{cookiecutter.app_name}}.logger import get_logger
from tests.conftest import TEST_PORT

_logger = get_logger()


class ApiInstanceFixture:
    """
    Fixture that encapsulates an API instance to test. It's either running locally, or on a remote host.
    """

    def __init__(self, swagger_spec: Spec):
        """
        :param swagger_spec: Complete swagger specification for the API to test.
        """
        self.host = "localhost"

        self.swagger_spec = swagger_spec
        self.base_path = swagger_spec.client_spec_dict.get("basePath", "")

        self.swagger_spec.spec_dict['host'] = f'{self.host}:{TEST_PORT}'

        # setting validate requests to false since we only care about
        # responses
        config = {
            "also_return_response": True,
            "use_models": False,
            "validate_requests": False,
            "formats": swagger_spec.config.get("formats", [])
        }
        self.config = config

        # Bravado provides an async client, but it doesnt run on ioloop? from docs:
        # Fido is a simple, asynchronous HTTP client built on top of Crochet and Twisted with an implementation
        # inspired by the book "Twisted Network Programming Essentials". It is intended to be used in environments
        # where there is no event loop, and where you cannot afford to spin up lots of threads (otherwise you
        # could just use a ThreadPoolExecutor).

        self.swagger_client = SwaggerClient.from_spec(
            self.swagger_spec.spec_dict,
            http_client=RequestsClient(),
            config=config)

"""
Base Controllers module.
"""

from typing import Any, List, Dict

import ujson as json
from aiohttp import web


class BaseJsonApiController:
    """
    API Controller base class.
    """

    def __init__(self, *args, **kwargs):
        pass

    STATUS_MESSAGES = {
        200: 'OK',
        201: 'Created',
        207: 'Mixed status',
        400: 'Invalid {model} resource representation',
        401: 'Unauthorized request.',
        404: 'The requested resource was not found.',
        405: 'Method not allowed.',
        409: 'Another resource exists with the same <id or unique field>.',
        500: 'An error occurred while processing your request, please retry!',
        520: 'Unknown error.'
    }

    @classmethod
    def json_response(cls, body: Any=None, status: int=200, reason: str=None,
                      headers: Dict[str, Any]=None) -> web.Response:
        """
        Returns a complete aiohttp.web.Response with json-formatted text body that is
          utf-8 encoded with a content-type header set to "application/json".

        :param Any body: JSON-serializable response body
        :param int status: response status code, by default: 200.
        :param str reason: Explanation for status code, i.e.: "OK".
        :type headers: multidict.CIMultiDict
        :param dict headers: a dictionary of headers and their values.
        :return: an `aiohttp.web.Response` instance.
        """
        json_body = json.dumps(body)

        return web.Response(
            text=json_body,
            status=status,
            reason=reason,
            headers=headers,
            charset="utf-8",
            content_type="application/json")

    @classmethod
    def write_error(cls, status: int, reason: str=None, errors: List[Dict[str, str]]=None,
                    headers: Dict[str, Any]=None) -> web.Response:
        """
        Sends an error response

        :param status: the HTTP code of the response
        :param reason: the reason that will be sent as the error message
        :param errors: list of occurred errors
        :param headers: a dictionary of headers
        :return: web Response
        """
        body = {
            'message': reason or cls.STATUS_MESSAGES.get(status, '')
        }

        if errors:
            body['errors'] = errors

        return cls.json_response(body=body, status=status, headers=headers)


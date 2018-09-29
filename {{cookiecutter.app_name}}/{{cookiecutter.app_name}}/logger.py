import sys
import logging

from {{cookiecutter.app_name}} import APP_NAME
from {{cookiecutter.app_name}}.config import logging_option as config_logging_option


logging.basicConfig(
    stream=sys.stderr,
    level=logging.getLevelName(config_logging_option("level")),
    format="%(asctime)s\t[%(levelname)s]\t%(message)s")


###
# LOGGING FACTORY
#
def make_logger(is_development=False):
    """
    Sets up logging with a standard format, creates a logger instance and returns it.

    :param Bool is_development: controls whether to mark the logger's level as DEBUG or
           as specified in the config file
    :rtype: logging.Logger.
    :return: logger instance.
    """
    _logger = logging.Logger(name=APP_NAME)

    if is_development:
        _logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    _logger.addHandler(handler)
    return _logger


def get_logger():
    """
    Returns the application's logger instance by name.

    :rtype: logging.Logger.
    :return: logger instance.
    """
    _logger = logging.getLogger(APP_NAME)

    if isinstance(_logger, logging.RootLogger):
        _logger = make_logger()

    return _logger

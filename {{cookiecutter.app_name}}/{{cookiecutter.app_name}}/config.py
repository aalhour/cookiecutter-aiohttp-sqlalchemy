"""
Config module.

Responsible for providing the configuration reader.
"""

import pathlib
from functools import partial, lru_cache
from configparser import ConfigParser


CONFIG_DIR = ".config"
CONFIG_FILE_NAME = "{{cookiecutter.app_name}}.conf"
CONFIG_FILE_PATH = pathlib.Path.home() / CONFIG_DIR / CONFIG_FILE_NAME


@lru_cache()
def get_config(path: str = CONFIG_FILE_PATH) -> ConfigParser:
    """
    Parses ~/.config/{{cookiecutter.app_name}}.conf and returns the result

    :param path: path to config file
    :return:
    """
    config = ConfigParser()
    config.read(path)

    return config


def get_option(section: str, option: str, path: str = CONFIG_FILE_PATH) -> str:
    config = get_config(path)
    return config.get(section, option)


# Usage: db_option("host"), db_option("host", "/path_to_test_config_file")
server_option = partial(get_option, "server")
db_option = partial(get_option, "db")
sentry_option = partial(get_option, "sentry")
logging_option = partial(get_option, "logging")

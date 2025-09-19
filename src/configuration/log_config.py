"""Defines configuration for the logging."""

import logging
import sys

from src.configuration.app_config import settings


LOG_FORMAT = (
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(name)s - %(message)s"
)


def get_log_level():
    """Returns the log level based on the environment."""

    _env = settings.app_env.upper()
    if _env == "LOCAL":
        return logging.DEBUG
    elif _env == "DEV":
        return logging.INFO
    elif _env == "PROD":
        return logging.INFO
    raise ValueError(f"Invalid environment for logging: {_env}")


def setup_logging():
    """Set up logging configuration."""

    logging.basicConfig(
        format=LOG_FORMAT,
        level=get_log_level(),
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log"),
        ],
        force=True,
    )

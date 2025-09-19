"""Defines configuration for the application."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "local"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()

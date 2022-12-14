import pathlib
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    echo_active: bool = False
    app_auth_token: str
    app_auth_token_prod: str = None
    skip_auth: bool = False

    class Config:
        env_file = pathlib.Path(__file__).parent / ".env"


@lru_cache  # makes sure it's called once
def get_settings():
    return Settings()

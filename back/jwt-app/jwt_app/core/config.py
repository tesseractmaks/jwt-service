import os
import sys

from dotenv import load_dotenv
from loguru import logger
from pydantic_settings import BaseSettings

load_dotenv()


class Setting(BaseSettings):
    db_url: str = (
        f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:5432/test_jwt_db"
    )
    api_v1_prefix: str = "/api/v1"
    db_username: str = "jwt"
    db_password: str = "qwerty"
    db_name: str = "test_jwt_db"
    db_echo: bool = True

    test_db_username: str = "postgres"
    test_db_password: str = "qwerty"
    test_db_name: str = "test_jwt_db"
    test_db_echo: bool = True


settings = Setting()

logger.add(
    sys.stdout,
    format="{time} {level} {message}",
    level="ERROR",
    serialize=True,
    backtrace=True,
    diagnose=True,
)

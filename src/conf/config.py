from typing import Any

from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:123456@localhost:5432/database"
    SECRET_KEY_JWT: str = "1234567890"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "postgres@meail.com"
    MAIL_PASSWORD: str = "postgres"
    MAIL_FROM: str = "postgres"
    MAIL_PORT: int = 567234
    MAIL_SERVER: str = "postgres"
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLOUDINARY_NAME: str = "some_name"
    CLOUDINARY_API_KEY: str = "1111111111111111"
    CLOUDINARY_API_SECRET: str = "1i2uh3i1uhduni2u3oi3uhiu32eiui2h3"

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  


config = Settings()

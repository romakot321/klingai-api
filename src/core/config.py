from typing import Literal
from pydantic import AnyUrl, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    KLING_ACCESS_KEY: str
    KLING_SECRET_KEY: str
    FAL_KEY: str
    LOCAL_STORAGE_PATH: str = "storage"

    PROJECT_NAME: str = os.environ.get("PROJECT_NAME", "UNNAMED PROJECT")
    API_V1_STR: str = "/api/v1"
    DOMAIN: str = os.environ.get("DOMAIN")

    DB_TYPE: Literal['POSTGRESQL', 'ASYNC_POSTGRESQL', 'SQLITE', 'ASYNC_SQLITE'] = os.environ.get("DB_TYPE")
    DB_NAME: str = os.environ.get("DB_NAME")
    DB_USER: str | None = os.environ.get("DB_USER")
    DB_PASSWORD: str | None = os.environ.get("DB_PASSWORD")
    DB_HOST: str | None = os.environ.get("DB_HOST")
    DB_PORT: str | None = os.environ.get("DB_PORT")
    DATABASE_URI: str | None = None
    ALEMBIC_DATABASE_URI: str | None = None

    @staticmethod
    def _build_dsn(scheme: str, values: dict) -> str:
        return str(
            PostgresDsn.build(
                scheme=scheme,
                username=values.get("DB_USER"),
                password=values.get("DB_PASSWORD"),
                host=values.get("DB_HOST"),
                port=int(values["DB_PORT"]) if values.get("DB_PORT") else None,
                path=values.get("DB_NAME"),
            )
        )

    @field_validator("DATABASE_URI")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        elif isinstance(v, AnyUrl):
            return str(v)
        db_type = info.data.get("DB_TYPE")
        if db_type == "POSTGRESQL":
            return cls._build_dsn("postgresql+psycopg", info.data)
        elif db_type == "ASYNC_POSTGRESQL":
            return cls._build_dsn("postgresql+asyncpg", info.data)
        raise ValueError("Unsupported database type")

    @field_validator("ALEMBIC_DATABASE_URI", mode="before")
    def assemble_alembic_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        elif isinstance(v, AnyUrl):
            return str(v)
        return info.data.get("DATABASE_URI")


settings = Settings()

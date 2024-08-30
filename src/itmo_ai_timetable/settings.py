from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8")

    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str

    days_column: int = Field(2, description="Column with days")
    timetable_offset: int = Field(3, description="Offset between date and timetable")
    timetable_len: int = Field(5, description="Number of columns that relate to timetable")
    keywords: list[str] = Field(
        [
            "Экзамен",
            "Зачет",
            "Дифф. зачет",
        ],
        description="Extra words in cell that contains type of pair",
    )

    timezone: str = "Europe/Moscow"

    @property
    def database_settings(self) -> Any:
        """Get all settings for connection with database."""
        return {
            "database": self.postgres_db,
            "user": self.postgres_user,
            "password": self.postgres_password,
            "host": self.postgres_host,
            "port": self.postgres_port,
        }

    @property
    def database_uri(self) -> str:
        """Get uri for connection with database."""
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

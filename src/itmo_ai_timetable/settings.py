from pydantic import Field, FilePath, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env", "../../.env"), env_file_encoding="utf-8")

    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str

    days_column: int = Field(2, description="Column with days")
    timetable_offset: int = Field(3, description="Offset between date and timetable")
    timetable_len: int = Field(5, description="Number of columns that relate to timetable")
    keywords: list[str] = Field(
        ["Экзамен", "Лекция", "Зачет", "Семинар", "Защита", "Дифф. зачет"],
        description="Extra words in cell that contains type of pair",
    )
    max_days_difference: int = Field(180, description="Max days difference between date and today")

    tz: str = "Europe/Moscow"

    courses_to_skip: list[str] = Field(["Выходной", "Demoday 12:00-15:30"], description="Courses to skip")

    course_1_excel_calendar_id: HttpUrl = Field(description="Link to course 1 calendar")
    course_1_list_name: str = Field("Расписание", description="Name of course 1 list")
    course_2_excel_calendar_id: HttpUrl = Field(description="Link to course 2 calendar")
    course_2_list_name: str = Field("Расписание", description="Name of course 2 list")

    google_credentials_path: FilePath = Field(
        description="Path to google credentials file",
    )
    google_token_path: FilePath = Field(description="Path to google token file")

    tg_bot_token: str = Field(description="Telegram bot token")
    admin_chat_id: int = Field(description="Admin chat id")

    course_info_url: HttpUrl = Field(description="Course info url")

    @property
    def database_settings(self) -> dict[str, str | int]:
        return {
            "database": self.postgres_db,
            "user": self.postgres_user,
            "password": self.postgres_password,
            "host": self.postgres_host,
            "port": self.postgres_port,
        }

    @property
    def database_uri(self) -> str:
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

    def get_calendar_settings(self) -> list[tuple[HttpUrl, str]]:
        return [
            (transform_calndar_id_to_url(self.course_1_excel_calendar_id), self.course_1_list_name),
            (transform_calndar_id_to_url(self.course_2_excel_calendar_id), self.course_2_list_name),
        ]


def transform_calndar_id_to_url(calendar_id: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{calendar_id}/export?format=xlsx"

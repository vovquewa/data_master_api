from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_TOKEN: str = Field(..., env="API_TOKEN")
    APP_TITLE: str = "Data Master API"
    APP_DESCRIPTION: str = "Excel data processing service"
    APP_VERSION: str = "1.0.0"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "app" / "data"

    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = "env/.env"
        env_file_encoding = "utf-8"


settings = Settings()

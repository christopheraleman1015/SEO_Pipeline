from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/seo_agent"
    redis_url: str = "redis://localhost:6379/0"
    storage_root: Path = Field(default=Path("./storage"))
    celery_task_always_eager: bool = False

    llm_api_key: str | None = None
    llm_default_model: str | None = None
    llm_cheap_model: str | None = None
    llm_strong_model: str | None = None

    max_llm_calls_per_project_per_day: int = 100
    max_llm_cost_per_project_per_day: float = 25.0
    serp_priority_threshold: float = 0.65
    brief_priority_threshold: float = 0.70


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

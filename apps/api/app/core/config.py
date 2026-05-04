from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Offer Center API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/offer_center"
    cors_origins: list[str] = ["*"]
    llm_provider: str = "none"
    moonshot_api_key: str | None = None
    moonshot_base_url: str = "https://api.moonshot.ai/v1"
    moonshot_model: str = "kimi-k2.5"
    moonshot_timeout_seconds: int = 60
    gemini_api_key: str | None = None
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    gemini_model: str = "gemini-2.5-flash"
    gemini_timeout_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_prefix="OFFER_CENTER_")


@lru_cache
def get_settings() -> Settings:
    return Settings()

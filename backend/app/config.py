from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./mail_automation.db"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"
    google_cloud_project: str = ""
    google_pubsub_topic: str = ""
    google_pubsub_subscription: str = ""
    ai_provider: str = "heuristic"
    ai_api_key: str = ""
    ai_model: str = ""
    encryption_key: str = ""
    app_secret: str = "development-secret-change-me"
    app_base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()

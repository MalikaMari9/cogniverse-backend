from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "AI Agent Simulation Backend"
    app_version: str = "1.0.0"
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    stripe_public_key: str = ""
    stripe_secret_key: str = ""
    simulation_service_base_url: str = "https://new-model-r733.onrender.com"
    simulation_service_timeout_seconds: int = 30
    simulation_service_api_key: str | None = None
    stripe_webhook_secret : str = ""

    # Email settings
    to_email: str | None = None
    from_email: str | None = None
    email_password: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

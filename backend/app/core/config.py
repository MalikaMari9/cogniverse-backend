from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "AI Agent Simulation Backend"
    app_version: str = "1.0.0"
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    stripe_public_key: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret : str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

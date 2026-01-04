from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI Event-Driven Clean Architecture"
    debug: bool = True
    environment: str = "development"
    
    # Database - required but with default for development
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_db"
    database_echo: bool = True
    
    # Test Database - optional, defaults to test database
    test_database_url: Optional[str] = None
    
    # Security - required but with default for development
    secret_key: str = "change-me-in-production-please-use-a-secure-key"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    encryption_algorithm: str = "HS256"
    cors_origins: list[str] = ["*"]
    
    events_enabled: bool = True
    
    # Resend configuration - optional
    resend_api_key: Optional[str] = None
    resend_from_email: Optional[str] = None
    
    # RabbitMQ configuration - with defaults
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "user_events"
    rabbitmq_queue: str = "user_events_queue"

    class Config:
        env_file = ".env"
        case_sensitive = False
        # Ignore errors when reading .env file
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

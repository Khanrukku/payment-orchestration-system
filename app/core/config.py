from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Payment Orchestration System"
    database_url: str = "sqlite+aiosqlite:///./payments.db"
    redis_url: str = "redis://localhost:6379/0"
    max_gateway_retries: int = 2
    gateway_timeout_seconds: float = 3.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

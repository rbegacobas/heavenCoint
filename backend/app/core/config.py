"""Heaven Coint Backend — Core Configuration."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_KEYS = {
    "change-me-to-a-random-64-char-string",
    "secret",
    "changeme",
    "",
}


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General
    app_name: str = "heavencoint"
    app_env: str = "development"
    app_debug: bool = True
    app_version: str = "0.1.0"

    # Backend
    backend_port: int = 8000
    backend_host: str = "0.0.0.0"
    secret_key: str = "change-me-to-a-random-64-char-string"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_be_secure(cls, v: str) -> str:
        if v in _INSECURE_KEYS or len(v) < 32:
            import os
            if os.getenv("APP_ENV", "development") == "production":
                raise ValueError(
                    "SECRET_KEY must be a random string of at least 32 characters in production. "
                    "Generate one with: python3 -c \"import secrets; print(secrets.token_hex(32))\""
                )
        return v

    # Database
    postgres_user: str = "heavencoint"
    postgres_password: str = "heavencoint_dev_2026"
    postgres_db: str = "heavencoint"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    # Market Data APIs
    polygon_api_key: str = ""
    binance_api_key: str = ""
    binance_api_secret: str = ""

    # FRED
    fred_api_key: str = ""

    # Schwab / Thinkorswim
    schwab_app_key: str = ""
    schwab_secret: str = ""
    schwab_callback_url: str = "https://127.0.0.1"

    # LLM
    openai_api_key: str = ""
    llm_model: str = "gpt-4o"
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.1

    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()

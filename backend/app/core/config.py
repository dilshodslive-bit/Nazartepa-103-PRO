"""Ilova konfiguratsiyasi — .env fayldan o'qiladi (Pydantic Settings)."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- App ---
    app_name: str = "Nazartepa 103"
    environment: Literal["development", "production", "test"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # --- Security ---
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    jwt_algorithm: str = "HS256"

    # --- Database ---
    database_url: str = "postgresql+asyncpg://nazartepa:nazartepa_dev_password@localhost:5432/nazartepa103"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- CORS ---
    # NoDecode: pydantic-settings env qiymatini JSON emas, oddiy satr sifatida oladi;
    # keyin quyidagi validator vergul bo'yicha ajratadi.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    # --- Brute-force / rate limit ---
    login_max_attempts: int = 5
    login_lockout_minutes: int = 15

    # --- Seed super-admin ---
    first_superadmin_email: str = "admin@nazartepa.uz"
    first_superadmin_password: str = "Admin12345!"

    # --- AI Triage ---
    ai_triage_provider: Literal["rule_based", "ollama", "openai", "anthropic"] = "rule_based"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        """Vergul bilan ajratilgan satrni ro'yxatga aylantiradi."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Sozlamalarni bir marta o'qib, kesh'da saqlaydi."""
    return Settings()


settings = get_settings()

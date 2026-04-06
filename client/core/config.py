from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "FastAPI Service with gRPC Auth"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    port: int = 8000
    host: str = "127.0.0.1"
    description: str = "FastAPI service that delegates all auth to gRPC Auth service"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ========== PostgreSQL (for Todo service) ==========
    postgres_user: str = Field(default="postgres", description="postgres user")
    postgres_password: str = Field(default="postgres", description="postgres password")
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="fastapi_service", description="PostgreSQL database name for FastAPI")

    # ========== JWT Configuration (shared with Auth service) ==========
    # IMPORTANT: Must match Auth service settings!
    jwt_secret: str = Field(default="change-me-in-production", description="jwt_secret - MUST MATCH AUTH SERVICE")
    jwt_algorithm: str = Field(default="HS256", description="jwt algorithm")
    access_token_expires_minutes: int = Field(
        default=15, description="Access token expiry in minutes"
    )
    refresh_token_expires_days: int = Field(
        default=7, description="Refresh token expiry in days"
    )

    # ========== Auth Service (gRPC) Connection ==========
    auth_service_host: str = Field(default="localhost", description="Auth service gRPC host")
    auth_service_port: int = Field(default=5501, description="Auth service gRPC port")

    @property
    def db_url(self) -> str:
        """Database URL for FastAPI service (Todo database)."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    def get(self, key: str, default=None):
        """Get setting by key for backward compatibility."""
        return getattr(self, key, default)


settings = Settings()


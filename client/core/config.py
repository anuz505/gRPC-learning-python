from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "GRPC learning"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    port: int = 8000
    host: str = "127.0.0.1"
    description: str = "App description here.."

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # db settings
    postgres_user: str = Field(default="postgres", description="postgres user")
    postgres_password: str = Field(default="root",
                                   description="postgres password")
    postgres_host: str = Field(default="localhost",
                               description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="Boilerplate",
                             description="PostgreSQL database name")

    # JWT and auth settings
    access_token_expires_minutes: int = Field(
        default=15, description="Access token expiry in minutes"
    )
    refresh_token_expires_days: int = Field(
        default=7, description="Refresh token expiry in days"
    )
    cookie_secure: bool = Field(default=False, description="Set secure cookies")
    jwt_secret: str = Field(default="change-me-in-production", description="jwt_secret")
    jwt_algorithm: str = Field(default="HS256", description="jwt algorithm")

    @property
    def db_url(self) -> str:
        return (
            (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        )


settings = Settings()

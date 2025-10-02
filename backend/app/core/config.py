from typing import List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
from pathlib import Path


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CAD Viewer API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5174",  # Alternative Vite port
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str = "sqlite:///./cadviewer.db"
    DATABASE_ECHO: bool = False

    # PostgreSQL support (optional)
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values) -> str:
        if isinstance(v, str):
            return v
        # Build PostgreSQL URL if components are provided
        if values.get("POSTGRES_SERVER"):
            return PostgresDsn.build(
                scheme="postgresql",
                username=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=values.get("POSTGRES_SERVER"),
                path=f"{values.get('POSTGRES_DB') or ''}",
            )
        return v

    # Redis (for caching and background tasks)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 300  # 5 minutes default

    # File Upload Settings
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".gltf", ".glb", ".babylon", ".obj", ".stl", ".fbx", ".dae"]
    CHUNK_SIZE: int = 1024 * 1024  # 1MB chunks

    # Email Settings (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # Background Tasks
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # Authentication Providers (future)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = False

    # Development/Testing
    TESTING: bool = False

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    @property
    def server_host(self) -> str:
        # Use for server host
        if self.DEBUG:
            return "http://localhost:8000"
        return "https://api.cadviewer.com"  # Change to your domain

    @property
    def emails_enabled(self) -> bool:
        return bool(
            self.SMTP_HOST
            and self.SMTP_PORT
            and self.EMAILS_FROM_EMAIL
        )

    @property
    def redis_enabled(self) -> bool:
        return bool(self.REDIS_URL)


settings = Settings()
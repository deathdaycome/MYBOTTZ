"""
Configuration management using Pydantic Settings
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========== APPLICATION ==========
    ENV: str = Field(default="production", description="Environment")
    DEBUG: bool = Field(default=False, description="Debug mode")
    APP_NAME: str = Field(default="Enterprise CRM", description="Application name")
    VERSION: str = Field(default="1.0.0", description="Application version")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # ========== DATABASE ==========
    DATABASE_URL: str = Field(..., description="PostgreSQL connection URL")
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")
    DATABASE_POOL_SIZE: int = Field(default=20, description="DB pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=40, description="DB max overflow")
    DATABASE_TIMEOUT: int = Field(default=10, description="DB timeout in seconds")

    # ========== REDIS ==========
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    REDIS_TIMEOUT: int = Field(default=5, description="Redis timeout in seconds")
    REDIS_CACHE_DB: int = Field(default=1, description="Redis cache DB")
    REDIS_CELERY_DB: int = Field(default=2, description="Redis Celery DB")

    # ========== CELERY ==========
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/2", description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/3", description="Celery result backend"
    )
    CELERY_TIMEZONE: str = Field(default="Europe/Moscow", description="Celery timezone")
    CELERY_TASK_TIME_LIMIT: int = Field(default=3600, description="Task time limit (1 hour)")
    CELERY_TASK_SOFT_TIME_LIMIT: int = Field(default=3000, description="Task soft time limit")
    CELERY_RESULT_EXPIRES: int = Field(default=86400, description="Result expiration (24h)")
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = Field(default=4, description="Worker prefetch")
    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = Field(default=1000, description="Max tasks per child")
    REDIS_POOL_SIZE: int = Field(default=50, description="Redis pool size")

    # ========== SECURITY ==========
    SECRET_KEY: str = Field(..., description="Secret key for sessions")
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token expiration"
    )

    # ========== ADMIN PANEL ==========
    ADMIN_SECRET_KEY: str = Field(..., description="Admin secret key")
    ADMIN_USERNAME: str = Field(default="admin", description="Admin username")
    ADMIN_PASSWORD: str = Field(..., description="Admin password")
    ADMIN_PORT: int = Field(default=8001, description="Admin port")

    # ========== TELEGRAM BOT ==========
    BOT_TOKEN: str = Field(..., description="Telegram bot token")
    BOT_USERNAME: str = Field(default="", description="Telegram bot username")

    # ========== AI SERVICES ==========
    OPENROUTER_API_KEY: Optional[str] = Field(
        default=None, description="OpenRouter API key"
    )
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")

    # ========== CORS ==========
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:8000",
        description="CORS origins (comma-separated)",
    )

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ========== RATE LIMITING ==========
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60, description="Rate limit per minute"
    )

    # ========== MONITORING ==========
    PROMETHEUS_ENABLED: bool = Field(default=True, description="Enable Prometheus")
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN")
    SENTRY_ENVIRONMENT: str = Field(default="production", description="Sentry env")

    # ========== FEATURE FLAGS ==========
    FEATURE_NEW_UI: bool = Field(default=True, description="New UI feature flag")
    FEATURE_ANALYTICS: bool = Field(
        default=True, description="Analytics feature flag"
    )

    # ========== FILE UPLOAD ==========
    MAX_FILE_SIZE: int = Field(default=10485760, description="Max file size (10MB)")
    UPLOAD_PATH: str = Field(default="./uploads", description="Upload directory")

    # ========== LOGGING ==========
    LOG_FORMAT: str = Field(default="json", description="Log format (json/text)")
    LOG_FILE: str = Field(default="./logs/app.log", description="Log file path")
    LOG_MAX_BYTES: int = Field(default=10485760, description="Max log file size")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Log backup count")

    # ========== PERFORMANCE ==========
    WORKERS_COUNT: int = Field(default=4, description="Uvicorn workers count")
    MAX_REQUESTS: int = Field(default=1000, description="Max requests per worker")
    MAX_REQUESTS_JITTER: int = Field(default=100, description="Request jitter")
    REQUEST_TIMEOUT: int = Field(default=30, description="Request timeout")

    # ========== NOTIFICATIONS ==========
    ADMIN_CHAT_ID: Optional[str] = Field(
        default=None, description="Admin Telegram chat ID"
    )
    NOTIFICATION_CHAT_ID: Optional[str] = Field(
        default=None, description="Notification chat ID"
    )

    # ========== PROPERTIES ==========

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENV.lower() in ("development", "dev")

    @property
    def is_testing(self) -> bool:
        """Check if running in test mode"""
        return self.ENV.lower() in ("testing", "test")

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def model_dump_safe(self) -> dict:
        """
        Dump settings without sensitive information
        """
        data = self.model_dump()
        sensitive_fields = [
            "SECRET_KEY",
            "JWT_SECRET_KEY",
            "ADMIN_SECRET_KEY",
            "ADMIN_PASSWORD",
            "DATABASE_URL",
            "BOT_TOKEN",
            "OPENROUTER_API_KEY",
            "OPENAI_API_KEY",
            "SENTRY_DSN",
        ]
        for field in sensitive_fields:
            if field in data:
                data[field] = "***HIDDEN***"
        return data


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()

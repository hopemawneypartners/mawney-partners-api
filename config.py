"""
Configuration for Mawney Partners API
Security settings and environment variables
"""
import os
from pathlib import Path
from typing import Optional

# Try to use pydantic-settings if available, otherwise fall back to simple os.getenv
try:
    from pydantic_settings import BaseSettings
    USE_PYDANTIC = True
except ImportError:
    USE_PYDANTIC = False
    # Simple settings class without pydantic
    class BaseSettings:
        def __init__(self):
            pass

class Settings(BaseSettings if USE_PYDANTIC else object):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "Mawney Partners API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", os.urandom(32).hex())
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    # Fallback to SQLite for development if no PostgreSQL
    USE_SQLITE: bool = os.getenv("USE_SQLITE", "False").lower() == "true"
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "mawney_api.db")
    
    # Redis (for rate limiting and token blacklist)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", os.urandom(32).hex())
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "900"))  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "604800"))  # 7 days
    
    # Encryption
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", os.urandom(32).hex())
    # For production, generate a proper key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    RATE_LIMIT_AUTH_ATTEMPTS: int = int(os.getenv("RATE_LIMIT_AUTH_ATTEMPTS", "5"))
    
    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Security
    ALLOWED_IPS: Optional[list] = os.getenv("ALLOWED_IPS", "").split(",") if os.getenv("ALLOWED_IPS") else None
    REQUIRE_HTTPS: bool = os.getenv("REQUIRE_HTTPS", "True").lower() == "true"
    
    # Sentry (Error Tracking)
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = os.getenv("SENTRY_ENVIRONMENT", "production")
    
    # Base URL
    BASE_URL: str = os.getenv("BASE_URL", "https://mawney-daily-news-api.onrender.com")
    
    # GDPR
    AUDIT_LOG_RETENTION_DAYS: int = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "2555"))  # 7 years
    DATA_DELETION_RETENTION_DAYS: int = int(os.getenv("DATA_DELETION_RETENTION_DAYS", "30"))  # 30 days soft delete
    
    # Security Bot
    SECURITY_BOT_ENABLED: bool = os.getenv("SECURITY_BOT_ENABLED", "True").lower() == "true"
    SECURITY_ALERT_EMAIL: Optional[str] = os.getenv("SECURITY_ALERT_EMAIL")
    SECURITY_ALERT_SMS: Optional[str] = os.getenv("SECURITY_ALERT_SMS")
    
    # MFA
    MFA_ISSUER_NAME: str = os.getenv("MFA_ISSUER_NAME", "Mawney Partners")
    
    if USE_PYDANTIC:
        class Config:
            env_file = ".env"
            case_sensitive = True

# Global settings instance
if USE_PYDANTIC:
    settings = Settings()
else:
    # Simple settings without pydantic (fallback for Python 3.13 compatibility)
    import os
    settings = type('Settings', (), {
        'APP_NAME': os.getenv("APP_NAME", "Mawney Partners API"),
        'DEBUG': os.getenv("DEBUG", "False").lower() == "true",
        'SECRET_KEY': os.getenv("SECRET_KEY", os.urandom(32).hex()),
        'DATABASE_URL': os.getenv("DATABASE_URL"),
        'USE_SQLITE': os.getenv("USE_SQLITE", "False").lower() == "true",
        'SQLITE_PATH': os.getenv("SQLITE_PATH", "mawney_api.db"),
        'REDIS_URL': os.getenv("REDIS_URL"),
        'REDIS_HOST': os.getenv("REDIS_HOST", "localhost"),
        'REDIS_PORT': int(os.getenv("REDIS_PORT", "6379")),
        'REDIS_DB': int(os.getenv("REDIS_DB", "0")),
        'REDIS_PASSWORD': os.getenv("REDIS_PASSWORD"),
        'JWT_SECRET_KEY': os.getenv("JWT_SECRET_KEY", os.urandom(32).hex()),
        'JWT_ALGORITHM': "HS256",
        'JWT_ACCESS_TOKEN_EXPIRES': int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "900")),
        'JWT_REFRESH_TOKEN_EXPIRES': int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "604800")),
        'ENCRYPTION_KEY': os.getenv("ENCRYPTION_KEY", os.urandom(32).hex()),
        'RATE_LIMIT_ENABLED': os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true",
        'RATE_LIMIT_PER_MINUTE': int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")),
        'RATE_LIMIT_PER_HOUR': int(os.getenv("RATE_LIMIT_PER_HOUR", "1000")),
        'RATE_LIMIT_AUTH_ATTEMPTS': int(os.getenv("RATE_LIMIT_AUTH_ATTEMPTS", "5")),
        'CORS_ORIGINS': os.getenv("CORS_ORIGINS", "*").split(","),
        'ALLOWED_IPS': os.getenv("ALLOWED_IPS", "").split(",") if os.getenv("ALLOWED_IPS") else None,
        'REQUIRE_HTTPS': os.getenv("REQUIRE_HTTPS", "True").lower() == "true",
        'SENTRY_DSN': os.getenv("SENTRY_DSN"),
        'SENTRY_ENVIRONMENT': os.getenv("SENTRY_ENVIRONMENT", "production"),
        'BASE_URL': os.getenv("BASE_URL", "https://mawney-daily-news-api.onrender.com"),
        'AUDIT_LOG_RETENTION_DAYS': int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "2555")),
        'DATA_DELETION_RETENTION_DAYS': int(os.getenv("DATA_DELETION_RETENTION_DAYS", "30")),
        'SECURITY_BOT_ENABLED': os.getenv("SECURITY_BOT_ENABLED", "True").lower() == "true",
        'SECURITY_ALERT_EMAIL': os.getenv("SECURITY_ALERT_EMAIL"),
        'SECURITY_ALERT_SMS': os.getenv("SECURITY_ALERT_SMS"),
        'MFA_ISSUER_NAME': os.getenv("MFA_ISSUER_NAME", "Mawney Partners"),
    })()

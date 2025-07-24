"""
Конфигурация для производственного окружения
"""
import os
from typing import Optional

class ProductionConfig:
    """Конфигурация для продакшн сервера"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://username:password@localhost:5432/bot_business_card"
    )
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")
    
    # File Storage
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local или cloud
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/var/www/bot_business_card/uploads")
    
    # Cloud Storage (если используется)
    CLOUD_STORAGE_BUCKET: Optional[str] = os.getenv("CLOUD_STORAGE_BUCKET")
    CLOUD_STORAGE_REGION: Optional[str] = os.getenv("CLOUD_STORAGE_REGION")
    CLOUD_STORAGE_ACCESS_KEY: Optional[str] = os.getenv("CLOUD_STORAGE_ACCESS_KEY")
    CLOUD_STORAGE_SECRET_KEY: Optional[str] = os.getenv("CLOUD_STORAGE_SECRET_KEY")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "/var/www/bot_business_card/logs/app.log")
    
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    BASE_URL: str = os.getenv("BASE_URL", "https://localhost:8001")
    
    @classmethod
    def validate(cls) -> bool:
        """Проверяет, что все необходимые переменные заданы"""
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "SECRET_KEY",
            "DATABASE_URL"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var, None):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Создаем экземпляр конфигурации
config = ProductionConfig()

def get_production_config() -> ProductionConfig:
    """Возвращает конфигурацию продакшна"""
    config.validate()
    return config
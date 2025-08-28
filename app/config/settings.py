import os
from dotenv import load_dotenv
from typing import Dict, Any

# Загружаем переменные окружения
load_dotenv()

class Settings:
    """Настройки приложения"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "")
    PORTFOLIO_CHANNEL_ID: str = os.getenv("PORTFOLIO_CHANNEL_ID", "")  # ID канала для портфолио
    
    # OpenAI/OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "anthropic/claude-3.5-sonnet")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Database
    # Определяем путь к БД в зависимости от окружения
    if os.path.exists("/var/www/bot_business_card/data/bot.db"):
        # Продакшен сервер
        DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:////var/www/bot_business_card/data/bot.db")
    else:
        # Локальная разработка
        DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/bot.db")
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"
    
    # Admin Panel
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "default_secret_key_change_me")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")
    ADMIN_PORT: int = int(os.getenv("ADMIN_PORT", "8000"))
    
    # File Upload
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    UPLOAD_PATH: str = os.getenv("UPLOAD_PATH", "./uploads")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/bot.log")
    
    # Notifications
    NOTIFICATION_CHAT_ID: str = os.getenv("NOTIFICATION_CHAT_ID", "")
    ADMIN_CHAT_ID: str = os.getenv("ADMIN_CHAT_ID", os.getenv("NOTIFICATION_CHAT_ID", ""))
    
    # Admin IDs
    ADMIN_IDS: list = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
    
    # Pricing
    BASE_HOURLY_RATE: int = int(os.getenv("BASE_HOURLY_RATE", "1000"))
    URGENT_MULTIPLIER: float = float(os.getenv("URGENT_MULTIPLIER", "1.3"))
    
    # Complexity multipliers
    COMPLEXITY_MULTIPLIERS: Dict[str, float] = {
        "simple": 1.0,
        "medium": 1.5,
        "complex": 2.5,
        "premium": 4.0
    }
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Speech Recognition
    SPEECH_API_KEY: str = os.getenv("SPEECH_API_KEY", "")
    
    # Consultant AI Settings
    CONSULTANT_SYSTEM_PROMPT: str = os.getenv(
        "CONSULTANT_SYSTEM_PROMPT", 
        "Ты - эксперт-консультант по разработке Telegram-ботов и чат-ботов. "
        "Помогай пользователям с вопросами по проектам, технологиям, архитектуре и лучшим практикам. "
        "Отвечай профессионально, но дружелюбно. Давай конкретные рекомендации."
    )
    CONSULTANT_MAX_TOKENS: int = int(os.getenv("CONSULTANT_MAX_TOKENS", "1000"))
    CONSULTANT_TEMPERATURE: float = float(os.getenv("CONSULTANT_TEMPERATURE", "0.7"))
    
    # Avito API Settings
    AVITO_CLIENT_ID: str = os.getenv("AVITO_CLIENT_ID", "")
    AVITO_CLIENT_SECRET: str = os.getenv("AVITO_CLIENT_SECRET", "")
    AVITO_USER_ID: str = os.getenv("AVITO_USER_ID", "")
    
    # Domain for webhooks
    DOMAIN: str = os.getenv("DOMAIN", "147.45.215.199:8001")
    
    # Paths
    UPLOADS_DIR: str = "uploads"
    DOCUMENTS_DIR: str = f"{UPLOADS_DIR}/documents"
    IMAGES_DIR: str = f"{UPLOADS_DIR}/images"
    AUDIO_DIR: str = f"{UPLOADS_DIR}/audio"
    TEMP_DIR: str = f"{UPLOADS_DIR}/temp"
    
    # Bot persistence
    bot_persistence_file: str = "data/bot_persistence.pkl"
    
    # Additional properties that might be needed
    bot_token: str = BOT_TOKEN
    server_host: str = "0.0.0.0"
    server_port: int = ADMIN_PORT
    
    # Создание необходимых папок
    @classmethod
    def create_directories(cls):
        """Создает необходимые директории"""
        directories = [
            cls.UPLOADS_DIR,
            cls.DOCUMENTS_DIR,
            cls.IMAGES_DIR,
            cls.AUDIO_DIR,
            cls.TEMP_DIR,
            "logs",
            "data"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    # Валидация настроек
    @classmethod
    def validate(cls) -> bool:
        """Проверяет корректность основных настроек"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен")
        
        if not cls.OPENROUTER_API_KEY and not cls.OPENAI_API_KEY:
            print("ПРЕДУПРЕЖДЕНИЕ: OPENROUTER_API_KEY или OPENAI_API_KEY не установлен. AI-функции могут не работать.")

        return True

# Создаем глобальный экземпляр настроек
settings = Settings()

# Выполняем проверки и создаем директории при импорте модуля
try:
    settings.validate()
    settings.create_directories()
except ValueError as e:
    import sys
    print(f"❌ Ошибка конфигурации: {e}")
    sys.exit(1)

def get_settings() -> Settings:
    """Возвращает глобальный экземпляр настроек."""
    return settings
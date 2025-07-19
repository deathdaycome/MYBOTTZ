import logging
import os
from datetime import datetime
from .settings import settings

def setup_logging():
    """Настройка логирования для проекта"""
    
    # Создаем папку для логов если её нет
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Настройка форматирования
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настройка основного логгера
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Очищаем существующие хендлеры
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Хендлер для файла
    file_handler = logging.FileHandler(
        settings.LOG_FILE, 
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG)
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Добавляем хендлеры
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Настройка логгеров для внешних библиотек
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return logger

# Создаем основной логгер
bot_logger = setup_logging()

def get_logger(name: str) -> logging.Logger:
    """Получить логгер для модуля"""
    return logging.getLogger(name)

def log_user_action(user_id: int, action: str, details: str = ""):
    """Логирование действий пользователей"""
    logger = get_logger("user_actions")
    logger.info(f"User {user_id}: {action} - {details}")

def log_error(error: Exception, context: str = ""):
    """Логирование ошибок"""
    logger = get_logger("errors")
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)

def log_api_call(service: str, method: str, success: bool, response_time: float = 0):
    """Логирование API вызовов"""
    logger = get_logger("api_calls")
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"API Call - {service}.{method}: {status} ({response_time:.2f}s)")

def log_consultant_query(user_id: int, query: str, response_length: int):
    """Логирование запросов к консультанту"""
    logger = get_logger("consultant")
    logger.info(f"Consultant query from user {user_id}: {query[:100]}... (response: {response_length} chars)")
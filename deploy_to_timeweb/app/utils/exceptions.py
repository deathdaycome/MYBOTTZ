"""
Кастомные исключения для бота
"""

class BotException(Exception):
    """Базовое исключение для бота"""
    
    def __init__(self, message: str, error_code: str = None, user_message: str = None):
        self.message = message
        self.error_code = error_code
        self.user_message = user_message or "Произошла ошибка. Попробуйте еще раз."
        super().__init__(self.message)

class UserNotFoundError(BotException):
    """Пользователь не найден"""
    
    def __init__(self, user_id: int):
        super().__init__(
            f"Пользователь с ID {user_id} не найден",
            "USER_NOT_FOUND",
            "Пользователь не найден в системе"
        )

class ProjectNotFoundError(BotException):
    """Проект не найден"""
    
    def __init__(self, project_id: int):
        super().__init__(
            f"Проект с ID {project_id} не найден",
            "PROJECT_NOT_FOUND",
            "Проект не найден"
        )

class InvalidProjectDataError(BotException):
    """Некорректные данные проекта"""
    
    def __init__(self, field: str, reason: str = None):
        message = f"Некорректные данные в поле '{field}'"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message,
            "INVALID_PROJECT_DATA",
            f"Некорректные данные в поле '{field}'"
        )

class FileProcessingError(BotException):
    """Ошибка обработки файла"""
    
    def __init__(self, filename: str, reason: str = None):
        message = f"Ошибка обработки файла '{filename}'"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message,
            "FILE_PROCESSING_ERROR",
            "Не удалось обработать файл. Проверьте формат и размер."
        )

class VoiceProcessingError(BotException):
    """Ошибка обработки голосового сообщения"""
    
    def __init__(self, reason: str = None):
        message = "Ошибка обработки голосового сообщения"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message,
            "VOICE_PROCESSING_ERROR",
            "Не удалось распознать голосовое сообщение. Попробуйте еще раз."
        )

class AIServiceError(BotException):
    """Ошибка AI сервиса"""
    
    def __init__(self, service: str, reason: str = None):
        message = f"Ошибка AI сервиса '{service}'"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message,
            "AI_SERVICE_ERROR",
            "Временная ошибка AI сервиса. Попробуйте позже."
        )

class DatabaseError(BotException):
    """Ошибка базы данных"""
    
    def __init__(self, operation: str, reason: str = None):
        message = f"Ошибка базы данных при операции '{operation}'"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message,
            "DATABASE_ERROR",
            "Временная ошибка сервера. Попробуйте позже."
        )

class ValidationError(BotException):
    """Ошибка валидации данных"""
    
    def __init__(self, field: str, reason: str):
        super().__init__(
            f"Ошибка валидации поля '{field}': {reason}",
            "VALIDATION_ERROR",
            f"Некорректное значение в поле '{field}': {reason}"
        )

class RateLimitError(BotException):
    """Превышен лимит запросов"""
    
    def __init__(self, limit: int, period: str = "минуту"):
        super().__init__(
            f"Превышен лимит запросов: {limit} за {period}",
            "RATE_LIMIT_ERROR",
            f"Слишком много запросов. Максимум {limit} за {period}."
        )

class PermissionError(BotException):
    """Недостаточно прав доступа"""
    
    def __init__(self, required_permission: str):
        super().__init__(
            f"Недостаточно прав для выполнения операции: {required_permission}",
            "PERMISSION_ERROR",
            "У вас нет прав для выполнения этой операции"
        )

class SessionNotFoundError(BotException):
    """Сессия не найдена"""
    
    def __init__(self, session_id: str):
        super().__init__(
            f"Сессия {session_id} не найдена",
            "SESSION_NOT_FOUND",
            "Сессия не найдена или истекла. Начните заново."
        )

class InvalidSessionStateError(BotException):
    """Некорректное состояние сессии"""
    
    def __init__(self, current_state: str, expected_state: str):
        super().__init__(
            f"Некорректное состояние сессии: {current_state}, ожидалось: {expected_state}",
            "INVALID_SESSION_STATE",
            "Некорректное состояние сессии. Начните заново."
        )

class ConfigurationError(BotException):
    """Ошибка конфигурации"""
    
    def __init__(self, setting: str, reason: str = None):
        message = f"Ошибка конфигурации '{setting}'"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message,
            "CONFIGURATION_ERROR",
            "Ошибка конфигурации сервиса. Обратитесь к администратору."
        )

class ExternalServiceError(BotException):
    """Ошибка внешнего сервиса"""
    
    def __init__(self, service: str, status_code: int = None, reason: str = None):
        message = f"Ошибка внешнего сервиса '{service}'"
        if status_code:
            message += f" (код {status_code})"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message,
            "EXTERNAL_SERVICE_ERROR",
            f"Временная ошибка сервиса {service}. Попробуйте позже."
        )

class TimeoutError(BotException):
    """Ошибка тайм-аута"""
    
    def __init__(self, operation: str, timeout: int):
        super().__init__(
            f"Тайм-аут операции '{operation}' ({timeout}s)",
            "TIMEOUT_ERROR",
            "Операция заняла слишком много времени. Попробуйте позже."
        )

class FileTooLargeError(BotException):
    """Файл слишком большой"""
    
    def __init__(self, size: int, max_size: int):
        super().__init__(
            f"Файл слишком большой: {size} bytes, максимум: {max_size} bytes",
            "FILE_TOO_LARGE",
            f"Файл слишком большой. Максимальный размер: {max_size // (1024*1024)} МБ"
        )

class UnsupportedFileTypeError(BotException):
    """Неподдерживаемый тип файла"""
    
    def __init__(self, file_type: str, supported_types: list):
        super().__init__(
            f"Неподдерживаемый тип файла: {file_type}",
            "UNSUPPORTED_FILE_TYPE",
            f"Неподдерживаемый формат файла. Поддерживаются: {', '.join(supported_types)}"
        )

class BusinessLogicError(BotException):
    """Ошибка бизнес-логики"""
    
    def __init__(self, message: str, user_message: str = None):
        super().__init__(
            message,
            "BUSINESS_LOGIC_ERROR",
            user_message or message
        )

class InsufficientDataError(BotException):
    """Недостаточно данных для операции"""
    
    def __init__(self, required_data: str):
        super().__init__(
            f"Недостаточно данных для операции: требуется {required_data}",
            "INSUFFICIENT_DATA",
            f"Для продолжения необходимо: {required_data}"
        )

class DuplicateDataError(BotException):
    """Дублирование данных"""
    
    def __init__(self, field: str, value: str):
        super().__init__(
            f"Дублирование данных в поле '{field}': {value}",
            "DUPLICATE_DATA",
            f"Значение '{value}' уже существует"
        )

class ServiceUnavailableError(BotException):
    """Сервис недоступен"""
    
    def __init__(self, service: str):
        super().__init__(
            f"Сервис '{service}' недоступен",
            "SERVICE_UNAVAILABLE",
            f"Сервис {service} временно недоступен. Попробуйте позже."
        )

class QuotaExceededError(BotException):
    """Превышена квота"""
    
    def __init__(self, resource: str, limit: int):
        super().__init__(
            f"Превышена квота для ресурса '{resource}': {limit}",
            "QUOTA_EXCEEDED",
            f"Превышен лимит для {resource}: {limit}"
        )

# Функции для обработки исключений

def handle_bot_exception(exception: BotException, update=None, context=None):
    """Обработка исключений бота"""
    from ..config.logging import get_logger
    
    logger = get_logger(__name__)
    logger.error(f"BotException [{exception.error_code}]: {exception.message}")
    
    return exception.user_message

def handle_unknown_exception(exception: Exception, update=None, context=None):
    """Обработка неизвестных исключений"""
    from ..config.logging import get_logger, log_error
    
    logger = get_logger(__name__)
    log_error(exception, "Unknown exception")
    
    return "Произошла неожиданная ошибка. Мы уже работаем над её устранением."

def create_error_response(exception: Exception, include_details: bool = False):
    """Создание ответа об ошибке"""
    if isinstance(exception, BotException):
        response = {
            "success": False,
            "error_code": exception.error_code,
            "user_message": exception.user_message
        }
        
        if include_details:
            response["details"] = exception.message
    else:
        response = {
            "success": False,
            "error_code": "UNKNOWN_ERROR",
            "user_message": "Произошла неожиданная ошибка"
        }
        
        if include_details:
            response["details"] = str(exception)
    
    return response
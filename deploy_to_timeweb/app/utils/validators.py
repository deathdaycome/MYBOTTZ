import re
from typing import Union, List, Dict, Any, Optional
from datetime import datetime

class ValidationError(Exception):
    """Исключение для ошибок валидации"""
    pass

class Validator:
    """Базовый класс валидатора"""
    
    def __init__(self, error_message: str = "Некорректное значение"):
        self.error_message = error_message
    
    def __call__(self, value: Any) -> bool:
        """Основной метод валидации"""
        raise NotImplementedError
    
    def validate_or_raise(self, value: Any) -> Any:
        """Валидация с выбросом исключения при ошибке"""
        if not self(value):
            raise ValidationError(self.error_message)
        return value

class EmailValidator(Validator):
    """Валидатор email адресов"""
    
    def __init__(self):
        super().__init__("Некорректный email адрес")
        self.pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        return bool(self.pattern.match(value.strip()))

class PhoneValidator(Validator):
    """Валидатор номеров телефонов"""
    
    def __init__(self):
        super().__init__("Некорректный номер телефона")
        # Российские номера в формате +7XXXXXXXXXX
        self.pattern = re.compile(r'^\+7\d{10}$')
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        # Очищаем номер
        clean_phone = re.sub(r'[^\d+]', '', value)
        
        # Заменяем 8 на +7
        if clean_phone.startswith('8'):
            clean_phone = '+7' + clean_phone[1:]
        elif clean_phone.startswith('7'):
            clean_phone = '+' + clean_phone
        
        return bool(self.pattern.match(clean_phone))

class LengthValidator(Validator):
    """Валидатор длины строки"""
    
    def __init__(self, min_length: int = 0, max_length: int = None):
        self.min_length = min_length
        self.max_length = max_length
        
        if max_length:
            message = f"Длина должна быть от {min_length} до {max_length} символов"
        else:
            message = f"Минимальная длина: {min_length} символов"
        
        super().__init__(message)
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        length = len(value.strip())
        
        if length < self.min_length:
            return False
        
        if self.max_length and length > self.max_length:
            return False
        
        return True

class NumberValidator(Validator):
    """Валидатор числовых значений"""
    
    def __init__(self, min_value: Union[int, float] = None, max_value: Union[int, float] = None):
        self.min_value = min_value
        self.max_value = max_value
        
        message_parts = []
        if min_value is not None:
            message_parts.append(f"минимум {min_value}")
        if max_value is not None:
            message_parts.append(f"максимум {max_value}")
        
        message = f"Значение должно быть: {', '.join(message_parts)}" if message_parts else "Некорректное число"
        super().__init__(message)
    
    def __call__(self, value: Union[int, float, str]) -> bool:
        try:
            num_value = float(value) if isinstance(value, str) else value
            
            if self.min_value is not None and num_value < self.min_value:
                return False
            
            if self.max_value is not None and num_value > self.max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False

class UrlValidator(Validator):
    """Валидатор URL адресов"""
    
    def __init__(self):
        super().__init__("Некорректный URL адрес")
        self.pattern = re.compile(
            r'^https?://'  # http:// или https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # домен
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # порт
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        return bool(self.pattern.match(value.strip()))

class TelegramUsernameValidator(Validator):
    """Валидатор Telegram username"""
    
    def __init__(self):
        super().__init__("Некорректный Telegram username")
        self.pattern = re.compile(r'^@?[a-zA-Z0-9_]{5,32}$')
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        # Убираем @ если есть
        clean_username = value.strip().lstrip('@')
        return bool(self.pattern.match(clean_username))

class ProjectTitleValidator(Validator):
    """Валидатор названия проекта"""
    
    def __init__(self):
        super().__init__("Название проекта должно быть от 3 до 100 символов")
        self.length_validator = LengthValidator(3, 100)
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        title = value.strip()
        
        # Проверяем длину
        if not self.length_validator(title):
            return False
        
        # Проверяем что не только пробелы и знаки препинания
        if not re.search(r'[a-zA-Zа-яА-Я0-9]', title):
            return False
        
        return True

class BudgetValidator(Validator):
    """Валидатор бюджета проекта"""
    
    def __init__(self):
        super().__init__("Бюджет должен быть от 1,000 до 10,000,000 рублей")
        self.number_validator = NumberValidator(1000, 10000000)
    
    def __call__(self, value: Union[int, float, str]) -> bool:
        return self.number_validator(value)

class ComplexityValidator(Validator):
    """Валидатор сложности проекта"""
    
    def __init__(self):
        super().__init__("Сложность должна быть: simple, medium, complex или premium")
        self.valid_values = ['simple', 'medium', 'complex', 'premium']
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        return value.lower() in self.valid_values

class PlatformValidator(Validator):
    """Валидатор платформ"""
    
    def __init__(self):
        super().__init__("Неподдерживаемая платформа")
        self.valid_platforms = [
            'telegram', 'whatsapp', 'web', 'vk', 'discord', 
            'facebook', 'instagram', 'viber', 'slack'
        ]
    
    def __call__(self, value: Union[str, List[str]]) -> bool:
        if isinstance(value, str):
            return value.lower() in self.valid_platforms
        elif isinstance(value, list):
            return all(isinstance(platform, str) and platform.lower() in self.valid_platforms 
                      for platform in value)
        return False

class FileTypeValidator(Validator):
    """Валидатор типов файлов"""
    
    def __init__(self, allowed_extensions: List[str]):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
        super().__init__(f"Разрешенные форматы: {', '.join(self.allowed_extensions)}")
    
    def __call__(self, filename: str) -> bool:
        if not isinstance(filename, str):
            return False
        
        extension = filename.split('.')[-1].lower() if '.' in filename else ''
        return f'.{extension}' in self.allowed_extensions or extension in self.allowed_extensions

class FileSizeValidator(Validator):
    """Валидатор размера файлов"""
    
    def __init__(self, max_size_mb: float):
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        super().__init__(f"Максимальный размер файла: {max_size_mb} МБ")
    
    def __call__(self, file_size: int) -> bool:
        return isinstance(file_size, int) and 0 < file_size <= self.max_size_bytes

class DateValidator(Validator):
    """Валидатор дат"""
    
    def __init__(self, min_date: datetime = None, max_date: datetime = None):
        self.min_date = min_date
        self.max_date = max_date
        super().__init__("Некорректная дата")
    
    def __call__(self, value: Union[datetime, str]) -> bool:
        try:
            if isinstance(value, str):
                # Пробуем разные форматы
                formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']
                date_obj = None
                
                for fmt in formats:
                    try:
                        date_obj = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                
                if date_obj is None:
                    return False
                
                value = date_obj
            
            if not isinstance(value, datetime):
                return False
            
            if self.min_date and value < self.min_date:
                return False
            
            if self.max_date and value > self.max_date:
                return False
            
            return True
        except (ValueError, TypeError):
            return False

class JSONValidator(Validator):
    """Валидатор JSON данных"""
    
    def __init__(self):
        super().__init__("Некорректный JSON формат")
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        try:
            import json
            json.loads(value)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

class ListValidator(Validator):
    """Валидатор списков"""
    
    def __init__(self, item_validator: Validator = None, min_items: int = 0, max_items: int = None):
        self.item_validator = item_validator
        self.min_items = min_items
        self.max_items = max_items
        super().__init__("Некорректный список")
    
    def __call__(self, value: List[Any]) -> bool:
        if not isinstance(value, list):
            return False
        
        if len(value) < self.min_items:
            return False
        
        if self.max_items and len(value) > self.max_items:
            return False
        
        if self.item_validator:
            return all(self.item_validator(item) for item in value)
        
        return True

class CompositeValidator(Validator):
    """Композитный валидатор (объединяет несколько валидаторов)"""
    
    def __init__(self, validators: List[Validator], mode: str = 'all'):
        self.validators = validators
        self.mode = mode  # 'all' или 'any'
        super().__init__("Ошибка валидации")
    
    def __call__(self, value: Any) -> bool:
        if self.mode == 'all':
            return all(validator(value) for validator in self.validators)
        else:  # mode == 'any'
            return any(validator(value) for validator in self.validators)

class ColorValidator(Validator):
    """Валидатор цветов (HEX)"""
    
    def __init__(self):
        super().__init__("Некорректный цвет (используйте HEX формат, например #FF0000)")
        self.pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        return bool(self.pattern.match(value.strip()))

class SlugValidator(Validator):
    """Валидатор slug (для URL)"""
    
    def __init__(self):
        super().__init__("Slug может содержать только буквы, цифры и дефисы")
        self.pattern = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        return bool(self.pattern.match(value.strip().lower()))

class PasswordValidator(Validator):
    """Валидатор паролей"""
    
    def __init__(self, min_length: int = 8, require_uppercase: bool = True, 
                 require_lowercase: bool = True, require_digit: bool = True, 
                 require_special: bool = True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        
        requirements = [f"минимум {min_length} символов"]
        if require_uppercase:
            requirements.append("заглавные буквы")
        if require_lowercase:
            requirements.append("строчные буквы")
        if require_digit:
            requirements.append("цифры")
        if require_special:
            requirements.append("специальные символы")
        
        super().__init__(f"Пароль должен содержать: {', '.join(requirements)}")
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str) or len(value) < self.min_length:
            return False
        
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            return False
        
        if self.require_lowercase and not re.search(r'[a-z]', value):
            return False
        
        if self.require_digit and not re.search(r'\d', value):
            return False
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            return False
        
        return True

class IPValidator(Validator):
    """Валидатор IP адресов"""
    
    def __init__(self, version: str = 'both'):  # 'v4', 'v6', 'both'
        self.version = version
        super().__init__("Некорректный IP адрес")
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        import socket
        
        if self.version in ['v4', 'both']:
            try:
                socket.inet_pton(socket.AF_INET, value)
                return True
            except socket.error:
                pass
        
        if self.version in ['v6', 'both']:
            try:
                socket.inet_pton(socket.AF_INET6, value)
                return True
            except socket.error:
                pass
        
        return False

class PortValidator(Validator):
    """Валидатор номеров портов"""
    
    def __init__(self):
        super().__init__("Порт должен быть от 1 до 65535")
        self.number_validator = NumberValidator(1, 65535)
    
    def __call__(self, value: Union[int, str]) -> bool:
        try:
            port = int(value)
            return self.number_validator(port)
        except (ValueError, TypeError):
            return False

class CronValidator(Validator):
    """Валидатор CRON выражений"""
    
    def __init__(self):
        super().__init__("Некорректное CRON выражение")
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        parts = value.strip().split()
        if len(parts) != 5:
            return False
        
        # Простая проверка каждой части
        patterns = [
            r'^(\*|[0-5]?\d(,[0-5]?\d)*|[0-5]?\d-[0-5]?\d)$',  # минуты (0-59)
            r'^(\*|[01]?\d|2[0-3](,[01]?\d|2[0-3])*|[01]?\d-[01]?\d|2[0-3])$',  # часы (0-23)
            r'^(\*|[0-2]?\d|3[01](,[0-2]?\d|3[01])*|[0-2]?\d-[0-2]?\d|3[01])$',  # дни (1-31)
            r'^(\*|[0]?\d|1[0-2](,[0]?\d|1[0-2])*|[0]?\d-[0]?\d|1[0-2])$',  # месяцы (1-12)
            r'^(\*|[0-6](,[0-6])*|[0-6]-[0-6])$'  # дни недели (0-6)
        ]
        
        for i, part in enumerate(parts):
            if not re.match(patterns[i], part):
                return False
        
        return True

class TokenValidator(Validator):
    """Валидатор токенов (API ключи и т.п.)"""
    
    def __init__(self, min_length: int = 10, max_length: int = 256):
        self.min_length = min_length
        self.max_length = max_length
        super().__init__(f"Токен должен быть от {min_length} до {max_length} символов")
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        token = value.strip()
        if len(token) < self.min_length or len(token) > self.max_length:
            return False
        
        # Проверяем что токен содержит только разрешенные символы
        if not re.match(r'^[a-zA-Z0-9._-]+$', token):
            return False
        
        return True

class TelegramBotTokenValidator(Validator):
    """Валидатор токенов Telegram ботов"""
    
    def __init__(self):
        super().__init__("Некорректный токен Telegram бота")
        self.pattern = re.compile(r'^\d{8,10}:[a-zA-Z0-9_-]{35}$')
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        return bool(self.pattern.match(value.strip()))

class SQLInjectionValidator(Validator):
    """Валидатор для защиты от SQL инъекций"""
    
    def __init__(self):
        super().__init__("Недопустимые символы в запросе")
        self.dangerous_patterns = [
            r"('|(\\'))+.*(\\*)((;)|(\\)|)+",
            r"(((select|union|insert|update|delete|drop|create|alter|exec|execute)\s+)|(\s*;\s*))",
            r"(script|javascript|vbscript|onload|onerror|onclick)"
        ]
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return True  # Если не строка, то проверка не нужна
        
        value_lower = value.lower()
        for pattern in self.dangerous_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return False
        
        return True

class XSSValidator(Validator):
    """Валидатор для защиты от XSS атак"""
    
    def __init__(self):
        super().__init__("Недопустимые HTML теги или скрипты")
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'javascript:',
            r'on\w+\s*=',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>'
        ]
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return True
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                return False
        
        return True

# Предустановленные валидаторы
email_validator = EmailValidator()
phone_validator = PhoneValidator()
url_validator = UrlValidator()
telegram_username_validator = TelegramUsernameValidator()
project_title_validator = ProjectTitleValidator()
budget_validator = BudgetValidator()
complexity_validator = ComplexityValidator()
platform_validator = PlatformValidator()
color_validator = ColorValidator()
slug_validator = SlugValidator()
password_validator = PasswordValidator()
ip_validator = IPValidator()
port_validator = PortValidator()
cron_validator = CronValidator()
telegram_bot_token_validator = TelegramBotTokenValidator()
sql_injection_validator = SQLInjectionValidator()
xss_validator = XSSValidator()

# Валидаторы для файлов
document_file_validator = FileTypeValidator(['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'])
image_file_validator = FileTypeValidator(['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'])
audio_file_validator = FileTypeValidator(['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'])
video_file_validator = FileTypeValidator(['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'])
archive_file_validator = FileTypeValidator(['.zip', '.rar', '.7z', '.tar', '.gz'])

# Валидаторы размера файлов
tiny_file_validator = FileSizeValidator(1)     # 1 МБ
small_file_validator = FileSizeValidator(5)    # 5 МБ
medium_file_validator = FileSizeValidator(20)  # 20 МБ
large_file_validator = FileSizeValidator(100)  # 100 МБ
huge_file_validator = FileSizeValidator(500)   # 500 МБ

# Валидаторы длины текста
name_validator = LengthValidator(2, 50)
title_validator = LengthValidator(3, 200)
short_text_validator = LengthValidator(1, 100)
medium_text_validator = LengthValidator(1, 500)
long_text_validator = LengthValidator(1, 2000)
description_validator = LengthValidator(10, 1000)
content_validator = LengthValidator(1, 10000)

# Валидаторы чисел
age_validator = NumberValidator(0, 150)
rating_validator = NumberValidator(1, 5)
percentage_validator = NumberValidator(0, 100)
price_validator = NumberValidator(0, 999999999)

def validate_user_input(value: Any, validator: Validator) -> tuple[bool, str]:
    """Универсальная функция валидации с возвратом результата и сообщения об ошибке"""
    try:
        is_valid = validator(value)
        return is_valid, "" if is_valid else validator.error_message
    except Exception as e:
        return False, str(e)

def validate_project_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Валидация данных проекта"""
    errors = []
    
    # Проверяем обязательные поля
    required_fields = ['title', 'description']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Поле '{field}' обязательно для заполнения")
    
    # Валидируем название
    if 'title' in data:
        is_valid, error = validate_user_input(data['title'], project_title_validator)
        if not is_valid:
            errors.append(f"Название проекта: {error}")
    
    # Валидируем описание
    if 'description' in data:
        is_valid, error = validate_user_input(data['description'], description_validator)
        if not is_valid:
            errors.append(f"Описание проекта: {error}")
    
    # Валидируем бюджет
    if 'budget' in data and data['budget']:
        is_valid, error = validate_user_input(data['budget'], budget_validator)
        if not is_valid:
            errors.append(f"Бюджет: {error}")
    
    # Валидируем сложность
    if 'complexity' in data and data['complexity']:
        is_valid, error = validate_user_input(data['complexity'], complexity_validator)
        if not is_valid:
            errors.append(f"Сложность: {error}")
    
    # Валидируем платформы
    if 'platforms' in data and data['platforms']:
        is_valid, error = validate_user_input(data['platforms'], platform_validator)
        if not is_valid:
            errors.append(f"Платформы: {error}")
    
    return len(errors) == 0, errors

def validate_user_profile(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Валидация профиля пользователя"""
    errors = []
    
    # Валидируем email
    if 'email' in data and data['email']:
        is_valid, error = validate_user_input(data['email'], email_validator)
        if not is_valid:
            errors.append(f"Email: {error}")
    
    # Валидируем телефон
    if 'phone' in data and data['phone']:
        is_valid, error = validate_user_input(data['phone'], phone_validator)
        if not is_valid:
            errors.append(f"Телефон: {error}")
    
    # Валидируем имя
    if 'first_name' in data and data['first_name']:
        is_valid, error = validate_user_input(data['first_name'], name_validator)
        if not is_valid:
            errors.append(f"Имя: {error}")
    
    # Валидируем фамилию
    if 'last_name' in data and data['last_name']:
        is_valid, error = validate_user_input(data['last_name'], name_validator)
        if not is_valid:
            errors.append(f"Фамилия: {error}")
    
    # Валидируем username
    if 'username' in data and data['username']:
        is_valid, error = validate_user_input(data['username'], telegram_username_validator)
        if not is_valid:
            errors.append(f"Username: {error}")
    
    return len(errors) == 0, errors

def validate_settings_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Валидация настроек системы"""
    errors = []
    
    # Валидируем токен бота
    if 'bot_token' in data and data['bot_token']:
        is_valid, error = validate_user_input(data['bot_token'], telegram_bot_token_validator)
        if not is_valid:
            errors.append(f"Токен бота: {error}")
    
    # Валидируем API ключи
    for key_field in ['openai_api_key', 'openrouter_api_key']:
        if key_field in data and data[key_field]:
            is_valid, error = validate_user_input(data[key_field], TokenValidator())
            if not is_valid:
                errors.append(f"{key_field}: {error}")
    
    # Валидируем email для уведомлений
    if 'notification_email' in data and data['notification_email']:
        is_valid, error = validate_user_input(data['notification_email'], email_validator)
        if not is_valid:
            errors.append(f"Email для уведомлений: {error}")
    
    # Валидируем цвета
    color_fields = ['primary_color', 'secondary_color', 'accent_color']
    for color_field in color_fields:
        if color_field in data and data[color_field]:
            is_valid, error = validate_user_input(data[color_field], color_validator)
            if not is_valid:
                errors.append(f"{color_field}: {error}")
    
    # Валидируем числовые настройки
    numeric_settings = {
        'max_file_size': NumberValidator(1, 1000),  # МБ
        'session_timeout': NumberValidator(1, 1440),  # минуты
        'rate_limit': NumberValidator(1, 1000),  # запросов в минуту
        'max_tokens': NumberValidator(1, 4000),
        'temperature': NumberValidator(0, 2)
    }
    
    for field, validator in numeric_settings.items():
        if field in data and data[field] is not None:
            is_valid, error = validate_user_input(data[field], validator)
            if not is_valid:
                errors.append(f"{field}: {error}")
    
    return len(errors) == 0, errors

def validate_portfolio_item(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Валидация элемента портфолио"""
    errors = []
    
    # Обязательные поля
    required_fields = ['title', 'description', 'category']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Поле '{field}' обязательно для заполнения")
    
    # Валидируем название
    if 'title' in data:
        is_valid, error = validate_user_input(data['title'], title_validator)
        if not is_valid:
            errors.append(f"Название: {error}")
    
    # Валидируем описание
    if 'description' in data:
        is_valid, error = validate_user_input(data['description'], description_validator)
        if not is_valid:
            errors.append(f"Описание: {error}")
    
    # Валидируем категорию
    valid_categories = ['telegram_bot', 'whatsapp_bot', 'web_bot', 'integration', 'automation']
    if 'category' in data and data['category']:
        if data['category'] not in valid_categories:
            errors.append(f"Категория должна быть одной из: {', '.join(valid_categories)}")
    
    # Валидируем ссылки
    if 'demo_link' in data and data['demo_link']:
        is_valid, error = validate_user_input(data['demo_link'], url_validator)
        if not is_valid:
            errors.append(f"Ссылка на демо: {error}")
    
    if 'github_link' in data and data['github_link']:
        is_valid, error = validate_user_input(data['github_link'], url_validator)
        if not is_valid:
            errors.append(f"Ссылка на GitHub: {error}")
    
    # Валидируем уровень сложности
    if 'complexity_level' in data and data['complexity_level'] is not None:
        is_valid, error = validate_user_input(data['complexity_level'], NumberValidator(1, 10))
        if not is_valid:
            errors.append(f"Уровень сложности: {error}")
    
    # Валидируем время разработки
    if 'development_time' in data and data['development_time'] is not None:
        is_valid, error = validate_user_input(data['development_time'], NumberValidator(1, 365))
        if not is_valid:
            errors.append(f"Время разработки (дни): {error}")
    
    # Валидируем технологии
    if 'technologies' in data and data['technologies']:
        if isinstance(data['technologies'], list):
            for tech in data['technologies']:
                is_valid, error = validate_user_input(tech, LengthValidator(1, 50))
                if not is_valid:
                    errors.append(f"Технология '{tech}': {error}")
        else:
            errors.append("Технологии должны быть списком")
    
    return len(errors) == 0, errors

def validate_file_upload(filename: str, file_size: int, file_type: str) -> tuple[bool, List[str]]:
    """Валидация загружаемого файла"""
    errors = []
    
    # Проверяем имя файла
    if not filename:
        errors.append("Имя файла не указано")
        return False, errors
    
    # Проверяем на безопасность имени файла
    is_valid, error = validate_user_input(filename, FilenameValidator())
    if not is_valid:
        errors.append(f"Имя файла: {error}")
    
    # Определяем тип файла и соответствующие валидаторы
    file_validators = {
        'document': (document_file_validator, medium_file_validator),
        'image': (image_file_validator, small_file_validator),
        'audio': (audio_file_validator, large_file_validator),
        'video': (video_file_validator, huge_file_validator),
        'archive': (archive_file_validator, medium_file_validator)
    }
    
    if file_type in file_validators:
        type_validator, size_validator = file_validators[file_type]
        
        # Проверяем тип файла
        is_valid, error = validate_user_input(filename, type_validator)
        if not is_valid:
            errors.append(f"Тип файла: {error}")
        
        # Проверяем размер файла
        is_valid, error = validate_user_input(file_size, size_validator)
        if not is_valid:
            errors.append(f"Размер файла: {error}")
    else:
        errors.append(f"Неподдерживаемый тип файла: {file_type}")
    
    return len(errors) == 0, errors

def validate_ai_settings(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Валидация настроек AI"""
    errors = []
    
    # Валидируем модель
    valid_models = [
        'gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo',
        'claude-3-sonnet', 'claude-3-opus', 'claude-3-haiku',
        'llama-3-70b', 'mistral-7b'
    ]
    
    if 'model' in data and data['model']:
        if data['model'] not in valid_models:
            errors.append(f"Модель должна быть одной из: {', '.join(valid_models)}")
    
    # Валидируем температуру
    if 'temperature' in data and data['temperature'] is not None:
        is_valid, error = validate_user_input(data['temperature'], NumberValidator(0, 2))
        if not is_valid:
            errors.append(f"Температура: {error}")
    
    # Валидируем максимальное количество токенов
    if 'max_tokens' in data and data['max_tokens'] is not None:
        is_valid, error = validate_user_input(data['max_tokens'], NumberValidator(1, 4000))
        if not is_valid:
            errors.append(f"Максимальное количество токенов: {error}")
    
    # Валидируем промпты
    prompt_fields = ['system_prompt', 'consultant_prompt', 'tz_analysis_prompt']
    for prompt_field in prompt_fields:
        if prompt_field in data and data[prompt_field]:
            is_valid, error = validate_user_input(data[prompt_field], LengthValidator(10, 2000))
            if not is_valid:
                errors.append(f"{prompt_field}: {error}")
    
    return len(errors) == 0, errors

def validate_security_input(value: str) -> bool:
    """Комплексная валидация на безопасность"""
    if not isinstance(value, str):
        return True
    
    # Проверяем на SQL инъекции
    if not sql_injection_validator(value):
        return False
    
    # Проверяем на XSS
    if not xss_validator(value):
        return False
    
    return True

def sanitize_input(value: str) -> str:
    """Очистка пользовательского ввода"""
    if not isinstance(value, str):
        return value
    
    # Убираем опасные символы
    value = re.sub(r'[<>"\']', '', value)
    
    # Убираем лишние пробелы
    value = ' '.join(value.split())
    
    # Ограничиваем длину
    if len(value) > 10000:
        value = value[:10000]
    
    return value.strip()

class FilenameValidator(Validator):
    """Валидатор имен файлов"""
    
    def __init__(self):
        super().__init__("Недопустимое имя файла")
        self.forbidden_chars = r'[<>:"/\\|?*]'
        self.forbidden_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
    
    def __call__(self, filename: str) -> bool:
        if not isinstance(filename, str):
            return False
        
        # Проверяем длину
        if len(filename) > 255 or len(filename) == 0:
            return False
        
        # Проверяем на запрещенные символы
        if re.search(self.forbidden_chars, filename):
            return False
        
        # Проверяем на запрещенные имена (Windows)
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in self.forbidden_names:
            return False
        
        # Проверяем что файл не начинается и не заканчивается точкой или пробелом
        if filename.startswith('.') or filename.endswith('.') or \
           filename.startswith(' ') or filename.endswith(' '):
            return False
        
        return True

class ChatIdValidator(Validator):
    """Валидатор Telegram Chat ID"""
    
    def __init__(self):
        super().__init__("Некорректный Chat ID")
    
    def __call__(self, value: Union[str, int]) -> bool:
        try:
            chat_id = int(value)
            # Chat ID может быть отрицательным для групп
            return -999999999999999 <= chat_id <= 999999999999999
        except (ValueError, TypeError):
            return False

class WebhookUrlValidator(Validator):
    """Валидатор URL для webhook"""
    
    def __init__(self):
        super().__init__("Webhook URL должен использовать HTTPS")
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        # Webhook должен использовать HTTPS
        if not value.startswith('https://'):
            return False
        
        return url_validator(value)

class DatabaseUrlValidator(Validator):
    """Валидатор URL базы данных"""
    
    def __init__(self):
        super().__init__("Некорректный URL базы данных")
        self.pattern = re.compile(
            r'^(sqlite:///|postgresql://|mysql://|mongodb://)'
        )
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        return bool(self.pattern.match(value))

class EnvironmentValidator(Validator):
    """Валидатор переменных окружения"""
    
    def __init__(self):
        super().__init__("Некорректное значение переменной окружения")
    
    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        # Переменные окружения не должны содержать переносы строк
        if '\n' in value or '\r' in value:
            return False
        
        return True

# Дополнительные валидаторы
chat_id_validator = ChatIdValidator()
webhook_url_validator = WebhookUrlValidator()
database_url_validator = DatabaseUrlValidator()
environment_validator = EnvironmentValidator()
filename_validator = FilenameValidator()

def validate_batch(data: Dict[str, Any], validation_rules: Dict[str, List[Validator]]) -> tuple[bool, Dict[str, List[str]]]:
    """Пакетная валидация данных по правилам"""
    all_errors = {}
    
    for field, validators in validation_rules.items():
        if field in data:
            field_errors = []
            value = data[field]
            
            for validator in validators:
                is_valid, error = validate_user_input(value, validator)
                if not is_valid:
                    field_errors.append(error)
            
            if field_errors:
                all_errors[field] = field_errors
    
    return len(all_errors) == 0, all_errors

def create_validation_schema() -> Dict[str, Dict[str, List[Validator]]]:
    """Создание схемы валидации для разных типов данных"""
    return {
        'user_registration': {
            'first_name': [name_validator, sql_injection_validator, xss_validator],
            'last_name': [name_validator, sql_injection_validator, xss_validator],
            'email': [email_validator],
            'phone': [phone_validator],
            'username': [telegram_username_validator]
        },
        'project_creation': {
            'title': [project_title_validator, sql_injection_validator, xss_validator],
            'description': [description_validator, sql_injection_validator, xss_validator],
            'budget': [budget_validator],
            'complexity': [complexity_validator],
            'platforms': [platform_validator]
        },
        'portfolio_item': {
            'title': [title_validator, sql_injection_validator, xss_validator],
            'description': [description_validator, sql_injection_validator, xss_validator],
            'demo_link': [url_validator],
            'complexity_level': [NumberValidator(1, 10)]
        },
        'system_settings': {
            'bot_token': [telegram_bot_token_validator],
            'openai_api_key': [TokenValidator()],
            'notification_email': [email_validator],
            'admin_chat_id': [chat_id_validator],
            'webhook_url': [webhook_url_validator]
        },
        'ai_configuration': {
            'temperature': [NumberValidator(0, 2)],
            'max_tokens': [NumberValidator(1, 4000)],
            'system_prompt': [LengthValidator(10, 2000), sql_injection_validator, xss_validator]
        }
    }

def get_validator_for_field(field_name: str, context: str = None) -> Optional[Validator]:
    """Получение валидатора для конкретного поля"""
    validators_map = {
        'email': email_validator,
        'phone': phone_validator,
        'url': url_validator,
        'username': telegram_username_validator,
        'title': title_validator,
        'description': description_validator,
        'budget': budget_validator,
        'complexity': complexity_validator,
        'platform': platform_validator,
        'color': color_validator,
        'password': password_validator,
        'token': TokenValidator(),
        'bot_token': telegram_bot_token_validator,
        'chat_id': chat_id_validator,
        'port': port_validator,
        'ip': ip_validator
    }
    
    return validators_map.get(field_name)

def validate_form_data(form_data: Dict[str, Any], form_type: str) -> tuple[bool, Dict[str, List[str]]]:
    """Валидация данных формы по типу"""
    schema = create_validation_schema()
    
    if form_type not in schema:
        return False, {'form': ['Неизвестный тип формы']}
    
    return validate_batch(form_data, schema[form_type])

# Экспорт основных функций для удобства использования
__all__ = [
    'ValidationError',
    'Validator',
    'validate_user_input',
    'validate_project_data',
    'validate_user_profile',
    'validate_settings_data',
    'validate_portfolio_item',
    'validate_file_upload',
    'validate_ai_settings',
    'validate_security_input',
    'sanitize_input',
    'validate_batch',
    'validate_form_data',
    'get_validator_for_field',
    'create_validation_schema',
    # Все валидаторы
    'email_validator',
    'phone_validator',
    'url_validator',
    'telegram_username_validator',
    'project_title_validator',
    'budget_validator',
    'complexity_validator',
    'platform_validator',
    'password_validator',
    'telegram_bot_token_validator',
    'chat_id_validator',
    'webhook_url_validator'
]
import functools
import asyncio
from typing import Callable, Any
from telegram import Update
from telegram.ext import ContextTypes

from ..config.logging import get_logger, log_user_action, log_error
from ..database.database import get_db_context, update_user_state

logger = get_logger(__name__)

def log_handler_call(handler_name: str = None):
    """Декоратор для логирования вызовов обработчиков"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self_or_update, context_or_update=None, *args, **kwargs):
            # Определяем, это метод класса или функция
            if hasattr(self_or_update, '__class__') and context_or_update is not None:
                # Это метод класса: self, update, context, ...
                self_obj = self_or_update
                update = context_or_update
                context = args[0] if args else kwargs.get('context')
                remaining_args = args[1:] if len(args) > 1 else ()
                result = await func(self_obj, update, context, *remaining_args, **kwargs)
            else:
                # Это обычная функция: update, context, ...
                update = self_or_update
                context = context_or_update
                result = await func(update, context, *args, **kwargs)
            
            user_id = update.effective_user.id if update.effective_user else 0
            name = handler_name or func.__name__
            
            log_user_action(user_id, name, "Handler called")
            
            return result
                
        return wrapper
    return decorator

def admin_only(func: Callable) -> Callable:
    """Декоратор для ограничения доступа только администраторам"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        from ..config.settings import settings
        
        user_id = update.effective_user.id
        admin_ids = getattr(settings, 'ADMIN_IDS', [])
        
        if user_id not in admin_ids:
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
            return
            
        return await func(update, context, *args, **kwargs)
    return wrapper

def rate_limit(calls_per_minute: int = 10):
    """Декоратор для ограничения частоты вызовов"""
    def decorator(func: Callable) -> Callable:
        call_times = {}
        
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            import time
            
            user_id = update.effective_user.id
            current_time = time.time()
            
            # Очищаем старые записи
            if user_id in call_times:
                call_times[user_id] = [
                    call_time for call_time in call_times[user_id]
                    if current_time - call_time < 60  # За последнюю минуту
                ]
            else:
                call_times[user_id] = []
            
            # Проверяем лимит
            if len(call_times[user_id]) >= calls_per_minute:
                await update.message.reply_text(
                    f"⏳ Слишком много запросов. Подождите немного и попробуйте снова."
                )
                return
            
            # Добавляем текущий вызов
            call_times[user_id].append(current_time)
            
            return await func(update, context, *args, **kwargs)
        
        return wrapper
    return decorator

def update_user_activity(func: Callable) -> Callable:
    """Декоратор для обновления активности пользователя"""
    @functools.wraps(func)
    async def wrapper(self_or_update, context_or_update=None, *args, **kwargs):
        result = None
        try:
            # Определяем, это метод класса или функция
            if hasattr(self_or_update, '__class__') and context_or_update is not None:
                # Это метод класса: self, update, context, ...
                update = context_or_update
                result = await func(self_or_update, update, args[0] if args else kwargs.get('context'), *(args[1:] if len(args) > 1 else ()), **kwargs)
            else:
                # Это обычная функция: update, context, ...
                update = self_or_update
                result = await func(update, context_or_update, *args, **kwargs)
            
            user_id = update.effective_user.id
            
            # Обновляем время последней активности
            with get_db_context() as db:
                from ..database.database import get_or_create_user
                get_or_create_user(db, user_id)
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении активности пользователя: {e}")
        
        return result
    
    return wrapper

def set_user_state(state: str):
    """Декоратор для установки состояния пользователя"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            try:
                user_id = update.effective_user.id
                
                with get_db_context() as db:
                    update_user_state(db, user_id, state)
                    
            except Exception as e:
                logger.error(f"Ошибка при установке состояния пользователя: {e}")
            
            return await func(update, context, *args, **kwargs)
        
        return wrapper
    return decorator

def handle_errors(func: Callable) -> Callable:
    """Декоратор для обработки ошибок в хендлерах"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            log_error(e, func.__name__)
            
            # Отправляем пользователю сообщение об ошибке
            error_message = (
                "❌ Произошла ошибка при обработке вашего запроса.\n"
                "Попробуйте еще раз или обратитесь в поддержку."
            )
            
            try:
                if update.callback_query:
                    await update.callback_query.answer("Произошла ошибка")
                    from ..bot.keyboards.main import get_main_menu_keyboard
                    await update.callback_query.edit_message_text(
                        error_message,
                        reply_markup=get_main_menu_keyboard()
                    )
                elif update.message:
                    from ..bot.keyboards.main import get_main_menu_keyboard
                    await update.message.reply_text(
                        error_message,
                        reply_markup=get_main_menu_keyboard()
                    )
            except Exception as send_error:
                logger.error(f"Не удалось отправить сообщение об ошибке: {send_error}")
    
    return wrapper

def typing_action(func: Callable) -> Callable:
    """Декоратор для показа индикатора печати"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        # Показываем индикатор печати
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action='typing'
        )
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper

def measure_time(func: Callable) -> Callable:
    """Декоратор для измерения времени выполнения"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        import time
        
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"Функция {func.__name__} выполнена за {execution_time:.2f}s")
        
        return result
    
    return wrapper

def cache_result(ttl: int = 300):
    """Декоратор для кэширования результатов функций"""
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            import time
            import hashlib
            import json
            
            # Создаем ключ кэша
            cache_key = hashlib.md5(
                json.dumps(str(args) + str(kwargs), sort_keys=True).encode()
            ).hexdigest()
            
            current_time = time.time()
            
            # Проверяем кэш
            if cache_key in cache:
                cached_result, cached_time = cache[cache_key]
                if current_time - cached_time < ttl:
                    return cached_result
            
            # Выполняем функцию и кэшируем результат
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            return result
        
        return wrapper
    return decorator

def validate_user_input(validation_func: Callable[[str], bool]):
    """Декоратор для валидации пользовательского ввода"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if update.message and update.message.text:
                if not validation_func(update.message.text):
                    await update.message.reply_text(
                        "❌ Некорректный ввод. Попробуйте еще раз."
                    )
                    return
            
            return await func(update, context, *args, **kwargs)
        
        return wrapper
    return decorator

# Комбинированные декораторы
def standard_handler(func: Callable) -> Callable:
    """Стандартный декоратор для большинства обработчиков"""
    return handle_errors(
        update_user_activity(
            log_handler_call()(func)
        )
    )

def api_handler(func: Callable) -> Callable:
    """Декоратор для обработчиков, которые работают с внешними API"""
    return handle_errors(
        typing_action(
            rate_limit(5)(  # 5 вызовов в минуту для API
                measure_time(func)
            )
        )
    )
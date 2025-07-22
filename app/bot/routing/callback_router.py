"""
Единый роутер для всех callback_data
Решает проблемы конфликтов обработчиков
"""
import re
import logging
from typing import Dict, List, Callable, Tuple, Pattern
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class CallbackRoute:
    """Маршрут для callback_data"""
    def __init__(self, pattern: str, handler: Callable, priority: int = 100, description: str = ""):
        self.pattern = pattern
        self.compiled_pattern = re.compile(pattern)
        self.handler = handler
        self.priority = priority  # Чем меньше число, тем выше приоритет
        self.description = description
    
    def matches(self, callback_data: str) -> bool:
        """Проверяет соответствие callback_data паттерну"""
        return bool(self.compiled_pattern.match(callback_data))
    
    def __str__(self):
        return f"Route(pattern={self.pattern}, priority={self.priority}, desc={self.description})"

class CallbackRouter:
    """Централизованный роутер для всех callback_data"""
    
    def __init__(self):
        self.routes: List[CallbackRoute] = []
        self.stats = {"total_calls": 0, "handled": 0, "unhandled": 0}
    
    def register(self, pattern: str, handler: Callable, priority: int = 100, description: str = ""):
        """Регистрирует новый маршрут"""
        route = CallbackRoute(pattern, handler, priority, description)
        
        # Проверяем конфликты с существующими маршрутами
        conflicts = self._check_conflicts(route)
        if conflicts:
            logger.warning(f"Потенциальные конфликты для паттерна '{pattern}': {conflicts}")
        
        self.routes.append(route)
        # Сортируем по приоритету (меньшее число = выше приоритет)
        self.routes.sort(key=lambda r: r.priority)
        
        logger.info(f"Зарегистрирован маршрут: {route}")
        return route
    
    def _check_conflicts(self, new_route: CallbackRoute) -> List[str]:
        """Проверяет конфликты с существующими маршрутами"""
        conflicts = []
        test_cases = [
            "main_menu", "portfolio", "create_tz", "project_123", 
            "portfolio_telegram", "tz_text", "revision_456"
        ]
        
        for test_case in test_cases:
            matching_routes = [r for r in self.routes if r.matches(test_case)]
            if matching_routes and new_route.matches(test_case):
                conflicts.append(f"'{test_case}' -> {[r.pattern for r in matching_routes]}")
        
        return conflicts
    
    async def route(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обрабатывает callback и направляет к нужному обработчику"""
        if not update.callback_query:
            return False
            
        callback_data = update.callback_query.data
        user_id = update.effective_user.id
        
        self.stats["total_calls"] += 1
        
        logger.info(f"🔀 ROUTER: callback='{callback_data}' user={user_id}")
        
        # Ищем подходящий маршрут
        for route in self.routes:
            if route.matches(callback_data):
                try:
                    logger.info(f"✅ ROUTER: маршрут найден - {route.pattern} (priority={route.priority})")
                    await route.handler(update, context)
                    self.stats["handled"] += 1
                    return True
                except Exception as e:
                    logger.error(f"❌ ROUTER: ошибка в обработчике {route.pattern}: {e}")
                    raise
        
        # Маршрут не найден
        logger.warning(f"⚠️ ROUTER: маршрут не найден для '{callback_data}'")
        self.stats["unhandled"] += 1
        
        # Отправляем сообщение об ошибке пользователю
        try:
            await update.callback_query.answer("❌ Неизвестная команда. Возвращайтесь в главное меню.")
            from ...handlers.start import StartHandler
            start_handler = StartHandler()
            await start_handler.start(update, context)
        except Exception as e:
            logger.error(f"Ошибка при обработке неизвестного callback: {e}")
        
        return False
    
    def get_stats(self) -> Dict:
        """Возвращает статистику работы роутера"""
        return self.stats.copy()
    
    def list_routes(self) -> List[str]:
        """Возвращает список всех зарегистрированных маршрутов"""
        return [str(route) for route in self.routes]
    
    def validate_all_patterns(self) -> List[str]:
        """Валидирует все паттерны на предмет конфликтов"""
        issues = []
        
        test_cases = [
            "main_menu", "portfolio", "create_tz", "project_123", "portfolio_telegram",
            "tz_text", "tz_voice", "revision_456", "admin_stats", "consultant_new_session"
        ]
        
        for test_case in test_cases:
            matching_routes = [r for r in self.routes if r.matches(test_case)]
            if len(matching_routes) > 1:
                patterns = [r.pattern for r in matching_routes]
                issues.append(f"Конфликт для '{test_case}': {patterns}")
        
        return issues

# Глобальный экземпляр роутера
callback_router = CallbackRouter()

def get_callback_router() -> CallbackRouter:
    """Возвращает глобальный роутер"""
    return callback_router
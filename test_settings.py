#!/usr/bin/env python3
"""
Тестовый скрипт для проверки загрузки метода show_settings
"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.bot.handlers.common import CommonHandler
    
    # Создаем экземпляр CommonHandler
    handler = CommonHandler()
    
    # Проверяем, есть ли метод show_settings
    if hasattr(handler, 'show_settings'):
        print("✅ Метод show_settings найден!")
        print(f"Тип: {type(handler.show_settings)}")
        print(f"Документация: {handler.show_settings.__doc__}")
    else:
        print("❌ Метод show_settings НЕ найден!")
        
    # Выводим все методы, содержащие 'show'
    show_methods = [method for method in dir(handler) if method.startswith('show')]
    print(f"\nВсе методы, начинающиеся с 'show': {show_methods}")
    
except Exception as e:
    print(f"❌ Ошибка при импорте: {e}")
    import traceback
    traceback.print_exc()
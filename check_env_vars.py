#!/usr/bin/env python3
"""
Проверка переменных окружения для Avito и Telegram
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_env_vars():
    """Проверяет все необходимые переменные окружения"""
    
    print("🔍 ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("=" * 50)
    
    # Загружаем настройки
    try:
        from app.config.settings import settings
        print("✅ Настройки загружены успешно")
    except Exception as e:
        print(f"❌ Ошибка загрузки настроек: {e}")
        return
    
    # Список переменных для проверки
    env_vars = [
        ('BOT_TOKEN', settings.BOT_TOKEN, 'Токен Telegram бота'),
        ('ADMIN_CHAT_ID', settings.ADMIN_CHAT_ID, 'ID чата для уведомлений'),
        ('OPENROUTER_API_KEY', settings.OPENROUTER_API_KEY, 'Ключ OpenRouter для AI'),
        ('NOTIFICATION_CHAT_ID', os.getenv("NOTIFICATION_CHAT_ID", ""), 'Альтернативный ID чата'),
    ]
    
    print("\n📋 СТАТУС ПЕРЕМЕННЫХ:")
    for var_name, var_value, description in env_vars:
        if var_value:
            if 'TOKEN' in var_name or 'KEY' in var_name:
                masked_value = '***' + str(var_value)[-4:] if len(str(var_value)) > 4 else '***'
                print(f"✅ {var_name}: {masked_value} - {description}")
            else:
                print(f"✅ {var_name}: {var_value} - {description}")
        else:
            print(f"❌ {var_name}: НЕ ЗАДАН - {description}")
    
    # Проверяем .env файл
    env_file = project_root / '.env'
    print(f"\n📁 ФАЙЛ .env: {'существует' if env_file.exists() else 'НЕ НАЙДЕН'}")
    
    if env_file.exists():
        print("📄 Содержимое .env (без секретов):")
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            if 'TOKEN' in key or 'KEY' in key or 'SECRET' in key:
                                print(f"  {key}=***")
                            else:
                                print(f"  {line}")
        except Exception as e:
            print(f"❌ Ошибка чтения .env: {e}")
    
    # Проверяем системные переменные окружения
    print(f"\n🖥️ СИСТЕМНЫЕ ПЕРЕМЕННЫЕ:")
    system_vars = ['BOT_TOKEN', 'ADMIN_CHAT_ID', 'NOTIFICATION_CHAT_ID', 'OPENROUTER_API_KEY']
    for var in system_vars:
        sys_value = os.environ.get(var)
        if sys_value:
            if 'TOKEN' in var or 'KEY' in var:
                masked = '***' + sys_value[-4:] if len(sys_value) > 4 else '***'
                print(f"✅ {var}: {masked} (системная)")
            else:
                print(f"✅ {var}: {sys_value} (системная)")
        else:
            print(f"❌ {var}: не установлена (системная)")
    
    print(f"\n📊 ИТОГОВАЯ ПРОВЕРКА:")
    critical_missing = []
    
    if not settings.BOT_TOKEN:
        critical_missing.append("BOT_TOKEN")
    if not settings.ADMIN_CHAT_ID:
        critical_missing.append("ADMIN_CHAT_ID")
    if not settings.OPENROUTER_API_KEY:
        critical_missing.append("OPENROUTER_API_KEY")
    
    if critical_missing:
        print(f"❌ Критические переменные не заданы: {', '.join(critical_missing)}")
        print("🔧 Uведомления и автоответы работать НЕ БУДУТ!")
    else:
        print("✅ Все критические переменные заданы")
        print("🚀 Уведомления и автоответы должны работать!")

if __name__ == "__main__":
    check_env_vars()
#!/usr/bin/env python3
"""
Скрипт для остановки Avito polling сервиса
Используется когда webhook активен
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def stop_polling_service():
    """Останавливает polling сервис"""
    try:
        from app.services.avito_polling_service import polling_service
        
        print("🛑 Останавливаем Avito polling сервис...")
        
        # Останавливаем polling
        polling_service.stop_polling()
        
        print("✅ Avito polling сервис остановлен")
        print("🔗 Теперь система использует только webhook для real-time обновлений")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка остановки polling: {e}")
        return False

def main():
    """Главная функция"""
    import asyncio
    
    print("🔧 Остановка Avito Polling сервиса...")
    print("=" * 50)
    
    success = asyncio.run(stop_polling_service())
    
    if success:
        print("🎉 Операция выполнена успешно!")
        print("💡 Перезапустите сервер для применения изменений")
    else:
        print("💥 Операция завершилась с ошибкой!")
        sys.exit(1)

if __name__ == "__main__":
    main()
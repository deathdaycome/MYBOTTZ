#!/usr/bin/env python3
"""
Отладочный скрипт для проверки интеграции Авито
Запустите на сервере: python3 debug_avito.py
"""

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, '/var/www/bot_business_card')

def test_imports():
    """Тестируем импорты"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ИМПОРТОВ")
    print("=" * 60)
    
    # Тест 1: Базовые импорты
    try:
        print("1. Импорт базовых модулей...")
        from app.admin import navigation
        print("   ✅ navigation импортирован")
    except Exception as e:
        print(f"   ❌ Ошибка импорта navigation: {e}")
        return False
    
    # Тест 2: Проверка навигации
    try:
        print("\n2. Проверка элементов навигации...")
        nav_items = navigation.get_navigation_items(user_role="owner")
        print(f"   Найдено элементов: {len(nav_items)}")
        
        avito_found = False
        for item in nav_items:
            if item.get('name') == 'Авито':
                avito_found = True
                print(f"   ✅ Авито найден: {item}")
                break
        
        if not avito_found:
            print("   ❌ Авито НЕ найден в навигации")
            print("   Список элементов:")
            for item in nav_items:
                print(f"      - {item.get('name')}: {item.get('url')}")
    except Exception as e:
        print(f"   ❌ Ошибка при получении навигации: {e}")
        return False
    
    # Тест 3: Импорт сервиса Авито
    try:
        print("\n3. Импорт сервиса Авито...")
        from app.services import avito_service
        print("   ✅ avito_service импортирован")
    except Exception as e:
        print(f"   ❌ Ошибка импорта avito_service: {e}")
        print("   Проверяем наличие aiohttp...")
        try:
            import aiohttp
            print("   ✅ aiohttp установлен")
        except:
            print("   ❌ aiohttp НЕ установлен! Выполните: pip install aiohttp")
    
    # Тест 4: Импорт роутера Авито
    try:
        print("\n4. Импорт роутера Авито...")
        from app.admin.routers import avito
        print("   ✅ Роутер avito импортирован")
        
        # Проверяем роутер
        print(f"   Router prefix: {avito.router.prefix}")
        print(f"   Routes count: {len(avito.router.routes)}")
        
    except Exception as e:
        print(f"   ❌ Ошибка импорта роутера avito: {e}")
        
        # Детальная диагностика
        print("\n   Детальная диагностика ошибки:")
        import traceback
        traceback.print_exc()
    
    # Тест 5: Проверка app.py
    try:
        print("\n5. Проверка подключения роутера в app.py...")
        
        # Читаем файл app.py
        with open('/var/www/bot_business_card/app/admin/app.py', 'r') as f:
            content = f.read()
            
        if 'from .routers.avito import router as avito_router' in content:
            print("   ✅ Импорт роутера найден в app.py")
        else:
            print("   ❌ Импорт роутера НЕ найден в app.py")
            
        if 'admin_router.include_router(avito_router)' in content:
            print("   ✅ Подключение роутера найдено в app.py")
        else:
            print("   ❌ Подключение роутера НЕ найдено в app.py")
            
    except Exception as e:
        print(f"   ❌ Ошибка при проверке app.py: {e}")
    
    # Тест 6: Проверка функции authenticate
    try:
        print("\n6. Проверка функции authenticate...")
        from app.admin.app import authenticate, get_current_user
        print("   ✅ authenticate и get_current_user импортированы")
    except Exception as e:
        print(f"   ❌ Ошибка импорта authenticate: {e}")
    
    return True

def check_running_app():
    """Проверяем запущенное приложение"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ЗАПУЩЕННОГО ПРИЛОЖЕНИЯ")
    print("=" * 60)
    
    import subprocess
    
    # Проверяем процессы
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        admin_processes = []
        for line in lines:
            if 'admin' in line.lower() and 'python' in line.lower():
                admin_processes.append(line)
        
        if admin_processes:
            print("Найдены процессы админ-панели:")
            for proc in admin_processes[:3]:  # Показываем первые 3
                print(f"  {proc[:120]}...")
        else:
            print("❌ Процессы админ-панели НЕ найдены")
            
    except Exception as e:
        print(f"Ошибка при проверке процессов: {e}")
    
    # Проверяем pm2
    try:
        result = subprocess.run(['pm2', 'list'], capture_output=True, text=True)
        print("\nСтатус PM2:")
        print(result.stdout[:500])
    except:
        print("PM2 не найден или не используется")

def test_direct_import():
    """Прямой тест импорта и инициализации"""
    print("\n" + "=" * 60)
    print("ПРЯМОЙ ТЕСТ ИМПОРТА")
    print("=" * 60)
    
    try:
        # Меняем директорию
        os.chdir('/var/www/bot_business_card')
        
        # Импортируем app
        print("Импортируем admin app...")
        from app.admin.app import admin_router
        
        # Проверяем роуты
        print(f"\nВсего роутов в admin_router: {len(admin_router.routes)}")
        
        # Ищем роуты Авито
        avito_routes = []
        for route in admin_router.routes:
            if hasattr(route, 'path') and '/avito' in str(route.path):
                avito_routes.append(route)
                print(f"  ✅ Найден роут Авито: {route.path}")
        
        if not avito_routes:
            print("  ❌ Роуты Авито НЕ найдены")
            print("\n  Список всех роутов:")
            for route in admin_router.routes[:20]:  # Первые 20
                if hasattr(route, 'path'):
                    print(f"    - {route.path}")
        
    except Exception as e:
        print(f"❌ Ошибка при прямом импорте: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🔍 ОТЛАДКА ИНТЕГРАЦИИ АВИТО")
    print("=" * 60)
    
    # Проверяем текущую директорию
    print(f"Текущая директория: {os.getcwd()}")
    
    # Проверяем наличие файлов
    if os.path.exists('/var/www/bot_business_card'):
        print("✅ Директория проекта найдена")
    else:
        print("❌ Директория /var/www/bot_business_card не найдена!")
        sys.exit(1)
    
    # Запускаем тесты
    test_imports()
    check_running_app()
    test_direct_import()
    
    print("\n" + "=" * 60)
    print("РЕКОМЕНДАЦИИ:")
    print("=" * 60)
    print("1. Если aiohttp не установлен: pip install aiohttp")
    print("2. Перезапустите приложение: pm2 restart all")
    print("3. Проверьте логи: pm2 logs --lines 50")
    print("4. Очистите кеш браузера и обновите страницу")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Скрипт для проверки наличия интеграции Авито на сервере
Запустите этот скрипт на сервере чтобы проверить файлы
"""

import os
import sys

def check_file_exists(filepath):
    """Проверка существования файла"""
    if os.path.exists(filepath):
        print(f"✅ {filepath} - НАЙДЕН")
        # Проверяем содержимое для ключевых строк
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'avito' in content.lower() or 'авито' in content.lower():
                    print(f"   └─ Содержит упоминание Авито")
                    return True
        except Exception as e:
            print(f"   └─ Ошибка чтения: {e}")
    else:
        print(f"❌ {filepath} - НЕ НАЙДЕН")
    return False

def main():
    print("=" * 60)
    print("ПРОВЕРКА ИНТЕГРАЦИИ АВИТО НА СЕРВЕРЕ")
    print("=" * 60)
    
    # Определяем базовую директорию
    base_dirs = [
        "/var/www/bot_business_card",
        "/root/bot_business_card",
        ".",
    ]
    
    base_dir = None
    for dir_path in base_dirs:
        if os.path.exists(dir_path):
            base_dir = dir_path
            break
    
    if not base_dir:
        print("❌ Не найдена директория проекта!")
        sys.exit(1)
    
    print(f"📁 Проверяем в директории: {base_dir}")
    print("-" * 60)
    
    # Список файлов для проверки
    files_to_check = [
        "app/services/avito_service.py",
        "app/admin/routers/avito.py", 
        "app/admin/templates/avito_messenger.html",
        "app/admin/navigation.py",
        "app/admin/app.py",
        "app/services/openai_service.py"
    ]
    
    os.chdir(base_dir)
    
    found_count = 0
    for filepath in files_to_check:
        if check_file_exists(filepath):
            found_count += 1
    
    print("-" * 60)
    print(f"РЕЗУЛЬТАТ: {found_count}/{len(files_to_check)} файлов найдено")
    
    # Проверяем navigation.py на наличие пункта Авито
    nav_file = "app/admin/navigation.py"
    if os.path.exists(nav_file):
        print("\n📋 Проверка навигации:")
        with open(nav_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if '"Авито"' in content:
                print("✅ Пункт 'Авито' найден в навигации")
                # Найдем строку с Авито
                for line in content.split('\n'):
                    if '"Авито"' in line:
                        print(f"   └─ {line.strip()}")
            else:
                print("❌ Пункт 'Авито' НЕ найден в навигации")
    
    # Проверяем requirements.txt
    req_file = "requirements.txt"
    if os.path.exists(req_file):
        print("\n📦 Проверка зависимостей:")
        with open(req_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'aiohttp' in content:
                print("✅ aiohttp найден в requirements.txt")
            else:
                print("❌ aiohttp НЕ найден в requirements.txt")
    
    # Проверяем последний git commit
    print("\n🔄 Последний коммит:")
    os.system("git log --oneline -1")
    
    print("\n📅 Время последнего обновления файлов:")
    os.system("ls -la app/admin/routers/avito.py 2>/dev/null || echo 'Файл avito.py не найден'")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Скрипт для запуска всех необходимых фиксов при деплое
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Выполняет команду и выводит результат"""
    print(f"\n>>> {description}")
    print(f"    Команда: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(f"    Вывод: {result.stdout}")
        if result.stderr:
            print(f"    Ошибки: {result.stderr}")
        if result.returncode != 0:
            print(f"    ⚠️ Команда завершилась с кодом {result.returncode}")
        else:
            print(f"    ✅ Успешно выполнено")
        return result.returncode == 0
    except Exception as e:
        print(f"    ❌ Ошибка выполнения: {e}")
        return False

def main():
    print("="*60)
    print("ЗАПУСК ИСПРАВЛЕНИЙ НА СЕРВЕРЕ")
    print("="*60)
    
    # 1. Применяем фикс колонок БД
    if os.path.exists("fix_database_columns.py"):
        run_command("python3 fix_database_columns.py", "Исправление колонок в БД")
    
    # 2. Применяем миграции (если есть)
    if os.path.exists("migrations/008_add_integration_fields.py"):
        run_command("python3 migrations/008_add_integration_fields.py", "Применение миграции 008")
    
    # 3. Проверяем импорты
    if os.path.exists("test_imports.py"):
        run_command("python3 test_imports.py", "Проверка импортов")
    
    # 4. Перезапускаем приложение
    print("\n>>> Перезапуск приложения")
    run_command("pm2 restart botdev-admin", "Перезапуск PM2")
    
    print("\n" + "="*60)
    print("ИСПРАВЛЕНИЯ ЗАВЕРШЕНЫ")
    print("="*60)

if __name__ == "__main__":
    main()
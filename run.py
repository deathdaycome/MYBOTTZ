#!/usr/bin/env python3
"""
Скрипт запуска Telegram-бота визитки разработчика ботов
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_requirements():
    """Проверка наличия необходимых зависимостей"""
    # Словарь: {имя для pip: имя для import}
    required_packages = {
        'python-telegram-bot': 'telegram',
        'sqlalchemy': 'sqlalchemy',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'python-dotenv': 'dotenv'
    }
    
    missing_packages = []
    
    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("❌ Отсутствуют необходимые пакеты:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Установите их командой:")
        print("pip install -r requirements.txt")
        sys.exit(1)

def check_env_file():
    """Проверка наличия .env файла"""
    env_path = project_root / '.env'
    
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        print("📝 Создайте файл .env в корне проекта со следующими переменными:")
        print("""
BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password
ADMIN_PORT=8001
""")
        sys.exit(1)

def check_directories():
    """Создание необходимых директорий"""
    directories = [
        'data',
        'logs', 
        'uploads',
        'uploads/documents',
        'uploads/images',
        'uploads/portfolio',
        'uploads/audio',
        'uploads/temp',
        'app/static',
        'app/static/images',
        'app/static/css',
        'app/static/js'
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Директории созданы/проверены")

def create_placeholder_image(path):
    """Создание простого placeholder изображения"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Создаем изображение 400x300
        img = Image.new('RGB', (400, 300), color='#e3f2fd')
        draw = ImageDraw.Draw(img)
        
        # Добавляем текст
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            font = ImageFont.load_default()
            
        text = "Placeholder"
        bbox = draw.textbbox((0, 0), text, font=font)
        textwidth = bbox[2] - bbox[0]
        textheight = bbox[3] - bbox[1]
        
        # Вычисляем позицию текста по центру
        x = (img.width - textwidth) / 2
        y = (img.height - textheight) / 2
        
        draw.text((x, y), text, font=font, fill="#000000")
        
        # Сохраняем изображение
        img.save(path)
        print(f"✅ Создано placeholder изображение: {path}")
    except Exception as e:
        print(f"❌ Не удалось создать placeholder изображение: {e}")

def main():
    """Основная функция запуска"""
    print("🚀 Запуск приложения \"Визитка разработчика ботов\"...")

    # 1. Проверка зависимостей
    check_requirements()
    print("✅ Зависимости в порядке")

    # 2. Проверка .env файла
    check_env_file()
    print("✅ Конфигурация .env загружена")

    # 3. Создание необходимых директорий
    check_directories()

    # 4. Запуск FastAPI приложения с ботом
    print("🌐 Запуск админ-панели и Telegram-бота...")
    
    # Импортируем здесь, чтобы избежать проблем с путем и конфигурацией
    import uvicorn
    from app.config.settings import get_settings

    settings = get_settings()
    
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=settings.ADMIN_PORT,
        reload=False,  # Отключаем автоперезагрузку для стабильной работы
        log_level="info"
    )

if __name__ == "__main__":
    # Удаляем создание placeholder-изображения, так как оно уже есть в check_directories
    main()
    
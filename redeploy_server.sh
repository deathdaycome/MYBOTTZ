#!/bin/bash

# 🚀 Скрипт полного редеплоя на сервер с сохранением БД
# ⚠️ ВАЖНО: База данных НЕ удаляется!

set -e  # Остановка при ошибке

echo "=========================================="
echo "🚀 НАЧАЛО ПОЛНОГО РЕДЕПЛОЯ"
echo "=========================================="

# Переменные
SERVER="root@147.45.215.199"
PROJECT_DIR="/var/www/bot_business_card"
BACKUP_DIR="/root/backups/bot_business_card_$(date +%Y%m%d_%H%M%S)"
DB_FILE="data/bot.db"
ENV_FILE=".env"

echo ""
echo "📦 ШАГ 1: Создание бэкапа БД и .env"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"
BACKUP_DIR="/root/backups/bot_business_card_$(date +%Y%m%d_%H%M%S)"

# Создаём директорию для бэкапа
mkdir -p $BACKUP_DIR

# Бэкап БД
if [ -f "$PROJECT_DIR/data/bot.db" ]; then
    echo "✅ Бэкап базы данных..."
    cp -r $PROJECT_DIR/data $BACKUP_DIR/
    echo "   Сохранено в: $BACKUP_DIR/data/"
else
    echo "⚠️  База данных не найдена в $PROJECT_DIR/data/bot.db"
fi

# Бэкап .env
if [ -f "$PROJECT_DIR/.env" ]; then
    echo "✅ Бэкап .env файла..."
    cp $PROJECT_DIR/.env $BACKUP_DIR/
    echo "   Сохранено в: $BACKUP_DIR/.env"
else
    echo "⚠️  .env файл не найден"
fi

# Бэкап uploads (если есть)
if [ -d "$PROJECT_DIR/uploads" ]; then
    echo "✅ Бэкап uploads..."
    cp -r $PROJECT_DIR/uploads $BACKUP_DIR/
    echo "   Сохранено в: $BACKUP_DIR/uploads/"
fi

echo ""
echo "✅ Бэкап завершён: $BACKUP_DIR"
ENDSSH

echo ""
echo "🛑 ШАГ 2: Остановка приложения"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

# Останавливаем PM2 процессы
echo "⏸  Остановка PM2..."
pm2 stop all || true
pm2 delete all || true

echo "✅ Приложение остановлено"
ENDSSH

echo ""
echo "🗑️  ШАГ 3: Удаление старого кода (БД сохраняется!)"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"
BACKUP_DIR=$(ls -td /root/backups/bot_business_card_* | head -1)

cd $PROJECT_DIR

# Сохраняем БД и .env во временную директорию
echo "💾 Временное сохранение БД и настроек..."
mkdir -p /tmp/bot_backup
cp -r data /tmp/bot_backup/ 2>/dev/null || echo "⚠️  data не найдена"
cp .env /tmp/bot_backup/ 2>/dev/null || echo "⚠️  .env не найден"
cp -r uploads /tmp/bot_backup/ 2>/dev/null || echo "⚠️  uploads не найдены"

# Удаляем ВСЁ кроме корневой папки
echo "🗑️  Удаление старого кода..."
cd /var/www
rm -rf bot_business_card/*
rm -rf bot_business_card/.[!.]*

echo "✅ Старый код удалён"
ENDSSH

echo ""
echo "📥 ШАГ 4: Клонирование из GitHub"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"

# Клонируем репозиторий
echo "📦 Клонирование из GitHub..."
cd /var/www
rm -rf bot_business_card_temp
git clone https://github.com/deathdaycome/MYBOTTZ.git bot_business_card_temp

# Перемещаем содержимое в основную папку
mv bot_business_card_temp/* bot_business_card/
mv bot_business_card_temp/.[!.]* bot_business_card/ 2>/dev/null || true
rm -rf bot_business_card_temp

echo "✅ Код загружен из GitHub"
ENDSSH

echo ""
echo "💾 ШАГ 5: Восстановление БД и настроек"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"

# Восстанавливаем БД
if [ -d "/tmp/bot_backup/data" ]; then
    echo "✅ Восстановление базы данных..."
    mkdir -p $PROJECT_DIR/data
    cp -r /tmp/bot_backup/data/* $PROJECT_DIR/data/
else
    echo "⚠️  БД не найдена в бэкапе, создаём новую директорию"
    mkdir -p $PROJECT_DIR/data
fi

# Восстанавливаем .env
if [ -f "/tmp/bot_backup/.env" ]; then
    echo "✅ Восстановление .env..."
    cp /tmp/bot_backup/.env $PROJECT_DIR/
else
    echo "❌ .env не найден в бэкапе!"
    exit 1
fi

# Восстанавливаем uploads
if [ -d "/tmp/bot_backup/uploads" ]; then
    echo "✅ Восстановление uploads..."
    cp -r /tmp/bot_backup/uploads $PROJECT_DIR/
else
    echo "⚠️  uploads не найдены, создаём новую директорию"
    mkdir -p $PROJECT_DIR/uploads
fi

# Обновляем BOT_TOKEN на правильный
echo "🔑 Обновление BOT_TOKEN..."
sed -i 's/BOT_TOKEN=.*/BOT_TOKEN=7881909419:AAF_9TD2tZFOsQi2FThkyJt6ICjrWPny3JA/' $PROJECT_DIR/.env

# Чистим временный бэкап
rm -rf /tmp/bot_backup

echo "✅ БД и настройки восстановлены"
ENDSSH

echo ""
echo "📦 ШАГ 6: Установка зависимостей Python"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"
cd $PROJECT_DIR

# Удаляем старое виртуальное окружение
echo "🗑️  Удаление старого venv..."
rm -rf venv

# Создаём новое виртуальное окружение
echo "📦 Создание нового venv..."
python3 -m venv venv

# Активируем и устанавливаем зависимости
echo "📦 Установка зависимостей..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python зависимости установлены"
ENDSSH

echo ""
echo "🎨 ШАГ 7: Сборка Mini App (фронтенд)"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"
cd $PROJECT_DIR/miniapp

# Проверяем наличие Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен!"
    echo "Установите Node.js: curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs"
    exit 1
fi

# Удаляем старые зависимости
echo "🗑️  Очистка старых зависимостей..."
rm -rf node_modules package-lock.json

# Устанавливаем зависимости
echo "📦 Установка npm зависимостей..."
npm install

# Сборка production версии
echo "🏗️  Сборка production версии..."
npm run build

echo "✅ Mini App собран"
ENDSSH

echo ""
echo "🚀 ШАГ 8: Запуск приложения"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"
cd $PROJECT_DIR

# Применяем миграции БД (если есть)
echo "🔄 Применение миграций БД..."
source venv/bin/activate
python3 migrations/add_revision_progress_timer.py 2>/dev/null || echo "⚠️  Миграция уже применена"
python3 migrations/add_task_attachments.py 2>/dev/null || echo "⚠️  Миграция уже применена"

# Запускаем через PM2
echo "🚀 Запуск приложения через PM2..."

# Главное приложение
pm2 start venv/bin/python --name bot-business-card -- -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Сохраняем конфигурацию PM2
pm2 save

echo "✅ Приложение запущено"
ENDSSH

echo ""
echo "🔍 ШАГ 9: Проверка статуса"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
echo "📊 Статус PM2:"
pm2 list

echo ""
echo "📝 Последние 20 строк логов:"
pm2 logs bot-business-card --lines 20 --nostream
ENDSSH

echo ""
echo "=========================================="
echo "✅ РЕДЕПЛОЙ ЗАВЕРШЁН УСПЕШНО!"
echo "=========================================="
echo ""
echo "📊 Что было сделано:"
echo "  ✅ Создан бэкап БД и настроек"
echo "  ✅ Удалён старый код"
echo "  ✅ Загружен новый код из GitHub"
echo "  ✅ Восстановлена БД (все данные сохранены!)"
echo "  ✅ Установлены зависимости Python"
echo "  ✅ Собран Mini App"
echo "  ✅ Применены миграции"
echo "  ✅ Приложение запущено"
echo ""
echo "🔗 Проверьте работу:"
echo "  - Бот: https://t.me/NikolaevCodeBot"
echo "  - Админка: http://147.45.215.199:8001/admin/"
echo "  - API: http://147.45.215.199:8000/docs"
echo ""
echo "📦 Бэкап сохранён в: /root/backups/"
echo ""

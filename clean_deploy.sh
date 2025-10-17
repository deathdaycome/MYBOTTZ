#!/bin/bash

# 🗑️ Полная очистка и переразвертывание (БД сохраняется)
# Удаляет ВСЁ кроме базы данных и загруженных файлов

set -e

echo "=========================================="
echo "🗑️ ПОЛНАЯ ОЧИСТКА И ПЕРЕРАЗВЕРТЫВАНИЕ"
echo "=========================================="
echo ""
echo "⚠️  ВНИМАНИЕ! Будет удалено всё кроме БД!"
echo ""

# Переменные
PROJECT_DIR="/var/www/bot_business_card"
BACKUP_DIR="/root/backups/bot_$(date +%Y%m%d_%H%M%S)"

echo "💾 ШАГ 1: Бэкап БД и файлов"
echo "=========================================="

# Сохраняем БД и файлы во временную директорию
if [ -d "$PROJECT_DIR/data" ]; then
    echo "✅ Сохранение БД..."
    mkdir -p $BACKUP_DIR
    cp -r $PROJECT_DIR/data $BACKUP_DIR/
    echo "   БД сохранена: $BACKUP_DIR/data"
fi

if [ -d "$PROJECT_DIR/uploads" ]; then
    echo "✅ Сохранение файлов..."
    mkdir -p $BACKUP_DIR
    cp -r $PROJECT_DIR/uploads $BACKUP_DIR/
    echo "   Файлы сохранены: $BACKUP_DIR/uploads"
fi

if [ -f "$PROJECT_DIR/.env" ]; then
    echo "✅ Сохранение .env..."
    cp $PROJECT_DIR/.env $BACKUP_DIR/
    echo "   .env сохранён: $BACKUP_DIR/.env"
fi

echo ""
echo "🛑 ШАГ 2: Остановка всех процессов"
echo "=========================================="

cd $PROJECT_DIR 2>/dev/null || true

# Останавливаем Docker
echo "🐳 Остановка Docker контейнеров..."
docker-compose down 2>/dev/null || true
docker stop bot-business-card 2>/dev/null || true
docker rm bot-business-card 2>/dev/null || true

# Удаляем образы
echo "🗑️ Удаление Docker образов..."
docker rmi bot_business_card_2-bot-business-card 2>/dev/null || true
docker rmi bot_business_card-bot-business-card 2>/dev/null || true

# Останавливаем PM2
echo "🛑 Остановка PM2..."
pm2 stop all 2>/dev/null || true
pm2 delete all 2>/dev/null || true
pm2 kill 2>/dev/null || true

# Убиваем все Python процессы бота
echo "🔫 Остановка Python процессов..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "python.*bot" 2>/dev/null || true

sleep 2

echo ""
echo "🗑️ ШАГ 3: ПОЛНОЕ УДАЛЕНИЕ проекта"
echo "=========================================="

cd /var/www

# Удаляем ВСЁ
echo "💥 Удаление директории $PROJECT_DIR..."
rm -rf $PROJECT_DIR

echo "✅ Всё удалено!"

echo ""
echo "📥 ШАГ 4: Клонирование из GitHub"
echo "=========================================="

# Клонируем заново
echo "📦 Клонирование репозитория..."
git clone https://github.com/deathdaycome/MYBOTTZ.git bot_business_card

cd bot_business_card

echo "✅ Код загружен"

echo ""
echo "💾 ШАГ 5: Восстановление БД и файлов"
echo "=========================================="

# Создаём директории
mkdir -p data uploads logs

# Восстанавливаем БД
if [ -d "$BACKUP_DIR/data" ]; then
    echo "✅ Восстановление БД..."
    cp -r $BACKUP_DIR/data/* data/
fi

# Восстанавливаем файлы
if [ -d "$BACKUP_DIR/uploads" ]; then
    echo "✅ Восстановление файлов..."
    cp -r $BACKUP_DIR/uploads/* uploads/
fi

# Восстанавливаем .env
if [ -f "$BACKUP_DIR/.env" ]; then
    echo "✅ Восстановление .env..."
    cp $BACKUP_DIR/.env .env
else
    echo "❌ .env не найден! Создайте .env файл"
    exit 1
fi

# Обновляем токен на правильный
echo "🔑 Обновление BOT_TOKEN..."
sed -i 's/BOT_TOKEN=.*/BOT_TOKEN=7881909419:AAF_9TD2tZFOsQi2FThkyJt6ICjrWPny3JA/' .env

# Обновляем MINIAPP_URL
echo "🔗 Обновление MINIAPP_URL..."
sed -i 's|MINIAPP_URL=.*|MINIAPP_URL=http://147.45.215.199:8000|' .env

echo ""
echo "🐳 ШАГ 6: Сборка Docker образа"
echo "=========================================="

echo "🏗️  Сборка образа с нуля (без кэша)..."
docker-compose build --no-cache

echo "✅ Образ собран"

echo ""
echo "🚀 ШАГ 7: Запуск контейнера"
echo "=========================================="

echo "🚀 Запуск Docker контейнера..."
docker-compose up -d

echo "⏳ Ожидание запуска (30 сек)..."
sleep 30

echo ""
echo "🔍 ШАГ 8: Проверка статуса"
echo "=========================================="

echo "📊 Статус контейнера:"
docker-compose ps

echo ""
echo "📝 Последние логи:"
docker-compose logs --tail=50

echo ""
echo "=========================================="
echo "✅ ПОЛНОЕ ПЕРЕРАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=========================================="
echo ""
echo "📊 Что было сделано:"
echo "  ✅ Создан бэкап БД и файлов: $BACKUP_DIR"
echo "  ✅ Остановлены ВСЕ процессы (Docker, PM2, Python)"
echo "  ✅ ПОЛНОСТЬЮ удалена директория проекта"
echo "  ✅ Заново клонирован код из GitHub"
echo "  ✅ Восстановлена БД и файлы"
echo "  ✅ Собран Docker образ с нуля (без кэша)"
echo "  ✅ Запущен контейнер"
echo ""
echo "🔗 Проверьте работу:"
echo "  - Бот: https://t.me/NikolaevCodeBot"
echo "  - API: http://147.45.215.199:8000/docs"
echo "  - Mini App: http://147.45.215.199:8000"
echo "  - Админка: http://147.45.215.199:8001/admin/"
echo ""
echo "📝 Полезные команды:"
echo "  cd /var/www/bot_business_card"
echo "  docker-compose logs -f              # Смотреть логи"
echo "  docker-compose restart              # Перезапуск"
echo "  docker-compose down                 # Остановка"
echo "  docker-compose up -d                # Запуск"
echo ""
echo "💾 Бэкап сохранён: $BACKUP_DIR"
echo ""

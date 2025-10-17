#!/bin/bash

# 🐳 Скрипт деплоя через Docker на сервер
# Сохраняет БД и данные, обновляет только код

set -e

echo "=========================================="
echo "🐳 ДЕПЛОЙ ЧЕРЕЗ DOCKER"
echo "=========================================="

# Переменные
SERVER="root@147.45.215.199"
PROJECT_DIR="/var/www/bot_business_card"
REPO_URL="https://github.com/deathdaycome/MYBOTTZ.git"

echo ""
echo "📦 ШАГ 1: Подготовка на сервере"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"

# Проверяем Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo "Установите Docker: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Проверяем docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Установка docker-compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo "✅ Docker готов"
ENDSSH

echo ""
echo "💾 ШАГ 2: Бэкап БД (если есть)"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"
BACKUP_DIR="/root/backups/bot_$(date +%Y%m%d_%H%M%S)"

if [ -d "$PROJECT_DIR/data" ]; then
    echo "✅ Создание бэкапа БД..."
    mkdir -p $BACKUP_DIR
    cp -r $PROJECT_DIR/data $BACKUP_DIR/
    cp $PROJECT_DIR/.env $BACKUP_DIR/ 2>/dev/null || true
    echo "   Бэкап: $BACKUP_DIR"
else
    echo "⚠️  БД не найдена (первый запуск?)"
fi
ENDSSH

echo ""
echo "🛑 ШАГ 3: Остановка старых контейнеров"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"
cd $PROJECT_DIR 2>/dev/null || true

# Останавливаем и удаляем контейнеры
docker-compose down 2>/dev/null || docker stop bot-business-card 2>/dev/null || true
docker rm bot-business-card 2>/dev/null || true

# Останавливаем PM2 (если был старый деплой)
pm2 stop all 2>/dev/null || true
pm2 delete all 2>/dev/null || true

echo "✅ Старые процессы остановлены"
ENDSSH

echo ""
echo "📥 ШАГ 4: Обновление кода из GitHub"
echo "=========================================="
ssh $SERVER << ENDSSH
set -e

PROJECT_DIR="/var/www/bot_business_card"

# Сохраняем данные
if [ -d "\$PROJECT_DIR/data" ]; then
    echo "💾 Сохранение данных..."
    cp -r \$PROJECT_DIR/data /tmp/bot_data_backup
    cp \$PROJECT_DIR/.env /tmp/bot_env_backup 2>/dev/null || true
    cp -r \$PROJECT_DIR/uploads /tmp/bot_uploads_backup 2>/dev/null || true
fi

# Создаём/очищаем директорию
mkdir -p \$PROJECT_DIR
cd \$PROJECT_DIR

# Обновляем код
if [ -d ".git" ]; then
    echo "🔄 Обновление из Git..."
    git fetch origin
    git reset --hard origin/main
else
    echo "📦 Клонирование из GitHub..."
    cd /var/www
    rm -rf bot_business_card
    git clone $REPO_URL bot_business_card
    cd bot_business_card
fi

# Восстанавливаем данные
if [ -d "/tmp/bot_data_backup" ]; then
    echo "💾 Восстановление данных..."
    mkdir -p data uploads
    cp -r /tmp/bot_data_backup/* data/ 2>/dev/null || true
    cp /tmp/bot_env_backup .env 2>/dev/null || true
    cp -r /tmp/bot_uploads_backup/* uploads/ 2>/dev/null || true
    rm -rf /tmp/bot_data_backup /tmp/bot_env_backup /tmp/bot_uploads_backup
fi

# Проверяем .env
if [ ! -f ".env" ]; then
    echo "❌ .env файл не найден!"
    echo "Создайте .env файл с настройками"
    exit 1
fi

# Обновляем токен на правильный
sed -i 's/BOT_TOKEN=.*/BOT_TOKEN=7881909419:AAF_9TD2tZFOsQi2FThkyJt6ICjrWPny3JA/' .env

echo "✅ Код обновлён"
ENDSSH

echo ""
echo "🐳 ШАГ 5: Сборка Docker образа"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"
cd $PROJECT_DIR

echo "🏗️  Сборка образа..."
docker-compose build --no-cache

echo "✅ Образ собран"
ENDSSH

echo ""
echo "🚀 ШАГ 6: Запуск контейнера"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"
cd $PROJECT_DIR

# Создаём необходимые директории
mkdir -p data uploads logs

# Запускаем
echo "🚀 Запуск контейнера..."
docker-compose up -d

# Ждём запуска
echo "⏳ Ожидание запуска (30 сек)..."
sleep 30

echo "✅ Контейнер запущен"
ENDSSH

echo ""
echo "🔍 ШАГ 7: Проверка статуса"
echo "=========================================="
ssh $SERVER << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/bot_business_card"
cd $PROJECT_DIR

echo "📊 Статус контейнера:"
docker-compose ps

echo ""
echo "📝 Последние логи:"
docker-compose logs --tail=30

echo ""
echo "🏥 Healthcheck:"
docker inspect bot-business-card --format='{{.State.Health.Status}}' 2>/dev/null || echo "Healthcheck не доступен"
ENDSSH

echo ""
echo "=========================================="
echo "✅ ДЕПЛОЙ ЗАВЕРШЁН!"
echo "=========================================="
echo ""
echo "📊 Что было сделано:"
echo "  ✅ Создан бэкап БД"
echo "  ✅ Остановлены старые процессы"
echo "  ✅ Обновлён код из GitHub"
echo "  ✅ Собран Docker образ с Mini App"
echo "  ✅ Запущен контейнер"
echo ""
echo "🔗 Проверьте работу:"
echo "  - Бот: https://t.me/NikolaevCodeBot"
echo "  - API: http://147.45.215.199:8000/docs"
echo "  - Mini App: http://147.45.215.199:8000"
echo "  - Админка: http://147.45.215.199:8001/admin/"
echo ""
echo "📝 Полезные команды на сервере:"
echo "  docker-compose logs -f              # Смотреть логи"
echo "  docker-compose restart              # Перезапуск"
echo "  docker-compose down                 # Остановка"
echo "  docker-compose up -d                # Запуск"
echo ""

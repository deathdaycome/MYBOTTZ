#!/bin/bash

# Скрипт для запуска всех сервисов Mini App с постоянным URL
# Использует localhost.run для стабильного туннеля

set -e

PROJECT_DIR="/Users/ivan/Downloads/bot_business_card 2"
cd "$PROJECT_DIR"

echo "=========================================="
echo "  Запуск Mini App сервисов"
echo "=========================================="

# 1. Остановка существующих процессов
echo "1. Остановка существующих процессов..."
pkill -f cloudflared 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
pkill -f "ssh.*localhost.run" 2>/dev/null || true
sleep 2

# 2. Запуск Backend (FastAPI)
echo "2. Запуск Backend (FastAPI на порту 8000)..."
cd "$PROJECT_DIR"
python3 -m uvicorn app.main:app --reload --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "✓ Backend запущен (PID: $BACKEND_PID)"
sleep 3

# 3. Запуск Frontend (Vite)
echo "3. Запуск Frontend (Vite на порту 5173)..."
cd "$PROJECT_DIR/miniapp"
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✓ Frontend запущен (PID: $FRONTEND_PID)"
sleep 5

# 4. Запуск localhost.run туннеля с постоянным поддоменом
echo "4. Запуск localhost.run туннеля..."
# Используем ваш telegram username для создания уникального поддомена
SUBDOMAIN="laytraces-miniapp"
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -R ${SUBDOMAIN}:80:localhost:5173 nokey@localhost.run > /tmp/tunnel.log 2>&1 &
TUNNEL_PID=$!
echo "✓ Туннель запущен (PID: $TUNNEL_PID)"
sleep 8

# 5. Получение URL туннеля из логов
echo "5. Получение URL туннеля..."
TUNNEL_URL=$(grep -o "https://${SUBDOMAIN}\.lhr\.life" /tmp/tunnel.log | head -1)

if [ -z "$TUNNEL_URL" ]; then
    # Пробуем альтернативный формат
    TUNNEL_URL=$(grep -oE "https://[a-zA-Z0-9-]+\.lhr\.life" /tmp/tunnel.log | head -1)
fi

if [ -z "$TUNNEL_URL" ]; then
    echo "✗ Не удалось получить URL туннеля"
    echo "  Проверьте логи: tail -f /tmp/tunnel.log"
    echo ""
    echo "Попробуем запустить с Cloudflare tunnel вместо localhost.run..."

    # Fallback на Cloudflare
    pkill -f "ssh.*localhost.run" 2>/dev/null || true
    cloudflared tunnel --url http://localhost:5173 > /tmp/tunnel.log 2>&1 &
    TUNNEL_PID=$!
    sleep 6

    TUNNEL_URL=$(grep -oE "https://[a-zA-Z0-9-]+\.trycloudflare\.com" /tmp/tunnel.log | head -1)

    if [ -z "$TUNNEL_URL" ]; then
        echo "✗ Cloudflare tunnel тоже не запустился"
        exit 1
    fi

    echo "✓ Используем Cloudflare tunnel (нестабильный)"
fi

echo "✓ Туннель создан!"
echo ""
echo "=========================================="
echo "  ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!"
echo "=========================================="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Туннель:  ${TUNNEL_URL}"
echo ""
echo "=========================================="
echo "  ВАЖНО: Обновите URL в BotFather!"
echo "=========================================="
echo ""
echo "1. Откройте @BotFather в Telegram"
echo "2. /mybots → выберите бота → Bot Settings → Menu Button"
echo "3. Вставьте этот URL:"
echo ""
echo "${TUNNEL_URL}"
echo ""
echo "=========================================="
echo ""
echo "Логи:"
echo "  Backend:  tail -f /tmp/backend.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo "  Tunnel:   tail -f /tmp/tunnel.log"
echo ""
echo "Для остановки всех сервисов:"
echo "  pkill -f 'uvicorn|npm run dev|ssh.*localhost.run|cloudflared'"
echo ""

# Сохранение URL в файл
echo "$TUNNEL_URL" > /tmp/miniapp_tunnel_url.txt
echo "URL сохранён в /tmp/miniapp_tunnel_url.txt"
echo ""

# Показать URL в виде QR-кода для удобства (если установлен qrencode)
if command -v qrencode &> /dev/null; then
    echo "QR-код для быстрой вставки URL:"
    qrencode -t ANSIUTF8 "$TUNNEL_URL"
fi

echo "=========================================="
echo "  Готово! Теперь откройте Mini App в Telegram"
echo "=========================================="

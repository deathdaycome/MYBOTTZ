#!/bin/bash

# Скрипт для запуска всех сервисов Mini App
# Использование: ./start_miniapp.sh

set -e

PROJECT_DIR="/Users/ivan/Downloads/bot_business_card 2"
cd "$PROJECT_DIR"

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Запуск Mini App сервисов${NC}"
echo -e "${BLUE}========================================${NC}"

# 1. Остановка существующих процессов
echo -e "${BLUE}1. Остановка существующих процессов...${NC}"
pkill -f cloudflared 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
pkill -f ngrok 2>/dev/null || true
sleep 2

# 2. Запуск Backend (FastAPI)
echo -e "${BLUE}2. Запуск Backend (FastAPI на порту 8000)...${NC}"
cd "$PROJECT_DIR"
python3 -m uvicorn app.main:app --reload --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend запущен (PID: $BACKEND_PID)${NC}"
sleep 3

# 3. Запуск Frontend (Vite)
echo -e "${BLUE}3. Запуск Frontend (Vite на порту 5173)...${NC}"
cd "$PROJECT_DIR/miniapp"
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend запущен (PID: $FRONTEND_PID)${NC}"
sleep 5

# 4. Запуск ngrok туннеля
echo -e "${BLUE}4. Запуск ngrok туннеля...${NC}"
ngrok http 5173 --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!
echo -e "${GREEN}✓ ngrok запущен (PID: $NGROK_PID)${NC}"
sleep 5

# 5. Получение URL туннеля
echo -e "${BLUE}5. Получение URL туннеля...${NC}"
TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok-free\.app' | head -1)

if [ -z "$TUNNEL_URL" ]; then
    echo -e "${RED}✗ Не удалось получить URL туннеля${NC}"
    echo -e "${RED}  Проверьте логи: tail -f /tmp/ngrok.log${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Туннель создан!${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "Frontend: ${GREEN}http://localhost:5173${NC}"
echo -e "Туннель:  ${GREEN}${TUNNEL_URL}${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ВАЖНО: Обновите URL в BotFather!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "1. Откройте @BotFather в Telegram"
echo -e "2. /mybots → выберите бота → Bot Settings → Menu Button"
echo -e "3. Вставьте этот URL:"
echo ""
echo -e "${GREEN}${TUNNEL_URL}${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Логи:"
echo -e "  Backend:  ${BLUE}tail -f /tmp/backend.log${NC}"
echo -e "  Frontend: ${BLUE}tail -f /tmp/frontend.log${NC}"
echo -e "  ngrok:    ${BLUE}tail -f /tmp/ngrok.log${NC}"
echo ""
echo -e "Для остановки всех сервисов:"
echo -e "  ${RED}pkill -f 'uvicorn|npm run dev|ngrok'${NC}"
echo ""

# Сохранение URL в файл
echo "$TUNNEL_URL" > /tmp/miniapp_tunnel_url.txt
echo -e "${GREEN}URL сохранён в /tmp/miniapp_tunnel_url.txt${NC}"

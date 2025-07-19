#!/bin/bash

# Скрипт остановки бота
# Использование: ./stop_bot.sh

echo "🛑 Остановка Telegram-бота..."

# Поиск и остановка процесса
PID=$(ps aux | grep "python run.py" | grep -v grep | awk '{print $2}')

if [ -n "$PID" ]; then
    echo "📍 Найден процесс бота: PID $PID"
    kill $PID
    echo "✅ Бот остановлен"
else
    echo "❌ Процесс бота не найден"
fi

# Также проверяем uvicorn процессы
UVICORN_PID=$(ps aux | grep "uvicorn" | grep -v grep | awk '{print $2}')

if [ -n "$UVICORN_PID" ]; then
    echo "📍 Найден процесс uvicorn: PID $UVICORN_PID"
    kill $UVICORN_PID
    echo "✅ Uvicorn остановлен"
fi

echo "🏁 Все процессы остановлены"

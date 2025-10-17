#!/bin/bash

# Скрипт для полного перезапуска бота

echo "🛑 Останавливаем все процессы бота..."

# Убиваем все процессы Python
killall -9 Python 2>/dev/null
killall -9 python3 2>/dev/null
pkill -9 -f "run.py" 2>/dev/null
pkill -9 -f "uvicorn" 2>/dev/null

# Ждем чтобы все процессы завершились
sleep 3

echo "✅ Все процессы остановлены"

# Проверяем что ничего не осталось
REMAINING=$(ps aux | grep -E "python3.*run.py" | grep -v grep | wc -l)
if [ $REMAINING -gt 0 ]; then
    echo "⚠️ Внимание: остались запущенные процессы!"
    ps aux | grep -E "python3.*run.py" | grep -v grep
else
    echo "✅ Все процессы успешно остановлены"
fi

echo ""
echo "🚀 Запускаем бота..."
cd "$(dirname "$0")"
python3 run.py

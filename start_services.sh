#!/bin/bash

# Запуск миграций
echo "🔄 Запуск миграций..."
python3 migrations/add_revision_progress_timer.py 2>/dev/null || true
python3 migrations/add_task_attachments.py 2>/dev/null || true
python3 migrations/create_crm_tables.py 2>/dev/null || true

echo "✅ Миграции завершены"

# Запуск основного API + бота в фоне
echo "🚀 Запуск основного API на порту 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Запуск админки
echo "🎛️ Запуск админки на порту 8001..."
uvicorn app.admin.app:app --host 0.0.0.0 --port 8001 &
ADMIN_PID=$!

echo "✅ Сервисы запущены:"
echo "   - API (PID: $API_PID)"
echo "   - Admin (PID: $ADMIN_PID)"

# Функция для корректного завершения при получении сигнала
cleanup() {
    echo ""
    echo "🛑 Остановка сервисов..."
    kill $API_PID $ADMIN_PID 2>/dev/null
    wait $API_PID $ADMIN_PID 2>/dev/null
    echo "✅ Сервисы остановлены"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Ждём завершения процессов
wait $API_PID $ADMIN_PID

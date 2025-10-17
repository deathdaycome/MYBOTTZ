#!/bin/bash
# Автоматическая синхронизация пользователей и клиентов каждые 30 секунд

cd "$(dirname "$0")"

while true; do
    python3 sync_users_to_clients.py >> /tmp/client_sync.log 2>&1
    sleep 30
done

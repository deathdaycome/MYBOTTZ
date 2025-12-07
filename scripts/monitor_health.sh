#!/bin/bash
# ============================================
# Система мониторинга и автовосстановления
# ============================================

LOG_FILE="/var/log/crm-monitor.log"
TELEGRAM_BOT_TOKEN="${ADMIN_BOT_TOKEN}"
TELEGRAM_CHAT_ID="${ADMIN_CHAT_ID}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_alert() {
    local message="$1"
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            -d "text=🚨 CRM Alert: ${message}" \
            -d "parse_mode=HTML" > /dev/null
    fi
    log "ALERT: $message"
}

check_container_health() {
    local container_name="$1"
    local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null)

    if [ "$health_status" != "healthy" ]; then
        send_alert "Container $container_name is unhealthy (status: $health_status). Restarting..."
        docker restart "$container_name"
        sleep 30

        local new_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null)
        if [ "$new_status" = "healthy" ]; then
            send_alert "Container $container_name successfully recovered!"
        else
            send_alert "Container $container_name failed to recover! Manual intervention needed."
        fi
        return 1
    fi
    return 0
}

check_api_endpoint() {
    local url="$1"
    local name="$2"

    if ! curl -f -s -m 10 "$url" > /dev/null 2>&1; then
        send_alert "$name endpoint ($url) is not responding!"
        return 1
    fi
    return 0
}

check_disk_space() {
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -gt 80 ]; then
        send_alert "Disk space critical: ${usage}% used!"
        # Очистка старых логов
        find /var/www/bot_business_card/logs -name "*.log" -mtime +7 -delete
        find /var/lib/docker -name "*.log" -mtime +3 -delete
    fi
}

check_memory() {
    local mem_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    if [ "$mem_usage" -gt 85 ]; then
        send_alert "Memory usage critical: ${mem_usage}%!"
    fi
}

# Основной цикл мониторинга
log "Starting CRM monitoring system..."

while true; do
    # Проверка контейнеров
    check_container_health "bot-business-card"

    # Проверка эндпоинтов
    check_api_endpoint "http://localhost:8000/docs" "Main API"
    check_api_endpoint "http://localhost:8001/admin/api/users/me" "Admin API"

    # Проверка ресурсов
    check_disk_space
    check_memory

    # Ждем 60 секунд до следующей проверки
    sleep 60
done

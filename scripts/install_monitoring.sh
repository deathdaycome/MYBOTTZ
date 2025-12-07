#!/bin/bash
# ============================================
# Установка системы мониторинга на сервер
# ============================================

echo "🔧 Устанавливаем систему мониторинга CRM..."

# Создаем директории
mkdir -p /var/www/bot_business_card/backups/database
mkdir -p /var/log/crm

# Делаем скрипты исполняемыми
chmod +x /var/www/bot_business_card/scripts/monitor_health.sh
chmod +x /var/www/bot_business_card/scripts/backup_database.sh

# Добавляем cron задачи
echo "⏰ Настраиваем автоматические задачи..."

# Создаем временный файл с cron задачами
cat > /tmp/crm_cron << 'EOF'
# Backup базы данных каждый день в 3:00
0 3 * * * /var/www/bot_business_card/scripts/backup_database.sh >> /var/log/crm/backup.log 2>&1

# Backup базы данных каждые 6 часов (дополнительно)
0 */6 * * * /var/www/bot_business_card/scripts/backup_database.sh >> /var/log/crm/backup.log 2>&1

# Очистка старых логов каждую неделю
0 2 * * 0 find /var/www/bot_business_card/logs -name "*.log" -mtime +7 -delete
EOF

# Добавляем cron задачи
crontab -l 2>/dev/null | cat - /tmp/crm_cron | crontab -
rm /tmp/crm_cron

echo "✅ Cron задачи добавлены"

# Создаем systemd сервис для мониторинга
cat > /etc/systemd/system/crm-monitor.service << 'EOF'
[Unit]
Description=CRM Health Monitoring Service
After=docker.service
Requires=docker.service

[Service]
Type=simple
Restart=always
RestartSec=10
User=root
WorkingDirectory=/var/www/bot_business_card
ExecStart=/var/www/bot_business_card/scripts/monitor_health.sh
StandardOutput=append:/var/log/crm/monitor.log
StandardError=append:/var/log/crm/monitor.log

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd и запускаем сервис
systemctl daemon-reload
systemctl enable crm-monitor.service
systemctl start crm-monitor.service

echo "✅ Системный сервис мониторинга запущен"
echo ""
echo "📊 Статус:"
systemctl status crm-monitor.service --no-pager -l

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📝 Полезные команды:"
echo "  - Проверить статус: systemctl status crm-monitor"
echo "  - Посмотреть логи: journalctl -u crm-monitor -f"
echo "  - Ручной backup: /var/www/bot_business_card/scripts/backup_database.sh"
echo "  - Список backup: ls -lh /var/www/bot_business_card/backups/database/"

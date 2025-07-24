#!/bin/bash

# Скрипт для первоначальной настройки сервера Timeweb
# Запускать с правами sudo

set -e

echo "=== Настройка сервера для Bot Business Card ==="

# Обновляем систему
echo "Обновление системы..."
apt update && apt upgrade -y

# Устанавливаем необходимые пакеты
echo "Установка необходимых пакетов..."
apt install -y python3 python3-pip python3-venv git nginx supervisor curl postgresql-client

# Создаем пользователя для приложения (если не существует)
if ! id -u botuser > /dev/null 2>&1; then
    echo "Создание пользователя botuser..."
    useradd -m -s /bin/bash botuser
    usermod -aG www-data botuser
fi

# Создаем директории
echo "Создание директорий..."
mkdir -p /var/www/bot_business_card
mkdir -p /var/www/bot_business_card/logs
mkdir -p /var/www/bot_business_card/uploads
mkdir -p /var/log/supervisor

# Настраиваем права доступа
chown -R botuser:www-data /var/www/bot_business_card
chmod -R 755 /var/www/bot_business_card

# Клонируем репозиторий (если не существует)
if [ ! -d "/var/www/bot_business_card/.git" ]; then
    echo "Клонирование репозитория..."
    cd /var/www/bot_business_card
    # Замените на ваш реальный URL репозитория
    git clone https://github.com/yourusername/bot_business_card.git .
    chown -R botuser:www-data .
fi

# Создаем виртуальное окружение
echo "Создание виртуального окружения..."
cd /var/www/bot_business_card
sudo -u botuser python3 -m venv venv
sudo -u botuser ./venv/bin/pip install --upgrade pip

# Устанавливаем зависимости Python
echo "Установка зависимостей Python..."
sudo -u botuser ./venv/bin/pip install -r requirements.txt

# Создаем systemd service
echo "Создание systemd сервиса..."
cat > /etc/systemd/system/bot-business-card.service << 'EOF'
[Unit]
Description=Bot Business Card Application
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/var/www/bot_business_card
Environment=PATH=/var/www/bot_business_card/venv/bin
ExecStart=/var/www/bot_business_card/venv/bin/python -m app.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Настраиваем Nginx
echo "Настройка Nginx..."
cat > /etc/nginx/sites-available/bot-business-card << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # Замените на ваш домен
    
    client_max_body_size 100M;
    
    # Статические файлы
    location /static/ {
        alias /var/www/bot_business_card/app/admin/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Загруженные файлы
    location /uploads/ {
        alias /var/www/bot_business_card/uploads/;
        expires 7d;
    }
    
    # Проксирование к приложению
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Активируем сайт
ln -sf /etc/nginx/sites-available/bot-business-card /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Создаем logrotate конфигурацию
cat > /etc/logrotate.d/bot-business-card << 'EOF'
/var/www/bot_business_card/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 botuser www-data
    postrotate
        systemctl reload bot-business-card || true
    endscript
}
EOF

# Перезагружаем systemd и nginx
systemctl daemon-reload
systemctl enable bot-business-card
systemctl enable nginx
systemctl restart nginx

echo "=== Настройка сервера завершена ==="
echo ""
echo "Следующие шаги:"
echo "1. Скопируйте .env.production как .env и заполните переменные"
echo "2. Настройте GitHub Secrets для деплоя"
echo "3. Запустите первый деплой: systemctl start bot-business-card"
echo "4. Проверьте статус: systemctl status bot-business-card"
echo "5. Настройте SSL сертификат (Let's Encrypt)"
echo ""
echo "Полезные команды:"
echo "  systemctl status bot-business-card  # Статус сервиса"
echo "  systemctl restart bot-business-card # Перезапуск"
echo "  journalctl -u bot-business-card -f  # Просмотр логов"
echo "  tail -f /var/www/bot_business_card/logs/app.log  # Логи приложения"
#!/bin/bash

echo "🔧 Исправленная установка SSL для nikolaevcodev.ru"
echo "=================================================="

# Устанавливаем рабочую директорию
WORK_DIR="/var/www/bot_business_card"
cd $WORK_DIR

# Исправляем проблему с certbot (несовместимость pyOpenSSL)
echo "🔧 Исправление зависимостей certbot..."
pip3 install --upgrade pyOpenSSL cryptography 2>/dev/null || true

# Альтернативный способ: используем snap для установки certbot
echo "📦 Устанавливаем certbot через snap..."
apt remove certbot -y 2>/dev/null || true
snap install --classic certbot 2>/dev/null || {
    echo "⚠️ Snap не установлен, устанавливаем..."
    apt update
    apt install snapd -y
    snap install core
    snap refresh core
    snap install --classic certbot
}

# Создаем симлинк для certbot
ln -sf /snap/bin/certbot /usr/bin/certbot

# Останавливаем nginx если запущен
echo "⏸️ Останавливаем Nginx..."
systemctl stop nginx 2>/dev/null || true

# Останавливаем Docker контейнеры на портах 80 и 443
echo "🐳 Останавливаем Docker контейнеры..."
docker-compose down 2>/dev/null || true

# Получаем SSL сертификат
echo "🔐 Получение SSL сертификата от Let's Encrypt..."
certbot certonly --standalone \
    -d nikolaevcodev.ru \
    -d www.nikolaevcodev.ru \
    --non-interactive \
    --agree-tos \
    --email noldor123@yandex.ru \
    --preferred-challenges http

if [ $? -eq 0 ]; then
    echo "✅ SSL сертификат успешно получен!"
else
    echo "❌ Ошибка получения сертификата!"
    echo "Проверьте:"
    echo "  1. DNS настройки (nikolaevcodev.ru -> 147.45.215.199)"
    echo "  2. Порт 80 открыт и доступен"
    echo "  3. Нет других процессов на порту 80"
    exit 1
fi

# Копируем nginx конфигурацию из текущей директории
echo "📝 Настройка Nginx конфигурации..."
if [ -f "$WORK_DIR/nginx.conf" ]; then
    cp $WORK_DIR/nginx.conf /etc/nginx/sites-available/nikolaevcodev.ru
    echo "✅ Конфигурация скопирована"
else
    echo "❌ nginx.conf не найден в $WORK_DIR"
    echo "Создаём конфигурацию вручную..."

    cat > /etc/nginx/sites-available/nikolaevcodev.ru << 'NGINXCONF'
server {
    listen 80;
    server_name nikolaevcodev.ru www.nikolaevcodev.ru;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name nikolaevcodev.ru www.nikolaevcodev.ru;

    ssl_certificate /etc/letsencrypt/live/nikolaevcodev.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nikolaevcodev.ru/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 10M;

    # Mini App
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Статические файлы
    location /static/ {
        proxy_pass http://localhost:8000/static/;
    }

    location /uploads/ {
        proxy_pass http://localhost:8000/uploads/;
    }

    # Админка
    location /admin/ {
        proxy_pass http://localhost:8001/admin/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXCONF
    echo "✅ Конфигурация создана"
fi

# Удаляем дефолтную конфигурацию
rm -f /etc/nginx/sites-enabled/default

# Создаем символическую ссылку
ln -sf /etc/nginx/sites-available/nikolaevcodev.ru /etc/nginx/sites-enabled/

# Проверяем конфигурацию nginx
echo "✅ Проверка конфигурации Nginx..."
if nginx -t; then
    echo "✅ Конфигурация Nginx корректна"
else
    echo "❌ Ошибка в конфигурации Nginx!"
    exit 1
fi

# Запускаем nginx
echo "🚀 Запуск Nginx..."
systemctl start nginx
systemctl enable nginx

# Проверяем статус
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx успешно запущен"
else
    echo "❌ Nginx не запустился!"
    systemctl status nginx
    exit 1
fi

# Запускаем Docker контейнеры обратно
echo "🐳 Запуск Docker контейнеров..."
cd $WORK_DIR
docker-compose up -d

# Настраиваем автообновление сертификата
echo "🔄 Настройка автообновления сертификата..."
(crontab -l 2>/dev/null | grep -v certbot; echo "0 3 * * * certbot renew --quiet && systemctl reload nginx") | crontab -

echo ""
echo "=========================================="
echo "✅ SSL УСПЕШНО НАСТРОЕН!"
echo "=========================================="
echo ""
echo "🌐 Ваш сайт доступен по адресу:"
echo "   https://nikolaevcodev.ru"
echo ""
echo "🔍 Проверьте работу:"
echo "   curl -I https://nikolaevcodev.ru"
echo ""
echo "📋 Статус сертификата:"
certbot certificates
echo ""
echo "📊 Статус сервисов:"
echo "   Nginx: $(systemctl is-active nginx)"
echo "   Docker: $(docker-compose ps | grep Up | wc -l) контейнеров запущено"

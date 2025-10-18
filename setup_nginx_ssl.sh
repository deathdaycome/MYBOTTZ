#!/bin/bash

echo "🔧 Установка и настройка Nginx с SSL сертификатом..."

# Обновляем систему
echo "📦 Обновление системы..."
apt update

# Устанавливаем nginx
echo "📦 Установка Nginx..."
apt install -y nginx

# Устанавливаем certbot
echo "📦 Установка Certbot..."
apt install -y certbot python3-certbot-nginx

# Останавливаем nginx на время получения сертификата
echo "⏸️ Останавливаем Nginx..."
systemctl stop nginx

# Создаем директорию для certbot
mkdir -p /var/www/certbot

# Получаем SSL сертификат
echo "🔐 Получение SSL сертификата от Let's Encrypt..."
certbot certonly --standalone \
    -d nikolaevcodev.ru \
    -d www.nikolaevcodev.ru \
    --non-interactive \
    --agree-tos \
    --email noldor123@yandex.ru \
    --preferred-challenges http

# Копируем конфигурацию nginx
echo "📝 Копирование конфигурации Nginx..."
cp /root/bot_business_card/nginx.conf /etc/nginx/sites-available/nikolaevcodev.ru

# Удаляем дефолтную конфигурацию
rm -f /etc/nginx/sites-enabled/default

# Создаем символическую ссылку
ln -sf /etc/nginx/sites-available/nikolaevcodev.ru /etc/nginx/sites-enabled/

# Проверяем конфигурацию
echo "✅ Проверка конфигурации Nginx..."
nginx -t

# Запускаем nginx
echo "🚀 Запуск Nginx..."
systemctl start nginx
systemctl enable nginx

# Настраиваем автообновление сертификата
echo "🔄 Настройка автообновления сертификата..."
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet && systemctl reload nginx") | crontab -

echo "✅ Nginx с SSL успешно настроен!"
echo "🌐 Ваш сайт доступен по адресу: https://nikolaevcodev.ru"
echo ""
echo "📋 Полезные команды:"
echo "  - Проверить статус Nginx: systemctl status nginx"
echo "  - Перезапустить Nginx: systemctl restart nginx"
echo "  - Проверить сертификат: certbot certificates"
echo "  - Обновить сертификат вручную: certbot renew"

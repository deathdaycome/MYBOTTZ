# 🔐 Инструкция по настройке SSL и домена

## ✅ Что уже сделано:
1. Исправлена проблема с дублированием admin роутов
2. Добавлен домен nikolaevcodev.ru в настройки
3. Обновлены CORS настройки
4. Создана конфигурация Nginx с SSL
5. Код задеплоен на сервер через GitHub Actions

## 📋 Что нужно сделать:

### Шаг 1: Настройка SSL сертификата на сервере

Подключитесь к серверу по SSH и выполните:

```bash
ssh root@147.45.215.199
cd /root/bot_business_card
chmod +x setup_nginx_ssl.sh
./setup_nginx_ssl.sh
```

Скрипт автоматически:
- Установит Nginx
- Получит SSL сертификат от Let's Encrypt для nikolaevcodev.ru
- Настроит автообновление сертификата
- Запустит Nginx

### Шаг 2: Проверка работы

После установки SSL проверьте:

1. **HTTP редирект**: http://nikolaevcodev.ru → должен редиректить на HTTPS
2. **Mini App**: https://nikolaevcodev.ru → должен открыться Mini App
3. **API**: https://nikolaevcodev.ru/api/... → API эндпоинты
4. **Админка**: http://147.45.215.199:8001/admin/ → админ панель

### Шаг 3: Обновление URL в BotFather

1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/mybots`
3. Выберите вашего бота
4. Выберите **"Bot Settings"** → **"Menu Button"** → **"Configure Menu Button"**
5. Или **"Web App"** в настройках бота
6. Укажите URL: `https://nikolaevcodev.ru`

### Шаг 4: Обновление кнопки Mini App в боте

Если в коде бота есть кнопки WebApp, обновите URL:

```python
from telegram import WebAppInfo, KeyboardButton

# Было:
# button = KeyboardButton("Открыть Mini App", web_app=WebAppInfo(url="http://147.45.215.199:8000"))

# Стало:
button = KeyboardButton("Открыть Mini App", web_app=WebAppInfo(url="https://nikolaevcodev.ru"))
```

## 🔍 Проверка SSL сертификата

После установки можно проверить:

```bash
# Проверить статус Nginx
systemctl status nginx

# Посмотреть информацию о сертификате
certbot certificates

# Проверить сертификат вручную
openssl s_client -connect nikolaevcodev.ru:443 -servername nikolaevcodev.ru
```

## ⚙️ Полезные команды

```bash
# Перезапуск Nginx
systemctl restart nginx

# Просмотр логов Nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Обновление сертификата вручную
certbot renew

# Тестирование конфигурации Nginx
nginx -t
```

## 🐛 Решение проблем

### Если SSL не установился:

1. Проверьте, что домен указывает на правильный IP:
```bash
nslookup nikolaevcodev.ru
```

2. Проверьте, что порт 80 открыт:
```bash
ufw status
ufw allow 80
ufw allow 443
```

3. Попробуйте получить сертификат вручную:
```bash
certbot certonly --standalone -d nikolaevcodev.ru -d www.nikolaevcodev.ru
```

### Если Mini App не открывается:

1. Проверьте логи Docker:
```bash
docker-compose logs -f
```

2. Проверьте логи Nginx:
```bash
tail -f /var/log/nginx/error.log
```

3. Проверьте что контейнер запущен:
```bash
docker-compose ps
```

## 📞 Контакты

При возникновении проблем проверьте:
- DNS настройки домена (A-запись должна указывать на 147.45.215.199)
- Firewall на сервере (порты 80, 443 должны быть открыты)
- Статус Docker контейнера
- Логи приложения

# Руководство по развертыванию на Timeweb

Это руководство поможет вам настроить автоматический деплой вашего бота на сервер Timeweb с использованием GitHub Actions.

## 📋 Предварительные требования

1. **Сервер Timeweb** с Ubuntu/Debian
2. **GitHub репозиторий** с вашим кодом
3. **Доступ к серверу по SSH** с использованием ключей
4. **Домен** (опционально, для SSL)

## 🚀 Пошаговая настройка

### Шаг 1: Подготовка сервера

1. **Подключитесь к серверу по SSH:**
   ```bash
   ssh root@your-server-ip
   ```

2. **Скачайте и запустите скрипт настройки:**
   ```bash
   wget https://raw.githubusercontent.com/yourusername/bot_business_card/main/scripts/setup_server.sh
   chmod +x setup_server.sh
   sudo ./setup_server.sh
   ```

3. **Настройте переменные окружения:**
   ```bash
   cd /var/www/bot_business_card
   cp .env.production .env
   nano .env
   ```

   Заполните следующие обязательные переменные:
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   SECRET_KEY=your_secure_secret_key_here
   ADMIN_PASSWORD=your_secure_admin_password_here
   DATABASE_URL=your_database_url_here
   BASE_URL=https://your-domain.com
   ```

### Шаг 2: Настройка базы данных

#### Вариант A: PostgreSQL в облаке (рекомендуется)

1. **Создайте облачную базу данных** (например, на Timeweb, AWS RDS, или DigitalOcean)

2. **Получите строку подключения:**
   ```
   postgresql://username:password@host:port/database_name
   ```

3. **Добавьте в .env:**
   ```bash
   DATABASE_URL=postgresql://username:password@host:port/database_name
   ```

#### Вариант B: Локальная PostgreSQL

1. **Установите PostgreSQL:**
   ```bash
   sudo apt install postgresql postgresql-contrib
   ```

2. **Создайте базу данных:**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE bot_business_card;
   CREATE USER botuser WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE bot_business_card TO botuser;
   \q
   ```

3. **Добавьте в .env:**
   ```bash
   DATABASE_URL=postgresql://botuser:secure_password@localhost:5432/bot_business_card
   ```

### Шаг 3: Настройка облачного хранилища (опционально)

Для хранения файлов в облаке добавьте в `.env`:

```bash
STORAGE_TYPE=cloud
CLOUD_STORAGE_BUCKET=your-bucket-name
CLOUD_STORAGE_REGION=us-east-1
CLOUD_STORAGE_ACCESS_KEY=your-access-key
CLOUD_STORAGE_SECRET_KEY=your-secret-key
```

### Шаг 4: Настройка GitHub Secrets

В вашем GitHub репозитории перейдите в **Settings → Secrets and variables → Actions** и добавьте:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `TIMEWEB_HOST` | IP адрес сервера | `192.168.1.100` |
| `TIMEWEB_USERNAME` | Имя пользователя для SSH | `root` |
| `TIMEWEB_SSH_KEY` | Приватный SSH ключ | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `TIMEWEB_SSH_PORT` | Порт SSH (обычно 22) | `22` |

#### Создание SSH ключа:

```bash
# На локальной машине
ssh-keygen -t rsa -b 4096 -C "github-actions"

# Скопируйте публичный ключ на сервер
ssh-copy-id -i ~/.ssh/id_rsa.pub root@your-server-ip

# Скопируйте приватный ключ в GitHub Secrets
cat ~/.ssh/id_rsa
```

### Шаг 5: Настройка Nginx и SSL

1. **Обновите конфигурацию Nginx:**
   ```bash
   sudo nano /etc/nginx/sites-available/bot-business-card
   ```

   Замените `your-domain.com` на ваш реальный домен.

2. **Установите SSL сертификат:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

3. **Перезапустите Nginx:**
   ```bash
   sudo systemctl restart nginx
   ```

### Шаг 6: Первый запуск

1. **Запустите сервис:**
   ```bash
   sudo systemctl start bot-business-card
   sudo systemctl status bot-business-card
   ```

2. **Проверьте логи:**
   ```bash
   journalctl -u bot-business-card -f
   ```

3. **Проверьте доступность:**
   ```bash
   curl http://localhost:8001/
   curl https://your-domain.com/
   ```

## 🔄 Автоматический деплой

После настройки каждый push в ветку `main` будет автоматически деплоить обновления на сервер.

Процесс деплоя:
1. GitHub Actions получает код
2. Устанавливает зависимости
3. Подключается к серверу по SSH
4. Обновляет код из git
5. Перезапускает приложение
6. Проверяет что всё работает

## 📊 Мониторинг

### Полезные команды:

```bash
# Статус сервиса
sudo systemctl status bot-business-card

# Просмотр логов приложения
tail -f /var/www/bot_business_card/logs/app.log

# Просмотр системных логов
journalctl -u bot-business-card -f

# Перезапуск сервиса
sudo systemctl restart bot-business-card

# Проверка процессов
ps aux | grep python

# Проверка портов
netstat -tlnp | grep 8001
```

### Логи находятся в:
- **Приложение:** `/var/www/bot_business_card/logs/app.log`
- **Nginx:** `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **Systemd:** `journalctl -u bot-business-card`

## 🛠 Разработка локально

Для разработки локально используйте:

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Копирование конфигурации
cp .env.example .env
# Отредактируйте .env для локальной разработки

# Запуск приложения
python -m app.main
```

## 🚨 Устранение неполадок

### Приложение не запускается:
1. Проверьте логи: `journalctl -u bot-business-card -f`
2. Проверьте конфигурацию: `cat /var/www/bot_business_card/.env`
3. Проверьте права доступа: `ls -la /var/www/bot_business_card/`

### База данных недоступна:
1. Проверьте строку подключения в `.env`
2. Проверьте доступность БД: `pg_isready -h host -p port`
3. Проверьте права пользователя БД

### GitHub Actions не может подключиться:
1. Проверьте SSH ключи в Secrets
2. Проверьте IP адрес сервера
3. Проверьте порт SSH

### Nginx показывает 502 Bad Gateway:
1. Проверьте что приложение запущено: `curl http://localhost:8001/`
2. Проверьте конфигурацию Nginx
3. Проверьте логи Nginx: `tail -f /var/log/nginx/error.log`

## 📞 Поддержка

Если у вас возникли проблемы:
1. Проверьте логи (команды выше)
2. Убедитесь что все переменные окружения заданы
3. Проверьте что сервисы запущены
4. Создайте issue в GitHub репозитории
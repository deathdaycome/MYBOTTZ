# 📚 Инструкция по настройке автоматического деплоя

## 🚀 Быстрый старт

После настройки вы сможете деплоить одной командой:
```bash
./scripts/deploy.sh
```

## 📋 Настройка с нуля

### 1. На сервере

1. **Подключитесь к серверу по SSH:**
```bash
ssh user@your-server.com
```

2. **Клонируйте репозиторий (если еще не клонирован):**
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/bot_business_card.git
cd bot_business_card
```

3. **Создайте виртуальное окружение:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Скопируйте файл окружения:**
```bash
cp .env.example .env
nano .env  # Отредактируйте переменные
```

5. **Настройте systemd сервис:**
```bash
chmod +x scripts/setup_service.sh
sudo ./scripts/setup_service.sh
```

### 2. В GitHub репозитории

1. **Перейдите в Settings → Secrets and variables → Actions**

2. **Добавьте следующие секреты:**

   - `SERVER_HOST` - IP адрес или домен вашего сервера
   - `SERVER_USER` - имя пользователя для SSH (например, `root` или `ubuntu`)
   - `SERVER_PORT` - SSH порт (обычно `22`)
   - `SERVER_SSH_KEY` - приватный SSH ключ для доступа к серверу

3. **Как получить SSH ключ:**
```bash
# На локальной машине
cat ~/.ssh/id_rsa  # или другой ваш приватный ключ
# Скопируйте содержимое и вставьте в GitHub Secret
```

### 3. На локальной машине

1. **Сделайте скрипт деплоя исполняемым:**
```bash
chmod +x scripts/deploy.sh
```

2. **Настройте git (если не настроен):**
```bash
git remote add origin https://github.com/YOUR_USERNAME/bot_business_card.git
```

## 🔄 Процесс деплоя

### Автоматический деплой (рекомендуется)

1. **Внесите изменения в код**
2. **Запустите скрипт деплоя:**
```bash
./scripts/deploy.sh
```
3. **Скрипт автоматически:**
   - Проверит незакоммиченные изменения
   - Предложит их закоммитить
   - Отправит на GitHub
   - GitHub Actions автоматически задеплоит на сервер

### Ручной деплой

1. **Закоммитьте изменения:**
```bash
git add .
git commit -m "Ваше сообщение"
```

2. **Отправьте на GitHub:**
```bash
git push origin main
```

3. **GitHub Actions автоматически выполнит деплой**

### Деплой через GitHub UI

1. Перейдите в раздел **Actions** в вашем репозитории
2. Выберите workflow **Deploy to Server**
3. Нажмите **Run workflow**
4. Выберите ветку и нажмите **Run workflow**

## 📊 Мониторинг

### Проверка статуса на сервере:
```bash
sudo systemctl status botdev
```

### Просмотр логов:
```bash
# Системные логи
sudo journalctl -u botdev -f

# Логи приложения
tail -f /var/log/botdev/output.log
tail -f /var/log/botdev/error.log

# Логи бота
tail -f ~/bot_business_card/logs/$(ls -t ~/bot_business_card/logs/ | head -1)
```

### Перезапуск вручную:
```bash
sudo systemctl restart botdev
```

## 🔧 Решение проблем

### Если деплой не работает:

1. **Проверьте GitHub Actions:**
   - Перейдите в Actions в вашем репозитории
   - Посмотрите логи последнего запуска

2. **Проверьте SSH доступ:**
```bash
ssh user@your-server.com "echo 'SSH работает'"
```

3. **Проверьте права на файлы:**
```bash
# На сервере
cd ~/bot_business_card
ls -la
# Убедитесь, что у вашего пользователя есть права
```

4. **Проверьте сервис:**
```bash
sudo systemctl status botdev
sudo journalctl -u botdev -n 50
```

## 📝 Дополнительные команды

### Откат к предыдущей версии:
```bash
# На сервере
cd ~/bot_business_card
git log --oneline -5  # Посмотреть последние коммиты
git checkout <commit-hash>  # Откатиться к нужному коммиту
sudo systemctl restart botdev
```

### Обновление зависимостей:
```bash
# На сервере
cd ~/bot_business_card
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart botdev
```

### Очистка логов:
```bash
# На сервере
sudo truncate -s 0 /var/log/botdev/output.log
sudo truncate -s 0 /var/log/botdev/error.log
```

## 🔄 PM2 Деплой (текущая конфигурация)

После `git pull` на сервере:

```bash
cd /var/www/bot_business_card

# 1. Установить зависимости
source venv/bin/activate
pip install -r requirements.txt

# 2. Перезапустить PM2 с обновленной конфигурацией
pm2 delete bot-business-card
pm2 start ecosystem.config.js
pm2 save

# 3. Проверить статус
pm2 status
pm2 logs bot-business-card --lines 20
```

### Проверка переменных окружения:

```bash
# Убедитесь, что .env файл существует и содержит правильные токены
cat /var/www/bot_business_card/.env | grep BOT_TOKEN

# Проверьте, что процесс видит токен
cat /proc/$(pgrep -f "python.*run.py")/environ | tr '\0' '\n' | grep BOT_TOKEN
```

### ⚠️ Важно:

- Файл `.env` НЕ должен быть в git (он в `.gitignore`)
- Используйте `.env.example` как шаблон
- Всегда проверяйте логи после деплоя: `pm2 logs bot-business-card`
- PM2 должен использовать `ecosystem.config.js` для правильной загрузки переменных окружения

## 🎯 Готово!

Теперь каждый раз, когда вы запускаете `./scripts/deploy.sh` или пушите в main ветку, ваш бот автоматически обновляется на сервере!
# 🎯 Настройка Webhook для автоматического деплоя

## 📋 Шаг 1: Установка webhook сервера на сервер

### 1.1 Подключаемся к серверу и создаем директории:
```bash
ssh root@77.232.142.158
mkdir -p /var/www/webhook
cd /var/www/webhook
```

### 1.2 Копируем скрипт webhook:
```bash
# Скопируй содержимое scripts/deploy_webhook.py на сервер
nano deploy_webhook.py
# Вставь код и сохрани (Ctrl+X, Y, Enter)
```

### 1.3 Устанавливаем Flask:
```bash
pip3 install --user flask
```

### 1.4 Делаем скрипт исполняемым:
```bash
chmod +x deploy_webhook.py
```

### 1.5 Создаем системный сервис:
```bash
cat > /etc/systemd/system/webhook.service << 'EOF'
[Unit]
Description=Deploy Webhook Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/webhook
ExecStart=/usr/bin/python3 deploy_webhook.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### 1.6 Запускаем webhook сервис:
```bash
systemctl daemon-reload
systemctl enable webhook
systemctl start webhook
systemctl status webhook
```

### 1.7 Проверяем что webhook работает:
```bash
curl http://localhost:9999/status
```

## 📋 Шаг 2: Настройка GitHub Webhook

### 2.1 Переходим в GitHub репозиторий:
- Открываем https://github.com/deathdaycome/MYBOTTZ
- Переходим в **Settings** → **Webhooks**
- Нажимаем **Add webhook**

### 2.2 Заполняем настройки:
- **Payload URL**: `http://77.232.142.158:9999/webhook`
- **Content type**: `application/json`
- **Secret**: `your-webhook-secret-key-2024`
- **Which events**: Just the push event
- **Active**: ✅ Включено

### 2.3 Сохраняем webhook

## 📋 Шаг 3: Тестирование

### 3.1 Делаем тестовый коммит:
```bash
# Из локальной папки проекта
echo "# Webhook test" >> README.md
git add .
git commit -m "Test webhook deployment"
git push origin main
```

### 3.2 Проверяем логи webhook:
```bash
# На сервере
journalctl -u webhook -f
```

### 3.3 Проверяем статус приложения:
```bash
curl http://77.232.142.158:9999/status
```

## 🔧 Отладка

### Проверка процессов:
```bash
# Webhook сервис
systemctl status webhook

# Приложение бота
screen -list
pgrep -f python
```

### Проверка логов:
```bash
# Логи webhook
journalctl -u webhook --no-pager -l

# Логи приложения
tail -f /var/www/bot_business_card/app.log
```

### Ручной запуск деплоя:
```bash
curl -X POST http://localhost:9999/webhook \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=test" \
  -d '{"ref": "refs/heads/main", "pusher": {"name": "test"}}'
```

## ✅ Готово!

После настройки каждый `git push` в ветку `main` будет автоматически запускать деплой на сервере!

Проверить можно по адресу: http://77.232.142.158:8000/
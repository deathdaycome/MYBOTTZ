# 🚀 Инструкция по развертыванию бота на TimeWeb

## 📦 Подготовка файлов

Все необходимые файлы уже скопированы в эту папку `deploy_to_timeweb/`.

## 🔧 Установка на сервере TimeWeb

### 1. Загрузка файлов
Загрузите все файлы из папки `deploy_to_timeweb/` на ваш сервер через:
- FileZilla (FTP/SFTP)
- Панель управления TimeWeb
- SCP команду: `scp -r deploy_to_timeweb/* user@your-server.com:/path/to/project/`

### 2. Настройка окружения
```bash
# Подключитесь к серверу по SSH
ssh user@your-server.com

# Перейдите в папку проекта
cd /path/to/project/

# Сделайте скрипты исполняемыми
chmod +x start_bot.sh stop_bot.sh

# Скопируйте пример .env файла
cp .env.example .env

# Отредактируйте .env файл
nano .env
```

### 3. Заполните .env файл
Обязательно измените следующие параметры в файле `.env`:

```bash
# Ваш токен бота от @BotFather
BOT_TOKEN=1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

# Username вашего бота (без @)
BOT_USERNAME=your_bot_username

# Надежный пароль для админ-панели
ADMIN_PASSWORD=your_secure_password_123

# Секретный ключ (сгенерируйте случайную строку)
SECRET_KEY=your_random_secret_key_here

# OpenAI API ключ (если используете)
OPENAI_API_KEY=sk-your_openai_key_here
```

### 4. Запуск бота
```bash
# Запуск бота
./start_bot.sh
```

### 5. Проверка работы
- Админ-панель: `http://your-server-ip:8001`
- Логи: `tail -f logs/app.log`
- Процессы: `ps aux | grep python`

### 6. Остановка бота
```bash
# Остановка бота
./stop_bot.sh
```

## 🔧 Настройка автозапуска (опционально)

### Создание systemd сервиса:
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Telegram Bot Business Card
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/project
ExecStart=/path/to/project/start_bot.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация сервиса:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

## 📋 Структура проекта на сервере

```
project/
├── app/                 # Основное приложение
├── data/               # База данных SQLite
├── uploads/            # Загруженные файлы
├── logs/               # Логи (создается автоматически)
├── venv/               # Виртуальная среда (создается автоматически)
├── requirements.txt    # Зависимости Python
├── run.py             # Файл запуска
├── .env               # Конфигурация (создать из .env.example)
├── .env.example       # Пример конфигурации
├── start_bot.sh       # Скрипт запуска
├── stop_bot.sh        # Скрипт остановки
└── README_DEPLOY.md   # Эта инструкция
```

## 🐛 Устранение неполадок

### Бот не запускается:
1. Проверьте .env файл
2. Проверьте логи: `tail -f logs/app.log`
3. Проверьте порт 8001: `netstat -tlnp | grep 8001`

### Админ-панель недоступна:
1. Проверьте что порт 8001 открыт в файрволе
2. Убедитесь что HOST=0.0.0.0 в .env
3. Проверьте процессы: `ps aux | grep python`

### База данных не работает:
1. Проверьте права доступа к папке data/
2. Убедитесь что SQLite установлен
3. Попробуйте пересоздать БД: удалите data/bot.db и перезапустите

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи в папке logs/
2. Убедитесь что все зависимости установлены
3. Проверьте права доступа к файлам
4. Проверьте настройки фаерволла

## ✅ Проверочный список

- [ ] Все файлы загружены на сервер
- [ ] Создан файл .env с правильными настройками
- [ ] Скрипты имеют права на выполнение
- [ ] Python 3.8+ установлен на сервере
- [ ] Порт 8001 открыт в фаерволе
- [ ] Бот зарегистрирован у @BotFather
- [ ] Токен бота правильный
- [ ] Админ-панель доступна
- [ ] Telegram-бот отвечает на команды

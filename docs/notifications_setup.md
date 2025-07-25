# Настройка системы уведомлений

## Быстрая настройка

### 1. Настройка переменных окружения

Добавьте в файл `.env`:

```env
# Telegram Bot Token (получить у @BotFather)
BOT_TOKEN=your_bot_token_here

# ID чата администратора для уведомлений
# Получить можно, написав боту @userinfobot
NOTIFICATION_CHAT_ID=your_admin_chat_id
```

### 2. Получение BOT_TOKEN

1. Перейдите к @BotFather в Telegram
2. Создайте нового бота командой `/newbot`
3. Следуйте инструкциям и получите токен
4. Добавьте токен в переменную `BOT_TOKEN`

### 3. Получение NOTIFICATION_CHAT_ID

1. Перейдите к @userinfobot в Telegram
2. Отправьте команду `/start`
3. Скопируйте ваш ID из ответа
4. Добавьте ID в переменную `NOTIFICATION_CHAT_ID`

### 4. Тестирование

После настройки переменных окружения:

1. Перезапустите админ-панель
2. Перейдите на страницу "Уведомления" в админке
3. Нажмите "Тестовое уведомление"
4. Проверьте получение сообщения в Telegram

## Проверка настроек

Запустите тестовый скрипт:

```bash
python test_notifications.py
```

Если настройки корректны, вы должны получить уведомления в Telegram.

## Создание тестовых данных

Если в базе нет тестовых данных, запустите:

```bash
python add_test_data.py
```

## Возможные проблемы

### "Chat not found"
- Проверьте корректность NOTIFICATION_CHAT_ID
- Убедитесь, что бот может писать в чат

### "Unauthorized"
- Проверьте корректность BOT_TOKEN
- Убедитесь, что токен активен

### "Forbidden"
- Бот заблокирован пользователем
- Добавьте бота в чат или разблокируйте

## Дополнительные настройки

### Отключение уведомлений
Оставьте NOTIFICATION_CHAT_ID пустым для отключения уведомлений.

### Групповые уведомления
Добавьте бота в группу и используйте ID группы как NOTIFICATION_CHAT_ID.

### Логирование
Все уведомления логируются в файл `logs/bot.log`.

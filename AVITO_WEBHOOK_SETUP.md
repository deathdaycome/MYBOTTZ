# Настройка Avito Webhook для real-time обновлений

## 🎯 Что это дает

Вместо постоянного опроса Avito API каждые 30 секунд, система будет получать **мгновенные уведомления** о новых сообщениях через webhook. Это означает:

- ✅ **Мгновенные уведомления** - сообщения появляются сразу же
- ✅ **Экономия ресурсов** - меньше запросов к API
- ✅ **Лучший UX** - не нужно перезагружать страницу
- ✅ **Звуковые уведомления** при получении новых сообщений

## 🚀 Быстрая настройка

### Способ 1: Автоматический скрипт (рекомендуемый)

```bash
# В корневой папке проекта
./setup_webhook.sh
```

Выберите пункт `1` для настройки webhook.

### Способ 2: Ручная настройка

```bash
# Настроить webhook
python3 setup_avito_webhook.py setup

# Отключить webhook (если нужно)
python3 setup_avito_webhook.py unsubscribe

# Тестировать endpoint
python3 setup_avito_webhook.py test
```

## ⚙️ Требования

### Переменные окружения

Убедитесь что у вас настроены:

```env
# Основные настройки Avito
AVITO_CLIENT_ID=your_client_id
AVITO_CLIENT_SECRET=your_client_secret
AVITO_USER_ID=your_user_id

# Домен для webhook (без http/https)
DOMAIN=yourdomain.com
```

### Доступность сервера

Webhook endpoint должен быть доступен по адресу:
```
https://yourdomain.com/admin/avito/webhook
```

⚠️ **Важно:** Сервер должен отвечать в течение 2 секунд, иначе Avito отключит webhook.

## 🔧 Техническая информация

### Что происходит при настройке

1. Скрипт регистрирует URL `https://yourdomain.com/admin/avito/webhook` в Avito API
2. Avito начинает отправлять POST запросы с данными о новых сообщениях
3. Сервер обрабатывает webhook и отправляет обновления через WebSocket
4. Frontend получает мгновенные обновления без перезагрузки

### Структура webhook события

```json
{
  "message": {
    "id": "msg_id",
    "chat_id": "chat_id", 
    "author_id": 12345,
    "content": {
      "text": "Текст сообщения"
    },
    "created": 1692808800,
    "type": "text"
  }
}
```

### Endpoints

- `POST /admin/avito/webhook` - Получение webhook от Avito
- `GET /admin/avito/webhook/status` - Проверка статуса webhook
- `WS /admin/avito/ws` - WebSocket для real-time обновлений

## 🐛 Устранение проблем

### Webhook не работает

1. **Проверьте доступность endpoint:**
   ```bash
   curl -X POST https://yourdomain.com/admin/avito/webhook \
        -H "Content-Type: application/json" \
        -d '{"test": "message"}'
   ```

2. **Убедитесь в правильности переменных окружения:**
   ```bash
   python3 -c "from app.config.settings import settings; print(f'Domain: {settings.DOMAIN}')"
   ```

3. **Проверьте логи сервера на наличие ошибок**

### WebSocket не подключается

1. Убедитесь что сервер поддерживает WebSocket
2. Проверьте firewall правила
3. Откройте Developer Tools → Network → WS для отладки

### Avito отключил webhook

Частые причины:
- Сервер отвечает дольше 2 секунд
- Endpoint возвращает ошибки 4xx/5xx  
- Сервер недоступен

**Решение:** Перерегистрируйте webhook:
```bash
python3 setup_avito_webhook.py unsubscribe
python3 setup_avito_webhook.py setup
```

## 📊 Мониторинг

### Проверка статуса

```bash
# Статус webhook endpoint
curl https://yourdomain.com/admin/avito/webhook/status

# Количество WebSocket подключений
# Смотрите в ответе поле "websocket_connections"
```

### Логи

Webhook события записываются в стандартные логи приложения:
- `app.admin.routers.avito` - обработка webhook
- `app.services.avito_service` - взаимодействие с Avito API

## ✅ Проверка работы

После настройки:

1. Откройте админ-панель: `https://yourdomain.com/admin/avito/`
2. Должно появиться уведомление: "🔗 Real-time обновления включены"
3. Попросите кого-то написать вам в Avito
4. Сообщение должно появиться **мгновенно** без перезагрузки

## 🔄 Откат к старой системе

Если возникли проблемы, можно вернуться к polling:

```bash
python3 setup_avito_webhook.py unsubscribe
```

Система автоматически переключится на опрос каждые 30 секунд.

---

**💡 Подсказка:** После успешной настройки webhook, страница будет автоматически останавливать таймерные обновления и использовать только real-time данные.
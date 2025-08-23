# Исправление Internal Server Error на странице /clients

## Проблема
Страница `/clients` выдавала Internal Server Error из-за несоответствия между моделью Client в коде и структурой таблицы в базе данных. SQLAlchemy не видел новые Avito поля.

## Решение
Выполните на сервере следующие команды:

### 1. Обновите код из репозитория
```bash
cd /path/to/your/project
git pull origin main
```

### 2. Запустите скрипт исправления таблицы
```bash
python3 fix_clients_table.py
```

### 3. Перезапустите сервис
```bash
sudo systemctl restart bot-admin
# или если используете другой способ запуска:
# sudo systemctl restart your-service-name
```

### 4. Проверьте работу
Откройте в браузере страницу клиентов и убедитесь, что она загружается без ошибок:
- `http://your-domain.com/admin/clients`

## Что делает скрипт исправления

1. **Проверяет** текущую структуру таблицы clients
2. **Сохраняет** все существующие данные клиентов
3. **Удаляет** старую таблицу clients
4. **Пересоздаёт** таблицу с новыми Avito полями:
   - `avito_chat_id` - ID чата в Avito
   - `avito_user_id` - ID пользователя в Avito  
   - `avito_status` - статус клиента в Avito (HOT_LEAD, WARM_CONTACT, etc.)
   - `avito_dialog_history` - история диалога в Avito
   - `avito_notes` - заметки по Avito клиенту
   - `avito_follow_up` - напоминание о следующем контакте
5. **Восстанавливает** все данные клиентов

## Альтернативный способ (если скрипт не работает)

Если автоматический скрипт не сработает, выполните вручную:

```python
python3 -c "
from app.database.database import engine
from app.database.crm_models import Client
from sqlalchemy import MetaData, inspect

# Удаляем и пересоздаём таблицу
metadata = MetaData()
metadata.reflect(bind=engine, only=['clients'])
if 'clients' in metadata.tables:
    metadata.tables['clients'].drop(bind=engine)
Client.__table__.create(bind=engine)
print('Таблица clients пересоздана успешно')
"
```

## Проверка результата

После выполнения исправления страница `/clients` должна:
- ✅ Загружаться без Internal Server Error
- ✅ Показывать список клиентов
- ✅ Поддерживать интеграцию с Avito (когда клиенты будут добавлены через Avito мессенджер)

## Важно

⚠️ **Все данные клиентов сохраняются** при выполнении исправления, но рекомендуется сделать резервную копию базы данных перед выполнением:

```bash
cp admin_panel.db admin_panel.db.backup.$(date +%Y%m%d_%H%M%S)
```
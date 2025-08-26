# Инструкция по исправлению базы данных на сервере

## Проблема
Ошибки 500 на страницах лидов и клиентов:
```
no such column: clients.avito_chat_id
no such column: leads.source_type
```

## Решение - выполните на сервере:

### Вариант 1: Автоматический скрипт
```bash
# Подключитесь к серверу по SSH и выполните:
cd /var/www/bot_business_card
chmod +x fix_db_manual.sh
./fix_db_manual.sh
```

### Вариант 2: Ручные команды

```bash
# 1. Подключитесь к серверу
ssh root@YOUR_SERVER

# 2. Перейдите в директорию проекта
cd /var/www/bot_business_card

# 3. Найдите базу данных
find . -name "*.db" -type f

# 4. Выполните исправление (замените DATABASE_FILE на реальный путь)
python3 -c "
import sqlite3

# Подключение к базе данных (измените путь если нужно)
db_paths = ['app.db', 'business_card_bot.db', 'data/app.db', 'data/bot.db']
db_path = None

for path in db_paths:
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" LIMIT 1')
        if cursor.fetchone():
            db_path = path
            print(f'Используем базу: {path}')
            break
    except:
        continue

if not db_path:
    print('База данных не найдена!')
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Добавляем колонки в таблицу clients
client_columns = ['avito_chat_id', 'avito_user_id', 'avito_status', 'avito_dialog_history', 'avito_notes', 'avito_follow_up', 'telegram_user_id']

for column in client_columns:
    try:
        cursor.execute(f'ALTER TABLE clients ADD COLUMN {column} TEXT')
        print(f'Добавлена колонка clients.{column}')
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e):
            print(f'Колонка clients.{column} уже существует')
        else:
            print(f'Ошибка для {column}: {e}')

# Добавляем колонку в таблицу leads
try:
    cursor.execute('ALTER TABLE leads ADD COLUMN source_type TEXT')
    print('Добавлена колонка leads.source_type')
except sqlite3.OperationalError as e:
    if 'duplicate column' in str(e):
        print('Колонка leads.source_type уже существует')
    else:
        print(f'Ошибка: {e}')

conn.commit()
conn.close()
print('✅ База данных обновлена!')
"

# 5. Перезапустите приложение
pm2 restart bot-business-card
```

### Вариант 3: Если ничего не помогает

```bash
# Создайте новую базу данных
cd /var/www/bot_business_card
python3 -c "
from app.database.database import init_db
init_db()
print('База данных пересоздана')
"

# Перезапустите
pm2 restart bot-business-card
```

## Проверка результата

После выполнения команд проверьте:
1. Откройте страницу лидов: `http://your-server:8001/admin/leads`
2. Откройте страницу клиентов: `http://your-server:8001/admin/clients`
3. Они должны открываться без ошибок 500

## Если проблема остается

Отправьте логи:
```bash
pm2 logs bot-business-card --lines 20
```
# 🚨 СРОЧНЫЕ ИНСТРУКЦИИ ДЛЯ ИСПРАВЛЕНИЯ СЕРВЕРА

## Проблема
База данных не имеет необходимых колонок, из-за чего не работают страницы админки.

## Решение

### Вариант 1: Автоматическое исправление
```bash
# Зайдите на сервер по SSH и выполните:
cd /var/www/bot_business_card
python3 emergency_fix_db.py
pm2 restart botdev-admin
```

### Вариант 2: Полное исправление с проверкой
```bash
# Зайдите на сервер по SSH и выполните:
cd /var/www/bot_business_card
python3 run_fixes.py
```

### Вариант 3: Ручное исправление
```bash
# Если автоматические скрипты не работают:
cd /var/www/bot_business_card
sqlite3 db.sqlite

# В консоли SQLite выполните:
ALTER TABLE projects ADD COLUMN source_deal_id INTEGER;
ALTER TABLE projects ADD COLUMN paid_amount REAL DEFAULT 0.0;
ALTER TABLE finance_transactions ADD COLUMN account VARCHAR(50) DEFAULT 'card';
ALTER TABLE deals ADD COLUMN converted_to_project_id INTEGER;
.exit

# Перезапустите приложение:
pm2 restart botdev-admin
```

## Проверка
После выполнения исправлений проверьте:
1. Страница проектов должна открываться
2. Страница финансов должна работать
3. Можно создавать лиды, клиентов и сделки

## Если проблема остается
Проверьте логи:
```bash
pm2 logs botdev-admin --lines 50
```

И отправьте их для анализа.
# План миграции CRM системы с SQLite на PostgreSQL

## Проблемы SQLite для производственной CRM системы

### Критические ограничения:
1. **Конкурентный доступ**: SQLite блокирует всю базу при записи
2. **Масштабируемость**: Проблемы с производительностью при большом объеме данных
3. **Отсутствие репликации**: Невозможность создать резервные копии в реальном времени
4. **Блокировки на уровне таблицы**: Замедляет работу при множестве пользователей
5. **Ограниченный размер**: Рекомендуется до 140 ТБ, но на практике проблемы начинаются раньше
6. **Отсутствие продвинутых типов данных**: Нет JSON, массивов, JSONB

### Преимущества PostgreSQL:
- ✅ Поддержка конкурентного доступа (MVCC)
- ✅ Репликация и резервное копирование
- ✅ Продвинутые индексы (GiST, GIN, BRIN)
- ✅ Full-text search
- ✅ JSONB для гибких данных
- ✅ Партиционирование таблиц
- ✅ Поддержка до петабайтов данных

## Статус подготовки

У вас **уже полностью настроен PostgreSQL** в [docker-compose.yml](docker-compose.yml):
- PostgreSQL 16 Alpine
- Оптимизированная конфигурация (200 подключений, 256MB shared buffers)
- Redis для кэширования
- Alembic для миграций
- Celery для фоновых задач
- Prometheus + Grafana для мониторинга

## План миграции

### Этап 1: Подготовка (10-15 минут)

#### 1.1. Создание резервной копии SQLite
```bash
ssh root@147.45.215.199 "cd /var/www/bot_business_card && \
  cp business_card_bot.db business_card_bot.db.backup_$(date +%Y%m%d_%H%M%S)"
```

#### 1.2. Экспорт данных из SQLite
```bash
# Скрипт автоматически экспортирует все данные
python3 scripts/export_sqlite_to_json.py
```

#### 1.3. Проверка .env конфигурации
```bash
# В .env должны быть настройки PostgreSQL:
DATABASE_URL=postgresql://crm_user:crm_password@postgres:5432/crm_db
POSTGRES_DB=crm_db
POSTGRES_USER=crm_user
POSTGRES_PASSWORD=your_secure_password_here

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

### Этап 2: Развертывание PostgreSQL (5-10 минут)

#### 2.1. Остановка текущих сервисов
```bash
ssh root@147.45.215.199 "cd /var/www/bot_business_card && \
  docker-compose down"
```

#### 2.2. Копирование новой конфигурации
```bash
# Копируем docker-compose.yml с PostgreSQL
scp docker-compose.yml root@147.45.215.199:/var/www/bot_business_card/

# Копируем обновленный .env
scp .env.production root@147.45.215.199:/var/www/bot_business_card/.env
```

#### 2.3. Запуск PostgreSQL
```bash
ssh root@147.45.215.199 "cd /var/www/bot_business_card && \
  docker-compose up -d postgres redis"
```

#### 2.4. Проверка запуска PostgreSQL
```bash
ssh root@147.45.215.199 "docker logs bot-business-card-postgres-1 --tail 50"
```

### Этап 3: Миграция данных (15-30 минут в зависимости от объема)

#### 3.1. Применение миграций Alembic
```bash
# Создание схемы базы данных
ssh root@147.45.215.199 "cd /var/www/bot_business_card && \
  docker-compose run --rm bot-business-card alembic upgrade head"
```

#### 3.2. Импорт данных из SQLite
```bash
# Копируем скрипт миграции
scp scripts/migrate_sqlite_to_postgres.py root@147.45.215.199:/var/www/bot_business_card/scripts/

# Запускаем импорт
ssh root@147.45.215.199 "cd /var/www/bot_business_card && \
  python3 scripts/migrate_sqlite_to_postgres.py"
```

#### 3.3. Проверка данных
```bash
# Подключаемся к PostgreSQL и проверяем количество записей
ssh root@147.45.215.199 "docker-compose exec postgres psql -U crm_user -d crm_db -c '\
  SELECT
    (SELECT COUNT(*) FROM admin_users) as users,
    (SELECT COUNT(*) FROM projects) as projects,
    (SELECT COUNT(*) FROM tasks) as tasks,
    (SELECT COUNT(*) FROM clients) as clients,
    (SELECT COUNT(*) FROM leads) as leads;'"
```

### Этап 4: Запуск приложения (5 минут)

#### 4.1. Запуск всех сервисов
```bash
ssh root@147.45.215.199 "cd /var/www/bot_business_card && \
  docker-compose up -d"
```

#### 4.2. Проверка логов
```bash
# Проверяем что все сервисы запустились
ssh root@147.45.215.199 "docker-compose ps"

# Смотрим логи приложения
ssh root@147.45.215.199 "docker-compose logs -f bot-business-card --tail 100"
```

#### 4.3. Тестирование
- Открываем админ-панель: https://nikolaevcodev.ru/admin
- Проверяем авторизацию
- Проверяем загрузку проектов, задач, клиентов
- Проверяем создание новых записей
- Проверяем удаление пользователей

### Этап 5: Оптимизация (опционально, после успешной миграции)

#### 5.1. Создание индексов для производительности
```sql
-- Индексы для частых запросов
CREATE INDEX CONCURRENTLY idx_tasks_executor_id ON tasks(executor_id);
CREATE INDEX CONCURRENTLY idx_tasks_status ON tasks(status);
CREATE INDEX CONCURRENTLY idx_tasks_deadline ON tasks(deadline);
CREATE INDEX CONCURRENTLY idx_projects_client_id ON projects(client_id);
CREATE INDEX CONCURRENTLY idx_leads_status ON leads(status);
```

#### 5.2. Настройка автовакуума
```sql
ALTER TABLE tasks SET (autovacuum_vacuum_scale_factor = 0.1);
ALTER TABLE projects SET (autovacuum_vacuum_scale_factor = 0.1);
```

## Откат в случае проблем

Если что-то пойдет не так, можно быстро вернуться к SQLite:

```bash
# 1. Остановить сервисы
ssh root@147.45.215.199 "cd /var/www/bot_business_card && docker-compose down"

# 2. Восстановить старый docker-compose.yml (без PostgreSQL)
# 3. Восстановить SQLite из бэкапа
ssh root@147.45.215.199 "cd /var/www/bot_business_card && \
  cp business_card_bot.db.backup_* business_card_bot.db"

# 4. Запустить старую конфигурацию
ssh root@147.45.215.199 "cd /var/www/bot_business_card && docker-compose up -d"
```

## Время выполнения

| Этап | Время |
|------|-------|
| Подготовка и бэкап | 10-15 мин |
| Развертывание PostgreSQL | 5-10 мин |
| Миграция данных | 15-30 мин |
| Запуск и тестирование | 5-10 мин |
| **Итого** | **35-65 мин** |

## Риски и митигация

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| Потеря данных | Низкая | Резервная копия SQLite перед миграцией |
| Несовместимость данных | Средняя | Скрипт миграции с валидацией |
| Downtime > 1 час | Низкая | Возможность быстрого отката |
| Ошибки в индексах | Низкая | Применение индексов после миграции |

## Следующие шаги

1. Проверьте текущий размер базы данных:
   ```bash
   ssh root@147.45.215.199 "ls -lh /var/www/bot_business_card/business_card_bot.db"
   ```

2. Оцените объем данных для планирования времени миграции

3. Выберите время с минимальной нагрузкой (ночью/выходные)

4. Уведомите пользователей о плановых работах

5. Запустите миграцию следуя плану выше

#!/usr/bin/env python3
"""
Скрипт миграции данных из SQLite в PostgreSQL
Переносит все таблицы с сохранением связей и данных
"""
import sqlite3
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Класс для миграции данных из SQLite в PostgreSQL"""

    def __init__(self, sqlite_path: str, postgres_url: str):
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url

        # Подключения
        self.sqlite_conn = None
        self.postgres_engine = None
        self.postgres_session = None

        # Статистика
        self.stats = {}

    def connect(self):
        """Подключиться к базам данных"""
        try:
            # SQLite
            logger.info(f"📊 Подключение к SQLite: {self.sqlite_path}")
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            self.sqlite_conn.row_factory = sqlite3.Row

            # PostgreSQL
            logger.info(f"📊 Подключение к PostgreSQL: {self.postgres_url.split('@')[1]}")
            self.postgres_engine = create_engine(self.postgres_url)
            Session = sessionmaker(bind=self.postgres_engine)
            self.postgres_session = Session()

            logger.info("✅ Подключение к базам данных успешно")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка подключения: {e}")
            return False

    def get_sqlite_tables(self):
        """Получить список таблиц из SQLite"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        # Исключаем системные таблицы
        tables = [t for t in tables if not t.startswith('sqlite_')]

        logger.info(f"📋 Найдено {len(tables)} таблиц в SQLite: {', '.join(tables)}")
        return tables

    def get_postgres_tables(self):
        """Получить список таблиц из PostgreSQL"""
        inspector = inspect(self.postgres_engine)
        tables = inspector.get_table_names()
        logger.info(f"📋 Найдено {len(tables)} таблиц в PostgreSQL: {', '.join(tables)}")
        return tables

    def migrate_table(self, table_name: str):
        """Мигрировать одну таблицу"""
        try:
            logger.info(f"🔄 Миграция таблицы: {table_name}")

            # Читаем данные из SQLite
            cursor = self.sqlite_conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            if not rows:
                logger.info(f"ℹ️  Таблица {table_name} пустая, пропускаем")
                self.stats[table_name] = 0
                return True

            # Получаем имена колонок
            columns = [description[0] for description in cursor.description]

            # Подготавливаем INSERT запрос для PostgreSQL
            placeholders = ', '.join([f':{col}' for col in columns])
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            # Вставляем данные в PostgreSQL
            inserted = 0
            for row in rows:
                try:
                    # Конвертируем Row в словарь
                    row_dict = dict(zip(columns, row))

                    # Обработка специальных типов данных
                    for key, value in row_dict.items():
                        # Конвертируем пустые строки в NULL для внешних ключей
                        if value == '' and key.endswith('_id'):
                            row_dict[key] = None
                        # Конвертируем строковые даты в datetime
                        elif isinstance(value, str) and ('_at' in key or key == 'created' or key == 'updated'):
                            try:
                                # Пробуем несколько форматов даты
                                for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                                    try:
                                        row_dict[key] = datetime.strptime(value, fmt)
                                        break
                                    except ValueError:
                                        continue
                            except:
                                pass  # Оставляем как есть

                    self.postgres_session.execute(text(insert_query), row_dict)
                    inserted += 1

                except Exception as e:
                    logger.warning(f"⚠️  Ошибка вставки строки в {table_name}: {e}")
                    logger.debug(f"Данные строки: {row_dict}")
                    continue

            self.postgres_session.commit()
            self.stats[table_name] = inserted
            logger.info(f"✅ {table_name}: мигрировано {inserted} из {len(rows)} записей")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка миграции таблицы {table_name}: {e}")
            self.postgres_session.rollback()
            return False

    def fix_sequences(self):
        """Исправить последовательности (sequences) в PostgreSQL"""
        logger.info("🔧 Исправление sequences для автоинкремента...")

        try:
            # Получаем все таблицы с id колонками
            tables = self.get_postgres_tables()

            for table in tables:
                try:
                    # Получаем максимальный ID
                    result = self.postgres_session.execute(
                        text(f"SELECT MAX(id) FROM {table}")
                    ).fetchone()

                    max_id = result[0] if result[0] else 0

                    # Обновляем sequence
                    sequence_name = f"{table}_id_seq"
                    self.postgres_session.execute(
                        text(f"SELECT setval('{sequence_name}', {max_id + 1}, false)")
                    )
                    logger.info(f"✅ {table}: sequence обновлен до {max_id + 1}")

                except Exception as e:
                    # Не все таблицы имеют id sequence
                    logger.debug(f"Пропуск {table}: {e}")
                    continue

            self.postgres_session.commit()
            logger.info("✅ Sequences исправлены")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка исправления sequences: {e}")
            return False

    def verify_migration(self):
        """Проверить успешность миграции"""
        logger.info("🔍 Проверка миграции...")

        try:
            sqlite_cursor = self.sqlite_conn.cursor()
            comparison = []

            for table_name, migrated_count in self.stats.items():
                # Считаем записи в SQLite
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                sqlite_count = sqlite_cursor.fetchone()[0]

                # Считаем записи в PostgreSQL
                result = self.postgres_session.execute(
                    text(f"SELECT COUNT(*) FROM {table_name}")
                ).fetchone()
                postgres_count = result[0]

                match = "✅" if sqlite_count == postgres_count else "❌"
                comparison.append({
                    'table': table_name,
                    'sqlite': sqlite_count,
                    'postgres': postgres_count,
                    'match': match
                })

                logger.info(
                    f"{match} {table_name}: SQLite={sqlite_count}, "
                    f"PostgreSQL={postgres_count}"
                )

            # Итоговая статистика
            total_sqlite = sum(c['sqlite'] for c in comparison)
            total_postgres = sum(c['postgres'] for c in comparison)

            logger.info(f"\n📊 Итоговая статистика:")
            logger.info(f"  Всего таблиц: {len(comparison)}")
            logger.info(f"  Записей в SQLite: {total_sqlite}")
            logger.info(f"  Записей в PostgreSQL: {total_postgres}")

            if total_sqlite == total_postgres:
                logger.info("✅ Миграция успешна! Все данные перенесены")
                return True
            else:
                logger.warning(f"⚠️  Несоответствие данных: {total_sqlite - total_postgres} записей")
                return False

        except Exception as e:
            logger.error(f"❌ Ошибка проверки: {e}")
            return False

    def migrate(self):
        """Выполнить полную миграцию"""
        logger.info("🚀 Начало миграции из SQLite в PostgreSQL")
        logger.info("=" * 60)

        try:
            # Подключение
            if not self.connect():
                return False

            # Получаем таблицы
            sqlite_tables = self.get_sqlite_tables()
            postgres_tables = self.get_postgres_tables()

            # Проверяем что схема PostgreSQL создана
            if not postgres_tables:
                logger.error("❌ PostgreSQL база данных пуста! Запустите миграции Alembic сначала:")
                logger.error("   docker-compose run --rm bot-business-card alembic upgrade head")
                return False

            # Определяем порядок миграции (сначала родительские таблицы)
            ordered_tables = self.get_migration_order(sqlite_tables)

            # Мигрируем каждую таблицу
            for table in ordered_tables:
                if table not in postgres_tables:
                    logger.warning(f"⚠️  Таблица {table} не найдена в PostgreSQL, пропускаем")
                    continue

                if not self.migrate_table(table):
                    logger.error(f"❌ Остановка миграции из-за ошибки в {table}")
                    return False

            # Исправляем sequences
            self.fix_sequences()

            # Проверяем результат
            self.verify_migration()

            logger.info("=" * 60)
            logger.info("🎉 Миграция завершена успешно!")
            return True

        except Exception as e:
            logger.error(f"❌ Критическая ошибка миграции: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # Закрываем подключения
            if self.sqlite_conn:
                self.sqlite_conn.close()
            if self.postgres_session:
                self.postgres_session.close()

    def get_migration_order(self, tables):
        """Определить порядок миграции таблиц (родительские таблицы первыми)"""
        # Базовые таблицы без FK должны мигрироваться первыми
        priority_order = [
            'admin_users',
            'clients',
            'contractors',
            'services',
            'projects',
            'tasks',
            'revisions',
            'leads',
            'deals',
            'avito_accounts',
            'avito_chats',
            'avito_messages',
            'project_chats',
            'project_chat_messages',
            'employee_notification_settings',
            'notification_queue',
            'notification_log',
        ]

        # Сортируем таблицы по приоритету
        ordered = []
        for table in priority_order:
            if table in tables:
                ordered.append(table)
                tables.remove(table)

        # Добавляем оставшиеся таблицы
        ordered.extend(sorted(tables))

        return ordered


def main():
    """Главная функция"""
    # Пути к базам данных
    sqlite_path = os.getenv('SQLITE_DB_PATH', './business_card_bot.db')
    postgres_url = os.getenv(
        'DATABASE_URL',
        'postgresql://crm_user:crm_password@localhost:5432/crm_db'
    )

    # Проверяем существование SQLite
    if not os.path.exists(sqlite_path):
        logger.error(f"❌ SQLite база данных не найдена: {sqlite_path}")
        return 1

    # Создаем мигратор
    migrator = DatabaseMigrator(sqlite_path, postgres_url)

    # Запускаем миграцию
    success = migrator.migrate()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

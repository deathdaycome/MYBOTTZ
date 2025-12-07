#!/usr/bin/env python3
"""
Миграция: Добавление детальных прав доступа к UI элементам
Дата: 2025-01-09
Описание: Создает таблицу ui_element_permissions для управления доступом к каждому полю, кнопке и разделу
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Index
from datetime import datetime
import json

# Импортируем существующие модели
from app.database.models import Base, AdminUser

# Подключаемся к базе данных
DATABASE_URL = "sqlite:///./data/bot.db"
engine = create_engine(DATABASE_URL)


class UIElementPermission(Base):
    """
    Модель для детального управления доступом к элементам интерфейса
    Позволяет контролировать видимость и доступность каждого поля, кнопки, раздела
    """
    __tablename__ = "ui_element_permissions"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Модуль системы (раздел)
    module = Column(String(100), nullable=False, index=True)  # 'projects', 'tasks', 'analytics', 'hosting', etc.

    # Тип элемента
    element_type = Column(String(50), nullable=False, index=True)  # 'field', 'button', 'section', 'tab', 'column', 'action'

    # Уникальный идентификатор элемента
    element_id = Column(String(255), nullable=False, index=True)  # 'projects.title', 'projects.edit_button', 'projects.financial_section'

    # Разрешен ли доступ к элементу
    is_enabled = Column(Boolean, default=True, nullable=False)

    # Метаданные
    description = Column(Text, nullable=True)  # Описание элемента для админа

    # Даты
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Составной индекс для быстрого поиска
    __table_args__ = (
        Index('idx_user_module_element', 'admin_user_id', 'module', 'element_id'),
    )


# Определение всех UI элементов системы по модулям
UI_ELEMENTS_STRUCTURE = {
    "projects": {
        "name": "Проекты",
        "elements": {
            # Поля карточки проекта
            "field.title": {"type": "field", "name": "Название проекта"},
            "field.description": {"type": "field", "name": "Описание"},
            "field.client": {"type": "field", "name": "Клиент"},
            "field.client_telegram_id": {"type": "field", "name": "Telegram ID клиента"},
            "field.client_telegram_username": {"type": "field", "name": "Telegram username клиента"},
            "field.status": {"type": "field", "name": "Статус"},
            "field.priority": {"type": "field", "name": "Приоритет"},
            "field.project_type": {"type": "field", "name": "Тип проекта"},
            "field.complexity": {"type": "field", "name": "Сложность"},
            "field.estimated_cost": {"type": "field", "name": "Стоимость проекта"},
            "field.executor_cost": {"type": "field", "name": "Стоимость для исполнителя"},
            "field.final_cost": {"type": "field", "name": "Итоговая стоимость"},
            "field.prepayment_amount": {"type": "field", "name": "Предоплата"},
            "field.client_paid_total": {"type": "field", "name": "Оплачено клиентом"},
            "field.executor_paid_total": {"type": "field", "name": "Выплачено исполнителю"},
            "field.start_date": {"type": "field", "name": "Дата начала"},
            "field.planned_end_date": {"type": "field", "name": "Плановая дата завершения"},
            "field.actual_end_date": {"type": "field", "name": "Фактическая дата завершения"},
            "field.assigned_executor": {"type": "field", "name": "Исполнитель"},
            "field.responsible_manager": {"type": "field", "name": "Ответственный менеджер"},
            "field.contract_file": {"type": "field", "name": "Файл договора"},
            "field.tags": {"type": "field", "name": "Теги"},

            # Секции
            "section.general": {"type": "section", "name": "Общая информация"},
            "section.financial": {"type": "section", "name": "Финансовая информация"},
            "section.dates": {"type": "section", "name": "Даты и сроки"},
            "section.team": {"type": "section", "name": "Команда"},
            "section.files": {"type": "section", "name": "Файлы"},
            "section.tasks": {"type": "section", "name": "Задачи"},
            "section.revisions": {"type": "section", "name": "Правки"},
            "section.history": {"type": "section", "name": "История"},

            # Кнопки
            "button.create": {"type": "button", "name": "Создать проект"},
            "button.edit": {"type": "button", "name": "Редактировать"},
            "button.delete": {"type": "button", "name": "Удалить"},
            "button.archive": {"type": "button", "name": "Архивировать"},
            "button.export": {"type": "button", "name": "Экспорт"},
            "button.upload_contract": {"type": "button", "name": "Загрузить договор"},
            "button.assign_executor": {"type": "button", "name": "Назначить исполнителя"},
            "button.change_status": {"type": "button", "name": "Изменить статус"},

            # Колонки таблицы
            "column.id": {"type": "column", "name": "ID"},
            "column.title": {"type": "column", "name": "Название"},
            "column.client": {"type": "column", "name": "Клиент"},
            "column.status": {"type": "column", "name": "Статус"},
            "column.priority": {"type": "column", "name": "Приоритет"},
            "column.estimated_cost": {"type": "column", "name": "Стоимость"},
            "column.executor": {"type": "column", "name": "Исполнитель"},
            "column.deadline": {"type": "column", "name": "Дедлайн"},
            "column.actions": {"type": "column", "name": "Действия"},
        }
    },
    "tasks": {
        "name": "Задачи",
        "elements": {
            # Поля задачи
            "field.title": {"type": "field", "name": "Название задачи"},
            "field.description": {"type": "field", "name": "Описание"},
            "field.project": {"type": "field", "name": "Проект"},
            "field.status": {"type": "field", "name": "Статус"},
            "field.priority": {"type": "field", "name": "Приоритет"},
            "field.assigned_to": {"type": "field", "name": "Исполнитель"},
            "field.deadline": {"type": "field", "name": "Срок выполнения"},
            "field.tags": {"type": "field", "name": "Теги"},
            "field.attachments": {"type": "field", "name": "Вложения"},

            # Секции
            "section.general": {"type": "section", "name": "Основная информация"},
            "section.details": {"type": "section", "name": "Детали"},
            "section.comments": {"type": "section", "name": "Комментарии"},
            "section.attachments": {"type": "section", "name": "Вложения"},

            # Кнопки
            "button.create": {"type": "button", "name": "Создать задачу"},
            "button.edit": {"type": "button", "name": "Редактировать"},
            "button.delete": {"type": "button", "name": "Удалить"},
            "button.complete": {"type": "button", "name": "Завершить"},
            "button.add_comment": {"type": "button", "name": "Добавить комментарий"},
            "button.upload_file": {"type": "button", "name": "Загрузить файл"},

            # Колонки
            "column.title": {"type": "column", "name": "Название"},
            "column.project": {"type": "column", "name": "Проект"},
            "column.status": {"type": "column", "name": "Статус"},
            "column.priority": {"type": "column", "name": "Приоритет"},
            "column.assigned_to": {"type": "column", "name": "Исполнитель"},
            "column.deadline": {"type": "column", "name": "Срок"},
        }
    },
    "analytics": {
        "name": "Аналитика",
        "elements": {
            # Секции дашборда
            "section.overview": {"type": "section", "name": "Обзор"},
            "section.projects_stats": {"type": "section", "name": "Статистика проектов"},
            "section.financial_stats": {"type": "section", "name": "Финансовая статистика"},
            "section.team_performance": {"type": "section", "name": "Производительность команды"},
            "section.charts": {"type": "section", "name": "Графики"},

            # Метрики (поля)
            "field.total_projects": {"type": "field", "name": "Всего проектов"},
            "field.active_projects": {"type": "field", "name": "Активные проекты"},
            "field.total_revenue": {"type": "field", "name": "Общая выручка"},
            "field.total_expenses": {"type": "field", "name": "Расходы"},
            "field.profit": {"type": "field", "name": "Прибыль"},
            "field.conversion_rate": {"type": "field", "name": "Конверсия"},

            # Кнопки
            "button.export": {"type": "button", "name": "Экспорт"},
            "button.filter": {"type": "button", "name": "Фильтры"},
            "button.period_selector": {"type": "button", "name": "Выбор периода"},
        }
    },
    "clients": {
        "name": "Клиенты",
        "elements": {
            # Поля
            "field.telegram_id": {"type": "field", "name": "Telegram ID"},
            "field.username": {"type": "field", "name": "Username"},
            "field.first_name": {"type": "field", "name": "Имя"},
            "field.last_name": {"type": "field", "name": "Фамилия"},
            "field.phone": {"type": "field", "name": "Телефон"},
            "field.email": {"type": "field", "name": "Email"},
            "field.notes": {"type": "field", "name": "Заметки"},

            # Кнопки
            "button.create": {"type": "button", "name": "Создать клиента"},
            "button.edit": {"type": "button", "name": "Редактировать"},
            "button.delete": {"type": "button", "name": "Удалить"},
            "button.view_projects": {"type": "button", "name": "Просмотр проектов"},

            # Колонки
            "column.telegram_id": {"type": "column", "name": "Telegram ID"},
            "column.name": {"type": "column", "name": "Имя"},
            "column.phone": {"type": "column", "name": "Телефон"},
            "column.projects_count": {"type": "column", "name": "Кол-во проектов"},
        }
    },
    "hosting": {
        "name": "Хостинг",
        "elements": {
            # Поля
            "field.domain": {"type": "field", "name": "Домен"},
            "field.hosting_provider": {"type": "field", "name": "Хостинг провайдер"},
            "field.credentials": {"type": "field", "name": "Учетные данные"},
            "field.expiration_date": {"type": "field", "name": "Дата истечения"},

            # Кнопки
            "button.create": {"type": "button", "name": "Добавить хостинг"},
            "button.edit": {"type": "button", "name": "Редактировать"},
            "button.delete": {"type": "button", "name": "Удалить"},
        }
    },
    "avito": {
        "name": "Avito",
        "elements": {
            # Секции
            "section.chats": {"type": "section", "name": "Чаты"},
            "section.messages": {"type": "section", "name": "Сообщения"},

            # Кнопки
            "button.send_message": {"type": "button", "name": "Отправить сообщение"},
            "button.refresh": {"type": "button", "name": "Обновить"},
        }
    },
    "employees": {
        "name": "Сотрудники",
        "elements": {
            # Поля
            "field.username": {"type": "field", "name": "Логин"},
            "field.email": {"type": "field", "name": "Email"},
            "field.first_name": {"type": "field", "name": "Имя"},
            "field.last_name": {"type": "field", "name": "Фамилия"},
            "field.role": {"type": "field", "name": "Роль"},
            "field.telegram_id": {"type": "field", "name": "Telegram ID"},
            "field.is_active": {"type": "field", "name": "Активен"},

            # Кнопки
            "button.create": {"type": "button", "name": "Создать сотрудника"},
            "button.edit": {"type": "button", "name": "Редактировать"},
            "button.delete": {"type": "button", "name": "Удалить"},
            "button.reset_password": {"type": "button", "name": "Сбросить пароль"},

            # Колонки
            "column.username": {"type": "column", "name": "Логин"},
            "column.name": {"type": "column", "name": "Имя"},
            "column.role": {"type": "column", "name": "Роль"},
            "column.is_active": {"type": "column", "name": "Статус"},
        }
    },
    "permissions": {
        "name": "Права доступа",
        "elements": {
            # Секции
            "section.module_permissions": {"type": "section", "name": "Модульные права"},
            "section.ui_permissions": {"type": "section", "name": "Права на UI элементы"},

            # Кнопки
            "button.save": {"type": "button", "name": "Сохранить"},
            "button.reset": {"type": "button", "name": "Сбросить"},
            "button.copy_from_user": {"type": "button", "name": "Скопировать от пользователя"},
        }
    },
    "documents": {
        "name": "Документы",
        "elements": {
            # Поля
            "field.title": {"type": "field", "name": "Название"},
            "field.type": {"type": "field", "name": "Тип документа"},
            "field.file": {"type": "field", "name": "Файл"},
            "field.project": {"type": "field", "name": "Связанный проект"},

            # Кнопки
            "button.upload": {"type": "button", "name": "Загрузить"},
            "button.download": {"type": "button", "name": "Скачать"},
            "button.delete": {"type": "button", "name": "Удалить"},

            # Колонки
            "column.title": {"type": "column", "name": "Название"},
            "column.type": {"type": "column", "name": "Тип"},
            "column.size": {"type": "column", "name": "Размер"},
            "column.uploaded_at": {"type": "column", "name": "Дата загрузки"},
        }
    }
}


def upgrade():
    """Создание таблицы ui_element_permissions"""
    print("🔄 Создание таблицы ui_element_permissions...")

    try:
        # Создаем таблицу
        Base.metadata.create_all(bind=engine, tables=[UIElementPermission.__table__])
        print("✅ Таблица ui_element_permissions успешно создана")

        # Сохраняем структуру UI элементов в JSON файл для использования в коде
        structure_file = project_root / "app" / "config" / "ui_elements_structure.json"
        structure_file.parent.mkdir(parents=True, exist_ok=True)

        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(UI_ELEMENTS_STRUCTURE, f, ensure_ascii=False, indent=2)

        print(f"✅ Структура UI элементов сохранена в {structure_file}")

        return True

    except Exception as e:
        print(f"❌ Ошибка при создании таблицы: {e}")
        return False


def downgrade():
    """Удаление таблицы ui_element_permissions"""
    print("🔄 Удаление таблицы ui_element_permissions...")

    try:
        UIElementPermission.__table__.drop(engine)
        print("✅ Таблица ui_element_permissions успешно удалена")
        return True

    except Exception as e:
        print(f"❌ Ошибка при удалении таблицы: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Миграция: Добавление детальных прав доступа к UI элементам")
    print("=" * 60)

    if upgrade():
        print("\n✅ Миграция успешно выполнена!")
        print("\nДобавлена таблица для управления доступом к:")
        print("  • Полям (fields)")
        print("  • Кнопкам (buttons)")
        print("  • Секциям (sections)")
        print("  • Вкладкам (tabs)")
        print("  • Колонкам таблиц (columns)")
        print("\nМодули с поддержкой детальных прав:")
        for module_key, module_data in UI_ELEMENTS_STRUCTURE.items():
            element_count = len(module_data['elements'])
            print(f"  • {module_data['name']} ({module_key}): {element_count} элементов")
    else:
        print("\n❌ Миграция не выполнена")
        sys.exit(1)

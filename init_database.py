#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""

import sys
import os

# Добавляем путь к приложению
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import init_db, engine, SessionLocal
from app.database.models import Base, AdminUser
from app.database.crm_models import Lead, Client, Deal
from app.database.audit_models import AuditLog
from app.database.rbac_models import Role, Permission
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user():
    """Создать администратора по умолчанию"""
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже админ
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if admin:
            logger.info("Администратор уже существует")
            return
        
        # Создаем админа
        admin = AdminUser(
            username="admin",
            password="qwerty123",  # В реальности должен быть хеш
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info(f"Создан администратор: admin / qwerty123")
        
    except Exception as e:
        logger.error(f"Ошибка создания администратора: {e}")
        db.rollback()
    finally:
        db.close()

def add_whatsapp_column():
    """Добавить колонку contact_whatsapp в таблицу leads"""
    db = SessionLocal()
    try:
        # Проверяем, существует ли уже колонка
        result = db.execute(text("PRAGMA table_info(leads)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'contact_whatsapp' not in columns:
            db.execute(text("ALTER TABLE leads ADD COLUMN contact_whatsapp VARCHAR(50)"))
            db.commit()
            logger.info("Добавлена колонка contact_whatsapp в таблицу leads")
        else:
            logger.info("Колонка contact_whatsapp уже существует")
            
    except Exception as e:
        logger.error(f"Ошибка при добавлении колонки: {e}")
        db.rollback()
    finally:
        db.close()

def create_test_data():
    """Создать тестовые данные"""
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже лиды
        existing_leads = db.query(Lead).count()
        if existing_leads > 0:
            logger.info("Тестовые данные уже существуют")
            return
        
        # Создаем тестовые лиды
        test_leads = [
            Lead(
                title="акуаука",
                status="new",
                source="site",
                contact_name="Иван Петров",
                contact_phone="+7 (999) 123-45-67",
                contact_email="ivan@example.com",
                contact_telegram="@ivan_petrov",
                contact_whatsapp="+7 (999) 123-45-67",
                description="Требуется разработка бота для интернет-магазина",
                budget=50000.0,
                probability=50
            ),
            Lead(
                title="якуяка",
                status="contact_made",
                source="site",
                contact_name="Анна Сидорова",
                contact_phone="+7 (999) 987-65-43",
                contact_email="anna@example.com",
                contact_telegram="@anna_sidorova",
                description="Нужен бот для автоматизации процессов",
                budget=75000.0,
                probability=70
            ),
            Lead(
                title="укуука",
                status="qualification",
                source="site",
                contact_name="Сергей Иванов",
                contact_phone="+7 (999) 555-55-55",
                contact_email="sergey@example.com",
                contact_whatsapp="+7 (999) 555-55-55",
                description="Разработка CRM-бота",
                budget=100000.0,
                probability=80
            ),
            Lead(
                title="укаука",
                status="proposal_sent",
                source="site",
                contact_name="Мария Козлова",
                contact_phone="+7 (999) 111-11-11",
                contact_email="maria@example.com",
                contact_telegram="@maria_kozlova",
                contact_whatsapp="+7 (999) 111-11-11",
                description="Бот для интеграции с внешними системами",
                budget=120000.0,
                probability=60
            )
        ]
        
        for lead in test_leads:
            db.add(lead)
        
        db.commit()
        logger.info(f"Создано {len(test_leads)} тестовых лидов")
        
    except Exception as e:
        logger.error(f"Ошибка при создании тестовых данных: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Главная функция инициализации"""
    try:
        logger.info("Начинаем инициализацию базы данных...")
        
        # Создаем все таблицы
        logger.info("Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        logger.info("Таблицы созданы успешно")
        
        # Добавляем колонку WhatsApp если её нет
        add_whatsapp_column()
        
        # Создаем администратора
        create_admin_user()
        
        # Создаем тестовые данные
        create_test_data()
        
        logger.info("База данных инициализирована успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
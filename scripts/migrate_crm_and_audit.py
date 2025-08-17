#!/usr/bin/env python3
"""
Миграция для создания таблиц CRM и аудит-лога
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Импортируем все модели
from app.database.database import Base
from app.database.models import *
from app.database.crm_models import *
from app.database.automation_models import *
from app.database.audit_models import *
# Импортируем только существующие модули
try:
    from app.database.document_models import *
except ImportError:
    pass  # Модели документов могут быть в crm_models
try:
    from app.database.finance_models import *
except ImportError:
    pass  # Финансовые модели могут быть в crm_models
from app.database.rbac_models import *
try:
    from app.database.report_models import *
except ImportError:
    pass  # Модели отчетов могут быть в crm_models
from app.config.logging import get_logger

logger = get_logger(__name__)

# Настройки подключения к БД
DATABASE_URL = "sqlite:///./admin_panel.db"


def create_all_tables():
    """Создать все новые таблицы"""
    print("🔄 Начинаем создание новых таблиц CRM и аудит-лога...")
    
    try:
        # Создаем подключение
        engine = create_engine(DATABASE_URL, echo=False)
        
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        
        print("✅ Все таблицы успешно созданы!")
        
        # Проверяем созданные таблицы
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """))
            tables = result.fetchall()
            
            print(f"\n📊 Всего таблиц в БД: {len(tables)}")
            print("\nНовые таблицы CRM:")
            crm_tables = [t[0] for t in tables if any(x in t[0] for x in ['client', 'lead', 'deal', 'activity', 'communication'])]
            for table in crm_tables:
                print(f"  ✓ {table}")
            
            print("\nТаблицы автоматизации:")
            auto_tables = [t[0] for t in tables if any(x in t[0] for x in ['automation', 'notification', 'workflow'])]
            for table in auto_tables:
                print(f"  ✓ {table}")
            
            print("\nТаблицы аудита:")
            audit_tables = [t[0] for t in tables if 'audit' in t[0]]
            for table in audit_tables:
                print(f"  ✓ {table}")
            
            print("\nТаблицы документов:")
            doc_tables = [t[0] for t in tables if 'document' in t[0]]
            for table in doc_tables:
                print(f"  ✓ {table}")
            
            print("\nТаблицы финансов:")
            finance_tables = [t[0] for t in tables if any(x in t[0] for x in ['invoice', 'payment', 'expense', 'budget'])]
            for table in finance_tables:
                print(f"  ✓ {table}")
            
            print("\nТаблицы прав доступа:")
            rbac_tables = [t[0] for t in tables if any(x in t[0] for x in ['role', 'permission', 'user_role'])]
            for table in rbac_tables:
                print(f"  ✓ {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        return False


def migrate_existing_data():
    """Миграция существующих данных в новую структуру"""
    print("\n🔄 Начинаем миграцию существующих данных...")
    
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 1. Создаем роли по умолчанию
        print("\n📝 Создаем роли по умолчанию...")
        from app.database.rbac_models import Role, Permission
        
        # Проверяем, есть ли уже роли
        existing_roles = session.query(Role).count()
        if existing_roles == 0:
            # Создаем базовые роли
            roles_data = [
                {
                    'name': 'Администратор',
                    'code': 'admin',
                    'description': 'Полный доступ к системе',
                    'is_system': True
                },
                {
                    'name': 'Менеджер',
                    'code': 'manager',
                    'description': 'Управление клиентами и сделками',
                    'is_system': True
                },
                {
                    'name': 'Исполнитель',
                    'code': 'executor',
                    'description': 'Выполнение проектов и задач',
                    'is_system': True
                },
                {
                    'name': 'Наблюдатель',
                    'code': 'observer',
                    'description': 'Только просмотр',
                    'is_system': True
                }
            ]
            
            for role_data in roles_data:
                role = Role(**role_data)
                session.add(role)
            
            session.commit()
            print(f"  ✓ Создано {len(roles_data)} базовых ролей")
        else:
            print(f"  ℹ Роли уже существуют: {existing_roles}")
        
        # 2. Мигрируем пользователей телеграм в клиентов
        print("\n📝 Мигрируем пользователей в клиентов...")
        from app.database.models import TelegramUser
        from app.database.crm_models import Client, ClientType, ClientStatus
        
        tg_users = session.query(TelegramUser).all()
        migrated_clients = 0
        
        for tg_user in tg_users:
            # Проверяем, не создан ли уже клиент
            existing_client = session.query(Client).filter(
                Client.telegram_id == str(tg_user.telegram_id)
            ).first()
            
            if not existing_client:
                client = Client(
                    name=tg_user.first_name or f"User_{tg_user.telegram_id}",
                    type=ClientType.INDIVIDUAL,
                    status=ClientStatus.ACTIVE if tg_user.active_subscription else ClientStatus.INACTIVE,
                    telegram_id=str(tg_user.telegram_id),
                    telegram_username=tg_user.username,
                    source='telegram',
                    created_at=tg_user.registration_date or datetime.utcnow(),
                    tags=['telegram_user', 'migrated']
                )
                session.add(client)
                migrated_clients += 1
        
        session.commit()
        print(f"  ✓ Мигрировано {migrated_clients} пользователей в клиентов")
        
        # 3. Мигрируем проекты в сделки
        print("\n📝 Мигрируем проекты в сделки...")
        from app.database.models import Project
        from app.database.crm_models import Deal, DealStatus, DealStage
        
        projects = session.query(Project).all()
        migrated_deals = 0
        
        for project in projects:
            # Находим клиента
            client = session.query(Client).filter(
                Client.telegram_id == str(project.user.telegram_id)
            ).first() if project.user else None
            
            if client:
                # Проверяем, не создана ли уже сделка
                existing_deal = session.query(Deal).filter(
                    Deal.project_id == project.id
                ).first()
                
                if not existing_deal:
                    # Определяем статус сделки
                    if project.status in ['completed', 'paid']:
                        deal_status = DealStatus.WON
                        deal_stage = DealStage.CLOSED_WON
                    elif project.status == 'cancelled':
                        deal_status = DealStatus.LOST
                        deal_stage = DealStage.CLOSED_LOST
                    elif project.status in ['in_progress', 'testing']:
                        deal_status = DealStatus.IN_PROGRESS
                        deal_stage = DealStage.CONTRACT
                    else:
                        deal_status = DealStatus.NEW
                        deal_stage = DealStage.INITIAL_CONTACT
                    
                    deal = Deal(
                        title=project.title,
                        client_id=client.id,
                        project_id=project.id,
                        amount=float(project.estimated_cost) if project.estimated_cost else 0,
                        status=deal_status,
                        stage=deal_stage,
                        probability=100 if deal_status == DealStatus.WON else 50,
                        expected_close_date=project.planned_end_date,
                        actual_close_date=project.end_date if project.status == 'completed' else None,
                        created_at=project.created_at or datetime.utcnow(),
                        tags=['migrated_from_project']
                    )
                    session.add(deal)
                    migrated_deals += 1
        
        session.commit()
        print(f"  ✓ Мигрировано {migrated_deals} проектов в сделки")
        
        # 4. Создаем начальную запись в аудит-логе
        print("\n📝 Создаем начальную запись в аудит-логе...")
        from app.database.audit_models import AuditLog, AuditActionType
        
        audit_entry = AuditLog(
            action_type=AuditActionType.SETTING_CHANGE,
            description="Выполнена миграция базы данных для CRM и аудит-лога",
            success='success',
            extra_metadata={
                'migration': 'crm_and_audit',
                'migrated_clients': migrated_clients,
                'migrated_deals': migrated_deals,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        session.add(audit_entry)
        session.commit()
        print("  ✓ Создана начальная запись в аудит-логе")
        
        # 5. Создаем шаблоны документов по умолчанию
        print("\n📝 Создаем шаблоны документов...")
        from app.database.document_models import DocumentTemplate, DocumentType
        
        existing_templates = session.query(DocumentTemplate).count()
        if existing_templates == 0:
            templates = [
                {
                    'name': 'Договор на разработку',
                    'type': DocumentType.CONTRACT,
                    'content': '''
                        <h1>Договор на разработку №{{ contract_number }}</h1>
                        <p>г. Москва, {{ date }}</p>
                        <p>{{ client_name }}, именуемый в дальнейшем "Заказчик", и BotDev, именуемый в дальнейшем "Исполнитель", заключили настоящий договор о нижеследующем:</p>
                        <h2>1. Предмет договора</h2>
                        <p>{{ project_description }}</p>
                        <h2>2. Стоимость работ</h2>
                        <p>Общая стоимость: {{ amount }} руб.</p>
                    ''',
                    'variables': ['contract_number', 'date', 'client_name', 'project_description', 'amount'],
                    'is_active': True,
                    'is_system': True
                },
                {
                    'name': 'Счет на оплату',
                    'type': DocumentType.INVOICE,
                    'content': '''
                        <h1>Счет №{{ invoice_number }} от {{ date }}</h1>
                        <p>Плательщик: {{ client_name }}</p>
                        <table>
                            <tr><th>Наименование</th><th>Количество</th><th>Цена</th><th>Сумма</th></tr>
                            <tr><td>{{ service_name }}</td><td>1</td><td>{{ amount }}</td><td>{{ amount }}</td></tr>
                        </table>
                        <p><strong>Итого к оплате: {{ amount }} руб.</strong></p>
                    ''',
                    'variables': ['invoice_number', 'date', 'client_name', 'service_name', 'amount'],
                    'is_active': True,
                    'is_system': True
                },
                {
                    'name': 'Коммерческое предложение',
                    'type': DocumentType.PROPOSAL,
                    'content': '''
                        <h1>Коммерческое предложение</h1>
                        <p>Уважаемый {{ client_name }}!</p>
                        <p>Предлагаем Вам следующие услуги:</p>
                        <p>{{ proposal_content }}</p>
                        <p>Стоимость: {{ amount }} руб.</p>
                        <p>Срок выполнения: {{ deadline }}</p>
                    ''',
                    'variables': ['client_name', 'proposal_content', 'amount', 'deadline'],
                    'is_active': True,
                    'is_system': True
                }
            ]
            
            for template_data in templates:
                template = DocumentTemplate(**template_data)
                session.add(template)
            
            session.commit()
            print(f"  ✓ Создано {len(templates)} шаблонов документов")
        else:
            print(f"  ℹ Шаблоны документов уже существуют: {existing_templates}")
        
        # 6. Создаем правила автоматизации по умолчанию
        print("\n📝 Создаем правила автоматизации...")
        from app.database.automation_models import AutomationRule, AutomationType, TriggerType
        
        existing_rules = session.query(AutomationRule).count()
        if existing_rules == 0:
            rules = [
                {
                    'name': 'Напоминание о новом лиде',
                    'description': 'Уведомление менеджера о новом лиде через 30 минут',
                    'type': AutomationType.LEAD_FOLLOWUP,
                    'trigger_type': TriggerType.EVENT_BASED,
                    'conditions': {
                        'event_type': 'lead_created',
                        'checks': []
                    },
                    'actions': [
                        {
                            'type': 'send_notification',
                            'params': {
                                'channel': 'email',
                                'template_id': 1
                            }
                        }
                    ],
                    'is_active': True,
                    'priority': 8
                },
                {
                    'name': 'Смена статуса сделки',
                    'description': 'Уведомление при переходе сделки на новый этап',
                    'type': AutomationType.DEAL_STAGE_CHANGE,
                    'trigger_type': TriggerType.EVENT_BASED,
                    'conditions': {
                        'event_type': 'deal_stage_changed',
                        'checks': []
                    },
                    'actions': [
                        {
                            'type': 'send_notification',
                            'params': {
                                'channel': 'in_app'
                            }
                        }
                    ],
                    'is_active': True,
                    'priority': 7
                }
            ]
            
            for rule_data in rules:
                rule = AutomationRule(**rule_data)
                session.add(rule)
            
            session.commit()
            print(f"  ✓ Создано {len(rules)} правил автоматизации")
        else:
            print(f"  ℹ Правила автоматизации уже существуют: {existing_rules}")
        
        session.close()
        print("\n✅ Миграция данных завершена успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при миграции данных: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Основная функция миграции"""
    print("=" * 60)
    print("🚀 МИГРАЦИЯ БД: CRM И АУДИТ-ЛОГ")
    print("=" * 60)
    
    # Создаем таблицы
    if not create_all_tables():
        print("\n❌ Не удалось создать таблицы")
        return 1
    
    # Мигрируем данные
    if not migrate_existing_data():
        print("\n⚠️ Миграция данных завершена с ошибками")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 60)
    print("\n📌 Следующие шаги:")
    print("  1. Перезапустите приложение")
    print("  2. Проверьте новые разделы в админ-панели")
    print("  3. Настройте права доступа для пользователей")
    print("  4. Настройте автоматизации и шаблоны документов")
    
    return 0


if __name__ == "__main__":
    exit(main())
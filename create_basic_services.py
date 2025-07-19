#!/usr/bin/env python3
"""
Скрипт для создания базовых сервисов в системе
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import get_db_context
from app.database.models import ServiceProvider
from datetime import datetime

def create_basic_services():
    """Создает базовые сервисы"""
    
    # Базовые сервисы
    services = [
        {
            "name": "OpenAI API",
            "description": "API для доступа к моделям GPT",
            "provider_type": "ai",
            "website": "https://openai.com",
            "contact_info": {"email": "support@openai.com"},
            "pricing_model": "usage",
            "status": "active"
        },
        {
            "name": "OpenRouter",
            "description": "API-роутер для различных AI моделей",
            "provider_type": "ai", 
            "website": "https://openrouter.ai",
            "contact_info": {"email": "support@openrouter.ai"},
            "pricing_model": "usage",
            "status": "active"
        },
        {
            "name": "Claude API",
            "description": "API для доступа к моделям Claude от Anthropic",
            "provider_type": "ai",
            "website": "https://www.anthropic.com",
            "contact_info": {"email": "support@anthropic.com"},
            "pricing_model": "usage",
            "status": "active"
        },
        {
            "name": "DigitalOcean",
            "description": "Облачный хостинг и VPS",
            "provider_type": "hosting",
            "website": "https://digitalocean.com",
            "contact_info": {"email": "support@digitalocean.com"},
            "pricing_model": "monthly",
            "status": "active"
        },
        {
            "name": "Timeweb",
            "description": "Российский хостинг-провайдер",
            "provider_type": "hosting",
            "website": "https://timeweb.com",
            "contact_info": {"email": "support@timeweb.ru", "phone": "+7 (495) 663-65-65"},
            "pricing_model": "monthly",
            "status": "active"
        },
        {
            "name": "AWS S3",
            "description": "Облачное хранилище Amazon",
            "provider_type": "storage",
            "website": "https://aws.amazon.com/s3/",
            "contact_info": {"email": "aws-support@amazon.com"},
            "pricing_model": "usage",
            "status": "active"
        },
        {
            "name": "YooMoney",
            "description": "Платежная система (бывший Яндекс.Деньги)",
            "provider_type": "payment",
            "website": "https://yoomoney.ru",
            "contact_info": {"email": "support@yoomoney.ru", "phone": "8 800 250-66-99"},
            "pricing_model": "per_request",
            "status": "active"
        },
        {
            "name": "Telegram Bot API",
            "description": "API для разработки Telegram ботов",
            "provider_type": "other",
            "website": "https://core.telegram.org/bots/api",
            "contact_info": {"email": "support@telegram.org"},
            "pricing_model": "usage",
            "status": "active"
        },
        {
            "name": "Google Analytics",
            "description": "Веб-аналитика от Google",
            "provider_type": "analytics",
            "website": "https://analytics.google.com",
            "contact_info": {"email": "support@google.com"},
            "pricing_model": "usage",
            "status": "active"
        },
        {
            "name": "SendGrid",
            "description": "Email-сервис для рассылок",
            "provider_type": "email",
            "website": "https://sendgrid.com",
            "contact_info": {"email": "support@sendgrid.com"},
            "pricing_model": "usage",
            "status": "active"
        },
        {
            "name": "Cloudflare",
            "description": "CDN и защита сайтов",
            "provider_type": "cdn",
            "website": "https://cloudflare.com",
            "contact_info": {"email": "support@cloudflare.com"},
            "pricing_model": "monthly",
            "status": "active"
        },
        {
            "name": "SMS.ru",
            "description": "SMS-рассылки в России",
            "provider_type": "sms",
            "website": "https://sms.ru",
            "contact_info": {"email": "support@sms.ru", "phone": "+7 (495) 545-45-67"},
            "pricing_model": "per_request",
            "status": "active"
        }
    ]
    
    with get_db_context() as db:
        try:
            created_count = 0
            
            for service_data in services:
                # Проверяем, существует ли уже такой сервис
                existing = db.query(ServiceProvider).filter(
                    ServiceProvider.name == service_data["name"]
                ).first()
                
                if existing:
                    print(f"⚠️  Сервис '{service_data['name']}' уже существует")
                    continue
                
                # Создаем новый сервис
                service = ServiceProvider(**service_data)
                db.add(service)
                created_count += 1
                print(f"✅ Создан сервис: {service_data['name']}")
            
            db.commit()
            print(f"\n🎉 Создано {created_count} новых сервисов")
            
            # Показываем общую статистику
            total_services = db.query(ServiceProvider).count()
            active_services = db.query(ServiceProvider).filter(
                ServiceProvider.status == "active"
            ).count()
            
            print(f"\n📊 Статистика сервисов:")
            print(f"   • Всего сервисов: {total_services}")
            print(f"   • Активных: {active_services}")
            
            # Группировка по типам
            types = db.query(ServiceProvider.provider_type).distinct().all()
            print(f"\n📋 Типы сервисов:")
            for (type_name,) in types:
                count = db.query(ServiceProvider).filter(
                    ServiceProvider.provider_type == type_name
                ).count()
                
                type_labels = {
                    'ai': 'ИИ-сервисы',
                    'hosting': 'Хостинг',
                    'payment': 'Платежи',
                    'analytics': 'Аналитика',
                    'storage': 'Хранилище',
                    'email': 'Email',
                    'sms': 'SMS',
                    'cdn': 'CDN',
                    'monitoring': 'Мониторинг',
                    'other': 'Другое'
                }
                
                label = type_labels.get(type_name, type_name)
                print(f"   • {label}: {count}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании сервисов: {e}")
            db.rollback()
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Создание базовых сервисов...")
    print("=" * 50)
    
    if create_basic_services():
        print("\n✅ Базовые сервисы успешно созданы!")
    else:
        print("\n❌ Ошибка при создании сервисов")
        sys.exit(1)

#!/usr/bin/env python3
"""Тестирование импортов для диагностики проблемы"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    print("Тестирование импортов...")
    
    # 1. Базовые импорты
    try:
        from app.database.database import get_db_context
        print("✓ Импорт database успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта database: {e}")
    
    # 2. Модели
    try:
        from app.database.models import Project, FinanceTransaction
        print("✓ Импорт models успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта models: {e}")
    
    # 3. CRM модели
    try:
        from app.database.crm_models import Lead, Deal, Client, ClientStatus
        print("✓ Импорт crm_models успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта crm_models: {e}")
    
    # 4. IntegrationService
    try:
        from app.services.integration_service import IntegrationService
        print("✓ Импорт IntegrationService успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта IntegrationService: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Роутеры
    try:
        from app.admin.routers import leads, deals, projects
        print("✓ Импорт роутеров успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта роутеров: {e}")
    
    print("\nТестирование завершено!")

if __name__ == "__main__":
    test_imports()
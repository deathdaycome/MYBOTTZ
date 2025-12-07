#!/usr/bin/env python3
"""
Тест API для получения исполнителей
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.auth_service import AuthService

def test_get_executors():
    """Тестирование получения списка исполнителей"""
    
    print("Тестирование AuthService.get_executors()...")
    
    executors = AuthService.get_executors()
    
    print(f"\nПолучено {len(executors)} исполнителей:")
    
    for executor in executors:
        print(f"\n  Исполнитель ID {executor.get('id')}:")
        print(f"    - Username: {executor.get('username')}")
        print(f"    - Role: {executor.get('role')}")
        print(f"    - First Name: {executor.get('first_name')}")
        print(f"    - Last Name: {executor.get('last_name')}")
        print(f"    - Email: {executor.get('email')}")
        print(f"    - Active: {executor.get('is_active')}")
    
    return executors

if __name__ == "__main__":
    executors = test_get_executors()
    
    if not executors:
        print("\n⚠️ Список исполнителей пуст!")
    else:
        print(f"\n✅ Успешно получено {len(executors)} исполнителей")
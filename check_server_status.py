#!/usr/bin/env python3
"""
Скрипт для проверки статуса страниц сервера
"""

import requests
import time
from typing import Dict, List

def check_page_status(url: str, auth: tuple = None, timeout: int = 10) -> Dict:
    """Проверить статус страницы"""
    try:
        response = requests.get(url, auth=auth, timeout=timeout, allow_redirects=False)
        return {
            'url': url,
            'status_code': response.status_code,
            'success': 200 <= response.status_code < 400,
            'response_time': response.elapsed.total_seconds(),
            'error': None
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'status_code': None,
            'success': False,
            'response_time': None,
            'error': str(e)
        }

def test_server_pages():
    """Тестировать основные страницы сервера"""
    base_url = "http://147.45.215.199:8001"
    auth = None  # Проверяем без авторизации сначала
    
    pages_to_test = [
        f"{base_url}/admin/",
        f"{base_url}/admin/leads",
        f"{base_url}/admin/clients", 
        f"{base_url}/admin/deals",
        f"{base_url}/admin/users",
        f"{base_url}/admin/documents",
        f"{base_url}/admin/avito/"
    ]
    
    print("🔍 Проверяем состояние сервера...")
    print(f"Сервер: {base_url}")
    print(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    results = []
    for page in pages_to_test:
        print(f"Проверяем: {page}")
        result = check_page_status(page, auth)
        results.append(result)
        
        if result['success']:
            print(f"✅ {result['status_code']} - {result['response_time']:.2f}s")
        else:
            print(f"❌ {result['status_code']} - {result['error']}")
        
        time.sleep(0.5)  # Небольшая задержка между запросами
    
    print("-" * 60)
    
    # Сводка результатов
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Работают: {len(successful)}/{len(results)} страниц")
    if failed:
        print(f"❌ Не работают:")
        for fail in failed:
            print(f"   - {fail['url']} ({fail['status_code']} - {fail['error']})")
    
    return len(failed) == 0

if __name__ == "__main__":
    success = test_server_pages()
    exit(0 if success else 1)
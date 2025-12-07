#!/usr/bin/env python3
"""
Проверка всех страниц React админки на доступность и ошибки
"""

import asyncio
from playwright.async_api import async_playwright
import json

# Страницы для проверки
PAGES = [
    {'name': 'Dashboard', 'url': 'https://nikolaevcodev.ru/admin/'},
    {'name': 'Projects', 'url': 'https://nikolaevcodev.ru/admin/projects'},
    {'name': 'Tasks', 'url': 'https://nikolaevcodev.ru/admin/tasks'},
    {'name': 'Notifications', 'url': 'https://nikolaevcodev.ru/admin/notifications'},
    {'name': 'Analytics', 'url': 'https://nikolaevcodev.ru/admin/analytics'},
    {'name': 'Users', 'url': 'https://nikolaevcodev.ru/admin/users'},
    {'name': 'Finance', 'url': 'https://nikolaevcodev.ru/admin/finance'},
    {'name': 'Settings', 'url': 'https://nikolaevcodev.ru/admin/settings'},
]

async def check_page(page, page_info):
    """Проверка одной страницы"""
    url = page_info['url']
    name = page_info['name']

    print(f"\n{'='*80}")
    print(f"🔍 Проверка страницы: {name}")
    print(f"📍 URL: {url}")
    print(f"{'='*80}")

    errors = []
    warnings = []
    console_logs = []

    # Перехват ошибок консоли
    def handle_console(msg):
        msg_type = msg.type
        text = msg.text

        console_logs.append({
            'type': msg_type,
            'text': text
        })

        # Игнорируем шрифты и DevTools
        if 'roboto' in text.lower() or 'font' in text.lower():
            return
        if 'DevTools' in text:
            return

        if msg_type == 'error':
            errors.append(text)
            print(f"  ❌ ERROR: {text[:150]}")
        elif msg_type == 'warning':
            warnings.append(text)
            print(f"  ⚠️  WARNING: {text[:150]}")

    page.on('console', handle_console)

    # Перехват ошибок страницы
    def handle_page_error(error):
        errors.append(str(error))
        print(f"  ❌ PAGE ERROR: {error}")

    page.on('pageerror', handle_page_error)

    try:
        # Переход на страницу
        response = await page.goto(url, wait_until='networkidle', timeout=30000)

        if response:
            status = response.status
            print(f"  📊 HTTP Status: {status}")

            if status == 404:
                errors.append(f"404 Not Found - страница не существует")
                print(f"  ❌ Страница не найдена (404)")
                return {
                    'name': name,
                    'url': url,
                    'status': 'FAILED',
                    'http_status': status,
                    'errors': errors,
                    'warnings': warnings
                }

        # Ждем загрузки React
        await page.wait_for_timeout(3000)

        # Проверяем наличие root элемента
        root = await page.query_selector('#root')
        if root:
            print(f"  ✅ React root найден")
        else:
            errors.append("React root элемент не найден")
            print(f"  ❌ React root НЕ найден")

        # Проверяем title
        title = await page.title()
        print(f"  📄 Title: {title}")

        # Делаем скриншот
        screenshot_path = f"/Users/ivan/Desktop/СРМ РЕАКТ/screenshots/page_{name.lower().replace(' ', '_')}.png"
        await page.screenshot(path=screenshot_path)
        print(f"  📸 Скриншот: {screenshot_path}")

        # Итоги
        if errors:
            print(f"\n  ❌ ОШИБКИ ({len(errors)}):")
            for i, err in enumerate(errors[:5], 1):
                print(f"     {i}. {err[:200]}")

        if warnings:
            print(f"\n  ⚠️  ПРЕДУПРЕЖДЕНИЯ ({len(warnings)}):")
            for i, warn in enumerate(warnings[:3], 1):
                print(f"     {i}. {warn[:200]}")

        status = 'PASSED' if not errors else 'FAILED'
        print(f"\n  {'✅ УСПЕШНО' if status == 'PASSED' else '❌ ПРОВАЛ'}")

        return {
            'name': name,
            'url': url,
            'status': status,
            'http_status': response.status if response else None,
            'errors': errors,
            'warnings': warnings,
            'title': title
        }

    except Exception as e:
        error_msg = f"Исключение при проверке: {str(e)}"
        errors.append(error_msg)
        print(f"  ❌ EXCEPTION: {e}")

        return {
            'name': name,
            'url': url,
            'status': 'FAILED',
            'errors': errors,
            'warnings': warnings
        }

async def main():
    """Главная функция"""
    print("🚀 АВТОМАТИЧЕСКАЯ ПРОВЕРКА ВСЕХ СТРАНИЦ REACT АДМИНКИ")
    print("="*80)

    results = []

    async with async_playwright() as p:
        # Запускаем браузер
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )

        page = await context.new_page()

        # Проверяем каждую страницу
        for page_info in PAGES:
            result = await check_page(page, page_info)
            results.append(result)
            await page.wait_for_timeout(1000)

        await browser.close()

    # Итоговый отчет
    print("\n" + "="*80)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("="*80)

    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')

    print(f"\n✅ Успешно: {passed}/{len(results)}")
    print(f"❌ Провалено: {failed}/{len(results)}")

    if failed > 0:
        print(f"\n❌ ПРОВАЛЕННЫЕ СТРАНИЦЫ:")
        for r in results:
            if r['status'] == 'FAILED':
                print(f"\n  📄 {r['name']} ({r['url']})")
                print(f"     HTTP: {r.get('http_status', 'N/A')}")
                print(f"     Ошибок: {len(r['errors'])}")
                if r['errors']:
                    for err in r['errors'][:3]:
                        print(f"       - {err[:150]}")

    # Сохраняем отчет
    report_path = "/Users/ivan/Desktop/СРМ РЕАКТ/pages_check_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n📄 Полный отчет: {report_path}")

    print("\n" + "="*80)
    if failed == 0:
        print("🎉 ВСЕ СТРАНИЦЫ РАБОТАЮТ!")
    else:
        print("💥 ЕСТЬ ПРОБЛЕМЫ - ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ!")
    print("="*80)

    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

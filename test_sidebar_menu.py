#!/usr/bin/env python3
"""
Быстрый тест отображения бокового меню
"""
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# Настройки
BASE_URL = "https://nikolaevcodev.ru"
USERNAME = "admin"
PASSWORD = "testpass123"
SCREENSHOTS_DIR = "test_screenshots_sidebar"

# Создаем папку для скриншотов
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def take_screenshot(page, name):
    """Сделать скриншот с timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SCREENSHOTS_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"✅ Screenshot saved: {filename}")
    return filename

def test_sidebar_menu():
    """Тест отображения бокового меню"""
    with sync_playwright() as p:
        print("🚀 Запуск браузера...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()

        try:
            # 1. Логин
            print(f"\n1️⃣ Открываем {BASE_URL}/admin/login")
            page.goto(f"{BASE_URL}/admin/login", wait_until="networkidle", timeout=30000)
            time.sleep(2)
            take_screenshot(page, "01_login_page")

            print("\n2️⃣ Авторизация...")
            page.fill('input[type="text"]', USERNAME)
            page.fill('input[type="password"]', PASSWORD)
            page.click('button[type="submit"]')

            # Ждем редиректа после логина
            page.wait_for_url(f"{BASE_URL}/admin**", timeout=30000)
            time.sleep(3)
            take_screenshot(page, "02_after_login")
            print("✅ Авторизация успешна!")

            # 2. Проверяем роль в localStorage
            print("\n3️⃣ Проверяем роль пользователя в localStorage...")
            auth_data = page.evaluate("""
                () => {
                    const auth = localStorage.getItem('auth');
                    return auth ? JSON.parse(auth) : null;
                }
            """)

            if auth_data:
                print(f"   ✅ Auth data found:")
                print(f"      Username: {auth_data.get('username')}")
                print(f"      Role: {auth_data.get('role')}")
                print(f"      First Name: {auth_data.get('firstName')}")
            else:
                print(f"   ❌ Auth data NOT found in localStorage")

            # 3. Открываем боковое меню
            print("\n4️⃣ Открываем боковое меню...")

            # Ищем кнопку меню
            menu_button = page.locator('button:has-text(""), button[aria-label*="menu"], button[aria-label*="Меню"], [class*="menu-button"], [class*="hamburger"]').first

            if menu_button.is_visible(timeout=2000):
                print("   ✅ Кнопка меню найдена, кликаем...")
                menu_button.click()
                time.sleep(2)
            else:
                print("   ⚠️ Кнопка меню не найдена, возможно меню уже открыто")

            take_screenshot(page, "03_sidebar_opened")

            # 4. Проверяем содержимое меню
            print("\n5️⃣ Проверяем содержимое бокового меню...")

            # Проверяем есть ли пункты меню
            menu_items = page.locator('nav a, aside a, [class*="sidebar"] a, [class*="menu"] a')
            count = menu_items.count()

            if count > 0:
                print(f"   ✅ Найдено {count} пунктов меню:")
                for i in range(min(count, 10)):  # Показываем первые 10
                    text = menu_items.nth(i).text_content()
                    print(f"      - {text}")
            else:
                print("   ❌ Пункты меню НЕ найдены!")

                # Проверяем есть ли текст "Нет доступных разделов"
                no_sections = page.locator('text="Нет доступных разделов"')
                if no_sections.is_visible():
                    print("   ❌ Отображается: 'Нет доступных разделов'")
                else:
                    print("   ⚠️ Не найдено ни пунктов меню, ни сообщения об отсутствии")

            take_screenshot(page, "04_menu_content")

            print("\n✅ Тестирование завершено!")
            print(f"📁 Скриншоты сохранены в: {SCREENSHOTS_DIR}/")

        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            take_screenshot(page, "ERROR_final_state")
            import traceback
            traceback.print_exc()
            raise

        finally:
            print("\n🔚 Закрытие браузера...")
            browser.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ТЕСТ ОТОБРАЖЕНИЯ БОКОВОГО МЕНЮ")
    print("=" * 60)
    test_sidebar_menu()

#!/usr/bin/env python3
"""
Тест бокового меню с очисткой кэша
"""
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# Настройки
BASE_URL = "https://nikolaevcodev.ru"
USERNAME = "admin"
PASSWORD = "testpass123"
SCREENSHOTS_DIR = "test_screenshots_clean"

# Создаем папку для скриншотов
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def take_screenshot(page, name):
    """Сделать скриншот с timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SCREENSHOTS_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"✅ Screenshot saved: {filename}")
    return filename

def test_sidebar_with_clean_cache():
    """Тест бокового меню с полной очисткой кэша"""
    with sync_playwright() as p:
        print("🚀 Запуск браузера...")
        browser = p.chromium.launch(headless=True)
        # Создаем ЧИСТЫЙ контекст без сохраненных данных
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()

        try:
            # 1. Открываем сайт и очищаем localStorage
            print(f"\n1️⃣ Открываем {BASE_URL}/admin/login")
            page.goto(f"{BASE_URL}/admin/login", wait_until="networkidle", timeout=30000)

            print("   🧹 Очищаем localStorage...")
            page.evaluate("localStorage.clear()")
            print("   ✅ localStorage очищен")

            time.sleep(2)
            take_screenshot(page, "01_login_page")

            # 2. Авторизация
            print("\n2️⃣ Авторизация...")
            page.fill('input[type="text"]', USERNAME)
            page.fill('input[type="password"]', PASSWORD)
            page.click('button[type="submit"]')

            # Ждем редиректа после логина
            page.wait_for_url(f"{BASE_URL}/admin**", timeout=30000)
            time.sleep(3)
            take_screenshot(page, "02_after_login")
            print("   ✅ Авторизация успешна!")

            # 3. Проверяем роль в localStorage
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
                print(f"      Role: {auth_data.get('role')} {'✅ ВЕРХНИЙ РЕГИСТР!' if auth_data.get('role') == 'OWNER' else '❌ МАЛЕНЬКИЕ БУКВЫ!'}")
                print(f"      First Name: {auth_data.get('firstName')}")
            else:
                print(f"   ❌ Auth data NOT found in localStorage")

            # 4. Ищем кнопку открытия меню на dashboard
            print("\n4️⃣ Ищем кнопку открытия меню...")

            # Ищем любую кнопку с иконкой меню (обычно это три полоски или Menu)
            menu_open_buttons = [
                'button:has-text("☰")',
                'button[aria-label*="menu"]',
                'button[title*="меню"]',
                '[class*="menu-toggle"]',
                '[class*="sidebar-toggle"]'
            ]

            menu_button_found = False
            for selector in menu_open_buttons:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=1000):
                        print(f"   ✅ Кнопка меню найдена: {selector}")
                        btn.click()
                        time.sleep(2)
                        menu_button_found = True
                        break
                except:
                    continue

            if not menu_button_found:
                print("   ⚠️ Кнопка меню не найдена, возможно меню уже открыто")

            take_screenshot(page, "03_after_menu_click")

            # 5. Проверяем содержимое меню
            print("\n5️⃣ Проверяем содержимое бокового меню...")

            # Ждем появления sidebar
            time.sleep(2)

            # Проверяем есть ли пункты меню
            menu_selectors = [
                'nav a',
                'aside a',
                '[class*="sidebar"] a',
                '[class*="menu-item"]',
                '[class*="FlowingMenu"] a'
            ]

            total_found = 0
            for selector in menu_selectors:
                try:
                    items = page.locator(selector)
                    count = items.count()
                    if count > 0:
                        print(f"   ✅ Найдено {count} пунктов меню по селектору '{selector}':")
                        for i in range(min(count, 15)):
                            try:
                                text = items.nth(i).text_content(timeout=1000)
                                if text and text.strip():
                                    print(f"      - {text.strip()}")
                                    total_found += 1
                            except:
                                continue
                        break
                except:
                    continue

            if total_found == 0:
                print("   ❌ Пункты меню НЕ найдены!")

                # Проверяем есть ли текст "Нет доступных разделов"
                no_sections = page.locator('text="Нет доступных разделов"')
                if no_sections.is_visible(timeout=2000):
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

        finally:
            print("\n🔚 Закрытие браузера...")
            browser.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ТЕСТ БОКОВОГО МЕНЮ С ОЧИСТКОЙ КЭША")
    print("=" * 60)
    test_sidebar_with_clean_cache()

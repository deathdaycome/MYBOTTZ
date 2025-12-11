#!/usr/bin/env python3
"""
Автоматическое тестирование админки с созданием скриншотов
"""
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright, expect

# Настройки
BASE_URL = "https://nikolaevcodev.ru/admin"
USERNAME = "admin"
PASSWORD = "testpass123"
SCREENSHOTS_DIR = "test_screenshots"

# Создаем папку для скриншотов
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def take_screenshot(page, name):
    """Сделать скриншот с timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SCREENSHOTS_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"✅ Screenshot saved: {filename}")
    return filename

def test_admin_panel():
    """Тестирование админ панели"""
    with sync_playwright() as p:
        print("🚀 Запуск браузера...")
        browser = p.chromium.launch(headless=False)  # headless=True для фона
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()

        try:
            # 1. Открытие страницы логина
            print(f"\n1️⃣ Открываем {BASE_URL}/login")
            page.goto(f"{BASE_URL}/login", wait_until="networkidle")
            time.sleep(2)
            take_screenshot(page, "01_login_page")

            # 2. Авторизация
            print("\n2️⃣ Авторизация...")
            page.fill('input[type="text"]', USERNAME)
            page.fill('input[type="password"]', PASSWORD)
            take_screenshot(page, "02_login_filled")

            page.click('button[type="submit"]')
            page.wait_for_url(f"{BASE_URL}**", timeout=10000)
            time.sleep(3)
            take_screenshot(page, "03_after_login")

            # 3. Проверка бокового меню
            print("\n3️⃣ Проверка бокового меню...")
            sidebar = page.locator('nav, aside, [class*="sidebar"], [class*="menu"]').first
            if sidebar.is_visible():
                print("✅ Боковое меню видно!")
            else:
                print("❌ ОШИБКА: Боковое меню НЕ видно!")
            take_screenshot(page, "04_sidebar_check")

            # 4. Переход на страницу проектов
            print("\n4️⃣ Переход на страницу проектов...")
            page.goto(f"{BASE_URL}/projects", wait_until="networkidle")
            time.sleep(2)
            take_screenshot(page, "05_projects_page")

            # 5. Открытие модалки создания проекта
            print("\n5️⃣ Открытие модалки создания проекта...")
            create_button = page.get_by_text("Создать проект").or_(page.get_by_text("Создать")).first
            if create_button.is_visible():
                create_button.click()
                time.sleep(1)
                take_screenshot(page, "06_create_modal_opened")

                # 6. Заполнение формы
                print("\n6️⃣ Заполнение формы создания проекта...")
                page.fill('input[placeholder*="Название"]', "Тестовый проект автотест")
                page.fill('textarea', "Описание тестового проекта")
                time.sleep(1)
                take_screenshot(page, "07_form_filled")

                # 7. Отмена создания (не создаем реально)
                print("\n7️⃣ Закрытие модалки...")
                cancel_button = page.get_by_text("Отмена").first
                if cancel_button.is_visible():
                    cancel_button.click()
                    time.sleep(1)
                    take_screenshot(page, "08_modal_closed")
            else:
                print("❌ ОШИБКА: Кнопка создания проекта не найдена!")

            # 8. Проверка дашборда
            print("\n8️⃣ Переход на дашборд...")
            page.goto(f"{BASE_URL}/", wait_until="networkidle")
            time.sleep(3)
            take_screenshot(page, "09_dashboard")

            # 9. Проверка различных страниц
            print("\n9️⃣ Проверка страницы задач...")
            page.goto(f"{BASE_URL}/tasks", wait_until="networkidle")
            time.sleep(2)
            take_screenshot(page, "10_tasks_page")

            print("\n🔟 Проверка страницы клиентов...")
            page.goto(f"{BASE_URL}/clients", wait_until="networkidle")
            time.sleep(2)
            take_screenshot(page, "11_clients_page")

            print("\n✅ Тестирование завершено успешно!")
            print(f"📁 Скриншоты сохранены в: {SCREENSHOTS_DIR}/")

        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            take_screenshot(page, "ERROR_final_state")
            raise

        finally:
            print("\n🔚 Закрытие браузера...")
            browser.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ АДМИН ПАНЕЛИ")
    print("=" * 60)
    test_admin_panel()

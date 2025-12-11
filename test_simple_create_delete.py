#!/usr/bin/env python3
"""
Простой тест создания и удаления проекта
"""
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# Настройки
BASE_URL = "https://nikolaevcodev.ru"
USERNAME = "admin"
PASSWORD = "testpass123"
SCREENSHOTS_DIR = "test_screenshots_simple"

# Создаем папку для скриншотов
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def take_screenshot(page, name):
    """Сделать скриншот с timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SCREENSHOTS_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"✅ Screenshot saved: {filename}")
    return filename

def test_create_delete_project():
    """Тест создания и удаления проекта"""
    with sync_playwright() as p:
        print("🚀 Запуск браузера...")
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            # Очищаем кэш
            storage_state=None
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

            # 2. Переход на проекты через API тестирование
            print("\n3️⃣ Тестируем создание проекта через API...")

            # Делаем API запрос через evaluate (из браузера)
            result = page.evaluate("""
                async () => {
                    try {
                        const auth = localStorage.getItem('auth');
                        if (!auth) return { success: false, error: 'No auth in localStorage' };

                        const { username, password } = JSON.parse(auth);
                        const authHeader = 'Basic ' + btoa(username + ':' + password);

                        // Создание проекта
                        const formData = new FormData();
                        formData.append('title', 'Тест автотест ' + Date.now());
                        formData.append('project_type', 'website');
                        formData.append('complexity', 'low');
                        formData.append('priority', 'low');
                        formData.append('status', 'new');

                        const createResponse = await fetch('/admin/api/projects/create', {
                            method: 'POST',
                            headers: {
                                'Authorization': authHeader
                            },
                            body: formData
                        });

                        const createData = await createResponse.json();
                        console.log('Create response:', createData);

                        if (!createData.success) {
                            return { success: false, error: 'Create failed', data: createData };
                        }

                        const projectId = createData.project.id;

                        // Удаление проекта
                        const deleteResponse = await fetch(`/admin/api/projects/${projectId}`, {
                            method: 'DELETE',
                            headers: {
                                'Authorization': authHeader,
                                'Content-Type': 'application/json'
                            }
                        });

                        const deleteData = await deleteResponse.json();
                        console.log('Delete response:', deleteData);

                        return {
                            success: true,
                            projectId: projectId,
                            createData: createData,
                            deleteData: deleteData
                        };
                    } catch (error) {
                        return { success: false, error: error.message };
                    }
                }
            """)

            print(f"\n📊 Результат API теста:")
            print(f"   Success: {result.get('success')}")
            if result.get('success'):
                print(f"   ✅ Проект ID {result.get('projectId')} создан")
                print(f"   ✅ Проект успешно удален: {result.get('deleteData', {}).get('message')}")
            else:
                print(f"   ❌ Ошибка: {result.get('error')}")
                print(f"   Данные: {result.get('data')}")

            # 4. Проверка через UI
            print("\n4️⃣ Переход на страницу проектов...")
            page.goto(f"{BASE_URL}/admin/projects", wait_until="networkidle", timeout=30000)
            time.sleep(2)
            take_screenshot(page, "03_projects_page")

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
    print("🧪 ТЕСТ СОЗДАНИЯ И УДАЛЕНИЯ ПРОЕКТА")
    print("=" * 60)
    test_create_delete_project()

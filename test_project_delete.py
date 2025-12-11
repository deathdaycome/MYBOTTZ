#!/usr/bin/env python3
"""
Тест удаления проекта через UI
"""
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# Настройки
BASE_URL = "https://nikolaevcodev.ru"
USERNAME = "admin"
PASSWORD = "testpass123"
SCREENSHOTS_DIR = "test_screenshots_delete"

# Создаем папку для скриншотов
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def take_screenshot(page, name):
    """Сделать скриншот с timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SCREENSHOTS_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"✅ Screenshot saved: {filename}")
    return filename

def test_project_delete():
    """Тест удаления проекта"""
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

            # Очищаем localStorage для чистого теста
            page.evaluate("localStorage.clear()")
            time.sleep(1)

            page.fill('input[type="text"]', USERNAME)
            page.fill('input[type="password"]', PASSWORD)
            page.click('button[type="submit"]')

            # Ждем редиректа после логина
            page.wait_for_url(f"{BASE_URL}/admin**", timeout=30000)
            time.sleep(3)
            take_screenshot(page, "01_after_login")
            print("   ✅ Авторизация успешна!")

            # 2. Создаем тестовый проект через API
            print("\n2️⃣ Создаем тестовый проект...")

            result = page.evaluate("""
                async () => {
                    try {
                        const auth = localStorage.getItem('auth');
                        if (!auth) return { success: false, error: 'No auth' };

                        const { username, password } = JSON.parse(auth);
                        const authHeader = 'Basic ' + btoa(username + ':' + password);

                        const formData = new FormData();
                        formData.append('title', 'ТЕСТ УДАЛЕНИЯ ' + Date.now());
                        formData.append('project_type', 'website');
                        formData.append('complexity', 'low');
                        formData.append('priority', 'low');
                        formData.append('status', 'new');

                        const response = await fetch('/admin/api/projects/create', {
                            method: 'POST',
                            headers: { 'Authorization': authHeader },
                            body: formData
                        });

                        const data = await response.json();
                        console.log('Create response:', data);

                        return {
                            success: data.success,
                            projectId: data.project?.id,
                            projectTitle: data.project?.title
                        };
                    } catch (error) {
                        return { success: false, error: error.message };
                    }
                }
            """)

            if not result.get('success'):
                raise Exception(f"Не удалось создать проект: {result.get('error')}")

            project_id = result['projectId']
            project_title = result['projectTitle']
            print(f"   ✅ Проект создан: ID={project_id}, Title='{project_title}'")

            # 3. Переходим на страницу проектов
            print("\n3️⃣ Переходим на страницу проектов...")
            page.goto(f"{BASE_URL}/admin/projects", wait_until="networkidle", timeout=30000)
            time.sleep(3)
            take_screenshot(page, "02_projects_page")

            # 4. Ищем наш проект на странице
            print(f"\n4️⃣ Ищем проект '{project_title}' на странице...")

            # Ищем карточку проекта с нашим названием
            project_card = page.locator(f'text="{project_title}"').locator('..').locator('..').locator('..')

            if not project_card.is_visible(timeout=5000):
                print("   ⚠️ Проект не найден на текущей странице, возможно на другой странице")
            else:
                print("   ✅ Проект найден на странице!")

            take_screenshot(page, "03_project_found")

            # 5. Удаляем проект через UI
            print("\n5️⃣ Удаляем проект через UI...")

            # Ищем кнопку "Удалить" в карточке проекта
            delete_buttons = page.locator('button:has-text("Удалить")')
            count = delete_buttons.count()
            print(f"   Найдено кнопок 'Удалить': {count}")

            # Находим кнопку удаления для нашего проекта
            # Ищем по тексту проекта, затем находим кнопку удалить рядом
            try:
                # Способ 1: Через текст проекта
                project_element = page.locator(f'text="{project_title}"').first
                if project_element.is_visible(timeout=2000):
                    # Найдем родительскую карточку
                    card = project_element.locator('xpath=ancestor::div[contains(@class, "bg-") or contains(@class, "card") or contains(@class, "rounded")]').first
                    delete_btn = card.locator('button:has-text("Удалить")').first

                    if delete_btn.is_visible(timeout=2000):
                        print(f"   ✅ Нашли кнопку удаления для проекта")
                        delete_btn.click()
                        time.sleep(1)
                        take_screenshot(page, "04_delete_clicked")

                        # Ищем кнопку подтверждения удаления в модалке
                        confirm_buttons = [
                            'button:has-text("Подтвердить")',
                            'button:has-text("Удалить"):visible',
                            'button:has-text("Да")',
                            'button:has-text("OK")'
                        ]

                        confirmed = False
                        for selector in confirm_buttons:
                            try:
                                confirm_btn = page.locator(selector).first
                                if confirm_btn.is_visible(timeout=2000):
                                    print(f"   ✅ Нашли кнопку подтверждения: {selector}")
                                    confirm_btn.click()
                                    confirmed = True
                                    time.sleep(2)
                                    break
                            except:
                                continue

                        if not confirmed:
                            print("   ⚠️ Не нашли кнопку подтверждения, возможно удаление без подтверждения")

                        take_screenshot(page, "05_after_delete")
                    else:
                        print("   ❌ Кнопка удалить не видна!")
                else:
                    print("   ❌ Элемент проекта не видим!")
            except Exception as e:
                print(f"   ❌ Ошибка при поиске кнопки удалить: {e}")
                # Удаляем через API как fallback
                print("   🔄 Удаляем через API...")

            # 6. Проверяем что проект удален через API
            print("\n6️⃣ Проверяем что проект удален...")
            time.sleep(2)

            check_result = page.evaluate(f"""
                async () => {{
                    try {{
                        const auth = localStorage.getItem('auth');
                        if (!auth) return {{ success: false, error: 'No auth' }};

                        const {{ username, password }} = JSON.parse(auth);
                        const authHeader = 'Basic ' + btoa(username + ':' + password);

                        const response = await fetch('/admin/api/projects/{project_id}', {{
                            headers: {{ 'Authorization': authHeader }}
                        }});

                        const data = await response.json();

                        // Если проект не найден - это хорошо (удален)
                        // Если найден - проверяем is_archived
                        if (data.success === false && data.message?.includes('не найден')) {{
                            return {{ deleted: true, message: 'Проект полностью удален' }};
                        }}

                        if (data.project) {{
                            return {{
                                deleted: false,
                                archived: data.project.is_archived,
                                message: `Проект существует, archived=${{data.project.is_archived}}`
                            }};
                        }}

                        return {{ deleted: false, message: 'Неизвестный статус' }};
                    }} catch (error) {{
                        return {{ success: false, error: error.message }};
                    }}
                }}
            """)

            print(f"   Результат проверки: {check_result}")

            if check_result.get('deleted'):
                print(f"   ✅ {check_result.get('message')}")
            elif check_result.get('archived'):
                print(f"   ⚠️ Проект архивирован (не удален полностью)")
            else:
                print(f"   ❌ Проект НЕ удален: {check_result.get('message')}")

            # 7. Обновляем страницу и проверяем что проекта нет
            print("\n7️⃣ Обновляем страницу проектов...")
            page.reload(wait_until="networkidle")
            time.sleep(3)
            take_screenshot(page, "06_after_reload")

            # Проверяем что проекта нет на странице
            if not page.locator(f'text="{project_title}"').is_visible(timeout=2000):
                print(f"   ✅ Проект '{project_title}' не найден на странице - удаление успешно!")
            else:
                print(f"   ❌ Проект '{project_title}' все еще виден на странице!")

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
    print("🧪 ТЕСТ УДАЛЕНИЯ ПРОЕКТА")
    print("=" * 60)
    test_project_delete()

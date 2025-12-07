"""
Тест исправления загрузки роли для страницы регламентов
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json

# Настройки Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

# URL продакшн сайта
BASE_URL = "https://nikolaevcodev.ru"
USERNAME = "admin"
PASSWORD = "qwerty123"

print("=" * 80)
print("ТЕСТ ИСПРАВЛЕНИЯ ЗАГРУЗКИ РОЛИ ДЛЯ РЕГЛАМЕНТОВ")
print("=" * 80)

driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1920, 1080)

try:
    # Открываем страницу с Basic Auth
    auth_url = f"https://{USERNAME}:{PASSWORD}@nikolaevcodev.ru/admin/timlead-regulations"

    print(f"\n1. Открываем страницу регламентов...")
    driver.get(auth_url)

    # Очищаем localStorage (симулируем проблему пользователя)
    print("2. Очищаем localStorage (симулируем проблему)...")
    driver.execute_script("localStorage.clear()")

    # Перезагружаем страницу
    print("3. Перезагружаем страницу...")
    driver.refresh()

    # Ждем загрузки
    time.sleep(5)

    # Проверяем localStorage после загрузки
    print("\n4. Проверяем localStorage после перезагрузки:")
    auth_data = driver.execute_script("return localStorage.getItem('auth')")

    if auth_data:
        auth_obj = json.loads(auth_data)
        print(f"   ✅ localStorage восстановлен")
        print(f"   Username: {auth_obj.get('username', 'N/A')}")
        print(f"   Role: {auth_obj.get('role', 'НЕТ РОЛИ!')}")

        if auth_obj.get('role') == 'owner':
            print(f"   ✅ Роль 'owner' успешно загружена!")
        else:
            print(f"   ❌ Роль не загружена или неверная")
    else:
        print("   ❌ localStorage пуст")

    # Проверяем консоль на логи о загрузке роли
    print("\n5. Проверяем консоль на логи загрузки роли:")
    logs = driver.get_log('browser')

    role_fetch_logs = [log for log in logs if 'Role not in localStorage' in log['message'] or 'User role fetched' in log['message']]

    if role_fetch_logs:
        print(f"   ✅ Найдено {len(role_fetch_logs)} логов о загрузке роли:")
        for log in role_fetch_logs:
            print(f"      {log['message'][:150]}")
    else:
        print("   ℹ️  Логи о загрузке роли не найдены (возможно, роль уже была в localStorage)")

    # Ищем кнопку "Редактировать"
    print("\n6. Проверяем наличие кнопки 'Редактировать':")
    try:
        edit_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Редактировать')]")
        if edit_buttons:
            print(f"   ✅ Найдено {len(edit_buttons)} кнопок 'Редактировать'")
            print(f"   ✅ Редактирование доступно для owner!")
        else:
            print("   ❌ Кнопки 'Редактировать' не найдены")
    except Exception as e:
        print(f"   ❌ Ошибка при поиске кнопок: {e}")

    # Проверяем API запрос к /auth/me
    print("\n7. Проверяем API запросы:")
    performance_logs = driver.get_log('performance')

    auth_me_found = False
    for log_entry in performance_logs:
        try:
            import json
            log_data = json.loads(log_entry['message'])
            message = log_data.get('message', {})

            if message.get('method') == 'Network.responseReceived':
                response = message.get('params', {}).get('response', {})
                url = response.get('url', '')

                if '/admin/api/auth/me' in url:
                    auth_me_found = True
                    status = response.get('status')
                    print(f"   ✅ Найден запрос к /auth/me")
                    print(f"   Статус: {status}")
                    break
        except:
            pass

    if not auth_me_found:
        print("   ℹ️  Запрос к /auth/me не найден (роль была в localStorage)")

    # Делаем скриншот
    screenshot_path = "/Users/ivan/Desktop/СРМ РЕАКТ/test_regulations_role_fix.png"
    driver.save_screenshot(screenshot_path)
    print(f"\n8. Скриншот сохранён: {screenshot_path}")

    print("\n" + "=" * 80)
    print("ТЕСТ ЗАВЕРШЁН")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()

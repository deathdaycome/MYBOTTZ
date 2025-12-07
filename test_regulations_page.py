"""
Тест страницы регламентов тимлида
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import base64

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
print("ТЕСТ СТРАНИЦЫ РЕГЛАМЕНТОВ ТИМЛИДА")
print("=" * 80)

driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1920, 1080)

try:
    # Открываем страницу с Basic Auth
    auth_url = f"https://{USERNAME}:{PASSWORD}@nikolaevcodev.ru/admin/timlead-regulations"

    print(f"\n1. Открываем страницу: {auth_url}")
    driver.get(auth_url)

    # Ждем загрузки
    time.sleep(3)

    # Проверяем URL
    print(f"2. Текущий URL: {driver.current_url}")

    # Проверяем заголовок страницы
    print(f"3. Заголовок страницы: {driver.title}")

    # Ищем заголовок "ТИМЛИД — РЕГЛАМЕНТЫ"
    try:
        header = driver.find_element(By.XPATH, "//*[contains(text(), 'ТИМЛИД')]")
        print(f"✅ Найден заголовок: {header.text}")
    except:
        print("❌ Заголовок 'ТИМЛИД — РЕГЛАМЕНТЫ' не найден")

    # Ждем загрузки данных
    print("\n4. Ожидаем загрузку регламентов...")
    time.sleep(3)

    # Ищем карточки регламентов
    try:
        # Ищем элементы с текстом "Регламент"
        regulations = driver.find_elements(By.XPATH, "//*[contains(text(), 'Регламент')]")
        print(f"✅ Найдено карточек регламентов: {len(regulations)}")

        if len(regulations) > 0:
            print("\nНайденные регламенты:")
            for i, reg in enumerate(regulations[:5], 1):
                print(f"  {i}. {reg.text[:100]}")
        else:
            print("⚠️  Карточки регламентов не найдены")
    except Exception as e:
        print(f"❌ Ошибка при поиске регламентов: {e}")

    # Проверяем консоль браузера на ошибки
    print("\n5. Проверяем консоль браузера:")
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE']

    if errors:
        print(f"❌ Найдено ошибок в консоли: {len(errors)}")
        for error in errors[:5]:
            print(f"   {error['message'][:200]}")
    else:
        print("✅ Ошибок в консоли не найдено")

    # Проверяем network запросы
    print("\n6. Проверяем запрос к API:")
    performance_logs = driver.get_log('performance')

    api_found = False
    for log_entry in performance_logs:
        import json
        log_data = json.loads(log_entry['message'])
        message = log_data.get('message', {})

        if message.get('method') == 'Network.responseReceived':
            response = message.get('params', {}).get('response', {})
            url = response.get('url', '')

            if 'timlead-regulations' in url:
                api_found = True
                status = response.get('status')
                print(f"✅ Найден API запрос: {url}")
                print(f"   Статус: {status}")
                break

    if not api_found:
        print("⚠️  API запрос к /admin/api/timlead-regulations/ не найден")

    # Делаем скриншот
    screenshot_path = "/Users/ivan/Desktop/СРМ РЕАКТ/test_regulations_screenshot.png"
    driver.save_screenshot(screenshot_path)
    print(f"\n7. Скриншот сохранён: {screenshot_path}")

    # Получаем HTML страницы
    page_source = driver.page_source

    # Проверяем наличие ключевых элементов
    print("\n8. Проверка HTML содержимого:")
    checks = {
        "Загрузка...": "Загрузка" in page_source,
        "API endpoint в коде": "timlead-regulations" in page_source,
        "Текст 'Регламент'": "Регламент" in page_source,
        "React root div": 'id="root"' in page_source,
    }

    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")

    print("\n" + "=" * 80)
    print("ТЕСТ ЗАВЕРШЁН")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()

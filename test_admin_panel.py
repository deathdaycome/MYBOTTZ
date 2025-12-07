#!/usr/bin/env python3
"""
Автоматический тест админ-панели с проверкой ошибок в консоли
Использует Selenium ChromeDriver для проверки страницы
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URL для проверки
URL = "http://nikolaevcodev.ru/admin/"

def setup_driver():
    """Настройка ChromeDriver"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Запуск без GUI
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # Включаем логирование консоли браузера
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def check_console_errors(driver):
    """Проверка ошибок в консоли браузера"""
    logs = driver.get_log('browser')

    errors = []
    warnings = []

    for log in logs:
        level = log.get('level', '')
        message = log.get('message', '')

        # Игнорируем ошибки шрифтов и DevTools
        if 'roboto' in message.lower() or 'font' in message.lower():
            continue
        if 'DevTools' in message:
            continue

        if level == 'SEVERE':
            errors.append(message)
        elif level == 'WARNING':
            warnings.append(message)

    return errors, warnings

def test_page(url):
    """Тестирование страницы"""
    print(f"🔍 Тестирование: {url}")
    print("=" * 80)

    driver = None
    try:
        driver = setup_driver()
        driver.get(url)

        # Ждем загрузки страницы (максимум 30 секунд)
        print("⏳ Ожидание загрузки страницы...")
        time.sleep(5)  # Даем время React приложению загрузиться

        # Проверяем наличие root элемента
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "root"))
            )
            print("✅ Root элемент найден")
        except:
            print("❌ Root элемент не найден!")
            return False

        # Проверяем консоль на ошибки
        print("\n📋 Проверка консоли браузера...")
        errors, warnings = check_console_errors(driver)

        # Выводим результаты
        print(f"\n📊 Результаты:")
        print(f"   Ошибки (SEVERE): {len(errors)}")
        print(f"   Предупреждения (WARNING): {len(warnings)}")

        if errors:
            print("\n❌ ОШИБКИ В КОНСОЛИ:")
            for i, error in enumerate(errors, 1):
                print(f"\n{i}. {error}")
            return False

        if warnings:
            print("\n⚠️  ПРЕДУПРЕЖДЕНИЯ:")
            for i, warning in enumerate(warnings[:5], 1):  # Первые 5
                print(f"\n{i}. {warning}")

        # Проверяем заголовок страницы
        title = driver.title
        print(f"\n📄 Заголовок страницы: {title}")

        # Делаем скриншот
        screenshot_path = "/Users/ivan/Desktop/СРМ РЕАКТ/test_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"\n📸 Скриншот сохранен: {screenshot_path}")

        if not errors:
            print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Страница работает без ошибок.")
            return True
        else:
            return False

    except Exception as e:
        print(f"\n❌ ОШИБКА ТЕСТА: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("🚀 Автоматическая проверка админ-панели")
    print("=" * 80)

    success = test_page(URL)

    if success:
        print("\n" + "=" * 80)
        print("🎉 ТЕСТ УСПЕШЕН!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("💥 ТЕСТ ПРОВАЛЕН - обнаружены ошибки!")
        print("=" * 80)
        sys.exit(1)

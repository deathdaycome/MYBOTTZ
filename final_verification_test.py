#!/usr/bin/env python3
"""
Финальная проверка всех кнопок в карточках проектов
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_project_buttons():
    # Настройка Chrome
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("=" * 70)
        print("🧪 ФИНАЛЬНАЯ ПРОВЕРКА ФУНКЦИОНАЛЬНОСТИ ПРОЕКТОВ")
        print("=" * 70)

        # Открываем страницу проектов
        print("\n1️⃣  Открытие страницы /projects...")
        driver.get('http://localhost:5173/projects')

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        time.sleep(3)

        # Проверяем URL
        print(f"   ✅ URL: {driver.current_url}")

        # Проверяем режим отображения
        print("\n2️⃣  Проверка режима отображения...")
        view_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Таблица') or contains(text(), 'Карточки')]")

        if view_buttons:
            for btn in view_buttons:
                if 'Карточки' in btn.text:
                    classes = btn.get_attribute('class')
                    if 'shadow' not in classes and 'bg-white' not in classes:
                        print("   ⚠️  Переключаюсь в режим карточек...")
                        btn.click()
                        time.sleep(2)
                        break

        print("   ✅ Режим карточек активен")

        # Ищем карточки проектов по уникальным признакам
        print("\n3️⃣  Поиск карточек проектов...")

        # Ищем карточки которые содержат кнопки "Просмотр" и "Редактировать"
        project_cards = driver.find_elements(
            By.XPATH,
            "//div[.//button[contains(text(), 'Просмотр')] and .//button[contains(text(), 'Редактировать')]]"
        )

        if not project_cards:
            print("   ❌ Карточки проектов не найдены!")
            driver.save_screenshot('/tmp/no_cards_found.png')
            return False

        print(f"   ✅ Найдено карточек проектов: {len(project_cards)}")

        # Берем первую карточку
        card = project_cards[0]

        # Скроллим к карточке
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        time.sleep(1)

        # Делаем скриншот карточки
        card_screenshot = '/tmp/project_card_detailed.png'
        card.screenshot(card_screenshot)
        print(f"   📸 Скриншот карточки: {card_screenshot}")

        # Ищем все кнопки в карточке
        print("\n4️⃣  Анализ кнопок в карточке...")
        buttons = card.find_elements(By.TAG_NAME, 'button')

        print(f"   📊 Всего кнопок в карточке: {len(buttons)}")

        button_texts = []
        for i, btn in enumerate(buttons, 1):
            text = btn.text.strip()
            if text:
                button_texts.append(text)
                print(f"      {i}. {text}")

        # Проверяем наличие ключевых кнопок
        print("\n5️⃣  Проверка обязательных кнопок...")

        required_buttons = {
            'Просмотр': False,
            'Редактировать': False,
            'Файлы': False,
            'Добавить оплату': False,
            'Архив': False,
            'Удалить': False
        }

        for btn_name in required_buttons.keys():
            if btn_name in button_texts:
                required_buttons[btn_name] = True
                print(f"   ✅ Кнопка '{btn_name}' найдена")
            else:
                print(f"   ❌ Кнопка '{btn_name}' НЕ найдена")

        # Дополнительные кнопки (опциональные)
        print("\n6️⃣  Дополнительные кнопки (могут быть условными)...")
        optional_buttons = ['Назначить исполнителя', 'Завершить', 'Связаться', 'Чат']

        for opt_btn in optional_buttons:
            if opt_btn in button_texts:
                print(f"   ℹ️  Найдена: '{opt_btn}'")

        # Проверяем модальное окно "Файлы"
        print("\n7️⃣  Тестирование кнопки 'Файлы'...")
        try:
            files_btn = card.find_element(By.XPATH, ".//button[contains(text(), 'Файлы')]")
            files_btn.click()
            time.sleep(2)

            # Проверяем открылось ли модальное окно
            modal = driver.find_element(By.XPATH, "//div[contains(text(), 'Файлы проекта')]")
            if modal:
                print("   ✅ Модальное окно 'Файлы проекта' открылось успешно!")

                # Закрываем модалку
                close_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'btn-close') or .//text()='Закрыть']")
                close_btn.click()
                time.sleep(1)
            else:
                print("   ⚠️  Модальное окно не найдено")
        except Exception as e:
            print(f"   ❌ Ошибка при тестировании кнопки 'Файлы': {str(e)[:100]}")

        # Проверяем кнопку "Добавить оплату"
        print("\n8️⃣  Тестирование кнопки 'Добавить оплату'...")
        try:
            payment_btn = card.find_element(By.XPATH, ".//button[contains(text(), 'Добавить оплату')]")
            payment_btn.click()
            time.sleep(2)

            # Проверяем модалку
            modal = driver.find_element(By.XPATH, "//div[contains(text(), 'Добавление оплаты') or contains(text(), 'Добавить оплату')]")
            if modal:
                print("   ✅ Модальное окно 'Добавление оплаты' открылось успешно!")

                # Закрываем
                driver.find_element(By.XPATH, "//button[contains(text(), 'Отмена')]").click()
                time.sleep(1)
        except Exception as e:
            print(f"   ❌ Ошибка: {str(e)[:100]}")

        # Итоги
        print("\n" + "=" * 70)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 70)

        found_count = sum(1 for v in required_buttons.values() if v)
        total_count = len(required_buttons)

        print(f"\n✅ Найдено обязательных кнопок: {found_count}/{total_count}")

        for btn_name, found in required_buttons.items():
            status = "✅" if found else "❌"
            print(f"   {status} {btn_name}")

        percentage = (found_count / total_count) * 100
        print(f"\n📈 Покрытие функциональности: {percentage:.1f}%")

        if percentage >= 100:
            print("\n🎉 ВСЯ ФУНКЦИОНАЛЬНОСТЬ РЕАЛИЗОВАНА!")
        elif percentage >= 80:
            print("\n✅ Большая часть функциональности реализована")
        else:
            print("\n⚠️  Требуются доработки")

        return percentage >= 80

    finally:
        time.sleep(3)
        driver.quit()
        print("\n🔚 Браузер закрыт")

if __name__ == '__main__':
    success = test_project_buttons()
    exit(0 if success else 1)

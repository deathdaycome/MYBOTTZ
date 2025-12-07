"""
Тест системы входа в admin-react
Проверяет:
1. Редирект на /login при отсутствии авторизации
2. Вход под разными пользователями
3. Отображение информации о пользователе
4. Функцию выхода
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_login_system():
    """Основная функция тестирования"""

    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    try:
        print("\n" + "="*70)
        print("ТЕСТИРОВАНИЕ СИСТЕМЫ АВТОРИЗАЦИИ")
        print("="*70)

        # Тест 1: Редирект на /login
        print("\n1️⃣  Тест: Редирект на /login при отсутствии авторизации")
        print("-" * 70)

        driver.get("http://localhost:5173/")
        time.sleep(2)

        current_url = driver.current_url
        if "/login" in current_url:
            print("✅ Успешно: Редирект на страницу входа работает")
        else:
            print(f"❌ Ошибка: Ожидался редирект на /login, но URL: {current_url}")
            return

        # Тест 2: Проверка формы входа
        print("\n2️⃣  Тест: Проверка элементов формы входа")
        print("-" * 70)

        try:
            username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            print("✅ Успешно: Все элементы формы найдены")
            print(f"   - Поле username: {'найдено' if username_input else 'не найдено'}")
            print(f"   - Поле password: {'найдено' if password_input else 'не найдено'}")
            print(f"   - Кнопка входа: {'найдена' if submit_button else 'не найдена'}")
        except Exception as e:
            print(f"❌ Ошибка при поиске элементов формы: {e}")
            return

        # Тест 3: Вход под пользователем admin (owner)
        print("\n3️⃣  Тест: Вход под пользователем 'admin' (роль: владелец)")
        print("-" * 70)

        username_input.clear()
        username_input.send_keys("admin")
        password_input.clear()
        password_input.send_keys("qwerty123")

        submit_button.click()
        time.sleep(3)

        # Проверяем, что редиректнуло на главную
        current_url = driver.current_url
        if "/login" not in current_url:
            print(f"✅ Успешно: Вход выполнен, URL: {current_url}")
        else:
            print("❌ Ошибка: Вход не выполнен, остались на странице /login")
            # Проверим, есть ли сообщение об ошибке
            try:
                error_msg = driver.find_element(By.CSS_SELECTOR, ".text-red-600")
                print(f"   Сообщение об ошибке: {error_msg.text}")
            except:
                print("   Сообщение об ошибке не найдено")
            return

        # Тест 4: Проверка отображения информации о пользователе
        print("\n4️⃣  Тест: Проверка отображения информации о пользователе в header")
        print("-" * 70)

        try:
            time.sleep(2)
            # Ищем блок с информацией о пользователе
            user_info_block = driver.find_element(By.CSS_SELECTOR, ".bg-gray-50")

            print("✅ Успешно: Блок с информацией о пользователе найден")
            print(f"   Содержимое блока: {user_info_block.text}")

            # Проверяем localStorage
            auth_data = driver.execute_script("return localStorage.getItem('auth')")
            if auth_data:
                print(f"✅ Успешно: Данные авторизации сохранены в localStorage")
                import json
                auth_json = json.loads(auth_data)
                print(f"   Username: {auth_json.get('username')}")
                print(f"   Role: {auth_json.get('role')}")
                print(f"   First Name: {auth_json.get('firstName')}")
            else:
                print("❌ Ошибка: Данные авторизации не найдены в localStorage")
        except Exception as e:
            print(f"❌ Ошибка при проверке информации о пользователе: {e}")

        # Тест 5: Проверка кнопки выхода
        print("\n5️⃣  Тест: Проверка функции выхода")
        print("-" * 70)

        try:
            # Ищем кнопку выхода (LogOut icon)
            logout_button = driver.find_element(By.CSS_SELECTOR, "button[title='Выйти']")
            print("✅ Успешно: Кнопка выхода найдена")

            # Кликаем на кнопку выхода
            logout_button.click()
            time.sleep(2)

            # Проверяем редирект на /login
            current_url = driver.current_url
            if "/login" in current_url:
                print("✅ Успешно: После выхода выполнен редирект на /login")
            else:
                print(f"❌ Ошибка: Ожидался редирект на /login, но URL: {current_url}")

            # Проверяем, что localStorage очищен
            auth_data = driver.execute_script("return localStorage.getItem('auth')")
            if not auth_data:
                print("✅ Успешно: localStorage очищен после выхода")
            else:
                print(f"❌ Ошибка: localStorage не очищен: {auth_data}")
        except Exception as e:
            print(f"❌ Ошибка при тестировании выхода: {e}")

        # Тест 6: Вход под исполнителем
        print("\n6️⃣  Тест: Вход под пользователем 'executor1' (роль: исполнитель)")
        print("-" * 70)

        try:
            username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            username_input.clear()
            username_input.send_keys("executor1")
            password_input.clear()
            password_input.send_keys("test123")

            submit_button.click()
            time.sleep(3)

            # Проверяем вход
            current_url = driver.current_url
            if "/login" not in current_url:
                print(f"✅ Успешно: Вход выполнен под executor1")

                # Проверяем роль
                auth_data = driver.execute_script("return localStorage.getItem('auth')")
                if auth_data:
                    import json
                    auth_json = json.loads(auth_data)
                    role = auth_json.get('role')
                    print(f"   Роль пользователя: {role}")

                    if role == "executor":
                        print("✅ Успешно: Роль 'executor' корректно определена")
                    else:
                        print(f"❌ Ошибка: Ожидалась роль 'executor', получена '{role}'")

                # Проверяем отображение роли в UI
                time.sleep(1)
                user_info_block = driver.find_element(By.CSS_SELECTOR, ".bg-gray-50")
                if "Исполнитель" in user_info_block.text:
                    print("✅ Успешно: Роль 'Исполнитель' отображается в UI")
                else:
                    print(f"❌ Ошибка: Роль не отображается корректно. Текст блока: {user_info_block.text}")
            else:
                print("❌ Ошибка: Вход не выполнен под executor1")
                try:
                    error_msg = driver.find_element(By.CSS_SELECTOR, ".text-red-600")
                    print(f"   Сообщение об ошибке: {error_msg.text}")
                except:
                    pass
        except Exception as e:
            print(f"❌ Ошибка при входе под executor1: {e}")

        # Тест 7: Вход под тимлидом
        print("\n7️⃣  Тест: Вход под пользователем 'Casper123' (роль: тимлид)")
        print("-" * 70)

        try:
            # Сначала выходим
            logout_button = driver.find_element(By.CSS_SELECTOR, "button[title='Выйти']")
            logout_button.click()
            time.sleep(2)

            username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            username_input.clear()
            username_input.send_keys("Casper123")
            password_input.clear()
            password_input.send_keys("qwerty123")

            submit_button.click()
            time.sleep(3)

            # Проверяем вход
            current_url = driver.current_url
            if "/login" not in current_url:
                print(f"✅ Успешно: Вход выполнен под Casper123")

                # Проверяем роль
                auth_data = driver.execute_script("return localStorage.getItem('auth')")
                if auth_data:
                    import json
                    auth_json = json.loads(auth_data)
                    role = auth_json.get('role')
                    print(f"   Роль пользователя: {role}")

                    if role == "timlead":
                        print("✅ Успешно: Роль 'timlead' корректно определена")
                    else:
                        print(f"❌ Ошибка: Ожидалась роль 'timlead', получена '{role}'")

                # Проверяем отображение роли в UI
                time.sleep(1)
                user_info_block = driver.find_element(By.CSS_SELECTOR, ".bg-gray-50")
                if "Тимлид" in user_info_block.text:
                    print("✅ Успешно: Роль 'Тимлид' отображается в UI")
                else:
                    print(f"⚠️  Предупреждение: Роль не отображается корректно. Текст блока: {user_info_block.text}")
            else:
                print("❌ Ошибка: Вход не выполнен под Casper123")
                try:
                    error_msg = driver.find_element(By.CSS_SELECTOR, ".text-red-600")
                    print(f"   Сообщение об ошибке: {error_msg.text}")
                except:
                    pass
        except Exception as e:
            print(f"❌ Ошибка при входе под Casper123: {e}")

        # Итоговый отчет
        print("\n" + "="*70)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("="*70)
        print("\nБраузер останется открытым для ручной проверки.")
        print("Нажмите Enter чтобы закрыть браузер...")
        input()

    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        print("\nБраузер останется открытым для диагностики.")
        print("Нажмите Enter чтобы закрыть браузер...")
        input()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login_system()

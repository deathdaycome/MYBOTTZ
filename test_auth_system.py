"""
Тестирование системы авторизации CRM
Проверяем, что каждый пользователь может войти под своим аккаунтом
"""
import requests
from requests.auth import HTTPBasicAuth
import json

# Базовый URL продакшн сервера
BASE_URL = "https://nikolaevcodev.ru"

print("=" * 80)
print("ТЕСТИРОВАНИЕ СИСТЕМЫ АВТОРИЗАЦИИ")
print("=" * 80)

# Тестовые пользователи (username : пароль_который_нужно_установить)
test_users = {
    "admin": "qwerty123",  # owner - уже работает
    "Casper123": "test123",  # executor
    "omen": "test123",  # timlead
}

print("\n1. Проверяем endpoint /admin/api/auth/me для каждого пользователя:\n")

results = []

for username, password in test_users.items():
    try:
        response = requests.get(
            f"{BASE_URL}/admin/api/auth/me",
            auth=HTTPBasicAuth(username, password),
            timeout=10
        )

        if response.status_code == 200:
            user_data = response.json()
            results.append({
                "username": username,
                "status": "✅ УСПЕХ",
                "role": user_data.get("role"),
                "name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            })
            print(f"   ✅ {username:15} -> Роль: {user_data.get('role'):10} | Имя: {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
        elif response.status_code == 401:
            results.append({
                "username": username,
                "status": "❌ 401 (неверный пароль)",
                "role": None,
                "name": None
            })
            print(f"   ❌ {username:15} -> 401 Unauthorized (пароль '{password}' неверный)")
        else:
            results.append({
                "username": username,
                "status": f"❌ HTTP {response.status_code}",
                "role": None,
                "name": None
            })
            print(f"   ❌ {username:15} -> HTTP {response.status_code}")

    except Exception as e:
        results.append({
            "username": username,
            "status": f"❌ Ошибка: {str(e)[:50]}",
            "role": None,
            "name": None
        })
        print(f"   ❌ {username:15} -> Ошибка: {e}")

print("\n" + "=" * 80)
print("2. Проверяем, что разные роли имеют разный доступ:\n")

# Проверяем доступ к регламентам (только owner может редактировать)
print("   Проверяем доступ к регламентам тимлида:")

# Owner должен видеть регламенты
try:
    response = requests.get(
        f"{BASE_URL}/admin/api/timlead-regulations/",
        auth=HTTPBasicAuth("admin", "qwerty123"),
        timeout=10
    )
    if response.status_code == 200:
        print(f"   ✅ Owner (admin) видит регламенты: {len(response.json())} шт.")
    else:
        print(f"   ❌ Owner не может получить регламенты: HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

# Timlead тоже должен видеть регламенты
try:
    response = requests.get(
        f"{BASE_URL}/admin/api/timlead-regulations/",
        auth=HTTPBasicAuth("omen", "test123"),
        timeout=10
    )
    if response.status_code == 200:
        print(f"   ✅ Timlead (omen) видит регламенты: {len(response.json())} шт.")
    elif response.status_code == 401:
        print(f"   ⚠️  Timlead (omen) не может войти - пароль 'test123' неверный")
    elif response.status_code == 403:
        print(f"   ❌ Timlead не имеет доступа к регламентам (ошибка в коде)")
    else:
        print(f"   ❌ Timlead получил HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("\n" + "=" * 80)
print("РЕЗУЛЬТАТЫ ТЕСТА")
print("=" * 80)

successful = [r for r in results if "✅" in r["status"]]
failed = [r for r in results if "❌" in r["status"]]

print(f"\n✅ Успешно авторизовано: {len(successful)}/{len(results)}")
print(f"❌ Не удалось войти: {len(failed)}/{len(results)}")

if failed:
    print(f"\n⚠️  ПРОБЛЕМА: Следующие пользователи не могут войти:")
    for user in failed:
        print(f"   - {user['username']}: {user['status']}")
    print(f"\n💡 РЕШЕНИЕ: Нужно установить пароли для этих пользователей через скрипт set_password.py")

print("\n" + "=" * 80)
print("ЧТО ДЕЛАТЬ ДАЛЬШЕ?")
print("=" * 80)
print("""
1. Установить пароли для всех сотрудников (через миграцию или скрипт)
2. Создать страницу входа в React-приложении
3. Каждый сотрудник будет входить со своим username/password
4. localStorage будет хранить credentials текущего пользователя
5. Каждый будет видеть только свои задачи и проекты

ТЕКУЩАЯ ПРОБЛЕМА:
- В api.ts жестко прописаны credentials admin:qwerty123
- Все пользователи работают под одним аккаунтом
- Нет страницы входа - все автоматически входят как admin
""")

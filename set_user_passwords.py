"""
Установка паролей для всех пользователей системы
"""
import hashlib

def hash_password(password: str) -> str:
    """Хеширование пароля через SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Пароли для пользователей (ЗАМЕНИТЕ НА РЕАЛЬНЫЕ!)
USER_PASSWORDS = {
    "admin": "qwerty123",  # owner
    "Casper123": "test123",  # executor - Миша Ключка
    "daniltechno": "test123",  # executor - Даниил Михайлов
    "xfce0": "test123",  # executor - Павел
    "gennic": "test123",  # executor - Геннадий Николаев
    "hyperpop": "test123",  # executor - Андрей Карпов
    "batsievoleg": "test123",  # executor - Олег
    "Inisei": "test123",  # executor - Roman Pogrebnyak
    "deathdaycome": "test123",  # executor - Иван Николаев
    "omen": "test123",  # timlead - Никита Пирогов
}

# Генерируем SQL для обновления паролей
print("=" * 80)
print("SQL СКРИПТ ДЛЯ УСТАНОВКИ ПАРОЛЕЙ")
print("=" * 80)
print()
print("-- Копируйте этот SQL и выполните на сервере:")
print()

for username, password in USER_PASSWORDS.items():
    password_hash = hash_password(password)
    sql = f"UPDATE admin_users SET password_hash = '{password_hash}' WHERE username = '{username}';"
    print(sql)

print()
print("=" * 80)
print("КАК ВЫПОЛНИТЬ НА СЕРВЕРЕ:")
print("=" * 80)
print()
print("ssh root@147.45.215.199")
print('sqlite3 /var/www/bot_business_card/data/bot.db << EOF')
for username, password in USER_PASSWORDS.items():
    password_hash = hash_password(password)
    print(f"UPDATE admin_users SET password_hash = '{password_hash}' WHERE username = '{username}';")
print("EOF")
print()
print("=" * 80)
print("ПОСЛЕ УСТАНОВКИ ПАРОЛЕЙ:")
print("=" * 80)
print()
print("Все пользователи смогут войти:")
for username, password in USER_PASSWORDS.items():
    print(f"  - {username:15} : {password}")
print()
print("⚠️  ВАЖНО: Смените пароль 'test123' на уникальный для каждого сотрудника!")

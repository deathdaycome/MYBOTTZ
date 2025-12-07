"""
Сброс пароля администратора на qwerty123
"""
import sqlite3
import hashlib

# Подключаемся к базе данных
conn = sqlite3.connect('data/bot.db')
cursor = conn.cursor()

# Новый пароль
password = "qwerty123"
password_hash = hashlib.sha256(password.encode()).hexdigest()

print("=" * 60)
print("СБРОС ПАРОЛЯ АДМИНИСТРАТОРА")
print("=" * 60)

# Обновляем пароль
cursor.execute("""
    UPDATE admin_users
    SET password_hash = ?
    WHERE username = 'admin'
""", (password_hash,))

conn.commit()

print(f"✅ Пароль пользователя 'admin' обновлён на: {password}")
print(f"   Hash: {password_hash}")

# Проверяем
cursor.execute("SELECT username, role FROM admin_users WHERE username = 'admin'")
user = cursor.fetchone()

if user:
    print(f"\n✅ Проверка:")
    print(f"   Username: {user[0]}")
    print(f"   Role: {user[1]}")

print("=" * 60)

conn.close()

"""
Проверка и изменение роли пользователя admin
"""
import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('data/bot.db')
cursor = conn.cursor()

# Проверяем текущую роль пользователя admin
print("=" * 60)
print("ТЕКУЩАЯ РОЛЬ ПОЛЬЗОВАТЕЛЯ ADMIN:")
print("=" * 60)

cursor.execute("SELECT id, username, role FROM admin_users WHERE username = 'admin'")
user = cursor.fetchone()

if user:
    print(f"ID: {user[0]}")
    print(f"Username: {user[1]}")
    print(f"Role: {user[2]}")

    if user[2] != 'owner':
        print(f"\n⚠️  Текущая роль: '{user[2]}' - нужна роль 'owner' для редактирования регламентов!")

        # Изменяем роль на owner
        cursor.execute("UPDATE admin_users SET role = 'owner' WHERE username = 'admin'")
        conn.commit()

        print("\n✅ Роль изменена на 'owner'")

        # Проверяем изменение
        cursor.execute("SELECT username, role FROM admin_users WHERE username = 'admin'")
        updated_user = cursor.fetchone()
        print(f"\nОбновленная роль: {updated_user[1]}")
    else:
        print("\n✅ Роль уже 'owner' - редактирование должно работать")
else:
    print("❌ Пользователь 'admin' не найден!")

print("=" * 60)

conn.close()

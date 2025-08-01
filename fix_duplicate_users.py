#!/usr/bin/env python3
"""
Скрипт для исправления дублирующихся пользователей
Объединяет пользователей с одинаковыми именами, оставляя самого старого
"""
import sqlite3
import sys
import os

def fix_duplicate_users():
    """Исправляет дублирующихся пользователей"""
    db_path = "data/bot.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Файл базы данных {db_path} не найден!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Поиск дублирующихся пользователей...")
        
        # Находим пользователей с одинаковыми именами
        cursor.execute("""
            SELECT first_name, COUNT(*) as count 
            FROM users 
            WHERE first_name IS NOT NULL AND first_name != '' 
            GROUP BY first_name 
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("✅ Дублирующихся пользователей не найдено")
            return True
        
        print(f"📋 Найдено дубликатов имен: {len(duplicates)}")
        for name, count in duplicates:
            print(f"  - {name}: {count} записей")
        
        fixed_count = 0
        
        for duplicate_name, count in duplicates:
            print(f"\n🔧 Исправление дубликатов для '{duplicate_name}'...")
            
            # Получаем всех пользователей с этим именем
            cursor.execute("""
                SELECT id, first_name, last_name, username, telegram_id, phone, created_at, registration_date
                FROM users 
                WHERE first_name = ? 
                ORDER BY 
                    CASE 
                        WHEN registration_date IS NOT NULL THEN registration_date 
                        WHEN created_at IS NOT NULL THEN created_at 
                        ELSE '1970-01-01' 
                    END ASC
            """, (duplicate_name,))
            
            users = cursor.fetchall()
            
            if len(users) <= 1:
                continue
            
            # Оставляем самого старого пользователя (первый в списке)
            main_user = users[0]
            duplicate_users = users[1:]
            
            print(f"  📌 Основной пользователь: ID {main_user[0]} (создан: {main_user[6] or main_user[7] or 'неизвестно'})")
            
            # Переносим проекты от дубликатов к основному пользователю
            for dup_user in duplicate_users:
                dup_id = dup_user[0]
                
                # Проверяем сколько проектов у дубликата
                cursor.execute("SELECT COUNT(*) FROM projects WHERE user_id = ?", (dup_id,))
                projects_count = cursor.fetchone()[0]
                
                if projects_count > 0:
                    print(f"  🔄 Перенос {projects_count} проектов от пользователя ID {dup_id} к ID {main_user[0]}")
                    
                    # Переносим проекты
                    cursor.execute("""
                        UPDATE projects 
                        SET user_id = ? 
                        WHERE user_id = ?
                    """, (main_user[0], dup_id))
                
                # Удаляем дубликат
                cursor.execute("DELETE FROM users WHERE id = ?", (dup_id,))
                print(f"  🗑️  Удален дубликат пользователя ID {dup_id}")
            
            fixed_count += len(duplicate_users)
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Исправление завершено!")
        print(f"   Удалено дубликатов: {fixed_count}")
        print(f"   Объединено групп: {len(duplicates)}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def show_users_stats():
    """Показывает статистику пользователей"""
    db_path = "data/bot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📊 Статистика пользователей:")
        
        # Общее количество
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        print(f"   Всего пользователей: {total_users}")
        
        # Пользователи с проектами
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) 
            FROM projects 
            WHERE user_id IS NOT NULL
        """)
        users_with_projects = cursor.fetchone()[0]
        print(f"   Пользователей с проектами: {users_with_projects}")
        
        # Топ пользователей по количеству проектов
        cursor.execute("""
            SELECT u.first_name, u.last_name, u.username, COUNT(p.id) as projects_count
            FROM users u
            LEFT JOIN projects p ON u.id = p.user_id
            GROUP BY u.id, u.first_name, u.last_name, u.username
            HAVING projects_count > 0
            ORDER BY projects_count DESC
            LIMIT 10
        """)
        
        top_users = cursor.fetchall()
        if top_users:
            print("\n   Топ пользователей по проектам:")
            for user in top_users:
                name = f"{user[0] or ''} {user[1] or ''}".strip() or "Без имени"
                username = f"@{user[2]}" if user[2] else "без username"
                print(f"     - {name} ({username}): {user[3]} проектов")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")

if __name__ == "__main__":
    print("🧹 Скрипт исправления дублирующихся пользователей")
    print("=" * 50)
    
    # Показываем статистику до исправления
    show_users_stats()
    
    if fix_duplicate_users():
        # Показываем статистику после исправления
        show_users_stats()
        print("\n✅ Скрипт выполнен успешно!")
        sys.exit(0)
    else:
        print("\n❌ Скрипт выполнен с ошибками!")
        sys.exit(1)
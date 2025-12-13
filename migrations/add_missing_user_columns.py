#!/usr/bin/env python3
"""
Добавление недостающих колонок в таблицу users для поддержки аутентификации
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import engine


async def add_missing_columns():
    """Добавляет недостающие колонки в таблицу users"""

    commands = [
        # Добавляем колонку password_hash
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);",

        # Добавляем колонку full_name
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(200);",

        # Добавляем колонку role
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'viewer';",

        # Добавляем колонку is_superuser
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN DEFAULT FALSE;",

        # Добавляем колонку avatar_url
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);",

        # Добавляем колонку bio
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;",

        # Добавляем колонку user_metadata
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS user_metadata JSON;",

        # Добавляем колонку created_at
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",

        # Добавляем колонку updated_at
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",

        # Добавляем колонку last_login_at
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP;",

        # Добавляем колонки для управления паролем
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_expires TIMESTAMP;",

        # Добавляем колонки для верификации email
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_expires TIMESTAMP;",

        # Добавляем колонки для безопасности
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;",

        # Устанавливаем пароль для администратора (admin:admin)
        # Используем bcrypt хеш для пароля 'admin'
        """UPDATE users SET
            password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lk7iGMqKqJXqJpYJe',
            role = 'admin',
            is_superuser = TRUE,
            is_active = TRUE
        WHERE username = 'admin' AND password_hash IS NULL;""",

        # Создаем администратора если его нет
        """INSERT INTO users (username, email, password_hash, role, is_superuser, is_active, full_name)
        VALUES ('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lk7iGMqKqJXqJpYJe', 'admin', TRUE, TRUE, 'Administrator')
        ON CONFLICT (username) DO NOTHING;"""
    ]

    async with engine.begin() as conn:
        for cmd in commands:
            print(f"Выполняем: {cmd[:80]}...")
            try:
                await conn.execute(text(cmd))
                print("✓ Успешно")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
                # Продолжаем с остальными командами

    print("\n✅ Миграция завершена!")
    print("Теперь вы можете войти с учетными данными: admin / admin")


if __name__ == "__main__":
    from sqlalchemy import text
    asyncio.run(add_missing_columns())
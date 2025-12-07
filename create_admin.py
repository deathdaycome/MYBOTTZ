#!/usr/bin/env python3
"""
Enterprise CRM - Create Admin User Script

Creates initial superuser admin account for the enterprise CRM system.
Uses async PostgreSQL database connection.
"""

import sys
import os
import asyncio
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def create_admin():
    """Create initial superuser admin account"""
    try:
        from sqlalchemy import select
        from app.core.database import get_db
        from app.core.security import hash_password, Role
        from app.modules.users.models import User
        from datetime import datetime

        # Get database session
        async for db in get_db():
            # Check if admin already exists
            result = await db.execute(select(User).where(User.username == "admin"))
            existing_admin = result.scalar_one_or_none()

            if existing_admin:
                print("⚠️  Admin user already exists")
                print(f"   Username: {existing_admin.username}")
                print(f"   Email: {existing_admin.email}")
                print(f"   Role: {existing_admin.role}")
                return True

            # Create new admin user
            admin = User(
                username="admin",
                email="admin@enterprise-crm.local",
                password_hash=hash_password("admin123"),
                full_name="System Administrator",
                role=Role.ADMIN.value,
                is_active=True,
                is_superuser=True,
                email_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(admin)
            await db.commit()
            await db.refresh(admin)

            print("✅ Admin user created successfully!")
            print(f"   Username: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Password: admin123")
            print(f"   Role: {admin.role}")
            print(f"   ID: {admin.id}")
            print("\n⚠️  IMPORTANT: Change the admin password after first login!")

            return True

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(create_admin())
    if success:
        print("\n🚀 Done!")
    else:
        print("\n💥 Error!")
        sys.exit(1)

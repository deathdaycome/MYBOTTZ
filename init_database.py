#!/usr/bin/env python3
"""
Initialize database with proper schema for modular architecture
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def init_db():
    """Initialize database tables"""
    try:
        print("🔧 Initializing database...")

        # Import Base and engine
        from app.core.database import create_tables, check_connection
        from app.core.base import Base

        # Import all models so they're registered with Base
        print("📦 Loading models...")
        from app.modules.users.models import User, UserSession, UserActivity

        # Import other models if they exist
        try:
            from app.database.models import (
                Client, Project, Task, Service, Contractor,
                Deal, Lead, Document, Portfolio, Notification,
                TaskComment, ProjectFile, Revision
            )
            print("   ✓ Legacy models loaded")
        except ImportError as e:
            print(f"   ⚠️  Some legacy models not found (this is OK): {e}")

        # Check database connection
        print("🔌 Checking database connection...")
        db_ok = await check_connection()
        if not db_ok:
            print("❌ Database connection failed!")
            return False
        print("   ✓ Database connection OK")

        # Create all tables
        print("🏗️  Creating database tables...")
        await create_tables()
        print("   ✓ All tables created successfully")

        return True

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(init_db())
    if success:
        print("\n✅ Database initialized successfully!")
        print("\n📝 Next steps:")
        print("   1. Run: python3 create_admin.py")
        print("   2. Login with admin/admin123")
    else:
        print("\n💥 Database initialization failed!")
        sys.exit(1)
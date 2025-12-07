#!/usr/bin/env python3
"""
Migration: Add Reports Tables
Creates tables for Reports module

Run with:
    python3 migrations/add_reports_tables.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def run_migration():
    """Create reports tables"""

    print("Creating reports tables...")

    async with engine.begin() as conn:
        # Create reports table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS reports (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                report_type VARCHAR(50) NOT NULL,
                format VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                requested_by INTEGER NOT NULL,
                parameters JSONB,
                file_path VARCHAR(500),
                file_size INTEGER,
                error_message TEXT,
                generation_time_seconds FLOAT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                expires_at TIMESTAMP
            )
        """))

        # Create indexes for reports
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(report_type)
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_reports_user ON reports(requested_by)
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at DESC)
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_reports_expires ON reports(expires_at)
        """))

        # Create scheduled_reports table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS scheduled_reports (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                report_type VARCHAR(50) NOT NULL,
                format VARCHAR(20) NOT NULL,
                parameters JSONB,
                cron_expression VARCHAR(100) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT true,
                email_recipients JSONB,
                user_recipients JSONB,
                created_by INTEGER NOT NULL,
                last_run_at TIMESTAMP,
                next_run_at TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create indexes for scheduled_reports
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_scheduled_reports_active ON scheduled_reports(is_active)
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_scheduled_reports_next_run ON scheduled_reports(next_run_at)
        """))

    print("✅ Reports tables created successfully!")
    print("   - reports")
    print("   - scheduled_reports")
    print("   - All indexes created")


async def check_tables():
    """Check if tables exist"""
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('reports', 'scheduled_reports')
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]

        if tables:
            print(f"\n✅ Found tables: {', '.join(tables)}")
        else:
            print("\n⚠️  No reports tables found")

        return tables


async def main():
    """Main migration function"""
    print("=" * 60)
    print("REPORTS TABLES MIGRATION")
    print("=" * 60)
    print()

    try:
        # Check current state
        existing = await check_tables()

        if len(existing) == 2:
            print("\n⚠️  Tables already exist. Skipping migration.")
            print("   To re-run, drop tables first:")
            print("   DROP TABLE IF EXISTS reports CASCADE;")
            print("   DROP TABLE IF NOT EXISTS scheduled_reports CASCADE;")
            return

        # Run migration
        await run_migration()

        # Verify
        await check_tables()

        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""Migration: Add tags column to tasks table"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.database.models import Base

DATABASE_URL = "sqlite:///./data/bot.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def upgrade():
    """Add tags column to tasks table"""
    print("🔄 Adding tags column to tasks table...")

    with engine.connect() as conn:
        try:
            # Check if column already exists
            result = conn.execute(text("PRAGMA table_info(tasks)"))
            columns = [row[1] for row in result.fetchall()]

            if 'tags' in columns:
                print("✅ Column 'tags' already exists, skipping...")
                return

            # Add tags column
            conn.execute(text("""
                ALTER TABLE tasks
                ADD COLUMN tags TEXT DEFAULT '[]'
            """))
            conn.commit()

            print("✅ Successfully added tags column to tasks table")

        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("🚀 Running migration: Add tags to tasks\n")
    upgrade()
    print("\n✅ Migration completed successfully!")

"""
Database configuration and session management
Using async SQLAlchemy with PostgreSQL
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import event, text
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import logger
# Import Base from separate file to avoid circular imports
from app.core.base import Base


# ============================================
# ENGINE CONFIGURATION
# ============================================

# Engine kwargs
engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
    "future": True,
}

# Pool configuration
# For async engines, use NullPool for SQLite or let SQLAlchemy choose for PostgreSQL
if settings.is_testing or "sqlite" in str(settings.DATABASE_URL):
    # SQLite with async: use NullPool (no pooling)
    engine_kwargs["poolclass"] = NullPool
else:
    # PostgreSQL with async: use default async pooling
    # Don't set poolclass - let SQLAlchemy use AsyncAdaptedQueuePool
    engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
    engine_kwargs["pool_pre_ping"] = True  # Verify connections
    engine_kwargs["pool_recycle"] = 3600  # Recycle connections after 1 hour

# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ============================================
# SESSION MANAGEMENT
# ============================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения database session

    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}", exc_info=True)
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """
    Context manager для database session

    Usage:
        async with get_db_context() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database context error: {e}", exc_info=True)
            raise
        finally:
            await session.close()


# ============================================
# DATABASE EVENTS
# ============================================

@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Set pragmas for SQLite (if used for testing)
    """
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


@event.listens_for(engine.sync_engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """
    Log new database connections
    """
    logger.debug("Database connection established")


@event.listens_for(engine.sync_engine, "close")
def receive_close(dbapi_conn, connection_record):
    """
    Log database disconnections
    """
    logger.debug("Database connection closed")


# ============================================
# DATABASE UTILITIES
# ============================================

async def create_tables():
    """
    Create all database tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def drop_tables():
    """
    Drop all database tables (use with caution!)
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("Database tables dropped")


async def check_connection():
    """
    Check if database connection is working
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def close_db_connection():
    """
    Close all database connections
    """
    await engine.dispose()
    logger.info("Database connections closed")


# ============================================
# TRANSACTION DECORATOR
# ============================================

from functools import wraps
from typing import Callable, Any


def transactional(func: Callable) -> Callable:
    """
    Decorator для автоматического управления транзакциями

    Usage:
        @transactional
        async def create_user(db: AsyncSession, user_data: dict):
            user = User(**user_data)
            db.add(user)
            return user
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        # Find db session in args/kwargs
        db = None
        for arg in args:
            if isinstance(arg, AsyncSession):
                db = arg
                break
        if db is None:
            db = kwargs.get("db")

        if db is None:
            raise ValueError("No database session found in function arguments")

        try:
            result = await func(*args, **kwargs)
            await db.commit()
            return result
        except Exception as e:
            await db.rollback()
            logger.error(f"Transaction rolled back: {e}", exc_info=True)
            raise

    return wrapper

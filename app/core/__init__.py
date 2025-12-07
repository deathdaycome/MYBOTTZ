"""
Core module - базовая инфраструктура приложения
"""

from app.core.config import settings
from app.core.base import Base
from app.core.logging import logger

# Don't import get_db or engine here - they will trigger database engine creation
# Import them lazily when needed:
#   from app.core.database import get_db, engine

__all__ = [
    "settings",
    # "get_db",  # Import directly from database module when needed
    # "engine",  # Import directly from database module when needed
    "Base",
    "logger",
]

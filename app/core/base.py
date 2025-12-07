"""
SQLAlchemy declarative base - separate from database engine

This file only contains the Base definition to avoid circular imports
and prevent engine creation during imports.
"""

from sqlalchemy.orm import declarative_base

# Declarative Base for all ORM models
Base = declarative_base()

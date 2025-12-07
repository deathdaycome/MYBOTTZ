"""
User Database Models

SQLAlchemy models for user management and authentication.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, JSON,
    Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.core.base import Base
from app.core.security import Role


class User(Base):
    """
    User model for authentication and authorization

    Stores user information, credentials, and role-based access control data.
    """
    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Bcrypt hash

    # Personal Information
    full_name = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    telegram_id = Column(String(100), nullable=True, index=True)
    telegram_username = Column(String(100), nullable=True)

    # Role & Permissions
    role = Column(String(50), nullable=False, default=Role.VIEWER.value, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Additional Data
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    user_metadata = Column(JSON, nullable=True)  # Flexible additional data

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Password Management
    password_changed_at = Column(DateTime, nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)

    # Email Verification
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)

    # Account Management
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_role_active', 'role', 'is_active'),
        Index('idx_user_telegram', 'telegram_id'),
        Index('idx_user_email_verified', 'email_verified'),
        Index('idx_user_created', 'created_at'),
        CheckConstraint('failed_login_attempts >= 0', name='check_failed_attempts_positive'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == Role.ADMIN.value or self.is_superuser

    @property
    def is_locked(self) -> bool:
        """Check if account is locked"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False

    @property
    def is_deleted(self) -> bool:
        """Check if account is soft deleted"""
        return self.deleted_at is not None

    def to_dict(self) -> dict:
        """Convert user to dictionary (safe for API responses)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone,
            "telegram_username": self.telegram_username,
            "role": self.role,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "avatar_url": self.avatar_url,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }


class UserSession(Base):
    """
    User session tracking

    Tracks active user sessions for security and analytics.
    """
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # Session Info
    user_id = Column(Integer, nullable=False, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token_hash = Column(String(255), nullable=True)

    # Client Info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    device_name = Column(String(200), nullable=True)

    # Location (if available)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)

    # Metadata
    session_metadata = Column(JSON, nullable=True)

    __table_args__ = (
        Index('idx_session_user_active', 'user_id', 'expires_at'),
        Index('idx_session_expiry', 'expires_at'),
    )

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, session_id='{self.session_id[:8]}...')>"

    @property
    def is_active(self) -> bool:
        """Check if session is still active"""
        if self.revoked_at:
            return False
        return datetime.utcnow() < self.expires_at

    @property
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.utcnow() >= self.expires_at


class UserActivity(Base):
    """
    User activity log

    Tracks user actions for analytics and security.
    """
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)

    # User Info
    user_id = Column(Integer, nullable=False, index=True)

    # Activity Info
    activity_type = Column(String(100), nullable=False, index=True)
    activity_data = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_path = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)

    # Status
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index('idx_activity_user_type', 'user_id', 'activity_type'),
        Index('idx_activity_created', 'created_at'),
    )

    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, type='{self.activity_type}')>"

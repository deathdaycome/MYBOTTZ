"""
Audit trail system for tracking all important actions
"""

from datetime import datetime
from typing import Optional, Any, Dict
from enum import Enum
from functools import wraps
import json

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.base import Base
from app.core.logging import logger


# ============================================
# AUDIT ACTION TYPES
# ============================================

class AuditAction(str, Enum):
    """Types of auditable actions"""
    # User actions
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_PASSWORD_CHANGE = "user.password_change"
    USER_PASSWORD_RESET = "user.password_reset"

    # Project actions
    PROJECT_CREATE = "project.create"
    PROJECT_UPDATE = "project.update"
    PROJECT_DELETE = "project.delete"
    PROJECT_STATUS_CHANGE = "project.status_change"

    # Task actions
    TASK_CREATE = "task.create"
    TASK_UPDATE = "task.update"
    TASK_DELETE = "task.delete"
    TASK_ASSIGN = "task.assign"
    TASK_STATUS_CHANGE = "task.status_change"
    TASK_COMMENT_CREATE = "task.comment.create"

    # Vehicle actions
    VEHICLE_CREATE = "vehicle.create"
    VEHICLE_UPDATE = "vehicle.update"
    VEHICLE_DELETE = "vehicle.delete"

    # Driver actions
    DRIVER_CREATE = "driver.create"
    DRIVER_UPDATE = "driver.update"
    DRIVER_DELETE = "driver.delete"

    # Route actions
    ROUTE_CREATE = "route.create"
    ROUTE_UPDATE = "route.update"
    ROUTE_DELETE = "route.delete"

    # Trip actions
    TRIP_CREATE = "trip.create"
    TRIP_UPDATE = "trip.update"
    TRIP_DELETE = "trip.delete"
    TRIP_STATUS_CHANGE = "trip.status_change"

    # System actions
    SYSTEM_CONFIG_CHANGE = "system.config_change"
    SYSTEM_BACKUP = "system.backup"
    SYSTEM_RESTORE = "system.restore"

    # Security actions
    SECURITY_ROLE_CHANGE = "security.role_change"
    SECURITY_PERMISSION_GRANT = "security.permission_grant"
    SECURITY_PERMISSION_REVOKE = "security.permission_revoke"
    SECURITY_LOGIN_FAILED = "security.login_failed"
    SECURITY_ACCESS_DENIED = "security.access_denied"

    # Generic actions
    ENTITY_CREATE = "entity.create"
    ENTITY_UPDATE = "entity.update"
    ENTITY_DELETE = "entity.delete"


# ============================================
# AUDIT LOG MODEL
# ============================================

class AuditLog(Base):
    """
    Audit log database model
    Stores all important actions in the system
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Who performed the action
    user_id = Column(Integer, nullable=True, index=True)
    username = Column(String(255), nullable=True)

    # What action was performed
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=True, index=True)
    entity_id = Column(Integer, nullable=True)

    # When and where
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    user_agent = Column(String(500), nullable=True)

    # What changed
    changes = Column(JSON, nullable=True)  # Before/after values
    audit_metadata = Column(JSON, nullable=True)  # Additional context

    # Description
    description = Column(Text, nullable=True)

    # Request tracking
    request_id = Column(String(100), nullable=True, index=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"


# ============================================
# AUDIT LOG SCHEMAS
# ============================================

class AuditLogCreate(BaseModel):
    """Schema for creating audit log entry"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    audit_metadata: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    request_id: Optional[str] = None


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    user_id: Optional[int]
    username: Optional[str]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    changes: Optional[Dict[str, Any]]
    audit_metadata: Optional[Dict[str, Any]]
    description: Optional[str]
    request_id: Optional[str]

    class Config:
        from_attributes = True


# ============================================
# AUDIT LOG FUNCTIONS
# ============================================

async def create_audit_log(
    db: AsyncSession,
    action: str,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    changes: Optional[Dict[str, Any]] = None,
    audit_metadata: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
) -> AuditLog:
    """
    Create audit log entry

    Args:
        db: Database session
        action: Action type
        user_id: User who performed action
        username: Username
        entity_type: Type of entity affected
        entity_id: ID of entity affected
        changes: Before/after values
        audit_metadata: Additional context
        description: Human-readable description
        ip_address: IP address
        user_agent: User agent
        request_id: Request ID for tracking

    Returns:
        Created AuditLog entry
    """
    audit_log = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes,
        audit_metadata=audit_metadata,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
        timestamp=datetime.utcnow(),
    )

    db.add(audit_log)
    await db.flush()

    logger.info(
        "audit_log_created",
        audit_id=audit_log.id,
        action=action,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    return audit_log


async def get_audit_logs(
    db: AsyncSession,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[AuditLog]:
    """
    Query audit logs with filters

    Args:
        db: Database session
        user_id: Filter by user
        action: Filter by action type
        entity_type: Filter by entity type
        entity_id: Filter by entity ID
        start_date: Filter by start date
        end_date: Filter by end date
        skip: Pagination offset
        limit: Pagination limit

    Returns:
        List of AuditLog entries
    """
    query = select(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)

    query = query.order_by(AuditLog.timestamp.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def get_entity_audit_trail(
    db: AsyncSession,
    entity_type: str,
    entity_id: int,
    limit: int = 50,
) -> list[AuditLog]:
    """
    Get full audit trail for specific entity

    Args:
        db: Database session
        entity_type: Type of entity
        entity_id: ID of entity
        limit: Maximum number of entries

    Returns:
        List of AuditLog entries for entity
    """
    query = select(AuditLog).filter(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id,
    ).order_by(AuditLog.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def get_user_activity(
    db: AsyncSession,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
) -> list[AuditLog]:
    """
    Get user activity history

    Args:
        db: Database session
        user_id: User ID
        start_date: Start date filter
        end_date: End date filter
        limit: Maximum entries

    Returns:
        List of AuditLog entries for user
    """
    query = select(AuditLog).filter(AuditLog.user_id == user_id)

    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)

    query = query.order_by(AuditLog.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


# ============================================
# AUDIT DECORATORS
# ============================================

def audit_action(
    action: str,
    entity_type: Optional[str] = None,
    get_entity_id=None,
    description: Optional[str] = None,
):
    """
    Decorator to automatically audit function calls

    Args:
        action: Action type
        entity_type: Type of entity
        get_entity_id: Function to extract entity ID from result
        description: Description template

    Usage:
        @audit_action(
            action=AuditAction.USER_CREATE,
            entity_type="User",
            get_entity_id=lambda result: result.id,
            description="Created new user"
        )
        async def create_user(db: AsyncSession, user_data: dict, current_user):
            # Create user logic
            return new_user
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute the function
            result = await func(*args, **kwargs)

            # Extract database session and current user
            db = None
            current_user = None

            for arg in args:
                if isinstance(arg, AsyncSession):
                    db = arg
                elif hasattr(arg, 'id') and hasattr(arg, 'username'):
                    current_user = arg

            if 'db' in kwargs:
                db = kwargs['db']
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']

            # Extract entity ID
            entity_id = None
            if get_entity_id and result:
                try:
                    entity_id = get_entity_id(result)
                except Exception as e:
                    logger.warning("audit_entity_id_extraction_failed", error=str(e))

            # Create audit log
            if db:
                try:
                    await create_audit_log(
                        db=db,
                        action=action,
                        user_id=current_user.id if current_user else None,
                        username=current_user.username if current_user else None,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        description=description,
                    )
                except Exception as e:
                    logger.error("audit_log_creation_failed", error=str(e), exc_info=True)

            return result

        return wrapper
    return decorator


def audit_changes(
    action: str,
    entity_type: str,
    get_entity_id,
    get_old_state,
    get_new_state=None,
):
    """
    Decorator to audit changes with before/after values

    Args:
        action: Action type
        entity_type: Type of entity
        get_entity_id: Function to extract entity ID
        get_old_state: Function to get state before changes
        get_new_state: Function to get state after changes

    Usage:
        @audit_changes(
            action=AuditAction.USER_UPDATE,
            entity_type="User",
            get_entity_id=lambda result: result.id,
            get_old_state=lambda args, kwargs: args[1],  # old_user
            get_new_state=lambda result: result,
        )
        async def update_user(db: AsyncSession, old_user, new_data, current_user):
            # Update logic
            return updated_user
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get old state
            old_state = None
            try:
                old_state = get_old_state(args, kwargs)
            except Exception as e:
                logger.warning("audit_old_state_extraction_failed", error=str(e))

            # Execute function
            result = await func(*args, **kwargs)

            # Get new state
            new_state = result
            if get_new_state:
                try:
                    new_state = get_new_state(result)
                except Exception as e:
                    logger.warning("audit_new_state_extraction_failed", error=str(e))

            # Calculate changes
            changes = None
            if old_state and new_state:
                changes = {
                    "before": _serialize_object(old_state),
                    "after": _serialize_object(new_state),
                }

            # Extract components
            db = None
            current_user = None

            for arg in args:
                if isinstance(arg, AsyncSession):
                    db = arg
                elif hasattr(arg, 'id') and hasattr(arg, 'username'):
                    current_user = arg

            if 'db' in kwargs:
                db = kwargs['db']
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']

            # Get entity ID
            entity_id = None
            try:
                entity_id = get_entity_id(result)
            except Exception as e:
                logger.warning("audit_entity_id_extraction_failed", error=str(e))

            # Create audit log
            if db:
                try:
                    await create_audit_log(
                        db=db,
                        action=action,
                        user_id=current_user.id if current_user else None,
                        username=current_user.username if current_user else None,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        changes=changes,
                    )
                except Exception as e:
                    logger.error("audit_log_creation_failed", error=str(e), exc_info=True)

            return result

        return wrapper
    return decorator


# ============================================
# HELPER FUNCTIONS
# ============================================

def _serialize_object(obj: Any) -> Dict[str, Any]:
    """
    Serialize object for audit log

    Args:
        obj: Object to serialize

    Returns:
        Dictionary representation
    """
    if hasattr(obj, '__dict__'):
        return {
            key: value
            for key, value in obj.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }
    elif isinstance(obj, dict):
        return obj
    else:
        return {"value": str(obj)}


async def delete_old_audit_logs(
    db: AsyncSession,
    days: int = 90,
) -> int:
    """
    Delete audit logs older than specified days

    Args:
        db: Database session
        days: Number of days to keep

    Returns:
        Number of deleted entries
    """
    from datetime import timedelta
    from sqlalchemy import delete

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    stmt = delete(AuditLog).filter(AuditLog.timestamp < cutoff_date)
    result = await db.execute(stmt)
    await db.commit()

    deleted_count = result.rowcount

    logger.info(
        "audit_logs_cleanup",
        deleted_count=deleted_count,
        cutoff_date=cutoff_date.isoformat(),
    )

    return deleted_count

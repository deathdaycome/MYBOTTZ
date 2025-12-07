"""
User Service Layer

Business logic for user management, authentication, and authorization.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, update, delete
from sqlalchemy.orm import selectinload

from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, TokenType, Role,
    generate_reset_token,
)
from app.core.logging import logger
from app.core.audit import create_audit_log, AuditAction
from app.modules.users.models import User, UserSession, UserActivity
from app.modules.users.schemas import (
    UserCreate, UserUpdate, UserUpdateAdmin,
    PasswordChange, UserStatsResponse
)
from fastapi import HTTPException, status


# ============================================
# USER CRUD OPERATIONS
# ============================================

async def create_user(
    db: AsyncSession,
    user_data: UserCreate,
    created_by_user_id: Optional[int] = None
) -> User:
    """
    Create a new user

    Args:
        db: Database session
        user_data: User creation data
        created_by_user_id: ID of user creating this user (for audit)

    Returns:
        Created User object

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    existing = await db.execute(
        select(User).filter(
            or_(
                User.username == user_data.username.lower(),
                User.email == user_data.email.lower()
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Create user
    user = User(
        username=user_data.username.lower(),
        email=user_data.email.lower(),
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        telegram_id=user_data.telegram_id,
        telegram_username=user_data.telegram_username,
        role=user_data.role.value,
        bio=user_data.bio,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(user)
    await db.flush()

    # Create audit log
    await create_audit_log(
        db=db,
        action=AuditAction.USER_CREATE,
        user_id=created_by_user_id,
        entity_type="User",
        entity_id=user.id,
        description=f"Created user: {user.username}",
    )

    await db.commit()
    await db.refresh(user)

    logger.info("user_created", user_id=user.id, username=user.username)
    return user


async def get_user_by_id(
    db: AsyncSession,
    user_id: int,
    include_deleted: bool = False
) -> Optional[User]:
    """Get user by ID"""
    query = select(User).filter(User.id == user_id)

    if not include_deleted:
        query = query.filter(User.deleted_at.is_(None))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_username(
    db: AsyncSession,
    username: str,
    include_deleted: bool = False
) -> Optional[User]:
    """Get user by username"""
    query = select(User).filter(User.username == username.lower())

    if not include_deleted:
        query = query.filter(User.deleted_at.is_(None))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_email(
    db: AsyncSession,
    email: str,
    include_deleted: bool = False
) -> Optional[User]:
    """Get user by email"""
    query = select(User).filter(User.email == email.lower())

    if not include_deleted:
        query = query.filter(User.deleted_at.is_(None))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    role: Optional[Role] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    include_deleted: bool = False
) -> Tuple[List[User], int]:
    """
    Get list of users with filters and pagination

    Returns:
        Tuple of (users list, total count)
    """
    # Build base query
    query = select(User)

    if not include_deleted:
        query = query.filter(User.deleted_at.is_(None))

    # Apply filters
    if role:
        query = query.filter(User.role == role.value)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.execute(count_query)
    total_count = total.scalar()

    # Apply pagination and ordering
    query = query.order_by(User.created_at.desc())
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    return users, total_count


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_data: UserUpdate,
    updated_by_user_id: Optional[int] = None
) -> User:
    """Update user information"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Track changes
    changes = {}

    # Update fields
    update_fields = user_data.dict(exclude_unset=True)
    for field, value in update_fields.items():
        if hasattr(user, field):
            old_value = getattr(user, field)
            if old_value != value:
                changes[field] = {"old": old_value, "new": value}
                setattr(user, field, value)

    if changes:
        user.updated_at = datetime.utcnow()

        # Create audit log
        await create_audit_log(
            db=db,
            action=AuditAction.USER_UPDATE,
            user_id=updated_by_user_id,
            entity_type="User",
            entity_id=user.id,
            changes=changes,
            description=f"Updated user: {user.username}",
        )

        await db.commit()
        await db.refresh(user)

        logger.info("user_updated", user_id=user.id, changes=list(changes.keys()))

    return user


async def update_user_admin(
    db: AsyncSession,
    user_id: int,
    user_data: UserUpdateAdmin,
    admin_user_id: int
) -> User:
    """Update user (admin only - can change role and status)"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Track changes
    changes = {}

    # Update fields
    update_fields = user_data.dict(exclude_unset=True)
    for field, value in update_fields.items():
        if hasattr(user, field):
            old_value = getattr(user, field)
            if field == 'role' and isinstance(value, Role):
                value = value.value
            if old_value != value:
                changes[field] = {"old": old_value, "new": value}
                setattr(user, field, value)

    if changes:
        user.updated_at = datetime.utcnow()

        # Create audit log
        await create_audit_log(
            db=db,
            action=AuditAction.USER_UPDATE,
            user_id=admin_user_id,
            entity_type="User",
            entity_id=user.id,
            changes=changes,
            description=f"Admin updated user: {user.username}",
        )

        await db.commit()
        await db.refresh(user)

        logger.info("user_updated_by_admin", user_id=user.id, admin_id=admin_user_id)

    return user


async def delete_user(
    db: AsyncSession,
    user_id: int,
    deleted_by_user_id: Optional[int] = None,
    hard_delete: bool = False
) -> bool:
    """
    Delete user (soft delete by default)

    Args:
        db: Database session
        user_id: User ID to delete
        deleted_by_user_id: ID of user performing deletion
        hard_delete: If True, permanently delete from database

    Returns:
        True if deleted successfully
    """
    user = await get_user_by_id(db, user_id, include_deleted=True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if hard_delete:
        await db.delete(user)
        action = AuditAction.USER_DELETE
        logger.warning("user_hard_deleted", user_id=user.id)
    else:
        user.deleted_at = datetime.utcnow()
        user.is_active = False
        action = AuditAction.USER_DELETE
        logger.info("user_soft_deleted", user_id=user.id)

    # Create audit log
    await create_audit_log(
        db=db,
        action=action,
        user_id=deleted_by_user_id,
        entity_type="User",
        entity_id=user.id,
        description=f"Deleted user: {user.username} (hard={hard_delete})",
    )

    await db.commit()
    return True


# ============================================
# AUTHENTICATION
# ============================================

async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Tuple[Optional[User], Optional[str], Optional[str]]:
    """
    Authenticate user with username/password

    Returns:
        Tuple of (User, access_token, refresh_token) or (None, None, error_message)
    """
    # Get user
    user = await get_user_by_username(db, username)
    if not user:
        user = await get_user_by_email(db, username)

    if not user:
        logger.warning("authentication_failed_user_not_found", username=username)
        return None, None, "Invalid credentials"

    # Check if user is locked
    if user.is_locked:
        logger.warning("authentication_failed_account_locked", user_id=user.id)
        return None, None, f"Account locked until {user.locked_until}"

    # Check if user is active
    if not user.is_active:
        logger.warning("authentication_failed_account_inactive", user_id=user.id)
        return None, None, "Account is inactive"

    # Verify password
    if not verify_password(password, user.password_hash):
        # Increment failed attempts
        user.failed_login_attempts += 1

        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            logger.warning("account_locked_due_to_failed_attempts", user_id=user.id)

        await db.commit()

        # Create audit log
        await create_audit_log(
            db=db,
            action=AuditAction.SECURITY_LOGIN_FAILED,
            user_id=user.id,
            entity_type="User",
            entity_id=user.id,
            description="Failed login attempt",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.warning("authentication_failed_invalid_password", user_id=user.id)
        return None, None, "Invalid credentials"

    # Reset failed attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Create tokens
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role
    )
    refresh_token = create_refresh_token(user_id=user.id)

    # Create audit log
    await create_audit_log(
        db=db,
        action=AuditAction.USER_LOGIN,
        user_id=user.id,
        entity_type="User",
        entity_id=user.id,
        description="User logged in",
        ip_address=ip_address,
        user_agent=user_agent,
    )

    logger.info("user_authenticated", user_id=user.id, username=user.username)
    return user, access_token, refresh_token


async def change_password(
    db: AsyncSession,
    user_id: int,
    old_password: str,
    new_password: str
) -> bool:
    """Change user password"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify old password
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )

    # Update password
    user.password_hash = hash_password(new_password)
    user.password_changed_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()

    # Create audit log
    await create_audit_log(
        db=db,
        action=AuditAction.USER_PASSWORD_CHANGE,
        user_id=user.id,
        entity_type="User",
        entity_id=user.id,
        description="User changed password",
    )

    await db.commit()

    logger.info("password_changed", user_id=user.id)
    return True


# ============================================
# USER STATISTICS
# ============================================

async def get_user_statistics(db: AsyncSession) -> UserStatsResponse:
    """Get user statistics"""
    # Total users
    total_query = select(func.count(User.id)).filter(User.deleted_at.is_(None))
    total = await db.execute(total_query)
    total_users = total.scalar()

    # Active users
    active_query = select(func.count(User.id)).filter(
        User.deleted_at.is_(None),
        User.is_active == True
    )
    active = await db.execute(active_query)
    active_users = active.scalar()

    # Verified users
    verified_query = select(func.count(User.id)).filter(
        User.deleted_at.is_(None),
        User.email_verified == True
    )
    verified = await db.execute(verified_query)
    verified_users = verified.scalar()

    # Users by role
    role_query = select(User.role, func.count(User.id)).filter(
        User.deleted_at.is_(None)
    ).group_by(User.role)
    role_result = await db.execute(role_query)
    users_by_role = {role: count for role, count in role_result.all()}

    # New users last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_query = select(func.count(User.id)).filter(
        User.deleted_at.is_(None),
        User.created_at >= thirty_days_ago
    )
    new_result = await db.execute(new_query)
    new_users_last_30_days = new_result.scalar()

    # Online users (logged in last 15 minutes)
    fifteen_min_ago = datetime.utcnow() - timedelta(minutes=15)
    online_query = select(func.count(User.id)).filter(
        User.deleted_at.is_(None),
        User.last_login_at >= fifteen_min_ago
    )
    online_result = await db.execute(online_query)
    online_users = online_result.scalar()

    return UserStatsResponse(
        total_users=total_users,
        active_users=active_users,
        inactive_users=total_users - active_users,
        verified_users=verified_users,
        users_by_role=users_by_role,
        new_users_last_30_days=new_users_last_30_days,
        online_users=online_users,
    )

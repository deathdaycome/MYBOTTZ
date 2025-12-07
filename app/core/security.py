"""
Security module: JWT authentication, password hashing, RBAC
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any, List
from enum import Enum
import secrets

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import logger


# ============================================
# PASSWORD HASHING
# ============================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Balance between security and performance
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error("password_verification_error", error=str(e))
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if password hash needs to be updated

    Returns:
        True if hash should be regenerated
    """
    return pwd_context.needs_update(hashed_password)


# ============================================
# JWT TOKEN MANAGEMENT
# ============================================

class TokenType(str, Enum):
    """Token types"""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    EMAIL_VERIFICATION = "email_verification"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    username: Optional[str] = None
    role: Optional[str] = None
    token_type: TokenType = TokenType.ACCESS
    exp: Optional[datetime] = None


def create_token(
    data: dict,
    token_type: TokenType = TokenType.ACCESS,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT token

    Args:
        data: Data to encode in token
        token_type: Type of token (access, refresh, etc.)
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        if token_type == TokenType.ACCESS:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == TokenType.REFRESH:
            expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": token_type.value,
        "jti": secrets.token_urlsafe(16),  # JWT ID for tracking
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    logger.debug(
        "token_created",
        token_type=token_type.value,
        user_id=data.get("user_id"),
        expires=expire.isoformat(),
    )

    return encoded_jwt


def create_access_token(user_id: int, username: str = None, role: str = None, **extra_data) -> str:
    """
    Create access token

    Args:
        user_id: User ID
        username: Username (optional)
        role: User role (optional)
        **extra_data: Additional data to include in token

    Returns:
        JWT access token
    """
    data = {
        "user_id": user_id,
        "username": username,
        "role": role,
        **extra_data,
    }
    return create_token(data, TokenType.ACCESS)


def create_refresh_token(user_id: int) -> str:
    """
    Create refresh token

    Args:
        user_id: User ID

    Returns:
        JWT refresh token
    """
    return create_token({"user_id": user_id}, TokenType.REFRESH)


def decode_token(token: str) -> TokenData:
    """
    Decode and verify JWT token

    Args:
        token: JWT token to decode

    Returns:
        TokenData object

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id",
            )

        token_data = TokenData(
            user_id=user_id,
            username=payload.get("username"),
            role=payload.get("role"),
            token_type=TokenType(payload.get("type", "access")),
            exp=datetime.fromtimestamp(payload.get("exp")) if payload.get("exp") else None,
        )

        return token_data

    except JWTError as e:
        logger.warning("jwt_decode_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str, token_type: TokenType = TokenType.ACCESS) -> TokenData:
    """
    Verify token and check type

    Args:
        token: JWT token
        token_type: Expected token type

    Returns:
        TokenData if valid

    Raises:
        HTTPException: If token is invalid or wrong type
    """
    token_data = decode_token(token)

    if token_data.token_type != token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type: expected {token_type.value}",
        )

    return token_data


# ============================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ============================================

class Role(str, Enum):
    """User roles in the system"""
    ADMIN = "admin"
    DISPATCHER = "dispatcher"
    DRIVER = "driver"
    VIEWER = "viewer"
    CLIENT = "client"
    EXECUTOR = "executor"


class Permission(str, Enum):
    """System permissions"""
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Vehicle management
    VEHICLE_CREATE = "vehicle:create"
    VEHICLE_READ = "vehicle:read"
    VEHICLE_UPDATE = "vehicle:update"
    VEHICLE_DELETE = "vehicle:delete"

    # Driver management
    DRIVER_CREATE = "driver:create"
    DRIVER_READ = "driver:read"
    DRIVER_UPDATE = "driver:update"
    DRIVER_DELETE = "driver:delete"

    # Route management
    ROUTE_CREATE = "route:create"
    ROUTE_READ = "route:read"
    ROUTE_UPDATE = "route:update"
    ROUTE_DELETE = "route:delete"

    # Trip management
    TRIP_CREATE = "trip:create"
    TRIP_READ = "trip:read"
    TRIP_UPDATE = "trip:update"
    TRIP_DELETE = "trip:delete"

    # Project management
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"

    # Task management
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_ASSIGN = "task:assign"

    # Analytics
    ANALYTICS_VIEW = "analytics:view"

    # System administration
    ADMIN_PANEL = "admin:panel"
    SYSTEM_CONFIG = "system:config"


# Role -> Permissions mapping
ROLE_PERMISSIONS: dict[Role, List[Permission]] = {
    Role.ADMIN: list(Permission),  # All permissions

    Role.DISPATCHER: [
        Permission.USER_READ,
        Permission.VEHICLE_READ,
        Permission.VEHICLE_UPDATE,
        Permission.DRIVER_READ,
        Permission.DRIVER_UPDATE,
        Permission.ROUTE_CREATE,
        Permission.ROUTE_READ,
        Permission.ROUTE_UPDATE,
        Permission.ROUTE_DELETE,
        Permission.TRIP_CREATE,
        Permission.TRIP_READ,
        Permission.TRIP_UPDATE,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.TASK_CREATE,
        Permission.TASK_READ,
        Permission.TASK_UPDATE,
        Permission.TASK_ASSIGN,
        Permission.ANALYTICS_VIEW,
    ],

    Role.DRIVER: [
        Permission.TRIP_READ,
        Permission.TASK_READ,
        Permission.TASK_UPDATE,
    ],

    Role.VIEWER: [
        Permission.USER_READ,
        Permission.VEHICLE_READ,
        Permission.DRIVER_READ,
        Permission.ROUTE_READ,
        Permission.TRIP_READ,
        Permission.PROJECT_READ,
        Permission.TASK_READ,
        Permission.ANALYTICS_VIEW,
    ],

    Role.CLIENT: [
        Permission.PROJECT_READ,
        Permission.TASK_READ,
    ],

    Role.EXECUTOR: [
        Permission.TASK_READ,
        Permission.TASK_UPDATE,
        Permission.PROJECT_READ,
    ],
}


def get_role_permissions(role: Union[Role, str]) -> List[Permission]:
    """
    Get all permissions for a role

    Args:
        role: Role enum or string

    Returns:
        List of permissions
    """
    if isinstance(role, str):
        try:
            role = Role(role)
        except ValueError:
            logger.warning("invalid_role", role=role)
            return []

    return ROLE_PERMISSIONS.get(role, [])


def has_permission(user_role: Union[Role, str], permission: Permission) -> bool:
    """
    Check if role has specific permission

    Args:
        user_role: User's role
        permission: Permission to check

    Returns:
        True if role has permission
    """
    role_perms = get_role_permissions(user_role)
    return permission in role_perms


def has_any_permission(user_role: Union[Role, str], permissions: List[Permission]) -> bool:
    """
    Check if role has any of the specified permissions

    Args:
        user_role: User's role
        permissions: List of permissions to check

    Returns:
        True if role has at least one permission
    """
    role_perms = get_role_permissions(user_role)
    return any(perm in role_perms for perm in permissions)


def has_all_permissions(user_role: Union[Role, str], permissions: List[Permission]) -> bool:
    """
    Check if role has all specified permissions

    Args:
        user_role: User's role
        permissions: List of permissions to check

    Returns:
        True if role has all permissions
    """
    role_perms = get_role_permissions(user_role)
    return all(perm in role_perms for perm in permissions)


def check_permission(user_role: Union[Role, str], permission: Permission):
    """
    Check permission and raise exception if not allowed

    Args:
        user_role: User's role
        permission: Permission to check

    Raises:
        HTTPException: If user doesn't have permission
    """
    if not has_permission(user_role, permission):
        logger.warning(
            "permission_denied",
            role=user_role if isinstance(user_role, str) else user_role.value,
            permission=permission.value,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {permission.value}",
        )


# ============================================
# ROLE HIERARCHY
# ============================================

ROLE_HIERARCHY: dict[Role, int] = {
    Role.ADMIN: 100,
    Role.DISPATCHER: 50,
    Role.EXECUTOR: 30,
    Role.DRIVER: 30,
    Role.CLIENT: 20,
    Role.VIEWER: 10,
}


def get_role_level(role: Union[Role, str]) -> int:
    """
    Get numeric level of role (higher = more permissions)

    Args:
        role: Role enum or string

    Returns:
        Role level (0-100)
    """
    if isinstance(role, str):
        try:
            role = Role(role)
        except ValueError:
            return 0

    return ROLE_HIERARCHY.get(role, 0)


def can_manage_role(manager_role: Union[Role, str], target_role: Union[Role, str]) -> bool:
    """
    Check if one role can manage another

    Args:
        manager_role: Role of the manager
        target_role: Role to be managed

    Returns:
        True if manager can manage target
    """
    return get_role_level(manager_role) > get_role_level(target_role)


# ============================================
# API KEY MANAGEMENT
# ============================================

def generate_api_key() -> str:
    """
    Generate secure API key

    Returns:
        Random API key
    """
    return secrets.token_urlsafe(32)


def verify_api_key(api_key: str, stored_key: str) -> bool:
    """
    Verify API key

    Args:
        api_key: Provided API key
        stored_key: Stored API key

    Returns:
        True if keys match
    """
    return secrets.compare_digest(api_key, stored_key)


# ============================================
# SECURITY UTILITIES
# ============================================

def generate_verification_code(length: int = 6) -> str:
    """
    Generate numeric verification code

    Args:
        length: Length of code

    Returns:
        Numeric code as string
    """
    return "".join([str(secrets.randbelow(10)) for _ in range(length)])


def generate_reset_token() -> str:
    """
    Generate password reset token

    Returns:
        Secure random token
    """
    return secrets.token_urlsafe(32)


def create_password_reset_token(user_id: int, email: str) -> str:
    """
    Create JWT token for password reset

    Args:
        user_id: User ID
        email: User email

    Returns:
        Password reset JWT token
    """
    return create_token(
        {"user_id": user_id, "email": email},
        TokenType.RESET_PASSWORD,
        expires_delta=timedelta(hours=1),
    )


def verify_password_reset_token(token: str) -> TokenData:
    """
    Verify password reset token

    Args:
        token: Reset token

    Returns:
        TokenData if valid

    Raises:
        HTTPException: If token is invalid
    """
    return verify_token(token, TokenType.RESET_PASSWORD)


# ============================================
# IP WHITELIST/BLACKLIST
# ============================================

def is_ip_allowed(ip: str, whitelist: Optional[List[str]] = None, blacklist: Optional[List[str]] = None) -> bool:
    """
    Check if IP is allowed based on whitelist/blacklist

    Args:
        ip: IP address to check
        whitelist: Allowed IPs (if set, only these are allowed)
        blacklist: Blocked IPs

    Returns:
        True if IP is allowed
    """
    if blacklist and ip in blacklist:
        logger.warning("ip_blacklisted", ip=ip)
        return False

    if whitelist and ip not in whitelist:
        logger.warning("ip_not_whitelisted", ip=ip)
        return False

    return True


# ============================================
# SESSION MANAGEMENT
# ============================================

class SessionData(BaseModel):
    """Session data structure"""
    user_id: int
    username: str
    role: Role
    created_at: datetime
    last_active: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


async def create_session(user_id: int, username: str, role: Role, ip: str = None, user_agent: str = None) -> str:
    """
    Create user session in Redis

    Args:
        user_id: User ID
        username: Username
        role: User role
        ip: IP address
        user_agent: User agent string

    Returns:
        Session ID
    """
    from app.core.redis import cache

    session_id = secrets.token_urlsafe(32)

    session_data = SessionData(
        user_id=user_id,
        username=username,
        role=role,
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow(),
        ip_address=ip,
        user_agent=user_agent,
    )

    await cache.set(
        f"session:{session_id}",
        session_data.model_dump(mode="json"),
        ttl=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    logger.info("session_created", user_id=user_id, session_id=session_id)

    return session_id


async def get_session(session_id: str) -> Optional[SessionData]:
    """
    Get session data from Redis

    Args:
        session_id: Session ID

    Returns:
        SessionData if found
    """
    from app.core.redis import cache

    data = await cache.get(f"session:{session_id}")
    if data:
        return SessionData(**data)
    return None


async def delete_session(session_id: str):
    """
    Delete session from Redis

    Args:
        session_id: Session ID
    """
    from app.core.redis import cache

    await cache.delete(f"session:{session_id}")
    logger.info("session_deleted", session_id=session_id)


async def update_session_activity(session_id: str):
    """
    Update last active timestamp for session

    Args:
        session_id: Session ID
    """
    from app.core.redis import cache

    session = await get_session(session_id)
    if session:
        session.last_active = datetime.utcnow()
        await cache.set(
            f"session:{session_id}",
            session.model_dump(mode="json"),
            ttl=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

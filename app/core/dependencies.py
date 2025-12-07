"""
FastAPI dependencies for authentication, authorization, and common operations
"""

from typing import Optional, List, Annotated
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    decode_token,
    verify_token,
    TokenType,
    Role,
    Permission,
    has_permission,
    has_any_permission,
    has_all_permissions,
    check_permission,
    get_role_level,
)
from app.core.logging import logger, set_correlation_id, get_correlation_id
from app.core.redis import rate_limiter


# ============================================
# SECURITY SCHEMES
# ============================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="JWT",
    auto_error=False,
)

bearer_scheme = HTTPBearer(auto_error=False)


# ============================================
# AUTHENTICATION DEPENDENCIES
# ============================================

async def get_token(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[str]:
    """
    Extract JWT token from Authorization header or query parameter

    Returns:
        JWT token string or None
    """
    if authorization:
        return authorization.credentials
    return token


async def get_current_user_token(token: Optional[str] = Depends(get_token)) -> dict:
    """
    Get current user from JWT token

    Returns:
        Token data dict

    Raises:
        HTTPException: If token is invalid or missing
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = decode_token(token)

    return {
        "user_id": token_data.user_id,
        "username": token_data.username,
        "role": token_data.role,
    }


async def get_current_user(
    token_data: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user from database

    Returns:
        User model instance

    Raises:
        HTTPException: If user not found
    """
    from app.database.models import User

    user_id = token_data["user_id"]

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("user_not_found", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        logger.warning("inactive_user_access_attempt", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    logger.debug("current_user_authenticated", user_id=user.id, username=user.username)
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user),
):
    """
    Get current active user (alias for get_current_user)
    """
    return current_user


async def get_optional_current_user(
    token: Optional[str] = Depends(get_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user if authenticated, otherwise return None

    Returns:
        User model instance or None
    """
    if not token:
        return None

    try:
        token_data = decode_token(token)
        from app.database.models import User

        result = await db.execute(select(User).filter(User.id == token_data.user_id))
        user = result.scalar_one_or_none()

        if user and user.is_active:
            return user
    except Exception as e:
        logger.debug("optional_auth_failed", error=str(e))

    return None


# ============================================
# ROLE-BASED AUTHORIZATION
# ============================================

class RoleChecker:
    """
    Dependency class to check user role

    Usage:
        @app.get("/admin")
        async def admin_endpoint(user = Depends(require_role(Role.ADMIN))):
            pass
    """

    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user = Depends(get_current_user)):
        user_role = current_user.role

        # Convert string to Role enum if needed
        if isinstance(user_role, str):
            try:
                user_role = Role(user_role)
            except ValueError:
                logger.warning("invalid_user_role", role=user_role, user_id=current_user.id)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid user role",
                )

        if user_role not in self.allowed_roles:
            logger.warning(
                "role_access_denied",
                user_id=current_user.id,
                user_role=user_role.value,
                required_roles=[r.value for r in self.allowed_roles],
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in self.allowed_roles]}",
            )

        return current_user


def require_role(*roles: Role):
    """
    Create dependency to require specific role(s)

    Usage:
        @app.get("/admin")
        async def admin_endpoint(user = Depends(require_role(Role.ADMIN))):
            pass

        @app.get("/dashboard")
        async def dashboard(user = Depends(require_role(Role.ADMIN, Role.DISPATCHER))):
            pass
    """
    return RoleChecker(list(roles))


# Convenience dependencies for common roles
require_admin = require_role(Role.ADMIN)
require_dispatcher = require_role(Role.ADMIN, Role.DISPATCHER)
require_executor = require_role(Role.ADMIN, Role.DISPATCHER, Role.EXECUTOR)


# ============================================
# PERMISSION-BASED AUTHORIZATION
# ============================================

class PermissionChecker:
    """
    Dependency class to check user permissions

    Usage:
        @app.post("/users")
        async def create_user(user = Depends(require_permission(Permission.USER_CREATE))):
            pass
    """

    def __init__(self, required_permissions: List[Permission], require_all: bool = False):
        self.required_permissions = required_permissions
        self.require_all = require_all

    async def __call__(self, current_user = Depends(get_current_user)):
        user_role = current_user.role

        # Convert string to Role enum if needed
        if isinstance(user_role, str):
            try:
                user_role = Role(user_role)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid user role",
                )

        # Check permissions
        if self.require_all:
            has_access = has_all_permissions(user_role, self.required_permissions)
        else:
            has_access = has_any_permission(user_role, self.required_permissions)

        if not has_access:
            logger.warning(
                "permission_denied",
                user_id=current_user.id,
                user_role=user_role.value,
                required_permissions=[p.value for p in self.required_permissions],
                require_all=self.require_all,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user


def require_permission(*permissions: Permission, require_all: bool = False):
    """
    Create dependency to require specific permission(s)

    Usage:
        @app.post("/users")
        async def create_user(user = Depends(require_permission(Permission.USER_CREATE))):
            pass

        @app.get("/reports")
        async def reports(user = Depends(require_permission(
            Permission.ANALYTICS_VIEW,
            Permission.TRIP_READ,
            require_all=True
        ))):
            pass
    """
    return PermissionChecker(list(permissions), require_all)


# ============================================
# RATE LIMITING
# ============================================

class RateLimitChecker:
    """
    Rate limit dependency

    Usage:
        @app.get("/api/data", dependencies=[Depends(rate_limit(max_requests=10, window=60))])
        async def get_data():
            pass
    """

    def __init__(self, max_requests: int, window: int = 60, key_func=None):
        self.max_requests = max_requests
        self.window = window
        self.key_func = key_func or self._default_key_func

    def _default_key_func(self, request: Request, user_id: Optional[int] = None) -> str:
        """Generate rate limit key from request"""
        if user_id:
            return f"rate_limit:user:{user_id}:{request.url.path}"
        return f"rate_limit:ip:{request.client.host}:{request.url.path}"

    async def __call__(
        self,
        request: Request,
        current_user = Depends(get_optional_current_user),
    ):
        user_id = current_user.id if current_user else None
        key = self.key_func(request, user_id)

        allowed, remaining = await rate_limiter.is_allowed(
            key=key,
            max_requests=self.max_requests,
            window=self.window,
        )

        if not allowed:
            logger.warning(
                "rate_limit_exceeded",
                key=key,
                user_id=user_id,
                max_requests=self.max_requests,
                window=self.window,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window} seconds.",
                headers={"Retry-After": str(self.window)},
            )

        # Add rate limit headers
        request.state.rate_limit_remaining = remaining
        request.state.rate_limit_limit = self.max_requests


def rate_limit(max_requests: int, window: int = 60):
    """
    Create rate limit dependency

    Args:
        max_requests: Maximum number of requests
        window: Time window in seconds

    Usage:
        @app.get("/api/data", dependencies=[Depends(rate_limit(max_requests=10, window=60))])
        async def get_data():
            pass
    """
    return RateLimitChecker(max_requests, window)


# ============================================
# REQUEST CONTEXT
# ============================================

async def get_request_id(
    request: Request,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> str:
    """
    Get or generate request ID for tracing

    Returns:
        Request ID string
    """
    request_id = x_request_id or get_correlation_id()
    set_correlation_id(request_id)
    request.state.request_id = request_id
    return request_id


async def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request

    Returns:
        IP address string
    """
    # Check for proxy headers
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


async def get_user_agent(request: Request) -> str:
    """
    Get user agent from request

    Returns:
        User agent string
    """
    return request.headers.get("User-Agent", "unknown")


# ============================================
# PAGINATION
# ============================================

class PaginationParams:
    """
    Pagination parameters

    Usage:
        @app.get("/items")
        async def get_items(pagination: PaginationParams = Depends()):
            skip = pagination.skip
            limit = pagination.limit
    """

    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100,
    ):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), max_page_size)

    @property
    def skip(self) -> int:
        """Calculate offset for database query"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database query"""
        return self.page_size


def get_pagination(
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100,
) -> PaginationParams:
    """
    Get pagination parameters

    Usage:
        @app.get("/items")
        async def get_items(pagination: PaginationParams = Depends(get_pagination)):
            skip = pagination.skip
            limit = pagination.limit
    """
    return PaginationParams(page, page_size, max_page_size)


# ============================================
# COMMON FILTERS
# ============================================

class DateRangeFilter:
    """
    Date range filter for queries

    Usage:
        @app.get("/reports")
        async def get_reports(date_filter: DateRangeFilter = Depends()):
            # Use date_filter.start_date and date_filter.end_date
    """

    def __init__(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        from datetime import datetime

        self.start_date = datetime.fromisoformat(start_date) if start_date else None
        self.end_date = datetime.fromisoformat(end_date) if end_date else None


class SearchFilter:
    """
    Search filter for queries

    Usage:
        @app.get("/users")
        async def search_users(search: SearchFilter = Depends()):
            query = search.query
    """

    def __init__(
        self,
        q: Optional[str] = None,
        search: Optional[str] = None,
    ):
        self.query = q or search


# ============================================
# TYPED ANNOTATIONS (for convenience)
# ============================================

# These can be used as type hints in route handlers
CurrentUser = Annotated[object, Depends(get_current_user)]
OptionalUser = Annotated[Optional[object], Depends(get_optional_current_user)]
AdminUser = Annotated[object, Depends(require_admin)]
DispatcherUser = Annotated[object, Depends(require_dispatcher)]
ExecutorUser = Annotated[object, Depends(require_executor)]
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
Pagination = Annotated[PaginationParams, Depends(get_pagination)]
RequestId = Annotated[str, Depends(get_request_id)]
ClientIP = Annotated[str, Depends(get_client_ip)]


# ============================================
# WEBSOCKET AUTHENTICATION
# ============================================

async def websocket_auth(
    websocket,
    token: Optional[str] = None,
):
    """
    Authenticate WebSocket connection

    Usage:
        @app.websocket("/ws")
        async def websocket_endpoint(
            websocket: WebSocket,
            user = Depends(websocket_auth)
        ):
            await websocket.accept()
            # user is authenticated
    """
    if not token:
        # Try to get token from query params
        token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        token_data = decode_token(token)

        # Get user from database
        from app.database.models import User
        from app.core.database import get_db_context

        async with get_db_context() as db:
            result = await db.execute(select(User).filter(User.id == token_data.user_id))
            user = result.scalar_one_or_none()

            if not user or not user.is_active:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user",
                )

            return user

    except Exception as e:
        logger.warning("websocket_auth_failed", error=str(e))
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise

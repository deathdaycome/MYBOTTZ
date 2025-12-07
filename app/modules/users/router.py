"""
User API Router

FastAPI routes for user management and authentication.
"""

from typing import Optional
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user, require_admin,
    get_pagination, get_client_ip, get_user_agent,
    CurrentUser, AdminUser, DatabaseSession, Pagination
)
from app.core.security import Role
from app.modules.users import service
from app.modules.users.schemas import (
    UserCreate, UserUpdate, UserUpdateAdmin, PasswordChange,
    UserResponse, UserListResponse, UserDetailResponse, UserStatsResponse,
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
)
from app.core.logging import logger

router = APIRouter(prefix="/users", tags=["Users"])
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account. Email and username must be unique."
)
async def register(
    user_data: UserCreate,
    db: DatabaseSession,
) -> UserResponse:
    """Register a new user"""
    user = await service.create_user(db, user_data)
    return UserResponse.from_orm(user)


@auth_router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    description="Authenticate user and receive JWT tokens"
)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: DatabaseSession,
) -> LoginResponse:
    """Login user and return JWT tokens"""
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)

    user, access_token, refresh_token = await service.authenticate_user(
        db,
        credentials.username,
        credentials.password,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    if not user:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=refresh_token,  # Contains error message
            headers={"WWW-Authenticate": "Bearer"},
        )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800,  # 30 minutes
        user=UserResponse.from_orm(user),
    )


@auth_router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: DatabaseSession,
) -> RefreshTokenResponse:
    """Refresh access token"""
    from app.core.security import decode_token, create_access_token, create_refresh_token, TokenType
    from fastapi import HTTPException

    # Decode refresh token
    try:
        token_payload = decode_token(token_data.refresh_token)

        if token_payload.token_type != TokenType.REFRESH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # Get user
        user = await service.get_user_by_id(db, token_payload.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new tokens
        new_access_token = create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        new_refresh_token = create_refresh_token(user_id=user.id)

        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=1800,
        )

    except Exception as e:
        logger.error("refresh_token_error", error=str(e))
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
    description="Logout current user (invalidate session)"
)
async def logout(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """Logout current user"""
    # TODO: Implement session invalidation
    logger.info("user_logged_out", user_id=current_user.id)
    return None


# ============================================
# USER PROFILE ENDPOINTS
# ============================================

@router.get(
    "/me",
    response_model=UserDetailResponse,
    summary="Get current user profile",
    description="Get detailed information about current authenticated user"
)
async def get_current_user_profile(
    current_user: CurrentUser,
) -> UserDetailResponse:
    """Get current user profile"""
    return UserDetailResponse.from_orm(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update current user's own profile information"
)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> UserResponse:
    """Update current user profile"""
    updated_user = await service.update_user(
        db,
        current_user.id,
        user_data,
        updated_by_user_id=current_user.id
    )
    return UserResponse.from_orm(updated_user)


@router.post(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password",
    description="Change current user's password"
)
async def change_password(
    password_data: PasswordChange,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """Change user password"""
    await service.change_password(
        db,
        current_user.id,
        password_data.old_password,
        password_data.new_password,
    )
    return None


# ============================================
# USER MANAGEMENT ENDPOINTS (Admin)
# ============================================

@router.get(
    "/",
    response_model=UserListResponse,
    summary="List users",
    description="Get paginated list of users (Admin only)",
    dependencies=[Depends(require_admin)]
)
async def list_users(
    db: DatabaseSession,
    pagination: Pagination,
    role: Optional[Role] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
) -> UserListResponse:
    """List all users with pagination and filters"""
    users, total = await service.get_users(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        role=role,
        is_active=is_active,
        search=search,
    )

    return UserListResponse(
        users=[UserResponse.from_orm(u) for u in users],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=ceil(total / pagination.page_size) if total > 0 else 0,
    )


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user (Admin only)",
    dependencies=[Depends(require_admin)]
)
async def create_user(
    user_data: UserCreate,
    current_user: AdminUser,
    db: DatabaseSession,
) -> UserResponse:
    """Create new user (admin only)"""
    user = await service.create_user(
        db,
        user_data,
        created_by_user_id=current_user.id
    )
    return UserResponse.from_orm(user)


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Get user by ID",
    description="Get detailed user information by ID (Admin only)",
    dependencies=[Depends(require_admin)]
)
async def get_user(
    user_id: int,
    db: DatabaseSession,
) -> UserDetailResponse:
    """Get user by ID"""
    from fastapi import HTTPException

    user = await service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserDetailResponse.from_orm(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user information including role (Admin only)",
    dependencies=[Depends(require_admin)]
)
async def update_user(
    user_id: int,
    user_data: UserUpdateAdmin,
    current_user: AdminUser,
    db: DatabaseSession,
) -> UserResponse:
    """Update user (admin only)"""
    updated_user = await service.update_user_admin(
        db,
        user_id,
        user_data,
        admin_user_id=current_user.id
    )
    return UserResponse.from_orm(updated_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete user (soft delete by default, Admin only)",
    dependencies=[Depends(require_admin)]
)
async def delete_user(
    user_id: int,
    current_user: AdminUser,
    db: DatabaseSession,
    hard_delete: bool = False,
):
    """Delete user"""
    await service.delete_user(
        db,
        user_id,
        deleted_by_user_id=current_user.id,
        hard_delete=hard_delete,
    )
    return None


# ============================================
# USER STATISTICS (Admin)
# ============================================

@router.get(
    "/statistics/overview",
    response_model=UserStatsResponse,
    summary="Get user statistics",
    description="Get overall user statistics (Admin only)",
    dependencies=[Depends(require_admin)]
)
async def get_user_statistics(
    db: DatabaseSession,
) -> UserStatsResponse:
    """Get user statistics"""
    return await service.get_user_statistics(db)


# ============================================
# USER SEARCH
# ============================================

@router.get(
    "/search/by-username/{username}",
    response_model=UserResponse,
    summary="Find user by username",
    description="Search for user by exact username (Admin only)",
    dependencies=[Depends(require_admin)]
)
async def find_by_username(
    username: str,
    db: DatabaseSession,
) -> UserResponse:
    """Find user by username"""
    from fastapi import HTTPException

    user = await service.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.from_orm(user)


@router.get(
    "/search/by-email/{email}",
    response_model=UserResponse,
    summary="Find user by email",
    description="Search for user by exact email (Admin only)",
    dependencies=[Depends(require_admin)]
)
async def find_by_email(
    email: str,
    db: DatabaseSession,
) -> UserResponse:
    """Find user by email"""
    from fastapi import HTTPException

    user = await service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.from_orm(user)

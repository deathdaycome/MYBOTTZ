"""
User Pydantic Schemas

Data validation schemas for user-related operations.
"""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field, validator, constr

from app.core.security import Role


# ============================================
# BASE SCHEMAS
# ============================================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: constr(min_length=3, max_length=100) = Field(..., description="Username (3-100 characters)")
    email: EmailStr = Field(..., description="Valid email address")
    full_name: Optional[str] = Field(None, max_length=200, description="Full name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    telegram_username: Optional[str] = Field(None, max_length=100, description="Telegram username")
    role: Role = Field(Role.VIEWER, description="User role")
    bio: Optional[str] = Field(None, description="User biography")

    class Config:
        from_attributes = True


# ============================================
# USER CREATE/UPDATE SCHEMAS
# ============================================

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: constr(min_length=8, max_length=100) = Field(..., description="Password (min 8 characters)")
    telegram_id: Optional[str] = Field(None, description="Telegram ID")

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.lower()


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    telegram_username: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = Field(None, max_length=500)

    class Config:
        from_attributes = True


class UserUpdateAdmin(UserUpdate):
    """Schema for admin updating user (includes role changes)"""
    role: Optional[Role] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class PasswordChange(BaseModel):
    """Schema for changing password"""
    old_password: str = Field(..., min_length=1, description="Current password")
    new_password: constr(min_length=8, max_length=100) = Field(..., description="New password")

    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordReset(BaseModel):
    """Schema for password reset"""
    token: str = Field(..., description="Reset token")
    new_password: constr(min_length=8, max_length=100) = Field(..., description="New password")


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset"""
    email: EmailStr = Field(..., description="Email address")


# ============================================
# USER RESPONSE SCHEMAS
# ============================================

class UserResponse(UserBase):
    """Schema for user response (safe for API)"""
    id: int
    is_active: bool
    is_superuser: bool
    email_verified: bool
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Schema for detailed user information"""
    telegram_id: Optional[str]
    failed_login_attempts: int
    locked_until: Optional[datetime]
    password_changed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================
# AUTHENTICATION SCHEMAS
# ============================================

class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str = Field(..., min_length=1, description="Username or email")
    password: str = Field(..., min_length=1, description="Password")


class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse

    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenResponse(BaseModel):
    """Schema for refresh token response"""
    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="New JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    class Config:
        from_attributes = True


# ============================================
# SESSION SCHEMAS
# ============================================

class SessionResponse(BaseModel):
    """Schema for user session response"""
    id: int
    session_id: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_type: Optional[str]
    device_name: Optional[str]
    country: Optional[str]
    city: Optional[str]
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Schema for user sessions list"""
    sessions: list[SessionResponse]
    total: int

    class Config:
        from_attributes = True


# ============================================
# ACTIVITY SCHEMAS
# ============================================

class ActivityResponse(BaseModel):
    """Schema for user activity response"""
    id: int
    activity_type: str
    description: Optional[str]
    success: bool
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """Schema for user activity list"""
    activities: list[ActivityResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


# ============================================
# STATISTICS SCHEMAS
# ============================================

class UserStatsResponse(BaseModel):
    """Schema for user statistics"""
    total_users: int
    active_users: int
    inactive_users: int
    verified_users: int
    users_by_role: Dict[str, int]
    new_users_last_30_days: int
    online_users: int

    class Config:
        from_attributes = True

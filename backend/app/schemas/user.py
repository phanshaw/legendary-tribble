from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)
    password_confirm: str = Field(..., min_length=8, max_length=100)

    def validate_passwords_match(self) -> "UserCreate":
        """Validate that passwords match"""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class UserUpdate(BaseModel):
    """Schema for user profile update"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    company: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None


class UserPasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    new_password_confirm: str = Field(..., min_length=8, max_length=100)

    def validate_passwords_match(self) -> "UserPasswordChange":
        """Validate that new passwords match"""
        if self.new_password != self.new_password_confirm:
            raise ValueError("New passwords do not match")
        return self


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    email_verified: bool = False
    two_factor_enabled: bool = False
    storage_used: int = 0
    storage_quota: int = 1073741824
    storage_percentage: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class UserPublicResponse(BaseModel):
    """Schema for public user information"""
    id: int
    name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserAdminResponse(UserResponse):
    """Schema for admin user view"""
    email_verified_at: Optional[datetime] = None
    api_key_created_at: Optional[datetime] = None
    preferences: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class UserStorageInfo(BaseModel):
    """Schema for user storage information"""
    used: int
    quota: int
    remaining: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)


class UserPreferences(BaseModel):
    """Schema for user preferences"""
    theme: str = "light"
    language: str = "en"
    notifications_enabled: bool = True
    email_notifications: bool = True
    show_tutorials: bool = True
    default_file_visibility: str = "private"
    auto_save: bool = True
    viewer_settings: Dict[str, Any] = {}


class UserStatistics(BaseModel):
    """Schema for user statistics"""
    total_files: int = 0
    total_downloads: int = 0
    total_views: int = 0
    storage_used: int = 0
    files_by_type: Dict[str, int] = {}
    files_by_month: Dict[str, int] = {}

    model_config = ConfigDict(from_attributes=True)
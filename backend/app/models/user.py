from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import String, JSON as SQLAlchemyJSON


class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserBase(SQLModel):
    """Base user model for shared fields"""
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(
        sa_column=Column(String, unique=True, index=True),
        regex=r"^[\w\.-]+@[\w\.-]+\.\w+$"
    )
    is_active: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.USER)


class User(UserBase, table=True):
    """Database user model"""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(exclude=True)  # Exclude from API responses

    # Profile information
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=500)
    company: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=100)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None

    # Account settings
    email_verified: bool = Field(default=False)
    two_factor_enabled: bool = Field(default=False)
    two_factor_secret: Optional[str] = Field(default=None, exclude=True)

    # Metadata
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(SQLAlchemyJSON)
    )

    # Storage quota (in bytes)
    storage_quota: int = Field(default=1073741824)  # 1GB default
    storage_used: int = Field(default=0)

    # API access
    api_key: Optional[str] = Field(default=None, exclude=True)
    api_key_created_at: Optional[datetime] = None

    # Relationships
    files: List["FileRecord"] = Relationship(back_populates="user")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")

    @property
    def storage_remaining(self) -> int:
        """Calculate remaining storage"""
        return max(0, self.storage_quota - self.storage_used)

    @property
    def storage_percentage(self) -> float:
        """Calculate storage usage percentage"""
        if self.storage_quota == 0:
            return 0.0
        return (self.storage_used / self.storage_quota) * 100

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        # Admin has all permissions
        if self.role == UserRole.ADMIN:
            return True

        # Define permission mappings
        permissions = {
            UserRole.USER: ["read", "write:own", "delete:own"],
            UserRole.MODERATOR: ["read", "write:own", "delete:own", "moderate"],
        }

        return permission in permissions.get(self.role, [])


class RefreshToken(SQLModel, table=True):
    """Refresh token storage for JWT authentication"""
    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="users.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked: bool = Field(default=False)

    # Relationship
    user: Optional[User] = Relationship(back_populates="refresh_tokens")

    @property
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        return not self.revoked and self.expires_at > datetime.utcnow()
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserResponse


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenWithUser(Token):
    """Token response with user information"""
    user: UserResponse


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # Subject (usually user email or ID)
    exp: datetime  # Expiration time
    iat: datetime  # Issued at
    type: str  # Token type (access, refresh)
    jti: Optional[str] = None  # JWT ID (for refresh tokens)
    role: Optional[str] = None  # User role
    permissions: Optional[list[str]] = None  # User permissions


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str
    two_factor_code: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    new_password_confirm: str = Field(..., min_length=8, max_length=100)

    def validate_passwords_match(self) -> "PasswordResetConfirm":
        """Validate that passwords match"""
        if self.new_password != self.new_password_confirm:
            raise ValueError("Passwords do not match")
        return self


class EmailVerificationRequest(BaseModel):
    """Email verification request"""
    token: str


class TwoFactorSetupResponse(BaseModel):
    """Two-factor authentication setup response"""
    secret: str
    qr_code_uri: str
    backup_codes: list[str]


class TwoFactorVerifyRequest(BaseModel):
    """Two-factor verification request"""
    code: str


class APIKeyCreateRequest(BaseModel):
    """API key creation request"""
    name: str = Field(..., min_length=1, max_length=100)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """API key response"""
    key: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    message: str = "Store this key securely. It won't be shown again."
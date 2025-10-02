from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
import pyotp

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

# API Key scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class SecurityManager:
    """Central security management class"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        subject: str,
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "access",
            "iat": datetime.utcnow(),
        }

        if additional_claims:
            to_encode.update(additional_claims)

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(
        subject: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "refresh",
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32),  # JWT ID for revocation
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def generate_verification_token() -> str:
        """Generate email verification token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_password_reset_token(email: str) -> str:
        """Generate password reset token"""
        delta = timedelta(hours=1)  # Token valid for 1 hour
        expire = datetime.utcnow() + delta
        to_encode = {
            "exp": expire,
            "sub": email,
            "type": "password_reset"
        }
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[str]:
        """Verify password reset token and return email"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != "password_reset":
                return None
            return payload.get("sub")
        except JWTError:
            return None


class TwoFactorAuth:
    """Two-factor authentication management"""

    @staticmethod
    def generate_secret() -> str:
        """Generate 2FA secret"""
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(email: str, secret: str) -> str:
        """Generate QR code URL for 2FA setup"""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=email,
            issuer_name=settings.PROJECT_NAME
        )
        return provisioning_uri

    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """Verify 2FA token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

    @staticmethod
    def generate_backup_codes(count: int = 10) -> list[str]:
        """Generate backup codes for 2FA"""
        return [secrets.token_hex(4) for _ in range(count)]


class RateLimiter:
    """Simple rate limiting implementation"""

    def __init__(self):
        self.requests = {}

    def is_allowed(
        self,
        key: str,
        max_requests: int = settings.RATE_LIMIT_REQUESTS,
        window_seconds: int = settings.RATE_LIMIT_PERIOD
    ) -> bool:
        """Check if request is allowed based on rate limit"""
        now = datetime.utcnow()

        if key not in self.requests:
            self.requests[key] = []

        # Clean old requests
        cutoff = now - timedelta(seconds=window_seconds)
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > cutoff
        ]

        # Check limit
        if len(self.requests[key]) >= max_requests:
            return False

        # Add current request
        self.requests[key].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


def check_rate_limit(request: Request):
    """Dependency to check rate limiting"""
    if not settings.RATE_LIMIT_ENABLED:
        return

    # Use IP address as key
    client_ip = request.client.host

    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )


# Password validation
def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"

    return True, "Password is valid"
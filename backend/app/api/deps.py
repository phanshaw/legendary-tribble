from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlmodel import Session, select
from jose import JWTError

from app.core.database import get_db
from app.core.security import SecurityManager
from app.core.config import settings
from app.core.exceptions import UnauthorizedException, PermissionDeniedException
from app.models.user import User, UserRole

# OAuth2 scheme for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

# API Key scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token or API key
    """
    user = None

    # Try JWT token first
    if token:
        try:
            payload = SecurityManager.decode_token(token)
            email = payload.get("sub")
            token_type = payload.get("type")

            if not email or token_type != "access":
                raise UnauthorizedException("Invalid token")

            user = db.exec(select(User).where(User.email == email)).first()
        except JWTError:
            raise UnauthorizedException("Invalid token")

    # Try API key if no JWT token
    elif api_key:
        # Hash the API key for comparison
        hashed_key = SecurityManager.hash_api_key(api_key)
        user = db.exec(select(User).where(User.api_key == hashed_key)).first()

    if not user:
        raise UnauthorizedException("Not authenticated")

    if not user.is_active:
        raise UnauthorizedException("User account is disabled")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current user with verified email
    """
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current admin user
    """
    if current_user.role != UserRole.ADMIN:
        raise PermissionDeniedException("Admin access required")
    return current_user


async def get_current_moderator_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current moderator or admin user
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
        raise PermissionDeniedException("Moderator access required")
    return current_user


class PermissionChecker:
    """
    Dependency class for checking user permissions
    """

    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        """
        Check if user has required permissions
        """
        for permission in self.required_permissions:
            if not current_user.has_permission(permission):
                raise PermissionDeniedException(
                    f"Missing required permission: {permission}"
                )
        return current_user


class PaginationParams:
    """
    Common pagination parameters
    """

    def __init__(
        self,
        page: int = 1,
        per_page: int = 20,
        max_per_page: int = 100
    ):
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        if per_page > max_per_page:
            per_page = max_per_page

        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page
        self.limit = per_page


class SortParams:
    """
    Common sorting parameters
    """

    def __init__(
        self,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        self.sort_by = sort_by
        self.sort_order = sort_order.lower()

        if self.sort_order not in ["asc", "desc"]:
            self.sort_order = "desc"


class SearchParams:
    """
    Common search parameters
    """

    def __init__(
        self,
        q: Optional[str] = None,
        filters: Optional[dict] = None
    ):
        self.query = q
        self.filters = filters or {}


def get_db_session() -> Generator[Session, None, None]:
    """
    Alias for get_db for consistency
    """
    return get_db()


async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Verify API key without returning user
    """
    if not api_key:
        raise UnauthorizedException("API key required")

    # You can add additional API key validation here
    # For example, checking against a rate limit database

    return api_key
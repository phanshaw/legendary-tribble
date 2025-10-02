from typing import Any, Optional, Dict
from fastapi import HTTPException, status


class APIException(HTTPException):
    """Base API Exception"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class BadRequestException(APIException):
    """400 Bad Request"""

    def __init__(self, detail: str = "Bad request", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code or "BAD_REQUEST",
        )


class UnauthorizedException(APIException):
    """401 Unauthorized"""

    def __init__(self, detail: str = "Unauthorized", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code=error_code or "UNAUTHORIZED",
        )


class ForbiddenException(APIException):
    """403 Forbidden"""

    def __init__(self, detail: str = "Forbidden", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code or "FORBIDDEN",
        )


class NotFoundException(APIException):
    """404 Not Found"""

    def __init__(self, detail: str = "Not found", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code or "NOT_FOUND",
        )


class ConflictException(APIException):
    """409 Conflict"""

    def __init__(self, detail: str = "Conflict", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code or "CONFLICT",
        )


class ValidationException(APIException):
    """422 Validation Error"""

    def __init__(self, detail: str = "Validation error", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code or "VALIDATION_ERROR",
        )


class RateLimitException(APIException):
    """429 Too Many Requests"""

    def __init__(self, detail: str = "Too many requests", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code=error_code or "RATE_LIMIT_EXCEEDED",
        )


class InternalServerException(APIException):
    """500 Internal Server Error"""

    def __init__(self, detail: str = "Internal server error", error_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code or "INTERNAL_ERROR",
        )


# Specific business logic exceptions
class UserNotFoundException(NotFoundException):
    """User not found exception"""

    def __init__(self, user_id: Optional[int] = None):
        detail = f"User {user_id} not found" if user_id else "User not found"
        super().__init__(detail=detail, error_code="USER_NOT_FOUND")


class FileNotFoundException(NotFoundException):
    """File not found exception"""

    def __init__(self, file_id: Optional[int] = None):
        detail = f"File {file_id} not found" if file_id else "File not found"
        super().__init__(detail=detail, error_code="FILE_NOT_FOUND")


class InvalidCredentialsException(UnauthorizedException):
    """Invalid credentials exception"""

    def __init__(self):
        super().__init__(detail="Invalid email or password", error_code="INVALID_CREDENTIALS")


class EmailAlreadyExistsException(ConflictException):
    """Email already exists exception"""

    def __init__(self, email: str):
        super().__init__(
            detail=f"User with email {email} already exists",
            error_code="EMAIL_EXISTS",
        )


class InsufficientStorageException(ForbiddenException):
    """Insufficient storage exception"""

    def __init__(self, required: int, available: int):
        super().__init__(
            detail=f"Insufficient storage. Required: {required} bytes, Available: {available} bytes",
            error_code="INSUFFICIENT_STORAGE",
        )


class InvalidFileTypeException(BadRequestException):
    """Invalid file type exception"""

    def __init__(self, file_type: str, allowed_types: list):
        super().__init__(
            detail=f"Invalid file type '{file_type}'. Allowed types: {', '.join(allowed_types)}",
            error_code="INVALID_FILE_TYPE",
        )


class FileTooLargeException(BadRequestException):
    """File too large exception"""

    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            detail=f"File size {file_size} bytes exceeds maximum allowed size {max_size} bytes",
            error_code="FILE_TOO_LARGE",
        )


class TokenExpiredException(UnauthorizedException):
    """Token expired exception"""

    def __init__(self):
        super().__init__(detail="Token has expired", error_code="TOKEN_EXPIRED")


class InvalidTokenException(UnauthorizedException):
    """Invalid token exception"""

    def __init__(self):
        super().__init__(detail="Invalid token", error_code="INVALID_TOKEN")


class PermissionDeniedException(ForbiddenException):
    """Permission denied exception"""

    def __init__(self, action: str):
        super().__init__(
            detail=f"You don't have permission to {action}",
            error_code="PERMISSION_DENIED",
        )


class EmailNotVerifiedException(ForbiddenException):
    """Email not verified exception"""

    def __init__(self):
        super().__init__(
            detail="Email address is not verified",
            error_code="EMAIL_NOT_VERIFIED",
        )


class AccountDisabledException(ForbiddenException):
    """Account disabled exception"""

    def __init__(self):
        super().__init__(detail="Account has been disabled", error_code="ACCOUNT_DISABLED")


class InvalidPasswordException(BadRequestException):
    """Invalid password exception"""

    def __init__(self, reason: str):
        super().__init__(detail=reason, error_code="INVALID_PASSWORD")


class TwoFactorRequiredException(UnauthorizedException):
    """Two-factor authentication required exception"""

    def __init__(self):
        super().__init__(
            detail="Two-factor authentication required",
            error_code="2FA_REQUIRED",
        )


class InvalidTwoFactorCodeException(UnauthorizedException):
    """Invalid two-factor code exception"""

    def __init__(self):
        super().__init__(
            detail="Invalid two-factor authentication code",
            error_code="INVALID_2FA_CODE",
        )
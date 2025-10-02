from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import SecurityManager, TwoFactorAuth, validate_password
from app.core.exceptions import (
    InvalidCredentialsException,
    EmailAlreadyExistsException,
    InvalidPasswordException,
    InvalidTwoFactorCodeException,
    TwoFactorRequiredException,
)
from app.models.user import User, RefreshToken
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import (
    Token,
    TokenWithUser,
    LoginRequest,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
)
from app.services.email import EmailService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    # Validate password strength
    is_valid, error_msg = validate_password(user_data.password)
    if not is_valid:
        raise InvalidPasswordException(error_msg)

    # Validate passwords match
    user_data.validate_passwords_match()

    # Check if user exists
    existing_user = db.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise EmailAlreadyExistsException(user_data.email)

    # Create new user
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=SecurityManager.get_password_hash(user_data.password),
        is_active=user_data.is_active,
        role=user_data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Send verification email in background
    if settings.emails_enabled:
        verification_token = SecurityManager.generate_verification_token()
        background_tasks.add_task(
            EmailService.send_verification_email,
            user.email,
            user.name,
            verification_token
        )

    return user


@router.post("/login", response_model=TokenWithUser)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    """
    # Find user
    user = db.exec(
        select(User).where(User.email == login_data.email)
    ).first()

    if not user or not SecurityManager.verify_password(
        login_data.password, user.hashed_password
    ):
        raise InvalidCredentialsException()

    # Check if 2FA is enabled
    if user.two_factor_enabled:
        if not login_data.two_factor_code:
            raise TwoFactorRequiredException()

        if not TwoFactorAuth.verify_token(
            user.two_factor_secret, login_data.two_factor_code
        ):
            raise InvalidTwoFactorCodeException()

    # Update last login
    user.update_last_login()
    db.commit()

    # Create tokens
    access_token = SecurityManager.create_access_token(
        subject=user.email,
        additional_claims={"role": user.role}
    )

    refresh_token = SecurityManager.create_refresh_token(
        subject=user.email
    )

    # Store refresh token
    refresh_token_obj = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    )
    db.add(refresh_token_obj)
    db.commit()

    return TokenWithUser(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )


@router.post("/login/oauth", response_model=TokenWithUser)
async def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible login endpoint
    """
    login_data = LoginRequest(
        email=form_data.username,  # OAuth2 uses username field
        password=form_data.password
    )
    return await login(login_data, db)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        payload = SecurityManager.decode_token(refresh_data.refresh_token)
        email = payload.get("sub")
        token_type = payload.get("type")
        jti = payload.get("jti")

        if not email or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Check if refresh token exists and is valid
        stored_token = db.exec(
            select(RefreshToken).where(
                RefreshToken.token == refresh_data.refresh_token
            )
        ).first()

        if not stored_token or not stored_token.is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        # Get user
        user = db.exec(select(User).where(User.email == email)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new access token
        access_token = SecurityManager.create_access_token(
            subject=user.email,
            additional_claims={"role": user.role}
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    refresh_token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Logout and revoke refresh token
    """
    if refresh_token:
        # Revoke the refresh token
        stored_token = db.exec(
            select(RefreshToken).where(RefreshToken.token == refresh_token)
        ).first()

        if stored_token:
            stored_token.revoked = True
            db.commit()

    return {"message": "Successfully logged out"}


@router.post("/password-reset")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset email
    """
    user = db.exec(
        select(User).where(User.email == reset_data.email)
    ).first()

    # Don't reveal if user exists
    message = "If the email exists, a password reset link has been sent"

    if user and settings.emails_enabled:
        reset_token = SecurityManager.generate_password_reset_token(user.email)
        background_tasks.add_task(
            EmailService.send_password_reset_email,
            user.email,
            user.name,
            reset_token
        )

    return {"message": message}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token
    """
    # Validate passwords match
    reset_data.validate_passwords_match()

    # Verify token
    email = SecurityManager.verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Validate new password
    is_valid, error_msg = validate_password(reset_data.new_password)
    if not is_valid:
        raise InvalidPasswordException(error_msg)

    # Update password
    user = db.exec(select(User).where(User.email == email)).first()
    if user:
        user.hashed_password = SecurityManager.get_password_hash(
            reset_data.new_password
        )
        db.commit()

    return {"message": "Password successfully reset"}


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify email address with token
    """
    # In a real implementation, you would:
    # 1. Decode the verification token
    # 2. Get the user email from the token
    # 3. Update the user's email_verified status

    return {"message": "Email successfully verified"}


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_two_factor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set up two-factor authentication
    """
    # Generate secret
    secret = TwoFactorAuth.generate_secret()

    # Generate QR code
    qr_code_uri = TwoFactorAuth.generate_qr_code(current_user.email, secret)

    # Generate backup codes
    backup_codes = TwoFactorAuth.generate_backup_codes()

    # Store secret (temporarily - should be confirmed first)
    current_user.two_factor_secret = secret
    db.commit()

    return TwoFactorSetupResponse(
        secret=secret,
        qr_code_uri=qr_code_uri,
        backup_codes=backup_codes
    )


@router.post("/2fa/verify")
async def verify_two_factor(
    verification_data: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify and enable two-factor authentication
    """
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication not set up"
        )

    if not TwoFactorAuth.verify_token(
        current_user.two_factor_secret,
        verification_data.code
    ):
        raise InvalidTwoFactorCodeException()

    # Enable 2FA
    current_user.two_factor_enabled = True
    db.commit()

    return {"message": "Two-factor authentication enabled"}


@router.post("/2fa/disable")
async def disable_two_factor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable two-factor authentication
    """
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    db.commit()

    return {"message": "Two-factor authentication disabled"}
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.api.deps import get_db, get_current_user, get_current_admin_user, PaginationParams
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserPasswordChange, UserStatistics
from app.core.security import SecurityManager, validate_password
from app.core.exceptions import UserNotFoundException, InvalidPasswordException

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    """
    # Update user fields
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    if user_update.company is not None:
        current_user.company = user_update.company
    if user_update.location is not None:
        current_user.location = user_update.location
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/change-password")
async def change_password(
    password_data: UserPasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user password
    """
    # Validate passwords match
    password_data.validate_passwords_match()

    # Verify current password
    if not SecurityManager.verify_password(
        password_data.current_password,
        current_user.hashed_password
    ):
        raise InvalidPasswordException("Current password is incorrect")

    # Validate new password
    is_valid, error_msg = validate_password(password_data.new_password)
    if not is_valid:
        raise InvalidPasswordException(error_msg)

    # Update password
    current_user.hashed_password = SecurityManager.get_password_hash(
        password_data.new_password
    )
    db.commit()

    return {"message": "Password changed successfully"}


@router.get("/me/statistics", response_model=UserStatistics)
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user statistics
    """
    # In a real implementation, you would calculate these from the database
    return UserStatistics(
        total_files=len(current_user.files) if current_user.files else 0,
        storage_used=current_user.storage_used,
    )


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account
    """
    db.delete(current_user)
    db.commit()
    return {"message": "User account deleted successfully"}


# Admin endpoints
@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    pagination: PaginationParams = Depends(),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only)
    """
    users = db.exec(
        select(User)
        .offset(pagination.offset)
        .limit(pagination.limit)
    ).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (admin only)
    """
    user = db.get(User, user_id)
    if not user:
        raise UserNotFoundException(user_id)
    return user


@router.patch("/{user_id}/activate")
async def activate_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Activate user account (admin only)
    """
    user = db.get(User, user_id)
    if not user:
        raise UserNotFoundException(user_id)

    user.is_active = True
    db.commit()
    return {"message": "User activated successfully"}


@router.patch("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate user account (admin only)
    """
    user = db.get(User, user_id)
    if not user:
        raise UserNotFoundException(user_id)

    user.is_active = False
    db.commit()
    return {"message": "User deactivated successfully"}
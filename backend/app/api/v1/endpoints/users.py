from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.core.security import hash_password, verify_password
from app.models.organization import User, Organization

router = APIRouter()


class UserProfileUpdate:
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordUpdate:
    current_password: str
    new_password: str


class UserPreferencesUpdate:
    email_notifications: Optional[bool] = None
    theme: Optional[str] = None
    timezone: Optional[str] = None


@router.get("/me")
async def get_user_profile(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    org = await db.get(Organization, user.org_id)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "org_id": user.org_id,
        "org_name": org.name if org else None,
        "org_slug": org.slug if org else None,
        "created_at": user.created_at,
    }


@router.put("/me")
async def update_user_profile(
    name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if name is not None:
        user.name = name
    if avatar_url is not None:
        user.avatar_url = avatar_url
    await db.commit()
    await db.refresh(user)
    return {"message": "Profile updated"}


@router.post("/me/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = hash_password(new_password)
    await db.commit()
    return {"message": "Password changed"}


@router.get("/me/preferences")
async def get_preferences(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return {
        "email_notifications": True,
        "theme": "dark",
        "timezone": "UTC",
    }


@router.put("/me/preferences")
async def update_preferences(
    email_notifications: Optional[bool] = None,
    theme: Optional[str] = None,
    timezone: Optional[str] = None,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return {
        "message": "Preferences updated",
        "email_notifications": email_notifications,
        "theme": theme,
        "timezone": timezone,
    }

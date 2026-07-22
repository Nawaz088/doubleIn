from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.organization import Organization, User, OrgMembership
from app.schemas.auth import OrgSettingsResponse, OrgSettingsUpdate

router = APIRouter()


@router.get("/settings", response_model=OrgSettingsResponse)
async def get_org_settings(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    org = await db.get(Organization, user.org_id)
    return org


@router.put("/settings", response_model=OrgSettingsResponse)
async def update_org_settings(
    req: OrgSettingsUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    org = await db.get(Organization, user.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if req.name is not None:
        org.name = req.name
    if req.slug is not None:
        existing = await db.execute(select(Organization).where(Organization.slug == req.slug, Organization.id != org.id))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Slug already taken")
        org.slug = req.slug

    await db.commit()
    await db.refresh(org)
    return org


@router.get("/members")
async def list_members(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    result = await db.execute(
        select(OrgMembership, User)
        .join(User, User.id == OrgMembership.user_id)
        .where(OrgMembership.org_id == user.org_id)
    )
    members = []
    for membership, u in result:
        members.append({
            "id": membership.id,
            "user_id": u.id,
            "email": u.email,
            "name": u.name,
            "role": membership.role,
            "avatar_url": u.avatar_url,
            "is_active": u.is_active,
            "created_at": membership.created_at,
        })
    return members


@router.post("/members/invite", status_code=201)
async def invite_member(
    email: str,
    role: str = "member",
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    existing = await db.execute(select(User).where(User.email == email))
    existing_user = existing.scalar_one_or_none()
    if existing_user:
        existing_membership = await db.execute(
            select(OrgMembership).where(
                OrgMembership.org_id == user.org_id,
                OrgMembership.user_id == existing_user.id,
            )
        )
        if existing_membership.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already a member")
    return {"message": f"Invite sent to {email}", "email": email, "role": role}


@router.put("/members/{member_id}")
async def update_member(
    member_id: str,
    role: str,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    membership = await db.get(OrgMembership, member_id)
    if not membership or membership.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Membership not found")
    membership.role = role
    await db.commit()
    return {"message": "Role updated", "role": role}


@router.delete("/members/{member_id}", status_code=204)
async def remove_member(
    member_id: str,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    membership = await db.get(OrgMembership, member_id)
    if not membership or membership.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Membership not found")
    if membership.user_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")
    await db.delete(membership)
    await db.commit()

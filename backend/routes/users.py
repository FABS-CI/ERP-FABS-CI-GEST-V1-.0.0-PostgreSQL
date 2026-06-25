"""
User Routes - CRUD endpoints for user (Service-integrated)
GET, POST, PUT, DELETE operations with authentication
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from services.user_service import UserService
from db.base import get_session

router = APIRouter()

@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new user with hashed password"""
    try:
        service = UserService(session)
        user = await service.create_user(user_in.dict())
        return user
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Get user by ID"""
    try:
        service = UserService(session)
        user = await service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    """List all users with pagination"""
    try:
        service = UserService(session)
        users = await service.list_users(skip=skip, limit=limit)
        return {"items": users, "total": len(users), "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing users: {str(e)}")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update user"""
    try:
        service = UserService(session)
        user = await service.update_user(user_id, user_in.dict(exclude_unset=True))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Delete user (soft delete)"""
    try:
        service = UserService(session)
        await service.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

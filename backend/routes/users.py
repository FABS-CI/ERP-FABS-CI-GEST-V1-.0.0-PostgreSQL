"""User Routes - CRUD with Repository DI"""
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from db.base import get_session
from db.repositories import UserRepository
from db.dependencies import get_user_repo

router = APIRouter()

@router.post("", response_model=UserResponse, status_code=201)
async def create_user(user_in: UserCreate, session: AsyncSession = Depends(get_session), user_repo: UserRepository = Depends(get_user_repo)):
    try:
        result = await user_repo.create(user_in.dict())
        await session.commit()
        return result
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: UUID, session: AsyncSession = Depends(get_session), user_repo: UserRepository = Depends(get_user_repo)):
    try:
        user = await user_repo.read(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("", response_model=UserListResponse)
async def list_users(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: AsyncSession = Depends(get_session), user_repo: UserRepository = Depends(get_user_repo)):
    try:
        items, total = await user_repo.list(skip=skip, limit=limit)
        return {"items": items, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, user_in: UserUpdate, session: AsyncSession = Depends(get_session), user_repo: UserRepository = Depends(get_user_repo)):
    try:
        user = await user_repo.update(user_id, user_in.dict(exclude_unset=True))
        if not user:
            raise HTTPException(status_code=404, detail="Not found")
        await session.commit()
        return user
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: UUID, session: AsyncSession = Depends(get_session), user_repo: UserRepository = Depends(get_user_repo)):
    try:
        await user_repo.delete(user_id)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

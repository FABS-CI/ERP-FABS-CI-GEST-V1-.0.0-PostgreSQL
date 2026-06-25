"""
Client Routes - CRUD endpoints with Repository Dependency Injection
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.client import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse
from db.base import get_session
from db.repositories import ClientRepository
from db.dependencies import get_client_repo

router = APIRouter()

@router.post("", response_model=ClientResponse, status_code=201)
async def create_client(
    client_in: ClientCreate,
    session: AsyncSession = Depends(get_session),
    client_repo: ClientRepository = Depends(get_client_repo)
):
    """Create a new client"""
    try:
        result = await client_repo.create(client_in.dict())
        await session.commit()
        return result
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating client: {str(e)}")

@router.get("/{client_id}", response_model=ClientResponse)
async def read_client(
    client_id: UUID,
    session: AsyncSession = Depends(get_session),
    client_repo: ClientRepository = Depends(get_client_repo)
):
    """Get client by ID"""
    try:
        client = await client_repo.read(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("", response_model=ClientListResponse)
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    client_repo: ClientRepository = Depends(get_client_repo)
):
    """List all clients"""
    try:
        items, total = await client_repo.list(skip=skip, limit=limit)
        return {"items": items, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_in: ClientUpdate,
    session: AsyncSession = Depends(get_session),
    client_repo: ClientRepository = Depends(get_client_repo)
):
    """Update client"""
    try:
        client = await client_repo.update(client_id, client_in.dict(exclude_unset=True))
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        await session.commit()
        return client
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: UUID,
    session: AsyncSession = Depends(get_session),
    client_repo: ClientRepository = Depends(get_client_repo)
):
    """Delete client"""
    try:
        await client_repo.delete(client_id)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

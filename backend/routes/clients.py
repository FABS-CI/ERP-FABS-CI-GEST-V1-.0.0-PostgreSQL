"""
Client Routes - CRUD endpoints for client (Service-integrated)
GET, POST, PUT, DELETE operations with business logic
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.client import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse
from services.client_service import ClientService
from db.base import get_session

router = APIRouter()

@router.post("", response_model=ClientResponse, status_code=201)
async def create_client(
    client_in: ClientCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new client with validation"""
    try:
        service = ClientService(session)
        client = await service.create_client(client_in.dict())
        return client
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating client: {str(e)}")

@router.get("/{client_id}", response_model=ClientResponse)
async def read_client(
    client_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Get client by ID"""
    try:
        service = ClientService(session)
        client = await service.get_client(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching client: {str(e)}")

@router.get("", response_model=ClientListResponse)
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    """List all clients with pagination"""
    try:
        service = ClientService(session)
        clients = await service.list_clients(skip=skip, limit=limit)
        return {"items": clients, "total": len(clients), "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing clients: {str(e)}")

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_in: ClientUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update client"""
    try:
        service = ClientService(session)
        client = await service.update_client(client_id, client_in.dict(exclude_unset=True))
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating client: {str(e)}")

@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Delete client (soft delete)"""
    try:
        service = ClientService(session)
        await service.delete_client(client_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting client: {str(e)}")

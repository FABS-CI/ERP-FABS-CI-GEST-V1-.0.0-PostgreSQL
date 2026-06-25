"""
Order Routes - CRUD endpoints for order (Service-integrated)
GET, POST, PUT, DELETE operations with business logic
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderListResponse
from services.order_service import OrderService
from db.base import get_session

router = APIRouter()

@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    order_in: OrderCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new order with business logic"""
    try:
        service = OrderService(session)
        order = await service.create_order({
            "client_id": str(order_in.client_id),
            "numero_commande": order_in.numero_commande,
            "montant_ht": order_in.montant_ht,
            "montant_tva": order_in.montant_tva,
            "montant_ttc": order_in.montant_ttc,
        })
        return order
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating order: {str(e)}")

@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Get order by ID"""
    try:
        service = OrderService(session)
        order = await service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order: {str(e)}")

@router.get("", response_model=OrderListResponse)
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    """List all orders with pagination"""
    try:
        service = OrderService(session)
        orders = await service.list_orders(skip=skip, limit=limit)
        total = len(orders)
        return {"items": orders, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing orders: {str(e)}")

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    order_in: OrderUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update order"""
    try:
        service = OrderService(session)
        order = await service.update_order(order_id, order_in.dict(exclude_unset=True))
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating order: {str(e)}")

@router.delete("/{order_id}", status_code=204)
async def delete_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Delete order (soft delete)"""
    try:
        service = OrderService(session)
        await service.delete_order(order_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting order: {str(e)}")

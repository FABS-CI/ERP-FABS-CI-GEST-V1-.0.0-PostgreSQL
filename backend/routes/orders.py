"""Order Routes - CRUD with Repository DI"""
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderListResponse
from db.base import get_session
from db.repositories import OrderRepository, ClientRepository, ProductRepository
from db.dependencies import get_order_repo, get_client_repo, get_product_repo

router = APIRouter()

@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(order_in: OrderCreate, session: AsyncSession = Depends(get_session), order_repo: OrderRepository = Depends(get_order_repo), client_repo: ClientRepository = Depends(get_client_repo), product_repo: ProductRepository = Depends(get_product_repo)):
    try:
        result = await order_repo.create(order_in.dict())
        await session.commit()
        return result
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(order_id: UUID, session: AsyncSession = Depends(get_session), order_repo: OrderRepository = Depends(get_order_repo), client_repo: ClientRepository = Depends(get_client_repo), product_repo: ProductRepository = Depends(get_product_repo)):
    try:
        order = await order_repo.read(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("", response_model=OrderListResponse)
async def list_orders(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: AsyncSession = Depends(get_session), order_repo: OrderRepository = Depends(get_order_repo), client_repo: ClientRepository = Depends(get_client_repo), product_repo: ProductRepository = Depends(get_product_repo)):
    try:
        items, total = await order_repo.list(skip=skip, limit=limit)
        return {"items": items, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(order_id: UUID, order_in: OrderUpdate, session: AsyncSession = Depends(get_session), order_repo: OrderRepository = Depends(get_order_repo), client_repo: ClientRepository = Depends(get_client_repo), product_repo: ProductRepository = Depends(get_product_repo)):
    try:
        order = await order_repo.update(order_id, order_in.dict(exclude_unset=True))
        if not order:
            raise HTTPException(status_code=404, detail="Not found")
        await session.commit()
        return order
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/{order_id}", status_code=204)
async def delete_order(order_id: UUID, session: AsyncSession = Depends(get_session), order_repo: OrderRepository = Depends(get_order_repo), client_repo: ClientRepository = Depends(get_client_repo), product_repo: ProductRepository = Depends(get_product_repo)):
    try:
        await order_repo.delete(order_id)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

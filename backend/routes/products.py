"""Product Routes - CRUD with Repository DI"""
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from db.base import get_session
from db.repositories import ProductRepository
from db.dependencies import get_product_repo

router = APIRouter()

@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(product_in: ProductCreate, session: AsyncSession = Depends(get_session), product_repo: ProductRepository = Depends(get_product_repo)):
    try:
        result = await product_repo.create(product_in.dict())
        await session.commit()
        return result
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(product_id: UUID, session: AsyncSession = Depends(get_session), product_repo: ProductRepository = Depends(get_product_repo)):
    try:
        product = await product_repo.read(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("", response_model=ProductListResponse)
async def list_products(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: AsyncSession = Depends(get_session), product_repo: ProductRepository = Depends(get_product_repo)):
    try:
        items, total = await product_repo.list(skip=skip, limit=limit)
        return {"items": items, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: UUID, product_in: ProductUpdate, session: AsyncSession = Depends(get_session), product_repo: ProductRepository = Depends(get_product_repo)):
    try:
        product = await product_repo.update(product_id, product_in.dict(exclude_unset=True))
        if not product:
            raise HTTPException(status_code=404, detail="Not found")
        await session.commit()
        return product
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: UUID, session: AsyncSession = Depends(get_session), product_repo: ProductRepository = Depends(get_product_repo)):
    try:
        await product_repo.delete(product_id)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

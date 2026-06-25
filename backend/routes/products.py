"""
Product Routes - CRUD endpoints for product (Service-integrated)
GET, POST, PUT, DELETE operations with business logic
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from services.product_service import ProductService
from db.base import get_session

router = APIRouter()

@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    product_in: ProductCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new product"""
    try:
        service = ProductService(session)
        product = await service.create_product(product_in.dict())
        return product
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating product: {str(e)}")

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Get product by ID"""
    try:
        service = ProductService(session)
        product = await service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching product: {str(e)}")

@router.get("", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    """List all products with pagination"""
    try:
        service = ProductService(session)
        products = await service.list_products(skip=skip, limit=limit)
        return {"items": products, "total": len(products), "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing products: {str(e)}")

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_in: ProductUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update product"""
    try:
        service = ProductService(session)
        product = await service.update_product(product_id, product_in.dict(exclude_unset=True))
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")

@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Delete product (soft delete)"""
    try:
        service = ProductService(session)
        await service.delete_product(product_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")

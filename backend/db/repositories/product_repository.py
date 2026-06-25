"""
Product Repository
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories.base_repository import BaseRepository
from db.models.product import Product, ProductStatus


class ProductRepository(BaseRepository[Product]):
    """Product repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)
    
    async def find_by_code(self, code_produit: str) -> Optional[Product]:
        """Find product by code"""
        return await self.read_one_by(code_produit=code_produit, is_deleted=False)
    
    async def find_active_products(self, skip: int = 0, limit: int = 100) -> tuple[List[Product], int]:
        """Get active products"""
        query = select(self.model).where(
            and_(
                self.model.is_deleted == False,
                self.model.status == ProductStatus.active
            )
        ).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        products = result.scalars().all()
        total = await self.count(is_deleted=False, status=ProductStatus.active)
        return products, total
    
    async def find_by_category(self, categorie: str) -> List[Product]:
        """Find products by category"""
        return await self.read_by(categorie=categorie, is_deleted=False)
    
    async def find_low_stock(self, depot_id: UUID) -> List:
        """Find products with low stock in depot"""
        from sqlalchemy import func
        from db.models.product import Stock
        
        query = select(self.model).join(
            Stock, self.model.id == Stock.product_id
        ).where(
            and_(
                Stock.depot_id == depot_id,
                Stock.quantite_actuelle <= self.model.stock_minimum
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def find_by_brand(self, marque: str) -> List[Product]:
        """Find products by brand"""
        return await self.read_by(marque=marque, is_deleted=False)

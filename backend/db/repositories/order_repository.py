"""
Order Repository
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories.base_repository import BaseRepository
from db.models.order import Order, OrderStatus


class OrderRepository(BaseRepository[Order]):
    """Order repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Order)
    
    async def find_by_number(self, numero_commande: str) -> Optional[Order]:
        """Find order by number"""
        return await self.read_one_by(numero_commande=numero_commande, is_deleted=False)
    
    async def find_by_client(self, client_id: UUID, skip: int = 0, limit: int = 100) -> tuple[List[Order], int]:
        """Get all orders for a client"""
        query = select(self.model).where(
            and_(
                self.model.client_id == client_id,
                self.model.is_deleted == False
            )
        ).order_by(self.model.date_commande.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        orders = result.scalars().all()
        total = await self.count(client_id=client_id, is_deleted=False)
        return orders, total
    
    async def find_by_status(self, status: OrderStatus) -> List[Order]:
        """Find orders by status"""
        return await self.read_by(status=status, is_deleted=False)
    
    async def find_pending_orders(self) -> List[Order]:
        """Find orders awaiting processing"""
        query = select(self.model).where(
            and_(
                self.model.is_deleted == False,
                self.model.status.in_([OrderStatus.draft, OrderStatus.sent, OrderStatus.confirmed])
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def find_shipped_orders(self) -> List[Order]:
        """Find shipped but not delivered orders"""
        query = select(self.model).where(
            and_(
                self.model.is_deleted == False,
                self.model.status == OrderStatus.shipped
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

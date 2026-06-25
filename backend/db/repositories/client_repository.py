"""
Client Repository - CRUD + custom queries for clients
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories.base_repository import BaseRepository
from db.models.client import Client, ClientStatus


class ClientRepository(BaseRepository[Client]):
    """Client repository with custom business queries"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Client)
    
    async def find_by_code(self, code_client: str) -> Optional[Client]:
        """Find client by code"""
        return await self.read_one_by(code_client=code_client, is_deleted=False)
    
    async def find_by_email(self, email: str) -> Optional[Client]:
        """Find client by email"""
        return await self.read_one_by(email=email, is_deleted=False)
    
    async def find_active_clients(self, skip: int = 0, limit: int = 100) -> tuple[List[Client], int]:
        """Get active clients only"""
        query = select(self.model).where(
            and_(
                self.model.is_deleted == False,
                self.model.status == ClientStatus.active
            )
        ).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        clients = result.scalars().all()
        
        # Get total
        total = await self.count(is_deleted=False, status=ClientStatus.active)
        return clients, total
    
    async def find_by_status(self, status: ClientStatus) -> List[Client]:
        """Find all clients with specific status"""
        return await self.read_by(status=status, is_deleted=False)
    
    async def find_by_city(self, ville: str) -> List[Client]:
        """Find clients by city"""
        return await self.read_by(ville=ville, is_deleted=False)
    
    async def find_by_sector(self, secteur: str) -> List[Client]:
        """Find clients by business sector"""
        return await self.read_by(secteur_activite=secteur, is_deleted=False)
    
    async def get_clients_with_overdue_credit(self, days: int = 30) -> List[Client]:
        """Get clients with credit issues (high utilization)"""
        from sqlalchemy import func
        query = select(self.model).where(
            and_(
                self.model.is_deleted == False,
                self.model.credit_utilise > (self.model.credit_limit * 0.8)  # > 80% utilization
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_credit_used(self, client_id: UUID, amount: float) -> Optional[Client]:
        """Update credit used amount"""
        client = await self.read(client_id)
        if not client:
            return None
        
        current = float(client.credit_utilise or 0)
        updated = await self.update(client_id, {"credit_utilise": current + amount})
        return updated

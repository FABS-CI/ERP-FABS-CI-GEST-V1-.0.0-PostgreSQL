"""
User Repository - Database operations for User entity
Implements CRUD + custom queries for users
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories.base_repository import BaseRepository
from db.models.user import User


class UserRepository(BaseRepository[User]):
    """
    User repository - CRUD operations + custom queries
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        return await self.read_one_by(email=email, is_deleted=False)
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        return await self.read_one_by(username=username, is_deleted=False)
    
    async def find_active_users(self, skip: int = 0, limit: int = 100) -> tuple[List[User], int]:
        """Get all active users with pagination"""
        query = select(self.model).where(
            (self.model.is_deleted == False) & 
            (self.model.actif == True)
        ).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        users = result.scalars().all()
        
        # Count total
        count_query = select(self.model).where(
            (self.model.is_deleted == False) & 
            (self.model.actif == True)
        )
        count_result = await self.session.execute(count_query)
        total = len(count_result.scalars().all())
        
        return users, total
    
    async def find_by_role(self, role: str) -> List[User]:
        """Find all users with specific role"""
        return await self.read_by(role=role, is_deleted=False)
    
    async def admin_count(self) -> int:
        """Count admin users"""
        return await self.count(role="admin", is_deleted=False)
    
    async def deactivate_user(self, user_id: UUID) -> Optional[User]:
        """Deactivate user (soft disable)"""
        return await self.update(user_id, {"actif": False})
    
    async def reactivate_user(self, user_id: UUID) -> Optional[User]:
        """Reactivate user"""
        return await self.update(user_id, {"actif": True})

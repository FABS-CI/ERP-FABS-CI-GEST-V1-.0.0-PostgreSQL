"""
Employee Repository
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories.base_repository import BaseRepository
from db.models.hr import Employee, EmployeeStatus


class EmployeeRepository(BaseRepository[Employee]):
    """Employee repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Employee)
    
    async def find_by_code(self, code_employe: str) -> Optional[Employee]:
        """Find employee by code"""
        return await self.read_one_by(code_employe=code_employe, is_deleted=False)
    
    async def find_by_department(self, departement_id: UUID) -> List[Employee]:
        """Find all employees in department"""
        return await self.read_by(departement_id=departement_id, is_deleted=False)
    
    async def find_by_status(self, status: EmployeeStatus) -> List[Employee]:
        """Find employees by status"""
        return await self.read_by(statut=status, is_deleted=False)
    
    async def find_active_employees(self, skip: int = 0, limit: int = 100) -> tuple[List[Employee], int]:
        """Get active employees"""
        query = select(self.model).where(
            and_(
                self.model.is_deleted == False,
                self.model.statut == EmployeeStatus.active
            )
        ).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        employees = result.scalars().all()
        total = await self.count(is_deleted=False, statut=EmployeeStatus.active)
        return employees, total
    
    async def find_by_function(self, fonction_id: UUID) -> List[Employee]:
        """Find employees by function/position"""
        return await self.read_by(fonction_id=fonction_id, is_deleted=False)
    
    async def find_by_user(self, user_id: UUID) -> Optional[Employee]:
        """Find employee by user ID"""
        return await self.read_one_by(user_id=user_id, is_deleted=False)

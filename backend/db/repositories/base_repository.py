"""
Base Repository - Abstract interface for all database operations
Repository Pattern for consistent CRUD operations
"""

from typing import TypeVar, Generic, Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

DeclarativeBase = declarative_base().__class__
T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Abstract repository providing CRUD operations for any SQLAlchemy model.
    All repositories inherit from this to ensure consistent DB interface.
    """

    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def create(self, obj_in: Dict[str, Any]) -> T:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def read(self, id: UUID) -> Optional[T]:
        """Read a single record by ID"""
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def read_by(self, **filters) -> List[T]:
        """Read records matching filters"""
        query = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def read_one_by(self, **filters) -> Optional[T]:
        """Read single record matching filters"""
        query = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list(self, skip: int = 0, limit: int = 100, **filters) -> tuple[List[T], int]:
        """List records with pagination and filters"""
        query = select(self.model)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        # Count total before pagination
        count_result = await self.session.execute(select(func.count()).select_from(self.model))
        total = count_result.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all(), total

    async def update(self, id: UUID, obj_in: Dict[str, Any]) -> T:
        """Update a record"""
        query = update(self.model).where(self.model.id == id).values(**obj_in).returning(self.model)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.scalars().first()

    async def delete(self, id: UUID) -> bool:
        """Soft delete (set is_deleted=True if available, otherwise hard delete)"""
        obj = await self.read(id)
        if not obj:
            return False
        
        # Soft delete if model has is_deleted field
        if hasattr(self.model, 'is_deleted'):
            obj.is_deleted = True
            await self.session.flush()
        else:
            # Hard delete
            await self.session.delete(obj)
            await self.session.flush()
        
        return True

    async def hard_delete(self, id: UUID) -> bool:
        """Hard delete (remove permanently)"""
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0

    async def count(self, **filters) -> int:
        """Count records matching filters"""
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar()

    async def exists(self, **filters) -> bool:
        """Check if record exists"""
        count = await self.count(**filters)
        return count > 0

    async def commit(self):
        """Commit transaction"""
        await self.session.commit()

    async def rollback(self):
        """Rollback transaction"""
        await self.session.rollback()

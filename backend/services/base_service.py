"""
Base Service — Abstract service class with common methods
"""

import logging
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import BaseRepository

logger = logging.getLogger(__name__)


class ServiceException(Exception):
    """Custom exception for service layer"""
    pass


class BaseService:
    """Abstract service providing common operations"""

    def __init__(self, session: AsyncSession, repository: BaseRepository):
        """
        Initialize service
        
        Args:
            session: Async SQLAlchemy session
            repository: Repository instance for DB operations
        """
        self.session = session
        self.repo = repository
        self.logger = logger

    async def validate_exists(self, entity_id: UUID, entity_name: str) -> bool:
        """
        Validate that entity exists
        
        Args:
            entity_id: UUID of entity
            entity_name: Name for error message (e.g., "User", "Client")
            
        Returns:
            True if exists
            
        Raises:
            ServiceException if not found
        """
        entity = await self.repo.read(entity_id)
        if not entity:
            raise ServiceException(f"{entity_name} not found: {entity_id}")
        return True

    async def validate_unique(self, field: str, value: str, entity_name: str) -> bool:
        """
        Validate that field is unique
        
        Args:
            field: Column name (e.g., "email", "code_client")
            value: Value to check
            entity_name: Name for error message
            
        Returns:
            True if unique (not found)
            
        Raises:
            ServiceException if already exists
        """
        filters = {field: value}
        existing = await self.repo.read_one_by(**filters)
        if existing:
            raise ServiceException(f"{entity_name} with {field}={value} already exists")
        return True

    def log_operation(self, operation: str, entity_id: UUID, details: dict = None):
        """
        Log service operation
        
        Args:
            operation: Operation name (e.g., "create_order")
            entity_id: Entity UUID
            details: Additional details dict
        """
        msg = f"[{operation}] {entity_id}"
        if details:
            msg += f" | {details}"
        self.logger.info(msg)

    async def begin_transaction(self):
        """
        Begin database transaction
        
        Returns:
            Transaction context
        """
        return self.session.begin()

    async def commit_transaction(self):
        """Commit current transaction"""
        await self.session.commit()

    async def rollback_transaction(self):
        """Rollback current transaction"""
        await self.session.rollback()

    def validate_numeric(self, value, min_val=0, max_val=None, field_name="value"):
        """
        Validate numeric value
        
        Args:
            value: Value to validate
            min_val: Minimum value (default 0)
            max_val: Maximum value (optional)
            field_name: Field name for error message
            
        Raises:
            ServiceException if invalid
        """
        try:
            num = float(value)
            if num < min_val:
                raise ServiceException(f"{field_name} must be >= {min_val}")
            if max_val and num > max_val:
                raise ServiceException(f"{field_name} must be <= {max_val}")
        except (TypeError, ValueError):
            raise ServiceException(f"{field_name} must be numeric")

    def validate_enum(self, value, allowed_values, field_name="value"):
        """
        Validate enum value
        
        Args:
            value: Value to validate
            allowed_values: List of allowed values
            field_name: Field name for error message
            
        Raises:
            ServiceException if invalid
        """
        if value not in allowed_values:
            raise ServiceException(f"{field_name} must be one of: {allowed_values}")

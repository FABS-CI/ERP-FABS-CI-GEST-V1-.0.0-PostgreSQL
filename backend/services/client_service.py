"""
Client Service — Client validations, credit limits, business rules
"""

from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import ClientRepository
from .base_service import BaseService, ServiceException


class ClientService(BaseService):
    """Service for client operations"""

    def __init__(self, session: AsyncSession, client_repo: ClientRepository):
        super().__init__(session, client_repo)
        self.client_repo = client_repo

    async def validate_client_can_order(self, client_id: UUID) -> bool:
        """
        Validate that client can place orders
        
        Args:
            client_id: Client UUID
            
        Returns:
            True if client can order
            
        Raises:
            ServiceException if invalid state
        """
        # Validate client exists
        client = await self.client_repo.read(client_id)
        if not client:
            raise ServiceException(f"Client not found: {client_id}")

        # Check status
        if client.status != "active":
            raise ServiceException(
                f"Client cannot order. Status: {client.status}. Only 'active' clients can order."
            )

        # TODO: Add more validations as needed
        # - Check if client is in credit suspension
        # - Check if client has overdue invoices beyond threshold
        # - Check if client is on blacklist

        return True

    async def get_client_credit_info(self, client_id: UUID) -> dict:
        """
        Get client credit information
        
        Args:
            client_id: Client UUID
            
        Returns:
            Dict with credit details
            
        Raises:
            ServiceException if not found
        """
        client = await self.client_repo.read(client_id)
        if not client:
            raise ServiceException(f"Client not found: {client_id}")

        credit_limit = Decimal(str(client.credit_limit or 0))
        credit_used = Decimal(str(client.credit_utilise or 0))
        credit_available = credit_limit - credit_used

        return {
            "client_id": client_id,
            "code_client": client.code_client,
            "nom_client": client.nom_client,
            "credit_limit": credit_limit,
            "credit_used": credit_used,
            "credit_available": credit_available,
            "credit_percentage_used": float(credit_used / credit_limit * 100) if credit_limit > 0 else 0
        }

    async def update_credit_limit(self, client_id: UUID, new_limit: Decimal) -> dict:
        """
        Update client credit limit
        
        Args:
            client_id: Client UUID
            new_limit: New credit limit amount
            
        Returns:
            Updated credit info
            
        Raises:
            ServiceException if invalid
        """
        # Validate client exists
        await self.validate_exists(client_id, "Client")

        # Validate new limit
        new_limit = Decimal(str(new_limit))
        if new_limit < 0:
            raise ServiceException("Credit limit cannot be negative")

        # Update client
        await self.client_repo.update(client_id, {
            "credit_limit": new_limit
        })

        await self.session.flush()

        self.log_operation(
            "update_credit_limit",
            client_id,
            {"new_limit": str(new_limit)}
        )

        # Return updated credit info
        return await self.get_client_credit_info(client_id)

    async def validate_email_unique(self, email: str, exclude_client_id: UUID = None) -> bool:
        """
        Validate email is unique (excluding given client)
        
        Args:
            email: Email to check
            exclude_client_id: Client ID to exclude from check (for updates)
            
        Returns:
            True if unique
            
        Raises:
            ServiceException if duplicate
        """
        existing = await self.client_repo.read_one_by(email=email)
        
        if existing and (not exclude_client_id or existing.id != exclude_client_id):
            raise ServiceException(f"Email already in use: {email}")
        
        return True

    async def get_client_status_options(self) -> list:
        """
        Get available client status options
        
        Returns:
            List of valid status values
        """
        return ["active", "inactive", "prospective", "suspended", "discontinued"]

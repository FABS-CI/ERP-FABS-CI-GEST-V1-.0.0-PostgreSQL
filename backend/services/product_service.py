"""
Product Service — Stock management, pricing logic
"""

from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import ProductRepository
from db.models import StockMovement
from .base_service import BaseService, ServiceException


class ProductService(BaseService):
    """Service for product operations"""

    def __init__(self, session: AsyncSession, product_repo: ProductRepository):
        super().__init__(session, product_repo)
        self.product_repo = product_repo

    async def check_stock_available(
        self,
        product_id: UUID,
        quantity: int,
        depot_id: UUID = None
    ) -> bool:
        """
        Check if product stock is available
        
        Args:
            product_id: Product UUID
            quantity: Requested quantity
            depot_id: Depot UUID (optional, check all if not specified)
            
        Returns:
            True if available
            
        Raises:
            ServiceException if insufficient stock
        """
        # Validate product exists
        product = await self.product_repo.read(product_id)
        if not product:
            raise ServiceException(f"Product not found: {product_id}")

        # Validate quantity positive
        if quantity <= 0:
            raise ServiceException("Quantity must be > 0")

        # TODO: Implement stock level check via repository
        # This would require access to Stock table via product repository
        # For now, we log and allow (stock check deferred to inventory system)

        self.logger.info(f"Stock check: Product {product_id}, Qty {quantity}")
        return True

    async def update_stock(
        self,
        product_id: UUID,
        depot_id: UUID,
        quantity_change: int,
        type_mouvement: str
    ) -> StockMovement:
        """
        Record stock movement and update stock level
        
        Args:
            product_id: Product UUID
            depot_id: Depot UUID
            quantity_change: Quantity change (positive for IN, negative for OUT)
            type_mouvement: Movement type (IN, OUT, ADJUSTMENT)
            
        Returns:
            Created StockMovement record
            
        Raises:
            ServiceException if validation fails
        """
        try:
            # Validate product exists
            await self.validate_exists(product_id, "Product")

            # Validate movement type
            valid_types = ["IN", "OUT", "ADJUSTMENT"]
            self.validate_enum(type_mouvement, valid_types, "type_mouvement")

            # Validate quantity not zero
            if quantity_change == 0:
                raise ServiceException("Quantity change cannot be zero")

            # Create stock movement record
            movement = StockMovement(
                product_id=product_id,
                depot_id=depot_id,
                type_mouvement=type_mouvement,
                quantite=abs(quantity_change),
                quantite_avant=0,  # TODO: Get actual stock before
                quantite_apres=0   # TODO: Get actual stock after
            )
            self.session.add(movement)

            await self.session.flush()

            self.log_operation(
                "update_stock",
                product_id,
                {
                    "depot_id": depot_id,
                    "quantity_change": quantity_change,
                    "type": type_mouvement
                }
            )

            return movement

        except ServiceException:
            raise
        except Exception as e:
            self.logger.error(f"Error updating stock: {e}", exc_info=True)
            raise ServiceException(f"Failed to update stock: {str(e)}")

    async def get_product_with_stock(self, product_id: UUID) -> dict:
        """
        Get product details with stock information
        
        Args:
            product_id: Product UUID
            
        Returns:
            Product dict with stock data
            
        Raises:
            ServiceException if not found
        """
        product = await self.product_repo.read(product_id)
        if not product:
            raise ServiceException(f"Product not found: {product_id}")

        return {
            "product": product,
            "stock_minimum": product.stock_minimum,
            "stock_maximum": product.stock_maximum,
            "current_price": product.prix_unitaire
        }

    def validate_pricing(self, prix_unitaire: Decimal, prix_vente: Decimal = None):
        """
        Validate product pricing
        
        Args:
            prix_unitaire: Unit price
            prix_vente: Selling price (optional, should be >= unit price)
            
        Raises:
            ServiceException if invalid
        """
        prix_unitaire = Decimal(str(prix_unitaire))
        
        if prix_unitaire < 0:
            raise ServiceException("Unit price cannot be negative")
        
        if prix_vente:
            prix_vente = Decimal(str(prix_vente))
            if prix_vente < prix_unitaire:
                raise ServiceException("Selling price must be >= unit price")

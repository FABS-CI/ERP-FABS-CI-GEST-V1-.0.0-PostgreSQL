"""
Order Service — Complex order operations, calculations, validations
"""

from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import OrderRepository, ClientRepository, ProductRepository
from db.models import Order, OrderStatus
from .base_service import BaseService, ServiceException


class OrderService(BaseService):
    """Service for order operations and complex business logic"""

    def __init__(self, session: AsyncSession, order_repo: OrderRepository, client_repo: ClientRepository, product_repo: ProductRepository):
        super().__init__(session, order_repo)
        self.order_repo = order_repo
        self.client_repo = client_repo
        self.product_repo = product_repo

    async def create_order(
        self,
        client_id: UUID,
        numero_commande: str,
        items: List[Dict[str, Any]],
        discount_percent: Decimal = Decimal("0"),
        conditions_paiement: str = None,
        notes: str = None
    ) -> Order:
        """
        Create order with automatic total calculations
        
        Args:
            client_id: Client UUID
            numero_commande: Order number
            items: List of {product_id, quantity, price_unitaire}
            discount_percent: Discount percentage (0-100)
            conditions_paiement: Payment conditions text
            notes: Order notes
            
        Returns:
            Created Order with calculated totals
            
        Raises:
            ServiceException if validation fails
        """
        try:
            # Validate client exists and can order
            await self.validate_exists(client_id, "Client")
            client = await self.client_repo.read(client_id)
            if client.status != "active":
                raise ServiceException(f"Client status is {client.status}, must be 'active'")

            # Validate items not empty
            if not items or len(items) == 0:
                raise ServiceException("Order must have at least one item")

            # Validate and calculate item totals
            item_total = Decimal("0")
            for item in items:
                product_id = item.get("product_id")
                quantity = Decimal(str(item.get("quantity", 0)))
                price = Decimal(str(item.get("price_unitaire", 0)))

                # Validate product exists
                product = await self.product_repo.read(product_id)
                if not product:
                    raise ServiceException(f"Product not found: {product_id}")

                # Validate quantity positive
                if quantity <= 0:
                    raise ServiceException(f"Product {product_id}: quantity must be > 0")

                # Validate price positive
                if price < 0:
                    raise ServiceException(f"Product {product_id}: price cannot be negative")

                item_total += quantity * price

            # Calculate totals
            totals = self.calculate_totals(item_total, discount_percent)

            # Check client credit available
            await self.check_credit_available(client_id, totals["montant_ttc"])

            # Create order
            order = await self.order_repo.create({
                "numero_commande": numero_commande,
                "client_id": client_id,
                "status": OrderStatus.draft.value,
                "montant_ht": totals["montant_ht"],
                "montant_tva": totals["montant_tva"],
                "montant_ttc": totals["montant_ttc"],
                "reduction_percent": discount_percent,
                "reduction_montant": totals["reduction_montant"],
                "conditions_paiement": conditions_paiement,
                "notes": notes
            })

            await self.session.flush()

            # Log operation
            self.log_operation(
                "create_order",
                order.id,
                {
                    "numero_commande": numero_commande,
                    "client_id": client_id,
                    "items_count": len(items),
                    "montant_ttc": str(totals["montant_ttc"])
                }
            )

            return order

        except ServiceException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating order: {e}", exc_info=True)
            raise ServiceException(f"Failed to create order: {str(e)}")

    def calculate_totals(
        self,
        montant_ht: Decimal,
        discount_percent: Decimal = Decimal("0"),
        tax_rate: Decimal = Decimal("0.18")
    ) -> Dict[str, Decimal]:
        """
        Calculate order totals with tax and discount
        
        Formula:
          Subtotal = montant_ht
          Discount = Subtotal × discount_percent / 100
          Taxable = Subtotal - Discount
          Tax = Taxable × tax_rate
          Total = Taxable + Tax
          
        Args:
            montant_ht: Base amount (HT = before tax)
            discount_percent: Discount percentage (0-100)
            tax_rate: Tax rate (default 18% for Côte d'Ivoire)
            
        Returns:
            Dict with montant_ht, discount, montant_tva, montant_ttc
        """
        # Validate inputs
        self.validate_numeric(montant_ht, min_val=0, field_name="montant_ht")
        self.validate_numeric(discount_percent, min_val=0, max_val=100, field_name="discount_percent")
        self.validate_numeric(tax_rate, min_val=0, max_val=1, field_name="tax_rate")

        montant_ht = Decimal(str(montant_ht))
        discount_percent = Decimal(str(discount_percent))
        tax_rate = Decimal(str(tax_rate))

        # Calculate discount amount
        reduction_montant = montant_ht * (discount_percent / 100)

        # Calculate taxable amount (after discount)
        taxable = montant_ht - reduction_montant

        # Calculate tax
        montant_tva = taxable * tax_rate

        # Calculate total
        montant_ttc = taxable + montant_tva

        return {
            "montant_ht": montant_ht.quantize(Decimal("0.01")),
            "reduction_montant": reduction_montant.quantize(Decimal("0.01")),
            "montant_tva": montant_tva.quantize(Decimal("0.01")),
            "montant_ttc": montant_ttc.quantize(Decimal("0.01")),
        }

    async def check_credit_available(self, client_id: UUID, requested_amount: Decimal):
        """
        Check if client has available credit for order
        
        Args:
            client_id: Client UUID
            requested_amount: Requested amount
            
        Raises:
            ServiceException if insufficient credit
        """
        client = await self.client_repo.read(client_id)
        if not client or not client.credit_limit:
            return  # No credit limit configured, allow order

        credit_limit = Decimal(str(client.credit_limit))
        credit_used = Decimal(str(client.credit_utilise or 0))
        available = credit_limit - credit_used

        requested_amount = Decimal(str(requested_amount))

        if requested_amount > available:
            raise ServiceException(
                f"Insufficient credit. Limit: {credit_limit}, Used: {credit_used}, "
                f"Available: {available}, Requested: {requested_amount}"
            )

    async def update_order_status(self, order_id: UUID, new_status: str) -> Order:
        """
        Update order status with validation
        
        Args:
            order_id: Order UUID
            new_status: New status value
            
        Returns:
            Updated Order
            
        Raises:
            ServiceException if invalid transition
        """
        # Validate order exists
        order = await self.order_repo.read(order_id)
        if not order:
            raise ServiceException(f"Order not found: {order_id}")

        # Validate new status
        valid_statuses = [s.value for s in OrderStatus]
        self.validate_enum(new_status, valid_statuses, "status")

        # Validate status transition
        current_status = order.status
        valid_transitions = {
            "draft": ["pending", "cancelled"],
            "pending": ["confirmed", "cancelled"],
            "confirmed": ["shipped", "cancelled"],
            "shipped": ["delivered"],
            "delivered": [],
            "cancelled": []
        }

        if current_status not in valid_transitions or new_status not in valid_transitions.get(current_status, []):
            raise ServiceException(
                f"Invalid status transition: {current_status} → {new_status}"
            )

        # Update order
        updated_order = await self.order_repo.update(order_id, {"status": new_status})
        await self.session.flush()

        self.log_operation(
            "update_order_status",
            order_id,
            {"old_status": current_status, "new_status": new_status}
        )

        return updated_order

    async def get_order_with_details(self, order_id: UUID) -> Dict[str, Any]:
        """
        Get order with client and product details
        
        Args:
            order_id: Order UUID
            
        Returns:
            Order dict with related data
            
        Raises:
            ServiceException if not found
        """
        order = await self.order_repo.read(order_id)
        if not order:
            raise ServiceException(f"Order not found: {order_id}")

        client = await self.client_repo.read(order.client_id)

        return {
            "order": order,
            "client": client,
            "totals": self.calculate_totals(order.montant_ht, order.reduction_percent)
        }

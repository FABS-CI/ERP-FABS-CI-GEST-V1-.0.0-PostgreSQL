"""
Invoice Service — Invoice generation, payment tracking, financial calculations
"""

from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import InvoiceRepository, OrderRepository, ClientRepository
from db.models import Invoice, InvoiceStatus, Payment, PaymentStatus
from .base_service import BaseService, ServiceException


class InvoiceService(BaseService):
    """Service for invoice operations"""

    def __init__(self, session: AsyncSession, invoice_repo: InvoiceRepository, order_repo: OrderRepository, client_repo: ClientRepository):
        super().__init__(session, invoice_repo)
        self.invoice_repo = invoice_repo
        self.order_repo = order_repo
        self.client_repo = client_repo

    async def create_invoice_from_order(self, order_id: UUID) -> Invoice:
        """
        Create invoice from order
        
        Args:
            order_id: Order UUID
            
        Returns:
            Created Invoice with generated number
            
        Raises:
            ServiceException if order not found or invalid
        """
        try:
            # Validate order exists
            order = await self.order_repo.read(order_id)
            if not order:
                raise ServiceException(f"Order not found: {order_id}")

            # Generate invoice number (simple sequence: INV-YYYYMMDD-XXXX)
            numero_facture = await self._generate_invoice_number()

            # Create invoice with same totals as order
            invoice = await self.invoice_repo.create({
                "numero_facture": numero_facture,
                "client_id": order.client_id,
                "reference_commande": order.numero_commande,
                "date_facture": datetime.utcnow(),
                "date_echeance": datetime.utcnow() + timedelta(days=30),  # 30 days payment terms
                "status": InvoiceStatus.draft.value,
                "montant_ht": order.montant_ht,
                "montant_tva": order.montant_tva,
                "montant_ttc": order.montant_ttc,
                "montant_paye": Decimal("0"),
                "montant_restant": order.montant_ttc
            })

            await self.session.flush()

            self.log_operation(
                "create_invoice_from_order",
                invoice.id,
                {
                    "numero_facture": numero_facture,
                    "order_id": order_id,
                    "montant_ttc": str(order.montant_ttc)
                }
            )

            return invoice

        except ServiceException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating invoice from order: {e}", exc_info=True)
            raise ServiceException(f"Failed to create invoice: {str(e)}")

    async def record_payment(
        self,
        invoice_id: UUID,
        amount: Decimal,
        payment_method: str
    ) -> Dict[str, Any]:
        """
        Record payment for invoice
        
        Args:
            invoice_id: Invoice UUID
            amount: Payment amount
            payment_method: Payment method (cash, card, transfer, etc.)
            
        Returns:
            Dict with payment info and updated invoice status
            
        Raises:
            ServiceException if validation fails
        """
        try:
            # Validate invoice exists
            invoice = await self.invoice_repo.read(invoice_id)
            if not invoice:
                raise ServiceException(f"Invoice not found: {invoice_id}")

            # Validate amount
            amount = Decimal(str(amount))
            if amount <= 0:
                raise ServiceException("Payment amount must be > 0")

            # Check if already fully paid
            montant_restant = Decimal(str(invoice.montant_restant or 0))
            if montant_restant <= 0:
                raise ServiceException(f"Invoice {invoice_id} is already fully paid")

            # Validate payment doesn't exceed remaining amount
            if amount > montant_restant:
                raise ServiceException(
                    f"Payment amount ({amount}) exceeds remaining balance ({montant_restant})"
                )

            # Create payment record
            payment = Payment(
                id=UUID,
                invoice_id=invoice_id,
                amount=amount,
                payment_method=payment_method,
                payment_date=datetime.utcnow(),
                status=PaymentStatus.completed.value
            )
            self.session.add(payment)

            # Update invoice totals
            new_montant_paye = Decimal(str(invoice.montant_paye or 0)) + amount
            new_montant_restant = Decimal(str(invoice.montant_ttc or 0)) - new_montant_paye

            # Determine new status
            new_status = InvoiceStatus.paid.value if new_montant_restant <= 0 else InvoiceStatus.partially_paid.value

            await self.invoice_repo.update(invoice_id, {
                "montant_paye": new_montant_paye,
                "montant_restant": new_montant_restant,
                "status": new_status
            })

            await self.session.flush()

            self.log_operation(
                "record_payment",
                invoice_id,
                {
                    "amount": str(amount),
                    "method": payment_method,
                    "new_status": new_status
                }
            )

            return {
                "payment": payment,
                "invoice_id": invoice_id,
                "montant_paye": new_montant_paye,
                "montant_restant": new_montant_restant,
                "status": new_status
            }

        except ServiceException:
            raise
        except Exception as e:
            self.logger.error(f"Error recording payment: {e}", exc_info=True)
            raise ServiceException(f"Failed to record payment: {str(e)}")

    async def get_outstanding_invoices(self, client_id: UUID) -> List[Invoice]:
        """
        Get all unpaid invoices for client
        
        Args:
            client_id: Client UUID
            
        Returns:
            List of invoices with montant_restant > 0
        """
        # Validate client exists
        await self.validate_exists(client_id, "Client")

        # Query unpaid invoices
        invoices = await self.invoice_repo.read_by(
            client_id=client_id,
            is_deleted=False
        )

        # Filter invoices with remaining balance
        outstanding = [inv for inv in invoices if (inv.montant_restant or 0) > 0]

        return outstanding

    async def send_invoice(self, invoice_id: UUID) -> Invoice:
        """
        Mark invoice as sent (move from draft to sent)
        
        Args:
            invoice_id: Invoice UUID
            
        Returns:
            Updated Invoice
            
        Raises:
            ServiceException if invalid transition
        """
        invoice = await self.invoice_repo.read(invoice_id)
        if not invoice:
            raise ServiceException(f"Invoice not found: {invoice_id}")

        if invoice.status != InvoiceStatus.draft.value:
            raise ServiceException(f"Can only send draft invoices, current status: {invoice.status}")

        updated = await self.invoice_repo.update(invoice_id, {
            "status": InvoiceStatus.sent.value
        })

        self.log_operation("send_invoice", invoice_id, {"numero_facture": invoice.numero_facture})

        return updated

    async def _generate_invoice_number(self) -> str:
        """
        Generate unique invoice number
        
        Format: INV-YYYYMMDD-XXXX (e.g., INV-20260625-0001)
        
        Returns:
            Invoice number string
        """
        from datetime import datetime as dt
        
        today = dt.today().strftime("%Y%m%d")
        
        # Count invoices created today
        count_result = await self.session.execute(
            select(func.count(Invoice.id)).where(
                func.date_trunc('day', Invoice.created_at) == dt.today().date()
            )
        )
        count = count_result.scalar() or 0
        
        return f"INV-{today}-{str(count + 1).zfill(4)}"

    async def get_outstanding_balance(self, client_id: UUID) -> Decimal:
        """
        Get total outstanding amount for client
        
        Args:
            client_id: Client UUID
            
        Returns:
            Total outstanding balance
        """
        invoices = await self.get_outstanding_invoices(client_id)
        total = sum(Decimal(str(inv.montant_restant or 0)) for inv in invoices)
        return total

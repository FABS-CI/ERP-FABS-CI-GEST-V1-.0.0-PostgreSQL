"""
Invoice Repository - Complex financial operations
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories.base_repository import BaseRepository
from db.models.invoice import Invoice, InvoiceStatus


class InvoiceRepository(BaseRepository[Invoice]):
    """Invoice repository with financial operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Invoice)
    
    async def find_by_number(self, numero_facture: str) -> Optional[Invoice]:
        """Find invoice by number"""
        return await self.read_one_by(numero_facture=numero_facture, is_deleted=False)
    
    async def find_by_client(self, client_id: UUID, skip: int = 0, limit: int = 100) -> tuple[List[Invoice], int]:
        """Get all invoices for a client"""
        query = select(self.model).where(
            and_(
                self.model.client_id == client_id,
                self.model.is_deleted == False
            )
        ).order_by(self.model.date_facture.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        invoices = result.scalars().all()
        total = await self.count(client_id=client_id, is_deleted=False)
        return invoices, total
    
    async def find_unpaid_invoices(self, client_id: UUID = None) -> List[Invoice]:
        """Find unpaid/partially paid invoices"""
        query = select(self.model).where(
            and_(
                self.model.is_deleted == False,
                or_(
                    self.model.status == InvoiceStatus.partially_paid,
                    self.model.status == InvoiceStatus.sent,
                    self.model.status == InvoiceStatus.overdue
                )
            )
        )
        
        if client_id:
            query = query.where(self.model.client_id == client_id)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def find_overdue_invoices(self, days: int = 0) -> List[Invoice]:
        """Find invoices past due date"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(self.model).where(
            and_(
                self.model.is_deleted == False,
                or_(
                    self.model.status == InvoiceStatus.overdue,
                    and_(
                        self.model.date_echeance < cutoff_date,
                        self.model.status != InvoiceStatus.paid
                    )
                )
            )
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def find_by_status(self, status: InvoiceStatus) -> List[Invoice]:
        """Find invoices by status"""
        return await self.read_by(status=status, is_deleted=False)
    
    async def update_payment(self, invoice_id: UUID, payment_amount: float) -> Optional[Invoice]:
        """Update payment amount and calculate remaining"""
        invoice = await self.read(invoice_id)
        if not invoice:
            return None
        
        new_paid = float(invoice.montant_paye or 0) + payment_amount
        montant_ttc = float(invoice.montant_ttc or 0)
        remaining = max(0, montant_ttc - new_paid)
        
        # Determine new status
        new_status = InvoiceStatus.paid if remaining <= 0 else InvoiceStatus.partially_paid
        
        updated = await self.update(invoice_id, {
            "montant_paye": new_paid,
            "montant_restant": remaining,
            "status": new_status
        })
        
        return updated
    
    async def get_total_revenue(self, client_id: UUID = None, start_date: datetime = None, end_date: datetime = None) -> float:
        """Calculate total revenue from invoices"""
        from sqlalchemy import func
        
        query = select(func.sum(self.model.montant_ttc)).where(
            and_(
                self.model.is_deleted == False,
                self.model.status == InvoiceStatus.paid
            )
        )
        
        if client_id:
            query = query.where(self.model.client_id == client_id)
        
        if start_date:
            query = query.where(self.model.date_facture >= start_date)
        
        if end_date:
            query = query.where(self.model.date_facture <= end_date)
        
        result = await self.session.execute(query)
        total = result.scalar() or 0
        return float(total)
    
    async def get_outstanding_amount(self, client_id: UUID = None) -> float:
        """Get total outstanding (unpaid) amount"""
        from sqlalchemy import func
        
        query = select(func.sum(self.model.montant_restant)).where(
            and_(
                self.model.is_deleted == False,
                self.model.montant_restant > 0
            )
        )
        
        if client_id:
            query = query.where(self.model.client_id == client_id)
        
        result = await self.session.execute(query)
        total = result.scalar() or 0
        return float(total)

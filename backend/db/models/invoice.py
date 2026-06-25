"""
Invoice Models - Factures, Paiements, Avoirs
"""

from datetime import datetime
from uuid import uuid4
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Numeric, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class InvoiceStatus(str, PyEnum):
    """Invoice status"""
    draft = "draft"
    sent = "sent"
    partially_paid = "partially_paid"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"
    credited = "credited"


class PaymentStatus(str, PyEnum):
    """Payment status"""
    pending = "pending"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class PaymentMethod(str, PyEnum):
    """Payment method"""
    cash = "cash"
    bank_transfer = "bank_transfer"
    check = "check"
    credit_card = "credit_card"
    mobile_money = "mobile_money"


class Invoice(Base):
    """Customer invoice"""
    
    __tablename__ = "factures"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    numero_facture = Column(String(50), unique=True, nullable=False, index=True)
    
    # Reference
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    reference_commande = Column(String(100), nullable=True)
    
    # Dates
    date_facture = Column(DateTime, default=datetime.utcnow)
    date_echeance = Column(DateTime, nullable=True)
    
    # Status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.draft, index=True)
    
    # Amounts
    montant_ht = Column(Numeric(15, 2), nullable=True)
    montant_tva = Column(Numeric(15, 2), nullable=True)
    montant_ttc = Column(Numeric(15, 2), nullable=True)
    montant_paye = Column(Numeric(15, 2), default=0)
    montant_restant = Column(Numeric(15, 2), nullable=True)
    
    # Terms
    devise = Column(String(3), default="XOF")
    conditions_paiement = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    invoice_lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")
    
    def __repr__(self):
        return f"<Invoice(numero={self.numero_facture}, status={self.status})>"


class InvoiceLine(Base):
    """Invoice line items"""
    
    __tablename__ = "facture_lignes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    facture_id = Column(UUID(as_uuid=True), ForeignKey("factures.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("produits.id"), nullable=False)
    
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Numeric(15, 2), nullable=False)
    
    montant_ht = Column(Numeric(15, 2), nullable=True)
    montant_tva = Column(Numeric(15, 2), nullable=True)
    montant_ttc = Column(Numeric(15, 2), nullable=True)
    taux_tva = Column(Numeric(5, 2), default=18)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="invoice_lines")
    
    def __repr__(self):
        return f"<InvoiceLine(invoice_id={self.facture_id}, qty={self.quantite})>"


class Payment(Base):
    """Customer payment"""
    
    __tablename__ = "paiements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    numero_paiement = Column(String(50), unique=True, nullable=False, index=True)
    
    # Reference
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("factures.id"), nullable=True)
    
    # Payment Details
    date_paiement = Column(DateTime, default=datetime.utcnow)
    montant = Column(Numeric(15, 2), nullable=False)
    methode = Column(Enum(PaymentMethod), nullable=True)
    statut = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    
    # Bank Reference
    reference_bancaire = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(numero={self.numero_paiement}, montant={self.montant})>"


class CreditNote(Base):
    """Credit note / Avoir"""
    
    __tablename__ = "credit_notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    numero_avoir = Column(String(50), unique=True, nullable=False, index=True)
    
    # References
    facture_id = Column(UUID(as_uuid=True), ForeignKey("factures.id"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    
    # Dates & Amounts
    date_avoir = Column(DateTime, default=datetime.utcnow)
    montant_ht = Column(Numeric(15, 2), nullable=True)
    montant_tva = Column(Numeric(15, 2), nullable=True)
    montant_ttc = Column(Numeric(15, 2), nullable=True)
    
    # Details
    devise = Column(String(3), default="XOF")
    motif = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<CreditNote(numero={self.numero_avoir})>"

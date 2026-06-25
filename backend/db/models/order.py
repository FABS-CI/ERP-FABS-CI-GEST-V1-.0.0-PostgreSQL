"""
Order Models - Commandes, Proformas
"""

from datetime import datetime
from uuid import uuid4
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Numeric, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class OrderStatus(str, PyEnum):
    """Order status"""
    draft = "draft"
    sent = "sent"
    confirmed = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base):
    """Customer order/Purchase order"""
    
    __tablename__ = "commandes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    numero_commande = Column(String(50), unique=True, nullable=False, index=True)
    
    # Reference
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    reference_client = Column(String(100), nullable=True)
    
    # Dates
    date_commande = Column(DateTime, default=datetime.utcnow)
    date_livraison_prevue = Column(DateTime, nullable=True)
    date_livraison_reelle = Column(DateTime, nullable=True)
    
    # Status & Shipping
    status = Column(Enum(OrderStatus), default=OrderStatus.draft, index=True)
    lieu_livraison = Column(Text, nullable=True)
    frais_livraison = Column(Numeric(15, 2), default=0)
    
    # Amounts
    montant_ht = Column(Numeric(15, 2), nullable=True)
    montant_tva = Column(Numeric(15, 2), nullable=True)
    montant_ttc = Column(Numeric(15, 2), nullable=True)
    reduction_percent = Column(Numeric(5, 2), default=0)
    reduction_montant = Column(Numeric(15, 2), default=0)
    
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
    order_lines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(numero={self.numero_commande}, status={self.status})>"


class OrderLine(Base):
    """Order line items"""
    
    __tablename__ = "commande_lignes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    commande_id = Column(UUID(as_uuid=True), ForeignKey("commandes.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("produits.id"), nullable=False)
    
    # Quantities & Pricing
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Numeric(15, 2), nullable=False)
    
    # Amounts
    montant_ht = Column(Numeric(15, 2), nullable=True)
    montant_tva = Column(Numeric(15, 2), nullable=True)
    montant_ttc = Column(Numeric(15, 2), nullable=True)
    taux_tva = Column(Numeric(5, 2), default=18)
    
    notes = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="order_lines")
    
    def __repr__(self):
        return f"<OrderLine(order_id={self.commande_id}, qty={self.quantite})>"


class Proforma(Base):
    """Proforma invoice"""
    
    __tablename__ = "proformas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    numero_proforma = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    
    # Dates
    date_proforma = Column(DateTime, default=datetime.utcnow)
    date_validite = Column(DateTime, nullable=True)
    
    # Status & Amounts
    status = Column(String(50), default="draft")
    montant_ht = Column(Numeric(15, 2), nullable=True)
    montant_tva = Column(Numeric(15, 2), nullable=True)
    montant_ttc = Column(Numeric(15, 2), nullable=True)
    devise = Column(String(3), default="XOF")
    
    notes = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    proforma_lines = relationship("ProformaLine", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Proforma(numero={self.numero_proforma})>"


class ProformaLine(Base):
    """Proforma line items"""
    
    __tablename__ = "proforma_lignes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    proforma_id = Column(UUID(as_uuid=True), ForeignKey("proformas.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("produits.id"), nullable=False)
    
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Numeric(15, 2), nullable=False)
    montant_ht = Column(Numeric(15, 2), nullable=True)
    montant_tva = Column(Numeric(15, 2), nullable=True)
    montant_ttc = Column(Numeric(15, 2), nullable=True)
    taux_tva = Column(Numeric(5, 2), default=18)
    
    created_at = Column(DateTime, default=datetime.utcnow)

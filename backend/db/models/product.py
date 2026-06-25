"""
Product & Stock Models
"""

from datetime import datetime
from uuid import uuid4
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Numeric, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class ProductStatus(str, PyEnum):
    """Product status"""
    active = "active"
    inactive = "inactive"
    discontinued = "discontinued"
    draft = "draft"


class Product(Base):
    """Product/Article entity"""
    
    __tablename__ = "produits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code_produit = Column(String(100), unique=True, nullable=False, index=True)
    designation = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProductStatus), default=ProductStatus.active, nullable=True, index=True)
    
    # Classification
    categorie = Column(String(100), nullable=True)
    marque = Column(String(100), nullable=True)
    fabricant = Column(String(255), nullable=True)
    
    # Pricing
    prix_unitaire = Column(Numeric(15, 2), nullable=False)
    prix_vente_unitaire = Column(Numeric(15, 2), nullable=True)
    prix_achat_unitaire = Column(Numeric(15, 2), nullable=True)
    devise = Column(String(3), default="XOF")
    
    # Physical Properties
    unite_mesure = Column(String(20), nullable=True)
    poids = Column(Numeric(10, 3), nullable=True)
    dimension_l = Column(Numeric(10, 3), nullable=True)
    dimension_h = Column(Numeric(10, 3), nullable=True)
    dimension_p = Column(Numeric(10, 3), nullable=True)
    
    # Stock Control
    stock_minimum = Column(Integer, default=0)
    stock_maximum = Column(Integer, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    def __repr__(self):
        return f"<Product(code={self.code_produit}, designation={self.designation})>"


class Depot(Base):
    """Warehouse/Storage location"""
    
    __tablename__ = "depots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code_depot = Column(String(50), unique=True, nullable=False, index=True)
    nom_depot = Column(String(255), nullable=False)
    
    # Location
    adresse = Column(Text, nullable=True)
    ville = Column(String(100), nullable=True)
    codepostal = Column(String(20), nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Details
    responsable = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    surface = Column(Numeric(10, 2), nullable=True)
    type_depot = Column(String(50), nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False, index=True)
    
    def __repr__(self):
        return f"<Depot(code={self.code_depot}, nom={self.nom_depot})>"


class Stock(Base):
    """Stock quantity per product per depot"""
    
    __tablename__ = "stock"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("produits.id"), nullable=False, index=True)
    depot_id = Column(UUID(as_uuid=True), ForeignKey("depots.id"), nullable=False, index=True)
    
    # Quantities
    quantite_actuelle = Column(Integer, default=0)
    quantite_reserve = Column(Integer, default=0)
    quantite_disponible = Column(Integer, default=0)
    quantite_endommagee = Column(Integer, default=0)
    
    # Last Inventory
    date_dernier_inventaire = Column(DateTime, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('product_id', 'depot_id', name='uq_stock_product_depot'),
    )
    
    def __repr__(self):
        return f"<Stock(product_id={self.product_id}, qty={self.quantite_actuelle})>"


class StockMovement(Base):
    """Stock movement history"""
    
    __tablename__ = "mouvements_stock"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("produits.id"), nullable=False, index=True)
    depot_id = Column(UUID(as_uuid=True), ForeignKey("depots.id"), nullable=False)
    
    # Movement Info
    type_mouvement = Column(String(50), nullable=False)  # IN, OUT, ADJUSTMENT
    quantite = Column(Integer, nullable=False)
    quantite_avant = Column(Integer, nullable=True)
    quantite_apres = Column(Integer, nullable=True)
    
    # Reference
    reference_document = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_by = Column(UUID(as_uuid=True))
    
    def __repr__(self):
        return f"<StockMovement(type={self.type_mouvement}, qty={self.quantite})>"

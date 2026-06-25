"""
CRM Models - Client, Contact, Prospect
PostgreSQL ORM models for customer management
"""

from datetime import datetime
from uuid import uuid4
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Numeric, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class ClientStatus(str, PyEnum):
    """Client status values"""
    prospect = "prospect"
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    blacklisted = "blacklisted"


class Client(Base):
    """Client entity - Main customer table"""
    
    __tablename__ = "clients"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    
    # Identification
    code_client = Column(String(50), unique=True, nullable=False, index=True)
    nom_client = Column(String(255), nullable=False)
    type_client = Column(String(50), nullable=True)  # Individual, Company, etc.
    
    # Status
    status = Column(Enum(ClientStatus), default=ClientStatus.prospect, nullable=True, index=True)
    
    # Address & Location
    adresse = Column(Text, nullable=True)
    ville = Column(String(100), nullable=True)
    codepostal = Column(String(20), nullable=True)
    
    # Contact Information
    telephone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    contact_principal = Column(String(255), nullable=True)
    
    # Business Info
    secteur_activite = Column(String(100), nullable=True)
    groupe_client = Column(String(100), nullable=True)
    
    # Credit Management
    credit_limit = Column(Numeric(15, 2), nullable=True)
    credit_utilise = Column(Numeric(15, 2), default=0, nullable=True)
    
    # Payment Terms
    jour_paiement_standard = Column(Integer, nullable=True)  # Number of days for payment
    conditions_paiement = Column(Text, nullable=True)
    devise = Column(String(3), default="XOF", nullable=True)
    
    # Audit Columns
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=True, index=True)
    
    # Relationships
    contacts = relationship("Contact", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client(id={self.id}, code={self.code_client}, nom={self.nom_client})>"
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "code_client": self.code_client,
            "nom_client": self.nom_client,
            "status": self.status.value if self.status else None,
            "email": self.email,
            "telephone": self.telephone,
            "ville": self.ville,
            "credit_limit": float(self.credit_limit) if self.credit_limit else None,
            "credit_utilise": float(self.credit_utilise) if self.credit_utilise else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Contact(Base):
    """Contact entity - Individual contacts within clients"""
    
    __tablename__ = "contacts"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    
    # Foreign Key
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Contact Information
    nom = Column(String(255), nullable=False)
    fonction = Column(String(100), nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    adresse = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Audit Columns
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="contacts")
    
    def __repr__(self):
        return f"<Contact(id={self.id}, nom={self.nom}, client_id={self.client_id})>"


class Prospect(Base):
    """Prospect entity - Sales pipeline"""
    
    __tablename__ = "prospects"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    
    # Prospect Information
    nom_prospect = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    telephone = Column(String(20), nullable=True)
    secteur = Column(String(100), nullable=True)
    
    # Business Info
    budget_estime = Column(Numeric(15, 2), nullable=True)
    date_contact = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Audit Columns
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=True)
    
    def __repr__(self):
        return f"<Prospect(id={self.id}, nom={self.nom_prospect})>"

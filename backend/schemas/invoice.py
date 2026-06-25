"""Invoice Schemas - Pydantic models for Invoice endpoints"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from db.models import InvoiceStatus


class InvoiceCreate(BaseModel):
    """Create new invoice"""
    numero_facture: str = Field(..., min_length=3, max_length=50)
    client_id: UUID
    reference_commande: Optional[str] = None
    date_facture: Optional[datetime] = None
    date_echeance: Optional[datetime] = None
    status: Optional[InvoiceStatus] = InvoiceStatus.draft
    montant_ht: Optional[Decimal] = None
    montant_tva: Optional[Decimal] = None
    montant_ttc: Optional[Decimal] = None
    montant_paye: Optional[Decimal] = None
    montant_restant: Optional[Decimal] = None
    devise: Optional[str] = "XOF"
    conditions_paiement: Optional[str] = None
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    """Update existing invoice"""
    numero_facture: Optional[str] = None
    reference_commande: Optional[str] = None
    date_facture: Optional[datetime] = None
    date_echeance: Optional[datetime] = None
    status: Optional[InvoiceStatus] = None
    montant_ht: Optional[Decimal] = None
    montant_tva: Optional[Decimal] = None
    montant_ttc: Optional[Decimal] = None
    montant_paye: Optional[Decimal] = None
    montant_restant: Optional[Decimal] = None
    conditions_paiement: Optional[str] = None
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Invoice response model"""
    id: UUID
    numero_facture: str
    client_id: UUID
    reference_commande: Optional[str]
    date_facture: Optional[datetime]
    date_echeance: Optional[datetime]
    status: Optional[str]
    montant_ht: Optional[Decimal]
    montant_tva: Optional[Decimal]
    montant_ttc: Optional[Decimal]
    montant_paye: Optional[Decimal]
    montant_restant: Optional[Decimal]
    devise: Optional[str]
    conditions_paiement: Optional[str]
    notes: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_deleted: Optional[bool]

    class Config:
        orm_mode = True


class InvoiceListResponse(BaseModel):
    """Invoice list response with pagination"""
    items: list[InvoiceResponse]
    total: int
    skip: int
    limit: int

"""Order Schemas - Pydantic models for Order endpoints"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from db.models import OrderStatus


class OrderCreate(BaseModel):
    """Create new order"""
    numero_commande: str = Field(..., min_length=3, max_length=50)
    client_id: UUID
    reference_client: Optional[str] = None
    date_commande: Optional[datetime] = None
    date_livraison_prevue: Optional[datetime] = None
    status: Optional[OrderStatus] = OrderStatus.draft
    lieu_livraison: Optional[str] = None
    frais_livraison: Optional[Decimal] = None
    montant_ht: Optional[Decimal] = None
    montant_tva: Optional[Decimal] = None
    montant_ttc: Optional[Decimal] = None
    reduction_percent: Optional[Decimal] = None
    reduction_montant: Optional[Decimal] = None
    devise: Optional[str] = "XOF"
    conditions_paiement: Optional[str] = None
    notes: Optional[str] = None


class OrderUpdate(BaseModel):
    """Update existing order"""
    numero_commande: Optional[str] = None
    reference_client: Optional[str] = None
    date_livraison_prevue: Optional[datetime] = None
    status: Optional[OrderStatus] = None
    lieu_livraison: Optional[str] = None
    frais_livraison: Optional[Decimal] = None
    montant_ht: Optional[Decimal] = None
    montant_tva: Optional[Decimal] = None
    montant_ttc: Optional[Decimal] = None
    reduction_percent: Optional[Decimal] = None
    reduction_montant: Optional[Decimal] = None
    conditions_paiement: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    """Order response model"""
    id: UUID
    numero_commande: str
    client_id: UUID
    reference_client: Optional[str]
    date_commande: Optional[datetime]
    date_livraison_prevue: Optional[datetime]
    date_livraison_reelle: Optional[datetime]
    status: Optional[str]
    lieu_livraison: Optional[str]
    frais_livraison: Optional[Decimal]
    montant_ht: Optional[Decimal]
    montant_tva: Optional[Decimal]
    montant_ttc: Optional[Decimal]
    reduction_percent: Optional[Decimal]
    reduction_montant: Optional[Decimal]
    devise: Optional[str]
    conditions_paiement: Optional[str]
    notes: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_deleted: Optional[bool]

    class Config:
        orm_mode = True


class OrderListResponse(BaseModel):
    """Order list response with pagination"""
    items: list[OrderResponse]
    total: int
    skip: int
    limit: int

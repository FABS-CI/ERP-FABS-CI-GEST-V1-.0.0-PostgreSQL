"""Client Schemas - Pydantic models for Client endpoints"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from db.models import ClientStatus


class ClientCreate(BaseModel):
    """Create new client"""
    code_client: str = Field(..., min_length=3, max_length=50)
    nom_client: str = Field(..., min_length=2, max_length=255)
    type_client: Optional[str] = Field(None, max_length=50)
    status: Optional[ClientStatus] = ClientStatus.active
    adresse: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    codepostal: Optional[str] = Field(None, max_length=20)
    telephone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    contact_principal: Optional[str] = None
    secteur_activite: Optional[str] = None
    groupe_client: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    jour_paiement_standard: Optional[int] = None
    conditions_paiement: Optional[str] = None
    devise: Optional[str] = "XOF"


class ClientUpdate(BaseModel):
    """Update existing client"""
    nom_client: Optional[str] = Field(None, min_length=2, max_length=255)
    type_client: Optional[str] = None
    status: Optional[ClientStatus] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_principal: Optional[str] = None
    secteur_activite: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    jour_paiement_standard: Optional[int] = None
    conditions_paiement: Optional[str] = None


class ClientResponse(BaseModel):
    """Client response model"""
    id: UUID
    code_client: str
    nom_client: str
    type_client: Optional[str]
    status: Optional[str]
    adresse: Optional[str]
    ville: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    contact_principal: Optional[str]
    secteur_activite: Optional[str]
    groupe_client: Optional[str]
    credit_limit: Optional[Decimal]
    credit_utilise: Optional[Decimal]
    jour_paiement_standard: Optional[int]
    devise: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_deleted: Optional[bool]

    class Config:
        orm_mode = True


class ClientListResponse(BaseModel):
    """Client list response with pagination"""
    items: list[ClientResponse]
    total: int
    skip: int
    limit: int

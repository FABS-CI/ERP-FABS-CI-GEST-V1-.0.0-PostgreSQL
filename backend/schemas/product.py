"""Product Schemas - Pydantic models for Product endpoints"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from db.models import ProductStatus


class ProductCreate(BaseModel):
    """Create new product"""
    code_produit: str = Field(..., min_length=3, max_length=100)
    designation: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    status: Optional[ProductStatus] = ProductStatus.active
    categorie: Optional[str] = None
    marque: Optional[str] = None
    fabricant: Optional[str] = None
    prix_unitaire: Decimal = Field(..., ge=0)
    prix_vente_unitaire: Optional[Decimal] = None
    prix_achat_unitaire: Optional[Decimal] = None
    devise: Optional[str] = "XOF"
    unite_mesure: Optional[str] = None
    poids: Optional[Decimal] = None
    dimension_l: Optional[Decimal] = None
    dimension_h: Optional[Decimal] = None
    dimension_p: Optional[Decimal] = None
    stock_minimum: Optional[int] = None
    stock_maximum: Optional[int] = None


class ProductUpdate(BaseModel):
    """Update existing product"""
    designation: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProductStatus] = None
    categorie: Optional[str] = None
    marque: Optional[str] = None
    fabricant: Optional[str] = None
    prix_unitaire: Optional[Decimal] = None
    prix_vente_unitaire: Optional[Decimal] = None
    prix_achat_unitaire: Optional[Decimal] = None
    unite_mesure: Optional[str] = None
    poids: Optional[Decimal] = None
    dimension_l: Optional[Decimal] = None
    dimension_h: Optional[Decimal] = None
    dimension_p: Optional[Decimal] = None
    stock_minimum: Optional[int] = None
    stock_maximum: Optional[int] = None


class ProductResponse(BaseModel):
    """Product response model"""
    id: UUID
    code_produit: str
    designation: str
    description: Optional[str]
    status: Optional[str]
    categorie: Optional[str]
    marque: Optional[str]
    fabricant: Optional[str]
    prix_unitaire: Optional[Decimal]
    prix_vente_unitaire: Optional[Decimal]
    prix_achat_unitaire: Optional[Decimal]
    devise: Optional[str]
    unite_mesure: Optional[str]
    poids: Optional[Decimal]
    dimension_l: Optional[Decimal]
    dimension_h: Optional[Decimal]
    dimension_p: Optional[Decimal]
    stock_minimum: Optional[int]
    stock_maximum: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_deleted: Optional[bool]

    class Config:
        orm_mode = True


class ProductListResponse(BaseModel):
    """Product list response with pagination"""
    items: list[ProductResponse]
    total: int
    skip: int
    limit: int

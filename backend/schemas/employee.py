"""Employee Schemas - Pydantic models for Employee endpoints"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal


class EmployeeCreate(BaseModel):
    """Create new employee"""
    code_employe: str = Field(..., min_length=3, max_length=50)
    user_id: Optional[UUID] = None
    departement_id: UUID
    fonction_id: Optional[UUID] = None
    date_embauche: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    statut: Optional[str] = None
    salaire_mensuel: Optional[Decimal] = None
    devise: Optional[str] = "XOF"


class EmployeeUpdate(BaseModel):
    """Update existing employee"""
    code_employe: Optional[str] = None
    user_id: Optional[UUID] = None
    departement_id: Optional[UUID] = None
    fonction_id: Optional[UUID] = None
    date_fin_prevue: Optional[date] = None
    statut: Optional[str] = None
    salaire_mensuel: Optional[Decimal] = None


class EmployeeResponse(BaseModel):
    """Employee response model"""
    id: UUID
    code_employe: str
    user_id: Optional[UUID]
    departement_id: UUID
    fonction_id: Optional[UUID] = None
    date_embauche: Optional[date]
    date_fin_prevue: Optional[date]
    statut: Optional[str]
    salaire_mensuel: Optional[Decimal]
    devise: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_deleted: Optional[bool]

    class Config:
        orm_mode = True


class EmployeeListResponse(BaseModel):
    """Employee list response with pagination"""
    items: list[EmployeeResponse]
    total: int
    skip: int
    limit: int

"""User Schemas - Pydantic models for User endpoints"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from db.models import UserRole


class UserCreate(BaseModel):
    """Create new user"""
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password_hash: str = Field(..., min_length=8)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = UserRole.user
    actif: Optional[bool] = True


class UserUpdate(BaseModel):
    """Update existing user"""
    username: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    actif: Optional[bool] = None


class UserResponse(BaseModel):
    """User response model"""
    id: UUID
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    role: Optional[str]
    actif: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_deleted: Optional[bool]

    class Config:
        orm_mode = True


class UserListResponse(BaseModel):
    """User list response with pagination"""
    items: list[UserResponse]
    total: int
    skip: int
    limit: int

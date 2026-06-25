"""
User Model - SQLAlchemy ORM
Maps to PostgreSQL users table
"""

from datetime import datetime
from uuid import uuid4
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class UserRole(str, PyEnum):
    """User roles enum"""
    admin = "admin"
    manager = "manager"
    employee = "employee"
    user = "user"


class User(Base):
    """User entity - Authentication & access control"""
    
    __tablename__ = "users"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    
    # Core Fields
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Role & Status
    role = Column(Enum(UserRole), default=UserRole.user, nullable=True)
    actif = Column(Boolean, default=True, nullable=True)
    
    # Personal Info
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Audit Columns
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary (safe for JSON)"""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "role": self.role.value if self.role else None,
            "actif": self.actif,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

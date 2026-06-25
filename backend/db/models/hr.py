"""
HR Models - Employees, Departments, Contracts, Payroll
"""

from datetime import datetime, date
from uuid import uuid4
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, DateTime, Date, Enum, ForeignKey, Numeric, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class EmployeeStatus(str, PyEnum):
    """Employee status"""
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    retired = "retired"


class ContractType(str, PyEnum):
    """Contract type"""
    cdi = "cdi"
    cdd = "cdd"
    stage = "stage"
    consultant = "consultant"


class LeaveType(str, PyEnum):
    """Leave type"""
    paid = "paid"
    unpaid = "unpaid"
    sick = "sick"
    maternity = "maternity"


class Department(Base):
    """Department"""
    
    __tablename__ = "departements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code_departement = Column(String(50), unique=True, nullable=False, index=True)
    nom_departement = Column(String(255), nullable=False)
    responsable = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    budget_annuel = Column(Numeric(15, 2), nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    
    employees = relationship("Employee", back_populates="departement")
    
    def __repr__(self):
        return f"<Department(code={self.code_departement})>"


class Function(Base):
    """Function/Position"""
    
    __tablename__ = "fonctions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code_fonction = Column(String(50), unique=True, nullable=False)
    nom_fonction = Column(String(255), nullable=False)
    
    salaire_base = Column(Numeric(15, 2), nullable=True)
    prime_base = Column(Numeric(15, 2), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    employees = relationship("Employee", back_populates="fonction")
    
    def __repr__(self):
        return f"<Function(code={self.code_fonction})>"


class Employee(Base):
    """Employee"""
    
    __tablename__ = "employes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code_employe = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Department & Function
    departement_id = Column(UUID(as_uuid=True), ForeignKey("departements.id"), nullable=False)
    fonction_id = Column(UUID(as_uuid=True), ForeignKey("fonctions.id"), nullable=False)
    
    # Employment Details
    date_embauche = Column(Date, nullable=True)
    date_fin_prevue = Column(Date, nullable=True)
    statut = Column(Enum(EmployeeStatus), default=EmployeeStatus.active)
    
    # Compensation
    salaire_mensuel = Column(Numeric(15, 2), nullable=True)
    devise = Column(String(3), default="XOF")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    
    departement = relationship("Department", back_populates="employees")
    fonction = relationship("Function", back_populates="employees")
    contrats = relationship("Contract", back_populates="employee")
    conges = relationship("Leave", back_populates="employee")
    bulletins = relationship("Payroll", back_populates="employee")
    
    def __repr__(self):
        return f"<Employee(code={self.code_employe}, statut={self.statut})>"


class Contract(Base):
    """Employment contract"""
    
    __tablename__ = "contrats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    numero_contrat = Column(String(50), unique=True, nullable=False)
    employe_id = Column(UUID(as_uuid=True), ForeignKey("employes.id"), nullable=False)
    
    type_contrat = Column(Enum(ContractType), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    salaire_mensuel = Column(Numeric(15, 2), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    employee = relationship("Employee", back_populates="contrats")
    
    def __repr__(self):
        return f"<Contract(numero={self.numero_contrat})>"


class Leave(Base):
    """Leave/Time off"""
    
    __tablename__ = "conges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    employe_id = Column(UUID(as_uuid=True), ForeignKey("employes.id"), nullable=False)
    
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    type_conge = Column(Enum(LeaveType), nullable=True)
    nombre_jours = Column(Integer, nullable=True)
    
    approbation_par = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    statut = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    employee = relationship("Employee", back_populates="conges")
    
    def __repr__(self):
        return f"<Leave(employe_id={self.employe_id}, type={self.type_conge})>"


class Payroll(Base):
    """Payroll/Salary slip"""
    
    __tablename__ = "bulletins_paie"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    numero_bulletin = Column(String(50), unique=True, nullable=False)
    employe_id = Column(UUID(as_uuid=True), ForeignKey("employes.id"), nullable=False)
    
    # Period
    periode_debut = Column(Date, nullable=False)
    periode_fin = Column(Date, nullable=False)
    
    # Amounts
    salaire_brut = Column(Numeric(15, 2), nullable=True)
    deductions = Column(Numeric(15, 2), nullable=True)
    salaire_net = Column(Numeric(15, 2), nullable=True)
    devise = Column(String(3), default="XOF")
    
    # Payment
    date_paiement = Column(DateTime, nullable=True)
    statut_paiement = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    employee = relationship("Employee", back_populates="bulletins")
    
    def __repr__(self):
        return f"<Payroll(numero={self.numero_bulletin})>"

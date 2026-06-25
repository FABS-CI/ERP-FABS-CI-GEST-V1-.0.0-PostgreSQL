"""
SQLAlchemy Models - All ORM entities
PostgreSQL tables are defined here
"""

from db.models.user import User, UserRole
from db.models.client import Client, Contact, Prospect, ClientStatus
from db.models.product import Product, ProductStatus, Depot, Stock, StockMovement
from db.models.order import Order, OrderLine, OrderStatus, Proforma, ProformaLine
from db.models.invoice import (
    Invoice, InvoiceLine, Payment, CreditNote,
    InvoiceStatus, PaymentStatus, PaymentMethod
)
from db.models.hr import (
    Department, Function, Employee, Contract, Leave, Payroll,
    EmployeeStatus, ContractType, LeaveType
)

__all__ = [
    # User
    "User", "UserRole",
    # CRM
    "Client", "Contact", "Prospect", "ClientStatus",
    # Product & Stock
    "Product", "ProductStatus", "Depot", "Stock", "StockMovement",
    # Orders
    "Order", "OrderLine", "OrderStatus", "Proforma", "ProformaLine",
    # Invoices & Payments
    "Invoice", "InvoiceLine", "Payment", "CreditNote",
    "InvoiceStatus", "PaymentStatus", "PaymentMethod",
    # HR
    "Department", "Function", "Employee", "Contract", "Leave", "Payroll",
    "EmployeeStatus", "ContractType", "LeaveType",
]

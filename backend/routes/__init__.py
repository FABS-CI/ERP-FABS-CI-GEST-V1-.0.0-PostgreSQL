"""
FastAPI Routes for ERP FABS-CI
All endpoint routers are imported here
"""

from . import users, clients, products, orders, invoices, employees

__all__ = ["users", "clients", "products", "orders", "invoices", "employees"]

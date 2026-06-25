"""
Pydantic Schemas - Request/Response DTOs
All schemas for data validation and serialization
"""

from .user import UserCreate, UserUpdate, UserResponse, UserListResponse
from .client import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse
from .product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from .order import OrderCreate, OrderUpdate, OrderResponse, OrderListResponse
from .invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse
from .employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserListResponse",
    "ClientCreate", "ClientUpdate", "ClientResponse", "ClientListResponse",
    "ProductCreate", "ProductUpdate", "ProductResponse", "ProductListResponse",
    "OrderCreate", "OrderUpdate", "OrderResponse", "OrderListResponse",
    "InvoiceCreate", "InvoiceUpdate", "InvoiceResponse", "InvoiceListResponse",
    "EmployeeCreate", "EmployeeUpdate", "EmployeeResponse", "EmployeeListResponse",
]

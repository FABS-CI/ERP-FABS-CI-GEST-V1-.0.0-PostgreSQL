"""
Dependency Injection Providers for FastAPI
Each provider returns a repository instance bound to current session
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import get_session
from db.repositories import (
    ClientRepository,
    ProductRepository,
    OrderRepository,
    InvoiceRepository,
    EmployeeRepository,
    UserRepository,
)


async def get_client_repo(session: AsyncSession = Depends(get_session)) -> ClientRepository:
    """Provide ClientRepository instance"""
    return ClientRepository(session)


async def get_product_repo(session: AsyncSession = Depends(get_session)) -> ProductRepository:
    """Provide ProductRepository instance"""
    return ProductRepository(session)


async def get_order_repo(session: AsyncSession = Depends(get_session)) -> OrderRepository:
    """Provide OrderRepository instance"""
    return OrderRepository(session)


async def get_invoice_repo(session: AsyncSession = Depends(get_session)) -> InvoiceRepository:
    """Provide InvoiceRepository instance"""
    return InvoiceRepository(session)


async def get_employee_repo(session: AsyncSession = Depends(get_session)) -> EmployeeRepository:
    """Provide EmployeeRepository instance"""
    return EmployeeRepository(session)


async def get_user_repo(session: AsyncSession = Depends(get_session)) -> UserRepository:
    """Provide UserRepository instance"""
    return UserRepository(session)

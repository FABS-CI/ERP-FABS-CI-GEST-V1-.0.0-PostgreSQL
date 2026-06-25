"""
Invoice Routes - CRUD endpoints for invoice (Service-integrated)
GET, POST, PUT, DELETE operations with business logic
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse
from services.invoice_service import InvoiceService
from db.base import get_session

router = APIRouter()

@router.post("", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    invoice_in: InvoiceCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new invoice with financial calculations"""
    try:
        service = InvoiceService(session)
        invoice = await service.create_invoice(invoice_in.dict())
        return invoice
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating invoice: {str(e)}")

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def read_invoice(
    invoice_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Get invoice by ID"""
    try:
        service = InvoiceService(session)
        invoice = await service.get_invoice(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching invoice: {str(e)}")

@router.get("", response_model=InvoiceListResponse)
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    """List all invoices with pagination"""
    try:
        service = InvoiceService(session)
        invoices = await service.list_invoices(skip=skip, limit=limit)
        return {"items": invoices, "total": len(invoices), "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing invoices: {str(e)}")

@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: UUID,
    invoice_in: InvoiceUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update invoice"""
    try:
        service = InvoiceService(session)
        invoice = await service.update_invoice(invoice_id, invoice_in.dict(exclude_unset=True))
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating invoice: {str(e)}")

@router.delete("/{invoice_id}", status_code=204)
async def delete_invoice(
    invoice_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """Delete invoice (soft delete)"""
    try:
        service = InvoiceService(session)
        await service.delete_invoice(invoice_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting invoice: {str(e)}")

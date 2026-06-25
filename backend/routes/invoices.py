"""Invoice Routes - CRUD with Repository DI"""
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse
from db.base import get_session
from db.repositories import InvoiceRepository, OrderRepository, ClientRepository
from db.dependencies import get_invoice_repo, get_order_repo, get_client_repo

router = APIRouter()

@router.post("", response_model=InvoiceResponse, status_code=201)
async def create_invoice(invoice_in: InvoiceCreate, session: AsyncSession = Depends(get_session), invoice_repo: InvoiceRepository = Depends(get_invoice_repo), order_repo: OrderRepository = Depends(get_order_repo), client_repo: ClientRepository = Depends(get_client_repo)):
    try:
        result = await invoice_repo.create(invoice_in.dict())
        await session.commit()
        return result
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def read_invoice(invoice_id: UUID, session: AsyncSession = Depends(get_session), invoice_repo: InvoiceRepository = Depends(get_invoice_repo), order_repo: OrderRepository = Depends(get_order_repo), client_repo: ClientRepository = Depends(get_client_repo)):
    try:
        invoice = await invoice_repo.read(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Not found")
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("", response_model=InvoiceListResponse)
async def list_invoices(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: AsyncSession = Depends(get_session), invoice_repo: InvoiceRepository = Depends(get_invoice_repo), order_repo: OrderRepository = Depends(get_order_repo), client_repo: ClientRepository = Depends(get_client_repo)):
    try:
        items, total = await invoice_repo.list(skip=skip, limit=limit)
        return {"items": items, "total": total, "skip": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(invoice_id: UUID, invoice_in: InvoiceUpdate, session: AsyncSession = Depends(get_session), invoice_repo: InvoiceRepository = Depends(get_invoice_repo), order_repo: OrderRepository = Depends(get_order_repo), client_repo: ClientRepository = Depends(get_client_repo)):
    try:
        invoice = await invoice_repo.update(invoice_id, invoice_in.dict(exclude_unset=True))
        if not invoice:
            raise HTTPException(status_code=404, detail="Not found")
        await session.commit()
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/{invoice_id}", status_code=204)
async def delete_invoice(invoice_id: UUID, session: AsyncSession = Depends(get_session), invoice_repo: InvoiceRepository = Depends(get_invoice_repo), order_repo: OrderRepository = Depends(get_order_repo), client_repo: ClientRepository = Depends(get_client_repo)):
    try:
        await invoice_repo.delete(invoice_id)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

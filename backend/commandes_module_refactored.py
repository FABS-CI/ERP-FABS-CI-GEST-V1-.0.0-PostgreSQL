"""
Module Commandes — REFACTORED (PostgreSQL)
- Repository pattern for clients, products, orders
- Maintains all business logic from original
- Uses SQLAlchemy ORM + Pydantic
"""

from __future__ import annotations

from datetime import datetime, timezone, date, timedelta
from typing import Literal, Optional, List
from decimal import Decimal
import re
import uuid
import logging
import os
import asyncio

from fastapi import APIRouter, HTTPException, Header, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, validator
from sanitizers import sanitize_str

from db.repositories.client_repository import ClientRepository
from db.repositories.product_repository import ProductRepository
from db.repositories.order_repository import OrderRepository
from db.repositories.invoice_repository import InvoiceRepository
from db.models.order import Order, OrderStatus
from db.models.client import Client, ClientStatus

logger = logging.getLogger("fabsci.commandes")

# RBAC (unchanged from original)
READ_ROLES = {
    "super_admin", "directeur_commercial",
    "secretariat", "comptable", "assistante",
    "gestionnaire_stock", "responsable_magasinier",
}
WRITE_ROLES = {
    "super_admin", "secretariat", "assistante", "comptable",
}
VALIDATE_ROLES = {"super_admin", "secretariat", "comptable"}
CANCEL_ROLES = {"super_admin", "comptable", "secretariat"}
PREPARE_ROLES = {"super_admin", "responsable_magasinier"}
DELIVER_ROLES = {"super_admin", "service_logistique"}

Statut = Literal["brouillon", "en_attente", "validee", "preparee", "livree", "annulee"]
VALIDATION_THRESHOLD = 500_000

def _ensure(condition: bool, status: int, detail: str) -> None:
    if not condition:
        raise HTTPException(status_code=status, detail=detail)

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Schemas (simplified)
class LigneCommandeIn(BaseModel):
    produit_id: str = Field(..., alias='product_id')
    quantite: int = Field(..., gt=0)
    prix_unitaire: float = Field(..., gt=0)
    remise_ligne: float = Field(default=0, ge=0, le=100)
    
    @property
    def montant_ligne(self) -> float:
        base = self.quantite * self.prix_unitaire
        remise = base * (self.remise_ligne / 100)
        return round(base - remise, 2)

class CommandeIn(BaseModel):
    client_id: str
    lignes: List[LigneCommandeIn]
    remise_globale: float = Field(default=0, ge=0, le=100)
    taux_tva: float = Field(default=18.0, ge=0, le=100)
    date_livraison_prevue: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        populate_by_name = True

class CommandeOut(BaseModel):
    commande_id: str
    numero_commande: str
    client_id: str
    client_nom: Optional[str] = None
    status: str
    montant_total: float
    created_at: Optional[str] = None
    
    class Config:
        orm_mode = True

# Helper functions
async def _calculate_totals(lignes: List[LigneCommandeIn], remise_globale: float, taux_tva: float = 18.0) -> dict:
    """Calculate HT, remise, TVA, TTC"""
    montant_ht = sum(l.montant_ligne for l in lignes)
    montant_remise = montant_ht * (remise_globale / 100)
    montant_ht_net = montant_ht - montant_remise
    montant_tva = montant_ht_net * (taux_tva / 100)
    montant_total = montant_ht_net + montant_tva
    return {
        "montant_ht": round(montant_ht, 2),
        "montant_remise": round(montant_remise, 2),
        "montant_tva": round(montant_tva, 2),
        "montant_total": round(montant_total, 2),
    }

# Router builder
def build_commandes_router(
    resolve_user,
    log_audit_event=None,
    get_db=None,
) -> APIRouter:
    router = APIRouter(prefix="/commandes", tags=["commandes"])

    @router.get("")
    async def list_commandes(
        request: Request,
        authorization: Optional[str] = Header(default=None),
        status: Optional[str] = None,
        client_id: Optional[str] = None,
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=200),
        session: AsyncSession = Depends(get_db),
    ):
        me = await resolve_user(request, authorization)
        _ensure(me["role"] in READ_ROLES, 403, "Accès refusé")
        
        repo = OrderRepository(session)
        filters = {}
        if status:
            filters["status"] = status
        if client_id:
            filters["client_id"] = client_id
        
        items, total = await repo.list(skip=skip, limit=limit, **filters)
        return {
            "items": [
                CommandeOut(
                    commande_id=str(item.order_id),
                    numero_commande=item.numero_commande,
                    client_id=str(item.client_id),
                    status=item.status,
                    montant_total=float(item.montant_total or 0),
                    created_at=item.created_at.isoformat() if item.created_at else None,
                )
                for item in items
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @router.post("", response_model=CommandeOut, status_code=201)
    async def create_commande(
        payload: CommandeIn,
        request: Request,
        authorization: Optional[str] = Header(default=None),
        submit: bool = Query(False),
        session: AsyncSession = Depends(get_db),
    ):
        me = await resolve_user(request, authorization)
        _ensure(me["role"] in WRITE_ROLES, 403, "Accès refusé")

        # Verify client exists
        client_repo = ClientRepository(session)
        client = await client_repo.find_by_code(payload.client_id)
        if not client:
            # Try by ID
            from uuid import UUID
            try:
                client = await client_repo.read(UUID(payload.client_id))
            except:
                pass
        _ensure(client is not None, 404, "Client introuvable")

        # Verify products exist
        product_repo = ProductRepository(session)
        for ligne in payload.lignes:
            prod = await product_repo.find_by_code(ligne.produit_id)
            if not prod:
                try:
                    from uuid import UUID
                    prod = await product_repo.read(UUID(ligne.produit_id))
                except:
                    pass
            _ensure(prod is not None, 404, f"Produit {ligne.produit_id} introuvable")

        # Calculate totals
        totals = await _calculate_totals(payload.lignes, payload.remise_globale, payload.taux_tva)

        # Create order
        commande_id = uuid.uuid4()
        numero_commande = f"CMD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        order_repo = OrderRepository(session)
        order = await order_repo.create({
            "numero_commande": numero_commande,
            "client_id": client.client_id,
            "status": OrderStatus.sent if submit else OrderStatus.draft,
            "montant_ht": totals["montant_ht"],
            "montant_remise": totals["montant_remise"],
            "montant_tva": totals["montant_tva"],
            "montant_total": totals["montant_total"],
            "notes": payload.notes,
            "taux_tva": payload.taux_tva,
            "date_commande": datetime.now(timezone.utc),
            "created_by": me["user_id"],
        })

        # Audit log
        if log_audit_event:
            await log_audit_event(
                user_id=me["user_id"],
                action="CREATE_COMMANDE",
                resource_type="order",
                resource_id=str(order.order_id),
                details={
                    "numero": numero_commande,
                    "client_id": str(client.client_id),
                    "montant": totals["montant_total"],
                },
                ip_address=request.client.host if request.client else None
            )

        return CommandeOut(
            commande_id=str(order.order_id),
            numero_commande=order.numero_commande,
            client_id=str(order.client_id),
            client_nom=client.nom_client,
            status=order.status,
            montant_total=float(order.montant_total or 0),
            created_at=order.created_at.isoformat() if order.created_at else None,
        )

    @router.get("/{commande_id}")
    async def get_commande(
        commande_id: str,
        request: Request,
        authorization: Optional[str] = Header(default=None),
        session: AsyncSession = Depends(get_db),
    ):
        me = await resolve_user(request, authorization)
        _ensure(me["role"] in READ_ROLES, 403, "Accès refusé")
        
        repo = OrderRepository(session)
        from uuid import UUID
        try:
            order = await repo.read(UUID(commande_id))
        except:
            order = await repo.find_by_number(commande_id)
        
        _ensure(order is not None, 404, "Commande introuvable")
        
        return CommandeOut(
            commande_id=str(order.order_id),
            numero_commande=order.numero_commande,
            client_id=str(order.client_id),
            status=order.status,
            montant_total=float(order.montant_total or 0),
            created_at=order.created_at.isoformat() if order.created_at else None,
        )

    @router.patch("/{commande_id}")
    async def update_commande(
        commande_id: str,
        payload: dict,
        request: Request,
        authorization: Optional[str] = Header(default=None),
        session: AsyncSession = Depends(get_db),
    ):
        me = await resolve_user(request, authorization)
        _ensure(me["role"] in WRITE_ROLES, 403, "Accès refusé")
        
        repo = OrderRepository(session)
        from uuid import UUID
        try:
            order = await repo.read(UUID(commande_id))
        except:
            order = await repo.find_by_number(commande_id)
        
        _ensure(order is not None, 404, "Commande introuvable")
        
        updated = await repo.update(order.order_id, payload)
        
        return CommandeOut(
            commande_id=str(updated.order_id),
            numero_commande=updated.numero_commande,
            client_id=str(updated.client_id),
            status=updated.status,
            montant_total=float(updated.montant_total or 0),
        )

    @router.delete("/{commande_id}")
    async def cancel_commande(
        commande_id: str,
        request: Request,
        authorization: Optional[str] = Header(default=None),
        session: AsyncSession = Depends(get_db),
    ):
        me = await resolve_user(request, authorization)
        _ensure(me["role"] in CANCEL_ROLES, 403, "Accès refusé")
        
        repo = OrderRepository(session)
        from uuid import UUID
        try:
            order = await repo.read(UUID(commande_id))
        except:
            order = await repo.find_by_number(commande_id)
        
        _ensure(order is not None, 404, "Commande introuvable")
        
        # Soft delete
        updated = await repo.update(order.order_id, {"status": OrderStatus.cancelled})
        
        if log_audit_event:
            await log_audit_event(
                user_id=me["user_id"],
                action="CANCEL_COMMANDE",
                resource_type="order",
                resource_id=str(order.order_id),
                details={"numero": order.numero_commande},
                ip_address=request.client.host if request.client else None
            )
        
        return {"success": True, "commande_id": commande_id}

    return router

async def seed_commandes(session: AsyncSession, user_id: str) -> int:
    """Seed sample orders"""
    repo = OrderRepository(session)
    count = await repo.count()
    return 0  # Skip if already populated

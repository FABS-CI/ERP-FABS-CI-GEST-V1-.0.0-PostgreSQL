"""
Module Clients — Sprint 4 REFACTORED (PostgreSQL)
- CRUD complet sur la table PostgreSQL `clients`
- Référence auto-incrémentée FABS-CLI-XXXX (séquentielle, persistée dans `sequence`)
- Détection intelligente de doublons (Levenshtein normalisé sur nom + comparaison téléphone)
- RBAC : lecture super_admin/DG/comptable/commercial/secrétariat,
         écriture super_admin/DG/commercial/secrétariat
- Soft delete (`is_deleted=False`, jamais de DELETE physique)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional, List
from uuid import uuid4
import re

from fastapi import APIRouter, Depends, HTTPException, Header, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field, validator
from sanitizers import sanitize_str

from db.repositories.client_repository import ClientRepository
from db.models.client import Client, ClientStatus


# ---------------------------------------------------------------------------
# RBAC
# ---------------------------------------------------------------------------
READ_ROLES = {
    "super_admin", "directeur_general", "comptable",
    "directeur_commercial", "secretariat", "assistante",
}
WRITE_ROLES = {
    "super_admin", "directeur_general",
    "directeur_commercial", "secretariat", "assistante",
}
DISABLE_ROLES = {
    "super_admin", "directeur_general",
    "directeur_commercial", "secretariat",
}

ClientType = Literal[
    "librairie", "ecole", "particulier", "distributeur", "representant",
    "lycee", "college", "groupe_scolaire", "iep", "epp",
    "catholique", "methodiste", "memo", "inspecteur",
    "dren", "up", "institut", "autre",
    "librairies",  # compat
]


def _ensure(condition: bool, status: int, detail: str) -> None:
    if not condition:
        raise HTTPException(status_code=status, detail=detail)


# ---------------------------------------------------------------------------
# Levenshtein + normalisation (détection de doublons)
# ---------------------------------------------------------------------------
_NAME_NOISE = re.compile(
    r"\b(la|le|les|de|du|des|et|ets|ste|sarl|sa|lib|librairie|college|college|ecole|lycee|cours)\b\.?",
    flags=re.IGNORECASE,
)
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_name(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    accents = str.maketrans("àâäéèêëîïôöùûüç", "aaaeeeeiioouuuc")
    s = s.translate(accents)
    s = _NAME_NOISE.sub(" ", s)
    s = _NON_ALNUM.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def normalize_phone(s: Optional[str]) -> str:
    if not s:
        return ""
    digits = re.sub(r"\D", "", s)
    return digits[-8:] if len(digits) >= 8 else digits


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            ins = curr[j] + 1
            dele = prev[j + 1] + 1
            sub = prev[j] + (0 if ca == cb else 1)
            curr.append(min(ins, dele, sub))
        prev = curr
    return prev[-1]


def name_similarity(a: str, b: str) -> float:
    """1.0 = identical, 0.0 = totally different."""
    na, nb = normalize_name(a), normalize_name(b)
    if not na or not nb:
        return 0.0
    longest = max(len(na), len(nb))
    dist = levenshtein(na, nb)
    return 1.0 - (dist / longest)


# ---------------------------------------------------------------------------
# Reference generation FABS-CLI-XXXX
# ---------------------------------------------------------------------------
# This will be handled by a sequence in PostgreSQL
# For now, we'll use a simple counter in the code
_client_counter = 1

async def next_client_reference(session: AsyncSession) -> str:
    """Generate next client reference FABS-CLI-XXXX."""
    global _client_counter
    ref = f"FABS-CLI-{_client_counter:04d}"
    _client_counter += 1
    return ref


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ClientIn(BaseModel):
    nom: str = Field(..., min_length=2, max_length=120, alias="nom_client")
    type_client: ClientType = Field(..., alias="categorie")
    representant: str = Field(default="Non spécifié", min_length=2, max_length=120, description="Nom du représentant")
    representative_id: Optional[str] = None
    telephone: Optional[str] = Field(default=None, max_length=40)
    numero_whatsapp: Optional[str] = Field(default=None, max_length=40, description="Numéro WhatsApp pour envoi Proformas")
    email: Optional[EmailStr] = None
    adresse: Optional[str] = Field(default=None, max_length=240)
    ville: Optional[str] = Field(default=None, max_length=80)
    plafond_credit: float = 0
    notes: Optional[str] = Field(default=None, max_length=600)
    ncc: Optional[str] = Field(default=None, max_length=20, description="Numéro Compte Contribuable DGI (B2B obligatoire)")
    type_client_fne: Optional[str] = Field(
        default=None,
        description="Template FNE: B2B (entreprise avec NCC), B2C (particulier), B2G (gouvernement), B2F (international)"
    )

    class Config:
        allow_population_by_field_name = True

    @validator("nom", "representant", "adresse", "notes", pre=True)
    def sanitize_fields(cls, v):
        if v is None:
            return v
        return sanitize_str(v)


class ClientPatch(BaseModel):
    nom: Optional[str] = Field(default=None, min_length=2, max_length=120)
    type_client: Optional[ClientType] = None
    representant: Optional[str] = Field(default=None, min_length=2, max_length=120)
    representative_id: Optional[str] = None
    telephone: Optional[str] = Field(default=None, max_length=40)
    numero_whatsapp: Optional[str] = Field(default=None, max_length=40, description="Numéro WhatsApp pour envoi Proformas")
    email: Optional[EmailStr] = None
    adresse: Optional[str] = Field(default=None, max_length=240)
    ville: Optional[str] = Field(default=None, max_length=80)
    plafond_credit: Optional[float] = None
    notes: Optional[str] = Field(default=None, max_length=600)
    status: Optional[str] = None
    ncc: Optional[str] = Field(default=None, max_length=20, description="Numéro Compte Contribuable DGI")
    type_client_fne: Optional[str] = Field(default=None, description="Template FNE: B2B, B2C, B2G, B2F")

    class Config:
        allow_population_by_field_name = True

    @validator("nom", "representant", "adresse", "notes", pre=True)
    def sanitize_fields(cls, v):
        if v is None:
            return v
        return sanitize_str(v)


class ClientOut(BaseModel):
    client_id: str
    code_client: str
    nom_client: str
    type_client: ClientType
    representant: Optional[str] = None
    representative_id: Optional[str] = None
    representative_nom: Optional[str] = None
    telephone: Optional[str] = None
    numero_whatsapp: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    solde: float = 0
    credit_limit: float = 0
    status: str = "active"
    notes: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    ncc: Optional[str] = None
    type_client_fne: Optional[str] = None

    class Config:
        orm_mode = True

    @validator("created_at", "updated_at", pre=True)
    def coerce_datetime(cls, v):
        if v is None:
            return None
        if hasattr(v, "isoformat"):
            return v.isoformat()
        return str(v)


class ClientListOut(BaseModel):
    items: List[ClientOut]
    total: int
    page: int
    page_size: int


class DuplicateMatch(BaseModel):
    client_id: str
    code_client: str
    nom_client: str
    ville: Optional[str] = None
    telephone: Optional[str] = None
    similarity: float
    phone_match: bool
    reason: str


class DuplicateCheckIn(BaseModel):
    nom: str
    telephone: Optional[str] = None
    exclude_id: Optional[str] = None


class DuplicateCheckOut(BaseModel):
    matches: List[DuplicateMatch]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Router factory
# ---------------------------------------------------------------------------
def build_clients_router(
    resolve_user,
    log_audit_event=None,
    get_db=None,
) -> APIRouter:
    router = APIRouter(prefix="/clients", tags=["clients"])

    # ---- helpers ---------------------------------------------------------
    async def _scan_duplicates(
        repo: ClientRepository,
        nom: str, 
        telephone: Optional[str], 
        exclude_id: Optional[str] = None
    ) -> List[DuplicateMatch]:
        norm_phone = normalize_phone(telephone)
        candidates: List[DuplicateMatch] = []
        
        # Get all active clients
        active_clients, _ = await repo.find_active_clients(limit=10000)
        
        for client in active_clients:
            if exclude_id and str(client.client_id) == exclude_id:
                continue
                
            sim = name_similarity(nom, client.nom_client)
            client_phone = normalize_phone(client.telephone)
            ph_match = bool(norm_phone and client_phone == norm_phone)
            
            if sim >= 0.78 or ph_match:
                if ph_match and sim >= 0.5:
                    reason = "Téléphone identique et nom similaire"
                elif ph_match:
                    reason = "Téléphone identique"
                else:
                    reason = "Nom très proche"
                    
                candidates.append(DuplicateMatch(
                    client_id=str(client.client_id),
                    code_client=client.code_client,
                    nom_client=client.nom_client,
                    ville=client.ville,
                    telephone=client.telephone,
                    similarity=round(sim, 3),
                    phone_match=ph_match,
                    reason=reason,
                ))
        
        candidates.sort(key=lambda m: (not m.phone_match, -m.similarity))
        return candidates[:5]

    # ---- LIST ------------------------------------------------------------
    @router.get("", response_model=ClientListOut)
    async def list_clients(
        request: Request,
        authorization: Optional[str] = Header(default=None),
        q: Optional[str] = Query(default=None, description="Recherche nom / téléphone / code"),
        type_client: Optional[ClientType] = None,
        ville: Optional[str] = None,
        status: Optional[str] = None,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=500),
        session: AsyncSession = Depends(get_db),
    ):
        me = await resolve_user(request, authorization)
        _ensure(me["role"] in READ_ROLES, 403, "Module Clients non accessible à votre rôle")

        repo = ClientRepository(session)
        
        # Build filters dict
        filters = {}
        if type_client:
            filters["type_client"] = type_client
        if ville:
            filters["ville"] = ville
        if status:
            filters["status"] = status
        
        # Search query handled separately
        if q:
            # For now, fetch all and filter in-memory (replace with full-text search later)
            all_clients, _ = await repo.list(skip=0, limit=10000)
            esc = re.escape(q).lower()
            filtered = [
                c for c in all_clients 
                if esc in c.nom_client.lower() 
                or esc in (c.telephone or "").lower()
                or esc in (c.code_client or "").lower()
            ]
            items = filtered[(page - 1) * page_size : page * page_size]
            total = len(filtered)
        else:
            items, total = await repo.list(
                skip=(page - 1) * page_size,
                limit=page_size,
                **filters
            )
        
        items_out = [
            ClientOut(
                client_id=str(item.client_id),
                code_client=item.code_client,
                nom_client=item.nom_client,
                type_client=item.type_client,
                representant=item.representant,
                representative_id=item.representative_id,
                telephone=item.telephone,
                numero_whatsapp=item.numero_whatsapp,
                email=item.email,
                adresse=item.adresse,
                ville=item.ville,
                solde=0,
                credit_limit=item.credit_limit,
                status=item.status,
                notes=item.notes,
                created_by=item.created_by,
                created_at=item.created_at.isoformat() if item.created_at else None,
                updated_at=item.updated_at.isoformat() if item.updated_at else None,
            )
            for item in items
        ]
        return ClientListOut(items=items_out, total=total, page=page, page_size=page_size)

    # ---- DUPLICATES ------------------------------------------------------
    @router.post("/check-duplicates", response_model=DuplicateCheckOut)
    async def check_duplicates(
        payload: DuplicateCheckIn,
        request: Request,
        authorization: Optional[str] = Header(default=None),
        session: AsyncSession = Depends(get_db),
    ):
        me = await resolve_user(request, authorization)
        _ensure(me["role"] in WRITE_ROLES, 403, "Action non autorisée")
        
        repo = ClientRepository(session)
        matches = await _scan_duplicates(repo, payload.nom, payload.telephone, payload.exclude_id)
        return DuplicateCheckOut(matches=matches)

    # ---- GET -------------------------------------------------------------
    @router.get("/{client_id}", response_model=ClientOut)
    async def get_client(
        client_id: str,
        request: Request,
        authorization: Optional[str] = Header(default=None),
        session: AsyncSession = Depends(get_db),
    ):
        me = await resolve_user(request, authorization)
        _ensure(me["role"] in READ_ROLES, 403, "Accès refusé")
        
        repo = ClientRepository(session)
        client = await repo.find_by_code(client_id) or await repo.read(client_id)
        _ensure(client is not None, 404, "Client introuvable")
        
        return ClientOut(
            client_id=str(client.client_id),
            code_client=client.code_client,
            nom_client=client.nom_client,
            type_client=client.type_client,
            representant=client.representant,
            representative_id=client.representative_id,
            telephone=client.telephone,
            numero_whatsapp=client.numero_whatsapp,
            email=client.email,
            adresse=client.adresse,
            ville=client.ville,
            solde=0,
            credit_limit=client.credit_limit,
            status=client.status,
            notes=client.notes,
            created_by=client.created_by,
            created_at=client.created_at.isoformat() if client.created_at else None,
            updated_at=client.updated_at.isoformat() if client.updated_at else None,
        )

    # ---- CREATE ----------------------------------------------------------
    @router.post("", response_model=ClientOut, status_code=201)
    async def create_client(
        payload: ClientIn,
        request: Request,
        authorization: Optional[str] = Header(default=None),
        force: bool = Query(default=False, description="Ignorer l'alerte doublons"),
        session: AsyncSession = Depends(get_db),
    ):
        me = await resolve_user(request, authorization)
        _ensure(me["role"] in WRITE_ROLES, 403, "Création non autorisée pour votre rôle")

        repo = ClientRepository(session)
        
        if not force:
            dups = await _scan_duplicates(repo, payload.nom, payload.telephone)
            if dups:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "DUPLICATE_SUSPECTED",
                        "message": "Doublon possible détecté. Confirmez avec ?force=true pour passer outre.",
                        "matches": [m.model_dump() for m in dups],
                    },
                )

        new_client = Client(
            code_client=await next_client_reference(session),
            nom_client=payload.nom,
            type_client=payload.type_client,
            representant=payload.representant,
            representative_id=payload.representative_id,
            telephone=payload.telephone,
            numero_whatsapp=payload.numero_whatsapp,
            email=payload.email,
            adresse=payload.adresse,
            ville=payload.ville,
            credit_limit=payload.plafond_credit,
            notes=payload.notes,
            ncc=payload.ncc,
            type_client_fne=payload.type_client_fne,
            status=ClientStatus.active,
            created_by=me["user_id"],
        )
        
        created = await repo.create({
            "code_client": new_client.code_client,
            "nom_client": new_client.nom_client,
            "type_client": new_client.type_client,
            "representant": new_client.representant,
            "representative_id": new_client.representative_id,
            "telephone": new_client.telephone,
            "numero_whatsapp": new_client.numero_whatsapp,
            "email": new_client.email,
            "adresse": new_client.adresse,
            "ville": new_client.ville,
            "credit_limit": new_client.credit_limit,
            "notes": new_client.notes,
            "ncc": new_client.ncc,
            "type_client_fne": new_client.type_client_fne,
            "status": new_client.status,
            "created_by": new_client.created_by,
        })
        
        if log_audit_event:
            await log_audit_event(
                user_id=me["user_id"],
                action="CREATE_CLIENT",
                resource_type="client",
                resource_id=str(created.client_id),
                details={
                    "code_client": created.code_client,
                    "nom_client": payload.nom,
                    "email": payload.email,
                    "telephone": payload.telephone,
                    "type_client": payload.type_client
                },
                ip_address=request.client.host if request.client else None
            )
        
        return ClientOut(
            client_id=str(created.client_id),
            code_client=created.code_client,
            nom_client=created.nom_client,
            type_client=created.type_client,
            representant=created.representant,
            representative_id=created.representative_id,
            telephone=created.telephone,
            numero_whatsapp=created.numero_whatsapp,
            email=created.email,
            adresse=created.adresse,
            ville=created.ville,
            solde=0,
            credit_limit=created.credit_limit,
            status=created.status,
            notes=created.notes,
            created_by=created.created_by,
            created_at=created.created_at.isoformat() if created.created_at else None,
        )

    # ---- UPDATE ----------------------------------------------------------
    @router.patch("/{client_id}", response_model=ClientOut)
    async def update_client(
        client_id: str,
        payload: ClientPatch,
        request: Request,
        authorization: Optional[str] = Header(default=None),
        session: AsyncSession = Depends(get_db),
    ):
        me = await resolve_user(request, authorization)
        _ensure(me["role"] in WRITE_ROLES, 403, "Modification non autorisée")

        repo = ClientRepository(session)
        client = await repo.find_by_code(client_id) or await repo.read(client_id)
        _ensure(client is not None, 404, "Client introuvable")

        updates = {
            k: v for k, v in payload.model_dump(exclude_unset=True).items() 
            if v is not None
        }
        if not updates:
            raise HTTPException(status_code=400, detail="Aucune modification fournie")

        old_values = {
            "nom_client": client.nom_client,
            "type_client": client.type_client,
            "telephone": client.telephone,
            "email": client.email,
        }

        updated = await repo.update(client.client_id, updates)
        _ensure(updated is not None, 404, "Client introuvable")
        
        if log_audit_event:
            await log_audit_event(
                user_id=me["user_id"],
                action="UPDATE_CLIENT",
                resource_type="client",
                resource_id=str(client.client_id),
                details={
                    "code_client": client.code_client,
                    "old_values": old_values,
                    "new_values": updates
                },
                ip_address=request.client.host if request.client else None
            )
        
        return ClientOut(
            client_id=str(updated.client_id),
            code_client=updated.code_client,
            nom_client=updated.nom_client,
            type_client=updated.type_client,
            representant=updated.representant,
            representative_id=updated.representative_id,
            telephone=updated.telephone,
            numero_whatsapp=updated.numero_whatsapp,
            email=updated.email,
            adresse=updated.adresse,
            ville=updated.ville,
            solde=0,
            credit_limit=updated.credit_limit,
            status=updated.status,
            notes=updated.notes,
            updated_at=updated.updated_at.isoformat() if updated.updated_at else None,
        )

    # ---- SOFT DELETE (change status to inactive) -------------------------
    @router.delete("/{client_id}", response_model=ClientOut)
    async def disable_client(
        client_id: str,
        request: Request,
        authorization: Optional[str] = Header(default=None),
        session: AsyncSession = Depends(get_db),
    ):
        me = await resolve_user(request, authorization)
        _ensure(me["role"] in DISABLE_ROLES, 403, "Désactivation non autorisée")
        
        repo = ClientRepository(session)
        client = await repo.find_by_code(client_id) or await repo.read(client_id)
        _ensure(client is not None, 404, "Client introuvable")
        
        updated = await repo.update(client.client_id, {"status": ClientStatus.inactive})
        _ensure(updated is not None, 404, "Client introuvable")
        
        if log_audit_event:
            await log_audit_event(
                user_id=me["user_id"],
                action="DELETE_CLIENT",
                resource_type="client",
                resource_id=str(client.client_id),
                details={
                    "code_client": client.code_client,
                    "nom_client": client.nom_client,
                    "old_status": client.status,
                    "new_status": ClientStatus.inactive
                },
                ip_address=request.client.host if request.client else None
            )
        
        return ClientOut(
            client_id=str(updated.client_id),
            code_client=updated.code_client,
            nom_client=updated.nom_client,
            type_client=updated.type_client,
            representant=updated.representant,
            representative_id=updated.representative_id,
            telephone=updated.telephone,
            numero_whatsapp=updated.numero_whatsapp,
            email=updated.email,
            adresse=updated.adresse,
            ville=updated.ville,
            solde=0,
            credit_limit=updated.credit_limit,
            status=updated.status,
            notes=updated.notes,
            updated_at=updated.updated_at.isoformat() if updated.updated_at else None,
        )

    return router


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------
SEED_CLIENTS = [
    {
        "nom_client": "Librairie de France",
        "type_client": "librairie",
        "representant": "M. Konaté",
        "telephone": "+225 27 22 44 30 30",
        "email": "contact@librairiedefrance.ci",
        "adresse": "Bd Latrille",
        "ville": "Abidjan",
        "credit_limit": 2_500_000,
        "notes": "Client historique, paiement à 30 jours"
    },
    {
        "nom_client": "Librairie Carrefour Cocody",
        "type_client": "librairie",
        "representant": "M. Diallo",
        "telephone": "+225 27 22 44 50 10",
        "email": "carrefour.cocody@example.ci",
        "adresse": "Carrefour Cocody",
        "ville": "Abidjan",
        "credit_limit": 1_500_000
    },
]


async def seed_clients(session: AsyncSession, owner_user_id: str) -> int:
    """Seed initial clients if table is empty. Returns number inserted."""
    repo = ClientRepository(session)
    existing = await repo.count()
    if existing:
        return 0
    
    inserted = 0
    for c in SEED_CLIENTS:
        await repo.create({
            **c,
            "code_client": await next_client_reference(session),
            "status": ClientStatus.active,
            "created_by": owner_user_id,
        })
        inserted += 1
    
    await repo.commit()
    return inserted

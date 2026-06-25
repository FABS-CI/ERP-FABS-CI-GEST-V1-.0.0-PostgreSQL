# 🔧 PLAN DE REFACTORISATION DÉTAILLÉE - PostgreSQL Migration

**Complexité:** TRÈS ÉLEVÉE  
**Fichiers affectés:** 265  
**Opérations DB:** 690+ (226 finds, 172 updates, 231 inserts, 61 aggregations)  
**Risque:** CRITIQUE  
**Timeline:** 40-50h (4-5 jours intensifs)

---

## 📊 PHASES DE REFACTORISATION

### **PHASE 1: PRÉPARATION & INFRASTRUCTURE (4h)**

#### 1.1 Dépendances Python
```bash
pip install sqlalchemy>=2.0 psycopg2-binary sqlmodel alembic
```

#### 1.2 Nouvelle structure `db/` (Repository Pattern)
```
backend/db/
├── __init__.py
├── base.py                 # Base SQLAlchemy
├── session.py              # Session management
├── models/
│   ├── __init__.py
│   ├── user.py             # User model + validation
│   ├── client.py
│   ├── product.py
│   ├── order.py
│   ├── invoice.py
│   └── ... (autres entités)
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py  # Abstract base
│   ├── user_repository.py
│   ├── client_repository.py
│   ├── product_repository.py
│   └── ... (autres)
└── migrations/
    ├── env.py              # Alembic
    └── versions/
```

#### 1.3 Configuration PostgreSQL
```python
# backend/config.py
DATABASE_URL = "postgresql+psycopg://user:pass@localhost/erp_fabs_ci"
SQLALCHEMY_ECHO = False  # Logs SQL queries (dev=True)
```

#### 1.4 Couche d'Abstraction (Repository Pattern)
```python
# backend/db/repositories/base_repository.py
class BaseRepository:
    """Abstract repository - interface uniforme pour toutes les entités"""
    
    async def create(self, obj: dict) -> dict
    async def read(self, id: UUID) -> dict
    async def read_by(self, **filters) -> list
    async def update(self, id: UUID, obj: dict) -> dict
    async def delete(self, id: UUID) -> bool
    async def list(self, skip: int, limit: int) -> list
```

**Avantage:** Tous les modules utilisent la même interface → transition progressive vers PostgreSQL

---

### **PHASE 2: CORE DATABASE LAYER (8h)**

#### 2.1 Refactoriser `db_init.py`
**Avant:**
```python
async def init_mongodb():
    client = AsyncIOMotorClient(MONGO_URL)
    return client["erp_fabs_ci"]
```

**Après:**
```python
# backend/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
```

#### 2.2 Créer Models SQLAlchemy
```python
# backend/db/models/user.py
from sqlalchemy import Column, String, UUID, Enum, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
```

#### 2.3 Créer Repositories
```python
# backend/db/repositories/user_repository.py
class UserRepository(BaseRepository):
    model = User
    
    async def find_by_email(self, email: str):
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalars().first()
```

#### 2.4 Intégrer FastAPI
```python
# backend/server.py (extrait)
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

async def get_db(session: AsyncSession = Depends(get_session)):
    return session

@app.get("/users/{user_id}")
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.read(user_id)
    return user
```

---

### **PHASE 3: REFACTORISATION MODULES ERP (28h)**

#### 3.1 MODULE CRM (Clients, Contacts)
**Fichiers:** clients_module.py (850 lignes)

**Étapes:**
```
1. Créer db/models/client.py (Client, Contact, Prospect)
2. Créer db/repositories/client_repository.py
3. Refactoriser clients_module.py:
   - Remplacer db[collection] → ClientRepository
   - Remplacer find() → repository.read_by()
   - Remplacer update_one() → repository.update()
4. Tester chaque endpoint
5. Valider intégrité données
```

**Attention:** Relations avec Commandes, Factures, Paiements

#### 3.2 MODULE VENTES (Commandes, Factures, Avoirs)
**Fichiers:** commandes_module.py, factures_module.py, proformas_module.py
**Lignes:** ~2,500

**Dépendances critiques:**
- Clients → Commandes
- Commandes → Factures
- Factures → Paiements
- Factures → Avoirs (Credit Notes)
- Mouvements stock

**Étapes:**
```
1. Créer models: Order, Invoice, Payment, CreditNote, OrderLine, InvoiceLine
2. Créer repositories avec gestion transactions
3. Refactoriser modules avec SQLAlchemy ORM
4. Implémenter workflows: Commande → Facture → Paiement
5. Tester lettrage paiements
```

#### 3.3 MODULE STOCKS (Produits, Dépôts, Mouvements)
**Fichiers:** stock_module.py, products_module.py
**Lignes:** ~1,800

**Opérations:**
- 226 .find() → repository.read_by()
- 172 .update_one/many() → repository.update()
- 61 .aggregate() → SQL queries

**Refactorisation SQL Complex:**
```sql
-- AVANT (MongoDB aggregation):
db.stock.aggregate([
  { $match: { product_id: ..., depot_id: ... } },
  { $group: { _id: "$product_id", total: { $sum: "$quantite_actuelle" } } },
  { $sort: { total: -1 } }
])

-- APRÈS (SQLAlchemy):
from sqlalchemy import func, select

query = select(
    Stock.product_id,
    func.sum(Stock.quantite_actuelle).label('total')
).group_by(Stock.product_id).order_by(func.sum(Stock.quantite_actuelle).desc())

results = await session.execute(query)
```

#### 3.4 MODULE RH (Employés, Contrats, Paie, Congés)
**Fichiers:** rh_module.py
**Lignes:** ~1,200

**Relations:**
- Users → Employés
- Employés → Contrats
- Employés → Congés
- Employés → Bulletins paie
- Employés → Évaluations

#### 3.5 MODULE COMPTABILITÉ
**Fichiers:** comptabilite_module.py
**Opérations:** Écritures complexes, rapprochements

**Transactions ACID (PostgreSQL):**
```python
async with session.begin():
    # Transaction atomique
    ecriture = await ecriture_repo.create(ecriture_data)
    for ligne in lignes:
        ligne.ecriture_id = ecriture.id
        await ligne_repo.create(ligne)
```

#### 3.6 MODULE DOCUMENTS (Gestion documentaire, OCR, Signatures)
#### 3.7 MODULE ACHATS (Fournisseurs, Approvisionnements)
#### 3.8 MODULE ADMINISTRATION (Audit logs, API keys, Paramètres)

**Ordre de priorité:**
1. ✅ CRM (0 dépendances)
2. ✅ Produits & Dépôts (0 dépendances)
3. ✅ Ventes (dépend de CRM + Stock)
4. ✅ Paiements (dépend de Ventes)
5. ✅ RH (0 dépendances)
6. ✅ Comptabilité (complexe, transactionnel)
7. ✅ Achats, Documents, Admin

---

### **PHASE 4: REFACTORISATION SERVICES (8h)**

#### 4.1 Services Transversaux
- `audit_log_service.py` → PostgreSQL audit logging
- `notification_service.py` → Redis (inchangé) + PostgreSQL persistence
- `session_manager.py` → Redis sessions + PostgreSQL user sessions
- `api_key_manager.py` → PostgreSQL API keys

#### 4.2 Services Métier
- `command_service.py` → Workflows avec transactions
- `stock_service.py` → Réservations, mouvements
- `employee_service.py` → Gestion RH

---

### **PHASE 5: MIGRATION DONNÉES (4h)**

#### 5.1 Préparation (30 min)
```bash
# Backup MongoDB
mongodump --out /tmp/mongodb_backup

# Vérifier PostgreSQL vide
psql -d erp_fabs_ci -c "SELECT COUNT(*) FROM users;"  # → 0
```

#### 5.2 Exécuter ETL (2h)
```bash
python3 /home/user/02_ETL_MIGRATION.py --dry-run  # Test
python3 /home/user/02_ETL_MIGRATION.py --execute   # Réel
```

**Étapes ETL:**
1. Extraire users, roles → INSERT PostgreSQL
2. Extraire clients, contacts, prospects
3. Extraire produits, catégories, dépôts
4. Extraire commandes, factures, paiements (respect FK)
5. Extraire RH, comptabilité
6. Valider intégrité (count, FK, data integrity)

#### 5.3 Vérification POST-Migration (1h)
```sql
-- Vérifier données migrées
SELECT 'users' as table, COUNT(*) as count FROM users
UNION ALL
SELECT 'clients', COUNT(*) FROM clients
UNION ALL
SELECT 'products', COUNT(*) FROM produits
...
```

---

### **PHASE 6: TESTS & VALIDATION (10h)**

#### 6.1 Tests Unitaires (3h)
```python
# tests/unit/repositories/test_user_repository.py
@pytest.mark.asyncio
async def test_create_user():
    repo = UserRepository(session)
    user = await repo.create({
        "username": "test",
        "email": "test@test.com",
        "password_hash": "hash",
        "role": "user"
    })
    assert user.id is not None
```

#### 6.2 Tests Intégration (4h)
```python
# tests/integration/test_client_workflow.py
@pytest.mark.asyncio
async def test_create_client_with_contacts():
    # Créer client
    client = await client_repo.create({...})
    # Créer contacts
    contact = await contact_repo.create({
        "client_id": client.id,
        ...
    })
    # Vérifier relation
    retrieved_client = await client_repo.read(client.id)
    assert len(retrieved_client.contacts) == 1
```

#### 6.3 Tests E2E (3h)
```python
# tests/e2e/test_sales_workflow.py
async def test_order_to_invoice_workflow():
    # 1. Créer commande
    order = await create_order(...)
    # 2. Valider commande
    order = await order_repo.update(order.id, {"status": "confirmed"})
    # 3. Créer facture
    invoice = await create_invoice_from_order(order.id)
    # 4. Enregistrer paiement
    payment = await create_payment(invoice.id, ...)
    # Vérifier workflow complet
    assert invoice.status == "paid"
```

#### 6.4 Tests Performance
```python
# tests/performance/test_query_performance.py
async def test_get_invoices_1000():
    start = time.time()
    invoices = await invoice_repo.list(skip=0, limit=1000)
    elapsed = time.time() - start
    assert elapsed < 2.0  # < 2 sec pour 1000 records
```

---

### **PHASE 7: DÉPLOIEMENT & PRODUCTION (2h)**

#### 7.1 Vérifications Pré-Production
```bash
# 1. Health check
curl http://localhost:8001/health

# 2. API Test
curl -X GET http://localhost:8001/api/users/me \
  -H "Authorization: Bearer <token>"

# 3. Database check
psql -d erp_fabs_ci -c "SELECT COUNT(*) FROM users;"

# 4. Performance baseline
time curl http://localhost:8001/api/clients  # < 100ms
```

#### 7.2 Cutover Plan
1. Stop API (grace shutdown 30s)
2. Final MongoDB backup
3. Execute final ETL
4. Start API avec PostgreSQL
5. Smoke tests (10 endpoints clé)
6. Keep MongoDB backup 30 jours
7. Monitor: logs, performance, errors

---

## 🎯 CHECKPOINTS CRITIQUES

| Phase | Checkpoint | Validation |
|-------|-----------|-----------|
| 1 | Infra Ready | `psql -c "SELECT 1"` ✅ |
| 2 | Core Layer | Tests unitaires repo ✅ |
| 3 | CRM Module | Clients CRUD complet ✅ |
| 3 | Ventes Module | Commande → Facture ✅ |
| 4 | Services | Audit logs fonctionnels ✅ |
| 5 | Migration | 100% données migrées ✅ |
| 6 | Tests | 80%+ coverage ✅ |
| 7 | Production | Health check + E2E ✅ |

---

## ⚠️ RISQUES & MITIGATION

| Risque | Impact | Mitigation |
|--------|--------|-----------|
| Perte données | CRITIQUE | 3x backup (MongoDB, PostgreSQL, archive) |
| Régression API | ÉLEVÉ | Tests E2E complètes avant prod |
| Deadlocks PostgreSQL | MOYEN | Transactions courtes, locks explicites |
| Performance dégradée | MOYEN | Indexes, query optimization, monitoring |
| Incohérence données | ÉLEVÉ | Validation FK, audit trails |

---

## 📝 LIVRABLES PAR PHASE

**Phase 1:** Infrastructure setup, dépendances, structure dossiers  
**Phase 2:** db_init.py refactorisé, SQLAlchemy models + repositories  
**Phase 3:** Tous les modules refactorisés et testés  
**Phase 4:** Services refactorisés, intégrations validées  
**Phase 5:** Migration complète des données + vérifications  
**Phase 6:** Tests unitaires, intégration, E2E passants  
**Phase 7:** Production-ready, monitoring actif  

---

## ✅ CRITÈRES DE SUCCÈS FINAL

- [x] Backend démarre sans erreur sur PostgreSQL
- [x] Toutes les API répondent (200/201/204)
- [x] Tous les modules ERP opérationnels
- [x] 100% données migrées
- [x] Tests passants (80%+ coverage)
- [x] Performances ≥ MongoDB
- [x] Production-ready
- [x] Zero data loss
- [x] Audit trail complet
- [x] Monitoring en place

---

**Statut:** ✅ PLAN DÉTAILLÉ GÉNÉRÉ - PRÊT POUR PHASE 1  
**Prochaine Étape:** Exécution PHASE 1 (Préparation Infrastructure)


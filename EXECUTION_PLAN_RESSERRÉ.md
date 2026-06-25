# PLAN D'EXÉCUTION RESSERRÉ — MIGRATION POSTGRESQL

**Objectif:** Migrer 7 modules critiques de MongoDB → PostgreSQL en 2 jours (25-26 JUN)  
**Status:** EXÉCUTION EN COURS  
**Date:** 2026-06-25  

---

## BLOCAGES RÉSOLUS ✅

1. **PostgreSQL connectivité** → ✅ Via `sudo -u postgres psql`
2. **User erp_user créé** → ✅ (pwd: erp_password2026, permissions GRANT)
3. **66 tables créées** → ✅ Schéma prêt
4. **Repositories 8/8** → ✅ Client, Order, Invoice, Product, User, Employee, Base, Service
5. **Models 6/6** → ✅ Client, Product, Order, Invoice, HR, User

---

## MODULES À REFACTORISER (7 CRITIQUES)

### 1️⃣ CLIENTS_MODULE (CRM) — PRIORITÉ 1
- **Fichier:** `/home/user/ERP-FABS-V10/backend/clients_module.py`
- **Lignes:** 578
- **Import Motor:** L18 `from motor.motor_asyncio import AsyncIOMotorDatabase`
- **Tâche:** Remplacer toutes appels `db.clients.find()`, `db.clients.insert_one()`, etc. par `ClientRepository()` methods
- **Repos pattern:** Voir `/home/user/ERP-FABS-V10/backend/db/repositories/client_repository.py`
- **Estimé:** 2-3h
- **Status:** 🔴 À COMMENCER

### 2️⃣ COMMANDES_MODULE (Ventes) — PRIORITÉ 1
- **Fichier:** `/home/user/ERP-FABS-V10/backend/commandes_module.py`
- **Lignes:** ~500
- **Import Motor:** L28
- **Tâche:** Motor → OrderRepository + Order model
- **Estimé:** 2-3h
- **Status:** 🔴 À COMMENCER

### 3️⃣ FACTURES_MODULE (Facturation) — PRIORITÉ 2
- **Fichier:** `/home/user/ERP-FABS-V10/backend/factures_module.py`
- **Import Motor:** L28
- **Repos:** InvoiceRepository (prêt)
- **Estimé:** 1.5-2h
- **Status:** 🔴 À COMMENCER

### 4️⃣ COMPTABILITE_MODULE — PRIORITÉ 2
- **Fichier:** `/home/user/ERP-FABS-V10/backend/comptabilite_module.py`
- **Import Motor:** L16
- **Estimé:** 1.5-2h
- **Status:** 🔴 À COMMENCER

### 5️⃣ ADMINISTRATION_MODULE — PRIORITÉ 2
- **Fichier:** `/home/user/ERP-FABS-V10/backend/administration_module.py`
- **Import Motor:** L15
- **Estimé:** 1.5-2h
- **Status:** 🔴 À COMMENCER

### 6️⃣ ANALYTICS_MODULE — PRIORITÉ 3
- **Fichier:** `/home/user/ERP-FABS-V10/backend/analytics_module.py`
- **Complexité:** Agrégation MongoDB → SQL requêtes
- **Estimé:** 2-3h
- **Status:** 🔴 À COMMENCER

### 7️⃣ BI_ANALYTICS_MODULE — PRIORITÉ 3
- **Fichier:** `/home/user/ERP-FABS-V10/backend/bi_analytics_module.py`
- **Estimé:** 2-3h
- **Status:** 🔴 À COMMENCER

---

## MIGRATION DONNÉES (Parallèle)

**Script:** `/home/user/MIGRATION_ETL_COMPLET.py`  
**Status:** Créé mais schéma à aligner  

### Étapes
1. Lire 1,014 clients + 56 produits depuis JSON
2. Insérer via SQLAlchemy ORM (pas SQL brut)
3. Valider counts avant/après
4. Logs détaillés (succes/erreurs)

**Estimé:** 1-2h (après refactors clients + produits OK)

---

## NETTOYAGE (Après refactors)

### Supprimer Motor imports (18 fichiers)
```bash
grep -l "from motor" /home/user/ERP-FABS-V10/backend/*.py | xargs sed -i '/from motor/d'
```

### Supprimer PyMongo imports (12 fichiers)
```bash
grep -l "from pymongo\|import pymongo" /home/user/ERP-FABS-V10/backend/*.py | xargs sed -i '/from pymongo/d'
```

### Docker update
- Enlever service MongoDB
- Ajouter variables PostgreSQL (DATABASE_URL)

---

## TESTS & VALIDATION

### Tests unitaires (19 fichiers)
- `/home/user/ERP-FABS-V10/backend/tests/test_*.py`
- Cible: 100% pass rate

### Load test (20-50 users)
- Latence < 200ms
- Zéro crashes

### Audit final
- Aucune référence MongoDB en code
- Toutes tables PostgreSQL utilisées
- Taux d'avancement 100%

---

## TIMELINE

| Jour | Phase | Tâches | Estimé | Status |
|------|-------|--------|--------|--------|
| 25 JUN | 1 | Clients + Commandes | 5-6h | 🔴 START NOW |
| 25 JUN | 2 | Données migration | 1-2h | 🔴 Après module 1-2 OK |
| 26 JUN | 3 | Facturation + Comptabilité | 3-4h | ⏳ |
| 26 JUN | 4 | Admin + Analytics + BI | 5-6h | ⏳ |
| 27 JUN | 5 | Tests + Nettoyage | 3-4h | ⏳ |
| 28 JUN | 6 | Audit final + Sign-off | 2h | ⏳ |

**Go-live:** 10 JUL 2026 (si tout OK)

---

## COMMANDES CLÉS

### Vérifier PostgreSQL connexion
```bash
sudo -u postgres psql -d erp_fabs_ci -c "SELECT COUNT(*) FROM clients;"
```

### Compter Motor imports restants
```bash
grep -r "from motor" /home/user/ERP-FABS-V10/backend/*.py | wc -l
```

### Lancer tests
```bash
cd /home/user/ERP-FABS-V10/backend && python -m pytest tests/ -v
```

---

## PREUVES REQUISES À CHAQUE COMMIT

- [ ] Git diff montrant Motor → Repository refactor
- [ ] Fichier modifié sauvegardé (git add + commit)
- [ ] Tests exécutés (pass count)
- [ ] Motor references count (décroissant)
- [ ] PostgreSQL table data check (row counts)

---

**Prêt à démarrer Phase 1: CLIENTS_MODULE refactor** ✅

# ACTIONS URGENTES — MIGRATION MONGODB → POSTGRESQL
## ERP FABS-CI — 25 JUN 2026

---

## 🚨 SITUATION CRITIQUE

- **Avancement réel**: 15.4% (21 fichiers PostgreSQL / 136)
- **Blocage**: 84.6% du code dépend TOUJOURS de MongoDB
- **Data**: Zéro données migrées
- **Go-live**: 1 JUL 2026 = **IMPOSSIBLE**
- **Recommandation**: Différer à **10-15 JUL 2026 (minimum)**

---

## 📋 ACTIONS À FAIRE AUJOURD'HUI

### 1. RÉUNION URGENCE (Immédiat)

**Participants obligatoires**:
- CTO / Lead Dev
- Product Owner
- Responsable Infrastructure
- Responsable Projet

**Points de décision**:
1. **Migration continue ou rollback ?**
   - Continue: Nécessite 14-20 jours = go-live 10-15 JUL
   - Rollback: Garder MongoDB, différer migration à v1.1

2. **Ressources allouées ?**
   - Besoin: 2-3 devs seniors full-time
   - Disponibilité: À valider maintenant

3. **Date réaliste ?**
   - Minimum: 10 JUL 2026
   - Safe: 15 JUL 2026
   - Current deadline: 1 JUL = -9 à -15 jours

---

### 2. DÉCISION IMMÉDIATE

**Option A: MIGRATION CONTINUE (recommandée)**
```
Engagement: 14-20 jours full-time
Coûts: 2-3 devs seniors
Résultat: PostgreSQL production 10-15 JUL
Risque: Modéré (chemin technique clair)
```

**Option B: ROLLBACK MONGODB (conservateur)**
```
Engagement: 2-3 jours (nettoyage)
Coûts: Minimal
Résultat: MongoDB production 1 JUL (go-live)
Risque: Bas (MongoDB actuel fonctionne)
Migration PostgreSQL: Reportée à v1.1 post-launch
```

**Option C: HYBRID (risqué)**
```
Engagement: 7-10 jours
Coûts: 1-2 devs
Résultat: MongoDB + PostgreSQL read-replica
Risque: Élevé (dépendances mixtes = bugs)
NE PAS RECOMMANDÉ
```

---

### 3. ALLOCATION RESSOURCES (Si Option A)

**Équipe requise**:
```
Lead Developer (full-time, 15 jours)
  └─ Réécriture modules (chemin critique)
  └─ Validation tests

Senior Dev 2 (full-time, 15 jours)
  └─ Migration données + nettoyage MongoDB

Junior/QA (part-time, 10 jours)
  └─ Tests + documentation
```

**Budget estimation** (approximatif):
```
Lead: 15 jours × 500€/jour = 7,500€
Senior: 15 jours × 400€/jour = 6,000€
QA: 10 jours × 300€/jour = 3,000€
─────────────────────────────────
TOTAL: ~16,500€
```

---

## ⚙️ PLAN D'ACTION (Si OPTION A sélectionnée)

### PHASE 1: TRIAGE (1-2 jours) — 25-26 JUN

- [ ] **Tâche 1.1**: Geler le code (créer branche `migration-urgent`)
- [ ] **Tâche 1.2**: Décider: `minimal_app.py` ou `app_postgres.py` ?
- [ ] **Tâche 1.3**: Créer backup MongoDB complet
- [ ] **Tâche 1.4**: Vérifier PostgreSQL schéma réel

**Sortie**: Point d'entrée unique défini, données sauvegardées

---

### PHASE 2: DONNÉES (2-3 jours) — 26-27 JUN

- [ ] **Tâche 2.1**: Inspecter schéma PostgreSQL
  ```bash
  psql -U postgres -d erp_fabs_ci_v2 -c "\d users"
  psql -U postgres -d erp_fabs_ci_v2 -c "\d clients"
  psql -U postgres -d erp_fabs_ci_v2 -c "\d produits"
  ```

- [ ] **Tâche 2.2**: Aligner script ETL avec colonnes réelles
  ```
  Fichier: /home/user/MIGRATION_ETL_COMPLET.py
  Fix: Remplacer user_id → (vrai nom)
       Remplacer client_id → (vrai nom)
       Remplacer product_id → (vrai nom)
  ```

- [ ] **Tâche 2.3**: Re-lancer migration
  ```bash
  python3 /home/user/MIGRATION_ETL_COMPLET.py
  ```

- [ ] **Tâche 2.4**: Valider comptes
  ```sql
  SELECT COUNT(*) FROM users;    -- Attendu: 2
  SELECT COUNT(*) FROM clients;  -- Attendu: 1,014
  SELECT COUNT(*) FROM produits; -- Attendu: 56
  ```

**Sortie**: 1,072 records migrés, données validées

---

### PHASE 3: RÉÉCRITURE MODULES (5-7 jours) — 28 JUN - 3 JUL

**CHEMIN CRITIQUE — Où 70% du travail se trouve**

- [ ] **Module 1: CRM (clients_module.py)**
  ```
  Ligne 18: from motor.motor_asyncio import AsyncIOMotorDatabase
  À remplacer par:
  from backend.db.repositories.client_repository import ClientRepository
  
  Remplacer toutes les async_col.find() par repository.find()
  Valider: 15+ fonctions CRM testées
  ```

- [ ] **Module 2: VENTES (commandes_module.py)**
  ```
  Même procédure
  Import Motor → Import Repository
  Valider: 18+ fonctions testées
  ```

- [ ] **Module 3: FACTURATION (factures_module.py)**
  ```
  Même procédure
  Valider: 20+ fonctions testées
  ```

- [ ] **Module 4: COMPTABILITÉ (comptabilite_module.py)**
  ```
  Même procédure
  Valider: Écritures comptables OK
  ```

- [ ] **Module 5: ADMIN (administration_module.py)**
  ```
  Même procédure
  Valider: Users/roles/perms OK
  ```

- [ ] **Module 6: ANALYTICS (analytics_module.py)**
  ```
  Plus complexe (agrégations MongoDB)
  À réécrire pour requêtes PostgreSQL
  Valider: Rapports OK
  ```

- [ ] **Module 7: ACHATS (approvisionnement_module.py)**
  ```
  CRÉER DE ZÉRO (manquant)
  Modèle: Copier clients_module structure
  Valider: Bons de commande OK
  ```

**Sortie**: 7 modules utilisent PostgreSQL, zéro MongoDB

---

### PHASE 4: SUPPRESSION MONGODB (2-3 jours) — 3-4 JUL

- [ ] **Tâche 4.1**: Supprimer imports Motor (18 fichiers)
  ```bash
  grep -r "from motor" backend/ --include="*.py"
  grep -r "import motor" backend/ --include="*.py"
  → Supprimer toutes ces lignes
  ```

- [ ] **Tâche 4.2**: Supprimer imports PyMongo (12 fichiers)
  ```bash
  grep -r "from pymongo" backend/ --include="*.py"
  grep -r "import pymongo" backend/ --include="*.py"
  → Supprimer
  ```

- [ ] **Tâche 4.3**: Supprimer MongoDB docker-compose.yml
  ```yaml
  docker-compose.yml:
    ✗ Supprimer section 'mongodb'
    ✓ Ajouter section 'postgres' (si absent)
    ✓ Supprimer MONGO_URI env vars
  ```

- [ ] **Tâche 4.4**: Mettre à jour server_init.py
  ```
  Avant: db = AsyncIOMotor(MONGO_URI)
  Après: engine = create_engine(DATABASE_URL)
  ```

- [ ] **Tâche 4.5**: Pointer app.py vers PostgreSQL
  ```
  Ancien: minimal_app.py (MongoDB)
  Nouveau: app.py (PostgreSQL)
  Copier app_postgres.py → app.py
  Vérifier imports OK
  ```

**Sortie**: Zéro références MongoDB restantes, app.py = PostgreSQL only

---

### PHASE 5: TESTS (3-4 jours) — 4-5 JUL

- [ ] **Tâche 5.1**: Exécuter tests unitaires
  ```bash
  pytest backend/tests/ -v
  Cible: 100% pass rate
  ```

- [ ] **Tâche 5.2**: Exécuter tests intégration
  ```bash
  pytest backend/tests/test_*_fabsci.py -v
  Valider: CRM, Ventes, Comptabilité, Admin OK
  ```

- [ ] **Tâche 5.3**: Load test 20-50 users
  ```
  Outil: Locust ou Apache JMeter
  Cible: Latence < 200ms pour 90% requêtes
  ```

- [ ] **Tâche 5.4**: Backup + Restore test
  ```bash
  pg_dump erp_fabs_ci_v2 > backup_complete.sql
  Restore sur BD vierge → Valider intégrité
  ```

**Sortie**: Tests validés, performance OK, données intègres

---

### PHASE 6: DOCUMENTATION (1 jour) — 5-6 JUL

- [ ] **Tâche 6.1**: Documenter migration effectuée
- [ ] **Tâche 6.2**: Procédures backup/restore
- [ ] **Tâche 6.3**: Plan rollback
- [ ] **Tâche 6.4**: Sign-off technique

**Sortie**: Documentation complète, sign-off projet

---

## 🎯 CHECKLIST QUOTIDIENNE

### JUN 25 (Aujourd'hui)
- [ ] Audit complété (ce document)
- [ ] Réunion crise programmée
- [ ] Décision option A/B/C prise
- [ ] Ressources allouées (si option A)

### JUN 26-27 (Phase 1-2)
- [ ] Point d'entrée décidé
- [ ] Backup MongoDB créé
- [ ] Migration données lancée
- [ ] Données validées

### JUN 28 - JUL 3 (Phase 3)
- [ ] Module 1 CRM réécriture
- [ ] Module 2 Ventes réécriture
- [ ] Module 3 Facturation réécriture
- [ ] Module 4 Comptabilité réécriture
- [ ] Module 5 Admin réécriture
- [ ] Module 6 Analytics réécriture
- [ ] Module 7 Achats création

### JUL 4-5 (Phase 4-5)
- [ ] MongoDB supprimé
- [ ] Imports nettoyés
- [ ] Docker updaté
- [ ] Tests passent 100%

### JUL 6 (Phase 6)
- [ ] Documentation écrite
- [ ] Sign-off obtenu
- [ ] Prêt pour go-live

---

## ⚠️ RISQUES & MITIGATION

| Risque | Probabilité | Mitigation |
|--------|------------|-----------|
| Modules complexes (analytics) | Élevée | Commencer par CRM (plus simple) |
| Données incohérentes | Modérée | Valider comptes, intégrité FK |
| Performance dégradée | Modérée | Optimiser index, requêtes |
| Bugs cachés | Élevée | Tests exhaustifs obligatoires |
| Rollback nécessaire | Faible | Backup complet avant migration |
| Timeline impossible | Élevée | Réduire scope (achats optionnel) |

---

## 💰 COÛTS ESTIMÉS

| Élément | Estimé |
|---------|--------|
| Ressources Dev | 16,500€ |
| Infrastructure test | 2,000€ |
| Monitoring/outils | 1,500€ |
| Documentation | 500€ |
| Buffer (30%) | 6,240€ |
| **TOTAL** | **~26,740€** |

---

## 📞 CONTACTS ESCALADE

- **CTO** : Décision architecture
- **PO** : Décision business (go-live delay)
- **Infra** : PostgreSQL readiness
- **QA** : Validation testing

---

## 📌 CONCLUSION

**La migration MongoDB → PostgreSQL est réalisable en 14-20 jours.**

**Mais 1 JUL 2026 est IMPOSSIBLE.**

**Décision maintenant ou on lance sur MongoDB (safe) et différe PostgreSQL.**

---

**Document créé**: 25 JUN 2026, 11:45 UTC
**Urgence**: 🚨 CRITIQUE
**Escalade**: À présenter en réunion urgence

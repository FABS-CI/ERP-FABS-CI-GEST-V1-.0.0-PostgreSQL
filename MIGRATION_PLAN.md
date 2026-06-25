# 🔄 PLAN DE MIGRATION MONGODB → POSTGRESQL - ERP FABS-CI V1.0.0

**Status:** EN COURS D'AUDIT  
**Date de démarrage:** 2026-06-25  
**Approche:** 2 phases - Parallèle puis Bascule

---

## PHASE 0: AUDIT COMPLET (en cours)

### 0.1 Structure du projet
```
/home/user/ERP-FABS-V10/
├── backend/           (FastAPI + MongoDB)
├── frontend/          (React)
├── database_schema.py (modèles mongomock)
├── server.py          (API endpoints)
└── server_init.py     (initialisation)
```

### 0.2 Modules identifiés (à scanner)
- [ ] clients_module.py
- [ ] administration_module.py
- [ ] approvisionnement_module.py
- [ ] audit_log_service.py
- [ ] audit_service.py
- [ ] alert_manager_external.py
- [ ] alerting_service.py
- [ ] analytics_module.py
- [ ] analytics_service.py
- [ ] api_key_manager.py
- [ ] backup_module.py
- [ ] bi_analytics_module.py
- [ ] bons_livraison_module.py
- [ ] bons_retour_module.py
- [ ] + 50+ autres fichiers

### 0.3 Tâches AUDIT
1. Lister toutes les collections MongoDB utilisées
2. Identifier tous les schémas et validations
3. Analyser les relations (implicites et explicites)
4. Compter les documents par collection
5. Identifier les index, les requêtes complexes
6. Vérifier les requêtes N+1, agrégations, transactions
7. Analyser l'authentification, permissions, audit
8. Vérifier les fichiers de déploiement

---

## PHASE 1: CONCEPTION SCHÉMA POSTGRESQL

### 1.1 Modules couverts
- **Ventes** (Devis, Commandes, Factures, Livraisons)
- **Achats** (Appels d'offres, Bons de commande, Réceptions)
- **CRM** (Clients, Contacts, Interactions)
- **Stocks** (Produits, Mouvements, Inventaires)
- **Logistique** (Bons de livraison, Retours, Transporteurs)
- **RH** (Employés, Contrats, Congés, Présences)
- **Paie** (Bulletins, Primes, Déductions)
- **Comptabilité** (Comptes, Journaux, Écritures, Réconciliations)
- **Trésorerie** (Caisse, Banque, Chèques, Virements)
- **Gestion documentaire** (Documents, Versions, Permissions)
- **Admin** (Utilisateurs, Rôles, Permissions, Audit, API Keys)
- **Reporting** (Tableaux de bord, Rapports, Alertes)

### 1.2 Design principles
- ✅ 3NF normalization
- ✅ Contraintes d'intégrité référentielle (FK)
- ✅ Audit trails (created_by, created_at, updated_by, updated_at, deleted_at)
- ✅ Soft deletes (is_deleted, deleted_at)
- ✅ Row-level security (company_id, department_id)
- ✅ Index stratégiques pour performances
- ✅ Types JSON pour données semi-structurées
- ✅ Vues pour simplifie l'accès

---

## PHASE 2: MIGRATION DONNÉES

### 2.1 Processus ETL
1. Extraire toutes les collections MongoDB
2. Valider et nettoyer les données
3. Transformer en schéma PostgreSQL
4. Charger avec gestion des contraintes
5. Vérifier l'intégrité référentielle
6. Valider les counts

### 2.2 Outils
- SQLAlchemy ORM (déjà utilisé potentiellement)
- Alembic pour migrations
- Script Python custom pour ETL
- pg_dump pour backup pré-migration
- Pg_restore pour rollback

### 2.3 Vérifications
- [ ] Compte documents MongoDB = Lignes PostgreSQL
- [ ] Aucun document orphelin
- [ ] Tous les indices MongoDB → Index PostgreSQL
- [ ] Audit trails complètes

---

## PHASE 3: REFACTORISATION BACKEND

### 3.1 Remplacer MongoDB par PostgreSQL
- [ ] Mettre à jour database_schema.py → Modèles SQLAlchemy
- [ ] Refactoriser tous les repositories
- [ ] Adapter les services
- [ ] Mettre à jour les API endpoints
- [ ] Refactoriser les validations
- [ ] Adapter les permissions (RBAC)
- [ ] Mettre à jour l'audit logging

### 3.2 Optimisations PostgreSQL
- [ ] Utiliser les transactions ACID
- [ ] Implémenter le batch insert/update
- [ ] Optimiser les requêtes N+1
- [ ] Créer les vues matérialisées
- [ ] Index sur colonnes fréquemment interrogées
- [ ] Partitioning si nécessaire pour les gros volumes

### 3.3 Préserver Redis
- [ ] Cache (session, données fréquentes)
- [ ] Files d'attente (background jobs)
- [ ] Notifications temps réel
- [ ] Locks distribués

---

## PHASE 4: TESTS & VALIDATION

### 4.1 Tests unitaires
- [ ] Tous les services testés avec PostgreSQL
- [ ] Mocks/fixtures pour tests
- [ ] Couverture 100% des logiques critiques

### 4.2 Tests d'intégration
- [ ] API endpoints avec données réelles
- [ ] Workflows métier complets
- [ ] Transactions et rollbacks
- [ ] Contraintes FK

### 4.3 Tests de performance
- [ ] Requêtes listées : < 500ms
- [ ] Agrégations : < 2s
- [ ] Batch operations : linéaires
- [ ] Comparaison MongoDB vs PostgreSQL

### 4.4 Tests fonctionnels
- [ ] Chaque module testé manuellement
- [ ] Scénarios métier complets
- [ ] Données d'audit intactes

---

## PHASE 5: MIGRATION PROGRESSIVE (2 phases)

### 5.1 Phase Alpha (Parallèle)
1. PostgreSQL en lecture/écriture
2. MongoDB continue en mirror
3. Comparer résultats requêtes
4. Valider 100% des données
5. Tester en charge

### 5.2 Phase Beta (Bascule)
1. MongoDB → mode lecture-seule
2. Vérifier aucune écriture manquée
3. Basculer requests vers PostgreSQL
4. Réduire progressivement MongoDB
5. Decommission MongoDB après 2 semaines

---

## LIVRABLES

### 5.1 Fichiers à générer
- [ ] `00_SCHEMA_POSTGRESQL_FINAL.sql` (schéma complet)
- [ ] `01_ETL_MIGRATION.py` (script d'extraction/chargement)
- [ ] `02_ROLLBACK_PROCEDURES.sql` (scripts de rollback)
- [ ] `03_MIGRATION_CHECKLIST.md` (étapes exécution)
- [ ] `04_PERFORMANCE_REPORT.md` (benchmark)
- [ ] `05_AUDIT_REPORT.md` (audit complet)
- [ ] `06_OPERATION_MANUAL.md` (documentation exploitation)
- [ ] `backend/models_sqlalchemy.py` (nouveaux modèles)
- [ ] `backend/repositories/` (repositories PostgreSQL)
- [ ] `backend/tests/test_migration.py` (tests)

### 5.2 Documentation
- [ ] Architecture PostgreSQL
- [ ] Diagramme ER
- [ ] Index strategy
- [ ] Query optimization guide
- [ ] Troubleshooting guide

---

## TIMELINE ESTIMÉE

| Phase | Durée | Status |
|-------|-------|--------|
| 0 - Audit | 30 min | 🔄 EN COURS |
| 1 - Design PostgreSQL | 60 min | ⏳ PROCHAINE |
| 2 - Migration données | 45 min | ⏳ PROCHAINE |
| 3 - Refactorisation backend | 90 min | ⏳ PROCHAINE |
| 4 - Tests complets | 60 min | ⏳ PROCHAINE |
| 5 - Déploiement | 30 min | ⏳ PROCHAINE |
| **TOTAL** | **≈5-6h** | |

---

## RISQUES & MITIGATIONS

| Risque | Impact | Mitigation |
|--------|--------|-----------|
| Données perdues | CRITIQUE | Backup complet avant, ETL validé, teste 10x |
| Downtime | HAUTE | Parallèle pendant tests, bascule progressive |
| Perf dégradées | MOYENNE | Benchmark MongoDB vs PostgreSQL, index strategy |
| Relations cassées | HAUTE | Validation FK, audit trails |
| Authentification OK? | HAUTE | Tests exhaustifs JWT + auth |

---

**PROCHAINE ÉTAPE:** Lancer audit complet des collections MongoDB et modèles existants.

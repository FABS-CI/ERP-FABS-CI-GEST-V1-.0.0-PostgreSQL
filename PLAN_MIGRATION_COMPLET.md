# 📋 PLAN COMPLET DE MIGRATION MONGODB → POSTGRESQL V2

## Objectif
Migrer **100% des données réelles** de MongoDB vers PostgreSQL v2:
- ✅ 1014 clients
- ✅ 56 produits  
- ✅ 9 utilisateurs + rôles
- ✅ Logos et fichiers
- ✅ Commandes, factures, employés
- ✅ Metadata et audit trails

---

## 🔄 PHASES DE MIGRATION

### Phase 1: PRÉPARATION (2h)
**Objectif:** Valider la source et le target

1. **Vérifier MongoDB Production**
   - [ ] Accès MongoDB Atlas confirmé
   - [ ] Collections listées: users, clients, products, orders, invoices, employees
   - [ ] Volume de données confirmé (1014 clients, 56 products, 9 users)
   - [ ] Sanity checks sur les données

2. **Vérifier PostgreSQL V2**
   - [ ] Base `erp_fabs_ci_v2` prête
   - [ ] 66 tables créées avec indices
   - [ ] Foreign keys et constraints OK
   - [ ] Droits d'accès confirmés

3. **Préparer les fichiers**
   - [ ] Localiser les logos et images
   - [ ] Vérifier le format (JPG, PNG, SVG, etc.)
   - [ ] Préparer la migration des fichiers

### Phase 2: ETL BATCH 1 - UTILISATEURS & RÔLES (30min)
**Ordre:** Migrer USERS EN PREMIER (FK requirement pour audit trail)

```
1. Utilisateurs (9 users)
   - Transformer MongoDB user → PostgreSQL user
   - Conserver les rôles: admin, manager, employee, user
   - Mapping des UUIDs
   - Timestamps: created_at, updated_at
   
2. Roles (si séparé)
   - Migrer les rôles associés
   - Vérifier les permissions
```

**Validation:**
```sql
SELECT COUNT(*) FROM users;  -- Expected: 9
SELECT DISTINCT role FROM users;  -- admin, manager, employee, user
```

### Phase 3: ETL BATCH 2 - PRODUITS (30min)
**Ordre:** Produits avant clients (moins de dépendances)

```
1. Produits (56 produits)
   - code_produit (unique)
   - nom_produit
   - prix_unitaire, prix_vente (Decimal)
   - quantite_stock, quantite_min
   - categorie
   - is_actif
   
2. Catégories (si séparé)
   - Migrer les catégories
```

**Validation:**
```sql
SELECT COUNT(*) FROM products;  -- Expected: 56
SELECT COUNT(DISTINCT categorie) FROM products;
SELECT SUM(quantite_stock) FROM products;
```

### Phase 4: ETL BATCH 3 - CLIENTS (1h)
**Ordre:** Clients avant commandes/factures

```
1. Clients (1014 clients!)
   - code_client (unique)
   - nom_client
   - statut: prospect, active, inactive, suspended, blacklisted
   - credit_limit, credit_utilise
   - Email, téléphone, adresse
   - Contact principal
   
2. Contacts (si table séparée)
   - Contacts associés aux clients
```

**Validation:**
```sql
SELECT COUNT(*) FROM clients;  -- Expected: 1014
SELECT COUNT(DISTINCT status) FROM clients;
SELECT SUM(credit_limit) FROM clients;
```

### Phase 5: ETL BATCH 4 - EMPLOYÉS (30min)

```
1. Employés
   - Nom, prénom
   - Fonction
   - Département
   - Email, téléphone
```

**Validation:**
```sql
SELECT COUNT(*) FROM employees;
SELECT DISTINCT fonction FROM employees;
```

### Phase 6: ETL BATCH 5 - COMMANDES & FACTURES (1h)

```
1. Commandes (Orders)
   - FK client_id
   - FK user_id (qui a créé)
   - Montant total, TVA 18%, remise
   - Statut: draft, confirmed, shipped, delivered, cancelled
   
2. Factures (Invoices)
   - FK order_id, client_id
   - Montant HT, TVA, montant TTC
   - Date d'émission, date d'échéance
   - Statut: draft, issued, paid, overdue, cancelled
```

**Validation:**
```sql
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM invoices;
SELECT AVG(montant_total) FROM orders;
```

### Phase 7: FICHIERS & LOGOS (1h)

```
1. Localiser les fichiers
   - Répertoires: /uploads, /assets, /logos, /documents
   
2. Copier les fichiers
   - Source: MongoDB GridFS ou filesystem
   - Destination: PostgreSQL BYTEA ou storage externe
   
3. Mettre à jour les références
   - Lier les logos aux clients/products
```

### Phase 8: VALIDATION COMPLÈTE (1h)

```sql
-- Vérifier l'intégrité référentielle
SELECT COUNT(*) FROM orders WHERE client_id NOT IN (SELECT id FROM clients);
SELECT COUNT(*) FROM invoices WHERE order_id NOT IN (SELECT id FROM orders);

-- Vérifier les volumes
SELECT 'users' as entity, COUNT(*) FROM users
UNION ALL SELECT 'clients', COUNT(*) FROM clients
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'invoices', COUNT(*) FROM invoices
UNION ALL SELECT 'employees', COUNT(*) FROM employees;

-- Vérifier les doublons
SELECT code_client, COUNT(*) FROM clients GROUP BY code_client HAVING COUNT(*) > 1;
SELECT code_produit, COUNT(*) FROM products GROUP BY code_produit HAVING COUNT(*) > 1;
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;
```

### Phase 9: POST-MIGRATION (1h)

```
1. Mise à jour des séquences
   UPDATE clients SET id = gen_random_uuid() WHERE id IS NULL;
   
2. Reindex des tables
   REINDEX DATABASE erp_fabs_ci_v2;
   
3. Statistiques
   ANALYZE;
   
4. Sauvegarde
   pg_dump -U postgres erp_fabs_ci_v2 > /backup/erp_v2_post_migration.sql
```

### Phase 10: TESTS COMPLETS (2h)

```
1. Tests API
   - GET /api/users → 9 users
   - GET /api/clients → 1014 clients
   - GET /api/products → 56 products
   - GET /api/orders → N orders
   - GET /api/invoices → N invoices
   
2. Tests Fonctionnels
   - Créer une commande (POST /api/orders)
   - Émettre une facture (POST /api/invoices)
   - Calculer la TVA 18%
   - Appliquer les remises
   
3. Tests de Performance
   - 10 utilisateurs concurrent
   - Requêtes complexes (JOIN multi-tables)
   - Temps de réponse < 100ms
```

---

## 📊 CHECKLIST D'EXÉCUTION

- [ ] MongoDB credentials fournis
- [ ] PostgreSQL v2 prêt
- [ ] Script ETL préparé
- [ ] Backup MongoDB pris
- [ ] Backup PostgreSQL pris
- [ ] Phase 1: Préparation ✅
- [ ] Phase 2: Users ✅
- [ ] Phase 3: Products ✅
- [ ] Phase 4: Clients ✅
- [ ] Phase 5: Employees ✅
- [ ] Phase 6: Orders & Invoices ✅
- [ ] Phase 7: Fichiers & Logos ✅
- [ ] Phase 8: Validation ✅
- [ ] Phase 9: Post-migration ✅
- [ ] Phase 10: Tests ✅
- [ ] Sign-off Go-Live 1er juillet 2026

---

## 🎯 RÉSULTATS ATTENDUS

**Volume Final PostgreSQL:**
- 9 utilisateurs
- 1014 clients
- 56 produits
- N employés
- N commandes
- N factures
- Logos & fichiers associés

**Performance Cible:**
- Insertion: < 50ms/100 records
- Query: < 30ms pour 1000 records
- Load test: 20-50 concurrent users, zero crashes

**Qualité:**
- 100% d'intégrité référentielle
- Zéro doublons
- Zéro données perdues
- Audit trail complet

---

**Timeline:** 6-8 heures pour la migration complète  
**Go-Live:** 1er juillet 2026  
**Responsable:** Odelia Ode  
**Date:** 25 Juin 2026

# 📊 AUDIT COMPLET MONGODB - ERP FABS-CI V1.0.0

**Date:** 2026-06-25  
**Status:** AUDIT EN COURS  
**Objectif:** Migration MongoDB → PostgreSQL

---

## 1. COLLECTIONS MONGODB IDENTIFIÉES (90+ collections)

### A. Gestion des Utilisateurs & Authentification (5)
- `users` — Utilisateurs du système
- `refresh_tokens` — Tokens de rafraîchissement
- `roles` — Rôles et permissions
- `habilitations` — Habilitations utilisateurs
- `parametres` — Paramètres système

### B. Gestion des Clients (4)
- `clients` — Clients
- `contacts` — Contacts clients
- `prospects` — Prospects
- `categories_pro` — Catégories professionnelles clients

### C. Gestion des Produits & Stocks (6)
- `produits` — Produits/articles
- `stock` — Stock actuel
- `mouvements_stock` — Historique mouvements stock
- `inventaires` — Inventaires (comptes physiques)
- `inventaire_lignes` — Lignes d'inventaire
- `depots` — Dépôts/magasins

### D. Gestion des Commandes (5)
- `commandes` — Commandes client
- `commande_lignes` — Lignes de commande
- `proformas` — Proformas
- `proforma_lignes` — Lignes proforma
- `approvisionnements` — Commandes d'approvisionnement

### E. Gestion des Factures & Paiements (8)
- `factures` — Factures
- `facture_lignes` — Lignes de factures
- `invoices` — Invoices (alias factures)
- `invoice_items` — Items invoices (alias lignes factures)
- `paiements` — Enregistrements de paiements
- `affectations_paiement` — Affectations paiements
- `credit_notes` — Notes de crédit
- `factures_pdf` — Factures PDF (documents)

### F. Gestion de la Logistique & Livraisons (8)
- `bons_livraison` — Bons de livraison
- `bl_lignes` — Lignes de bons de livraison
- `bons_retour` — Bons de retour
- `br_lignes` — Lignes de bons de retour
- `livraisons_directes` — Livraisons directes (sans commande)
- `suivi_livraisons` — Suivi livraisons
- `vehicules` — Véhicules de livraison
- `affectations_vehicules` — Affectations de véhicules

### G. Gestion de la Logistique Avancée (4)
- `colis` — Colis
- `cartons_colisage` — Cartons de colisage
- `ordres_colisage` — Ordres de colisage
- `mouvements_colis` — Mouvements des colis

### H. Gestion des Fournisseurs (1)
- `fournisseurs` — Fournisseurs

### I. Comptabilité & Finances (7)
- `ecritures_comptables` — Écritures comptables
- `journaux_comptables` — Journaux comptables
- `plan_comptable` — Plan comptable
- `rapprochements_bancaires` — Rapprochements bancaires
- `email_logs` — Logs d'email
- `envoi_logs` — Logs d'envoi
- `email_templates` — Templates d'email

### J. Ressources Humaines & Paie (9)
- `employes` — Employés
- `contrats` — Contrats d'emploi
- `departements` — Départements
- `departments` — Departments (alias)
- `fonctions` — Fonctions/postes
- `delegations` — Délégations de pouvoirs
- `absences` — Absences
- `conges` — Congés
- `bulletins_paie` — Bulletins de paie

### K. Évaluations & Formation (2)
- `evaluations` — Évaluations d'employés
- `maintenances` — Maintenances

### L. Gestion des Missions & Frais (3)
- `missions` — Missions
- `missions_logistiques` — Missions logistiques
- `couts_missions` — Coûts de missions

### M. Fleet Management & Assurances (3)
- `assurances` — Assurances vehicules
- `visites_techniques` — Visites techniques
- `expeditions` — Expéditions
- `expeditions_colisage` — Expéditions colisage

### N. Gestion Documentaire (4)
- `documents` — Documents généraux
- `documents_intelligents` — Documents intelligents
- `document_settings` — Settings des documents
- `signatures_electroniques` — Signatures électroniques

### O. Audit & Conformité (6)
- `audit_logs` — Logs d'audit
- `audit_log` — Logs d'audit (alias)
- `notification_logs` — Logs de notifications
- `fne_logs` — Logs FNE
- `fne_metadata` — Métadonnées FNE
- `fne_settings` — Settings FNE

### P. Alertes & Notifications (4)
- `notifications` — Notifications
- `notification_batches` — Batches de notifications
- `notification_preferences` — Préférences de notifications
- `approval_workflows` — Workflows d'approbation
- `approval_steps` — Étapes d'approbation

### Q. Utilitaires & Système (5)
- `counters` — Compteurs (pour IDs séquentiels)
- `doublon_logs` — Logs de détection de doublons
- `backup_config` — Configuration backups
- `backups` — Backups
- `restores` — Restores
- `secrets_rotation` — Rotation des secrets

---

## 2. ANALYSE DES MODULES BACKEND (50+ fichiers)

### Modules principaux identifiés

#### Approvisionnement & Achat
- `approvisionnement_module.py` — Gestion des commandes d'approvisionnement
- `fournisseurs` — Données fournisseurs

#### Clients & CRM
- `clients_module.py` — Gestion des clients
- Interactions avec table `clients`, `contacts`, `categories_pro`

#### Produits
- `products_module.py` — Gestion des produits
- `stock_module.py` — Gestion du stock
- Relations: `produits`, `stock`, `mouvements_stock`, `inventaires`

#### Commandes & Ventes
- `commandes_module.py` — Gestion des commandes clients
- `factures_module.py` — Gestion des factures
- Relations: `commandes`, `factures`, `facture_lignes`

#### Paiements
- `paiements_module.py` — Gestion des paiements
- Relations: `paiements`, `affectations_paiement`

#### Logistique
- `bons_livraison_module.py` — Bons de livraison
- `bons_retour_module.py` — Bons de retour
- `colisage_module.py` — Colisage
- `fleet_module.py` — Fleet management

#### Ressources Humaines
- `rh_module.py` — Gestion RH
- Relations: `employes`, `contrats`, `departements`, `absences`, `conges`

#### Comptabilité
- `comptabilite_module.py` — Comptabilité
- `comptabilite_avancee_module.py` — Comptabilité avancée
- Relations: `ecritures_comptables`, `journaux_comptables`, `plan_comptable`

#### Gestion Documentaire
- Documents, signatures électroniques
- `documents_intelligents` — Documents intelligents
- `signatures_electroniques` — Signatures

#### Proformas
- `proformas_module.py` — Gestion des proformas
- Relations: `proformas`, `proforma_lignes`

#### Rapports & Analytics
- `rapports_module.py` — Rapports
- `analytics_module.py` — Analytics
- `bi_analytics_module.py` — Business Intelligence

#### Notifications
- `notifications_module.py` — Gestion notifications
- `alert_manager_external.py` — Gestion des alertes externes
- `alerting_service.py` — Service d'alerting

#### API & Audit
- `audit_log_service.py` — Service d'audit
- `audit_metier.py` — Audit métier
- `api_key_manager.py` — Gestion des clés API

#### Admin & Configuration
- `administration_module.py` — Module administration

---

## 3. RELATIONS IMPLICITES IDENTIFIÉES

### Hiérarchies documentaires
```
Commandes ↓
  ├─ Lignes commandes
  └─ Factures ↓
      ├─ Lignes factures
      ├─ Paiements
      └─ Bons de livraison ↓
          ├─ Lignes BL
          └─ Mouvements stock
```

### Relations Clients
```
Clients ↓
  ├─ Contacts
  ├─ Commandes
  ├─ Factures
  ├─ Paiements
  └─ Suivi livraisons
```

### Relations Produits
```
Produits ↓
  ├─ Stock (par dépôt)
  ├─ Mouvements stock
  ├─ Inventaires
  ├─ Lignes commande
  ├─ Lignes facture
  └─ Lignes BL
```

### Relations Employés
```
Employés ↓
  ├─ Contrats
  ├─ Absences
  ├─ Congés
  ├─ Bulletins paie
  └─ Évaluations
```

---

## 4. DÉTAILS SCHÉMA MONGODB ACTUEL

### Collection: `users`
```javascript
{
  _id: ObjectId,
  user_id: String (unique),
  email: String (unique),
  nom_complet: String,
  role: String (super_admin, directeur_general, etc),
  actif: Boolean,
  password_hash: String,
  picture: String (nullable),
  created_at: ISO8601,
  updated_at: ISO8601
}
```

### Collection: `clients`
```javascript
{
  _id: ObjectId,
  client_id: String (unique),
  name: String,
  email: String,
  phone: String,
  address: String,
  city: String,
  status: String (actif, inactif, suspendu),
  category: String,
  credit_limit: Number,
  balance: Number,
  created_at: ISO8601,
  updated_at: ISO8601
}
```

### Collection: `produits`
```javascript
{
  _id: ObjectId,
  product_id: String (unique),
  produit_id: String,
  name: String,
  code: String (unique),
  category: String,
  price: Number,
  cost: Number,
  status: String,
  quantity: Number,
  created_at: ISO8601,
  updated_at: ISO8601
}
```

### Collection: `commandes`
```javascript
{
  _id: ObjectId,
  order_id: String (unique),
  order_number: String (unique),
  client_id: String,
  status: String (draft, sent, accepted, invoiced, delivered),
  total_amount: Number,
  tax_amount: Number,
  created_at: ISO8601,
  updated_at: ISO8601,
  items: [{
    produit_id: String,
    quantity: Number,
    unit_price: Number,
    total: Number
  }]
}
```

### Collection: `factures`
```javascript
{
  _id: ObjectId,
  facture_id: String (unique),
  invoice_number: String (unique),
  client_id: String,
  order_id: String,
  status: String (draft, sent, paid, overdue),
  total_amount: Number,
  paid_amount: Number,
  due_date: ISO8601,
  created_at: ISO8601,
  updated_at: ISO8601,
  items: [{
    product_id: String,
    quantity: Number,
    unit_price: Number,
    total: Number,
    tax: Number
  }]
}
```

### Collection: `paiements`
```javascript
{
  _id: ObjectId,
  paiement_id: String (unique),
  transaction_id: String (unique),
  invoice_id: String,
  amount: Number,
  payment_date: ISO8601,
  status: String (completed, pending, failed),
  payment_method: String (cash, check, transfer, card),
  reference: String,
  created_at: ISO8601
}
```

### Collection: `stock`
```javascript
{
  _id: ObjectId,
  stock_id: String (unique),
  product_id: String,
  warehouse: String,
  quantity: Number,
  last_updated: ISO8601,
  min_quantity: Number,
  max_quantity: Number
}
```

### Collection: `audit_logs`
```javascript
{
  _id: ObjectId,
  timestamp: ISO8601,
  user_id: String,
  action: String (CREATE, READ, UPDATE, DELETE),
  resource_type: String,
  resource_id: String,
  old_values: Object,
  new_values: Object,
  ip_address: String,
  user_agent: String,
  severity: String
}
```

---

## 5. PROBLÈMES IDENTIFIÉS

### 5.1 Incohérences de nommage
- ❌ `product_id` vs `produit_id` (mélange français/anglais)
- ❌ `invoice_items` vs `facture_lignes`
- ❌ `departments` vs `departements`

### 5.2 Pas de clés étrangères
- MongoDB n'enforce pas les FK
- Relations basées sur IDs string uniquement
- Risque: orphelins de données

### 5.3 IDs inconsistants
- ❌ String UUIDs vs ObjectId
- ❌ Compteurs (sequences) dans table `counters`
- ❌ Pas de contraintes uniques applicables

### 5.4 Données non normalisées
- ❌ Documents imbriqués (`items: [...]` dans commandes)
- ❌ Risque de redondance dans les sous-documents
- ❌ Modifications cascades complexes

### 5.5 Audit & Timestamps
- ✅ `created_at`, `updated_at` présents
- ❌ Pas de `deleted_at` (soft delete)
- ❌ Pas de `created_by`, `updated_by` (qui a modifié)

### 5.6 Sécurité
- ❌ Pas de column-level encryption
- ❌ Pas de row-level security (RLS)
- ❌ Permissions basées sur rôles (basiques)

### 5.7 Transactions
- ❌ MongoDB 4.0+ supporte transactions multi-docs
- ❌ Pas d'utilisation visible dans le code
- ❌ Risque: incohérence de données

### 5.8 Index
- ✅ Index sur `created_at`, `status`, clés fréquentes
- ❌ Pas d'index sur certaines jointures
- ❌ Performance potentiellement dégradée

---

## 6. DONNÉES APPROXIMATIVES (mongomock)

Basé sur les seeds et tests:
- **Users:** 2-10
- **Clients:** 1,014
- **Products:** 56
- **Orders:** 100
- **Invoices:** 50
- **Payments:** ~150-200
- **Audit logs:** ~500-1000
- **Total documents:** ~5,000-10,000

---

## 7. DÉPENDANCES IDENTIFIÉES

### Modules critiques
1. **Authentication** — `users`, `roles`, `refresh_tokens`
2. **CRM** — `clients`, `contacts`, `prospects`
3. **Orders-to-Invoices** — `commandes`, `factures`, `paiements`
4. **Stock Management** — `produits`, `stock`, `mouvements_stock`
5. **Logistics** — `bons_livraison`, `bons_retour`, `vehicules`
6. **HR** — `employes`, `contrats`, `absences`, `conges`, `bulletins_paie`
7. **Accounting** — `ecritures_comptables`, `journaux_comptables`
8. **Audit** — `audit_logs`, `notifications`

### Dépendances critiques
- ✅ Clés primaires/uniques: `user_id`, `client_id`, `order_id`, `invoice_number`, `product_id`
- ✅ Séquences: `counters` (pour générer IDs)
- ✅ Relations: N-M implicites (clients ← commandes, produits ← lignes commandes)

---

## 8. RECOMMANDATIONS POUR MIGRATION

### Stratégie de conception PostgreSQL
1. ✅ **3NF normalization** — Éliminer les données imbriquées
2. ✅ **Clés étrangères** — Intégrité référentielle stricte
3. ✅ **Audit columns** — `created_by`, `updated_by`, `deleted_at`
4. ✅ **Soft deletes** — `is_deleted` boolean
5. ✅ **Timestamps** — `created_at`, `updated_at` automatiques
6. ✅ **Row-level security** — Avec `company_id` pour multi-tenant
7. ✅ **Index stratégiques** — Sur FK, statuts, dates
8. ✅ **Transactions** — ACID pour workflows critiques

### Ordre de migration
1. Phase 1: Setup, utilisateurs, paramètres
2. Phase 2: Clients, produits, stocks
3. Phase 3: Commandes, factures, paiements
4. Phase 4: Logistique, RH, comptabilité
5. Phase 5: Audit, notifications, documents

---

**PROCHAINE ÉTAPE:** Concevoir schéma PostgreSQL complet basé sur cet audit.

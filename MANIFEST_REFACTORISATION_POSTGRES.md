# 🚀 MANIFEST - REFACTORISATION COMPLÈTE ERP FABS-CI VERS PostgreSQL

**Date:** 25 juin 2026  
**Demandeur:** Odelia Ode  
**Priorité:** CRITIQUE - MISSION COMPLÈTE

---

## 📋 DÉCLARATION D'INTENTION

**Objectif Principal:**
L'ERP FABS-CI fonctionnera désormais entièrement sur PostgreSQL. 
Pas de migration partielle, pas d'architecture hybride pour les données métier.

**Option Choisie:** A - Refactorisation Complète du Backend

---

## ✅ TRAVAUX À EXÉCUTER (ORDRE DE PRIORITÉ)

### 1. Architecture & Dépendances
- [ ] Supprimer la dépendance fonctionnelle à MongoDB pour les données métier
- [ ] Connecter l'ensemble du backend au schéma PostgreSQL déjà créé
- [ ] Refactoriser tous les modèles, repositories, services, contrôleurs, API

### 2. ORM & Migrations
- [ ] Mettre en place SQLAlchemy (ou vérifier si déjà présent)
- [ ] Créer les migrations nécessaires
- [ ] Mapper tous les types de données MongoDB → PostgreSQL

### 3. Modules ERP Complets
- [ ] CRM (Clients, Contacts, Prospects)
- [ ] Ventes (Commandes, Proformas, Factures, Avoirs)
- [ ] Achats (Fournisseurs, Approvisionnements)
- [ ] Stocks (Produits, Dépôts, Mouvements, Inventaires)
- [ ] RH (Employés, Contrats, Paie, Congés, Évaluations)
- [ ] Comptabilité (Plan comptable, Écritures, Rapprochements)
- [ ] Facturation (Factures complètes, Paiements, Lettrage)
- [ ] Documents (Gestion documentaire, OCR, Signatures)
- [ ] Reporting (Tableaux de bord, Exports, Analyses)
- [ ] Administration (Paramètres, Audit logs, Alertes, API keys)

### 4. Intégrité Données
- [ ] Vérifier relations, contraintes FK, transactions
- [ ] Vérifier règles métier et workflows
- [ ] Migrer l'intégralité des données existantes sans perte

### 5. Infrastructure Persistante
- [ ] Redis: cache, sessions, files d'attente, notifications temps réel (INCHANGÉ)
- [ ] PostgreSQL: données métier uniquement

### 6. Qualité & Tests
- [ ] Corriger automatiquement tous les bugs post-migration
- [ ] Mettre à jour tests existants
- [ ] Créer nouveaux tests (unit, intégration, E2E)
- [ ] Validation fonctionnelle module par module

### 7. Performance & Production
- [ ] Vérifier performances ≥ version MongoDB
- [ ] Déploiement production-ready
- [ ] Audit de sécurité et données sensibles

---

## 🎯 CRITÈRES DE SUCCÈS

Mission considérée terminée UNIQUEMENT si:

1. ✅ Backend démarre sans erreur sur PostgreSQL
2. ✅ Toutes les API répondent correctement (200/201/204)
3. ✅ Tous les modules ERP opérationnels
4. ✅ Données existantes intégralement conservées
5. ✅ Tests passants (min 80% coverage)
6. ✅ Performances ≥ MongoDB
7. ✅ Production-ready sans régression fonctionnelle

---

## 📊 IMPACT ESTIMÉ

| Domaine | Impact | Effort |
|---------|--------|--------|
| Architecture | MAJEUR | 16h |
| ORM/Migrations | MAJEUR | 12h |
| Modules ERP | CRITIQUE | 28h |
| Tests | MAJEUR | 8h |
| Performance | MOYENNE | 4h |
| **TOTAL** | | **~68h** |

**Timeline Réaliste:** 8-10 jours (travail intensif)

---

## 🔒 PRINCIPES DE SÉCURITÉ

**Avant chaque modification majeure:**
- Audit d'impact systématique
- Changements cohérents sur tout le projet
- Zéro rupture de service
- Zéro incohérence de données
- Traçabilité complète (audit logs)

---

## 📝 STATUT

**Phase:** PRÉ-EXÉCUTION - AUDIT D'IMPACT
**Date Démarrage:** 25 juin 2026, 08:45
**Prochaine Étape:** Audit de dépendances MongoDB → Génération du plan détaillé

---

## 🔗 DOCUMENTS ASSOCIÉS

- `SETUP_POSTGRESQL_COMPLET.md` - Schéma PostgreSQL (65 tables, 113 indexes)
- `AUDIT_IMPACT_MONGODB_REMOVAL.md` - Audit impact (À générer)
- `PLAN_REFACTORISATION_DETAILLE.md` - Plan Phase-par-Phase (À générer)
- `MIGRATION_PLAN.md` - Plan migration données (existant)

---

**DÉCLARATION:** 
*Je reconnais les objectifs, les critères de succès, et je procède immédiatement à l'exécution avec rigueur, audits systématiques, et qualité production.*

---

✅ PRÊT POUR PHASE 1: AUDIT D'IMPACT

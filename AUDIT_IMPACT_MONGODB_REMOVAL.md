====================================================================================================
🔴 AUDIT D'IMPACT: DÉPENDANCES MONGODB - ERP FABS-V10
====================================================================================================

📊 STATISTIQUES GLOBALES:
  • Fichiers Python scannés: 136
  • Lignes de code: 53,774

🔍 DÉPENDANCES MONGODB DÉTECTÉES:

  1️⃣  IMPORTS MONGODB (63 fichiers):
     • administration_module.py: lignes [15, 15, 86]
     • analytics_module.py: lignes [14, 14, 35]
     • analytics_service.py: lignes [19, 19, 25]
     • approvisionnement_module.py: lignes [23, 23, 42]
     • audit_log_service.py: lignes [11]
     • bons_livraison_module.py: lignes [17, 17, 38]
     • bons_retour_module.py: lignes [16, 16, 36]
     • clients_module.py: lignes [18, 18, 115]
     • commandes_module.py: lignes [28, 28, 31]
     • comptabilite_module.py: lignes [16, 16, 37]
     • compte_client_pdf_generator.py: lignes [93]
     • create_indexes.py: lignes [7, 7, 14]
     • create_super_admin.py: lignes [7, 7, 17]
     • database_schema.py: lignes [150]
     • db_init.py: lignes [10, 10, 10]
     • document_settings_module.py: lignes [23, 23, 195]
     • documents_ai_module.py: lignes [17, 17, 169]
     • enrich_produits_infos.py: lignes [8]
     • factures_module.py: lignes [28, 28, 114]
     • fix_commande_codes.py: lignes [9, 12]
     • fne_module.py: lignes [23, 23, 199]
     • fne_queue.py: lignes [16, 16, 25]
     • fournisseurs_module.py: lignes [18, 18, 36]
     • import_clients_json.py: lignes [9]
     • import_data.py: lignes [9]
     • import_produits_json.py: lignes [6]
     • import_real_clients.py: lignes [28, 28, 152]
     • import_real_data.py: lignes [20]
     • import_users_roles.py: lignes [10]
     • load_fabs_catalogue.py: lignes [14, 15, 183]
     • migrations/add_fne_fields.py: lignes [11, 11, 24]
     • migrations/create_fournisseurs_approvisionnements.py: lignes [11, 11, 24]
     • minimal_app.py: lignes [4]
     • notification_service.py: lignes [17, 17, 49]
     • opentelemetry_setup.py: lignes [62]
     • optimization_utils.py: lignes [7, 7, 16]
     • paiements_module.py: lignes [24, 24, 57]
     • pdf_generator.py: lignes [186]
     • products_module.py: lignes [22, 22, 70]
     • proformas_module.py: lignes [26, 26, 28]
     • recherche_module.py: lignes [11, 11, 31]
     • rh_module.py: lignes [19, 19, 71]
     • scripts/check_doubles_comptabilite.py: lignes [10, 10, 17]
     • scripts/check_products.py: lignes [8, 8, 15]
     • scripts/drop_products.py: lignes [9, 9, 16]
     • scripts/seed_articles_fabs.py: lignes [20, 20, 114]
     • scripts/seed_utilisateurs_fabs.py: lignes [21, 21, 46]
     • seed_once.py: lignes [7]
     • seed_products_fabs.py: lignes [5]
     • server.py: lignes [28, 28, 28]
     • server_init.py: lignes [51, 74, 224]
     • services/command_service.py: lignes [8, 8, 14]
     • services/employee_service.py: lignes [8, 8, 14]
     • services/stock_service.py: lignes [8, 8, 14]
     • stock_module.py: lignes [20, 20, 173]
     • stock_pdf_generator.py: lignes [84]
     • tests/test_auth_fabsci.py: lignes [10]
     • tests/test_clients_fabsci.py: lignes [17]
     • tests/test_dashboard_fabsci.py: lignes [21]
     • tests/test_p6_e2e_workflow.py: lignes [8, 8, 28]
     • tests/test_products_fabsci.py: lignes [14]
     • tests/test_sprints_8_15_fabsci.py: lignes [23]
     • transaction_helper.py: lignes [6, 6, 14]

  2️⃣  APPELS DB DIRECTS (10 fichiers):
     • alerting_service.py: 3 appels
     • api_key_manager.py: 4 appels
     • audit_log_service.py: 3 appels
     • create_indexes.py: 4 appels
     • dgi_compliance_service.py: 5 appels
     • incident_response_service.py: 7 appels
     • log_export_service.py: 6 appels
     • performance_optimization_service.py: 1 appels
     • security_audit_service.py: 8 appels
     • session_manager.py: 7 appels

  3️⃣  OPÉRATIONS FIND (57 fichiers):
     • Total: 226 appels .find()

  4️⃣  OPÉRATIONS UPDATE (49 fichiers):
     • Total: 172 appels .update_*()

  5️⃣  OPÉRATIONS INSERT (67 fichiers):
     • Total: 231 appels .insert_*()

  6️⃣  PIPELINES AGGREGATION (19 fichiers):
     • Total: 61 pipelines

  7️⃣  SQLALCHEMY DÉJÀ PRÉSENT (30 fichiers):
     • OUI - Intégration possible

  8️⃣  MODÈLES/SCHEMAS (36 fichiers):
     • administration_module.py: ligne 52
     • approvisionnement_module.py: ligne 56
     • backup_module.py: ligne 42
     • bi_analytics_module.py: ligne 17
     • bons_livraison_module.py: ligne 50

====================================================================================================
⚠️  IMPACT DE LA REFACTORISATION:
====================================================================================================

🔴 Fichiers affectés: 265
🔴 Complexité: TRÈS ÉLEVÉE
🔴 Risque de régression: CRITIQUE

====================================================================================================
📋 RECOMMANDATIONS:
====================================================================================================

1. PHASE 1 (Préparation - 4h):
   • Installer SQLAlchemy + psycopg2-binary
   • Créer couche d'abstraction DB (repository pattern)
   • Identifier tous les modèles MongoDB → PostgreSQL

2. PHASE 2 (Refactorisation Core - 8h):
   • Refactoriser db_init.py pour PostgreSQL
   • Créer repositories pour chaque entité métier
   • Migrer modèles Pydantic → SQLAlchemy ORM

3. PHASE 3 (Modules - 16h):
   • Refactoriser module par module
   • Tester chaque module en isolation
   • Valider intégrité données

4. PHASE 4 (Tests & Validation - 8h):
   • Tests unitaires
   • Tests intégration
   • Tests performance

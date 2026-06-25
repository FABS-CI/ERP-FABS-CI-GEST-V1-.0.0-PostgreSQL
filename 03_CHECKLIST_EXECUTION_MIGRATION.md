# ✅ CHECKLIST COMPLÈTE MIGRATION MONGODB → POSTGRESQL

**ERP FABS-CI V1.0.0**  
**Date:** 2026-06-25  
**Status:** À EXÉCUTER  
**Durée estimée:** 5-6 heures (complète)

---

## PHASE 0: PRÉPARATION (30 min)

### 0.1 Vérifications préalables
- [ ] Backup complet MongoDB (mongodump)
  ```bash
  mongodump --db fabs_ci_erp --out /backups/mongodb_backup_$(date +%Y%m%d)
  ```

- [ ] PostgreSQL v14+ opérationnel
  ```bash
  psql --version
  createdb erp_fabs_ci_migration
  ```

- [ ] Environnements prêts
  - [ ] Dev/Test avec données réelles extraites
  - [ ] Staging/Prod en standby
  - [ ] Backups validés

### 0.2 Dépendances logicielles
- [ ] Python 3.9+ (déjà présent)
- [ ] pip packages:
  ```bash
  pip install sqlalchemy psycopg2-binary pymongo mongomock
  ```

- [ ] Tools:
  ```bash
  apt-get install postgresql postgresql-client
  ```

### 0.3 Droits d'accès
- [ ] MongoDB: Utilisateur avec accès read-all
- [ ] PostgreSQL: Utilisateur avec CREATE/INSERT/UPDATE privileges
- [ ] Fichiers: Permissions écriture sur /home/user/

### 0.4 Configuration environnement
```bash
export MONGODB_URI="mongodb://localhost:27017"
export MONGODB_DB="fabs_ci_erp"
export DATABASE_URL="postgresql://user:password@localhost:5432/erp_fabs_ci"
```

---

## PHASE 1: CRÉATION SCHÉMA POSTGRESQL (45 min)

### 1.1 Créer la base de données
```bash
createdb erp_fabs_ci -E UTF8 -T template0 -l C
```

### 1.2 Exécuter le schéma SQL
```bash
psql -d erp_fabs_ci -f /home/user/01_SCHEMA_POSTGRESQL_COMPLET.sql
```

Vérifier:
```sql
SELECT COUNT(*) as total_tables FROM information_schema.tables WHERE table_schema = 'public';
-- Doit retourner: ~100+ tables
```

### 1.3 Vérifications post-création
- [ ] Tables créées: 100+
- [ ] Enums créés: 10+
- [ ] Indexes créés: 50+
- [ ] Vues créées: 3+
- [ ] Pas d'erreurs dans schéma

Commandes de vérification:
```sql
-- Lister les tables
\dt

-- Lister les indexes
\di

-- Vérifier les enums
SELECT typname FROM pg_type WHERE typtype = 'e';

-- Vérifier les vues
\dv
```

---

## PHASE 2: PRÉPARATION DONNÉES MONGODB (15 min)

### 2.1 Vérifier MongoDB
```bash
mongo << EOF
use fabs_ci_erp
db.stats()
db.listCollections().forEach(c => print(c.name + ": " + db[c.name].count()))
EOF
```

### 2.2 Nettoyer les données (optionnel)
- [ ] Vérifier les documents orphelins
- [ ] Supprimer les duplicatas
- [ ] Valider les champs obligatoires

### 2.3 Exporter statistiques MongoDB
```bash
python3 << 'EOF'
import pymongo
from datetime import datetime

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['fabs_ci_erp']

stats = {
    'timestamp': datetime.now().isoformat(),
    'total_documents': 0,
    'collections': {}
}

for collection_name in db.list_collection_names():
    count = db[collection_name].count_documents({})
    stats['collections'][collection_name] = count
    stats['total_documents'] += count

print(f"Total documents: {stats['total_documents']}")
for coll, count in stats['collections'].items():
    print(f"  {coll}: {count}")

with open('/home/user/mongodb_stats_pre_migration.json', 'w') as f:
    import json
    json.dump(stats, f, indent=2)
EOF
```

---

## PHASE 3: EXÉCUTION MIGRATION (2-3 heures)

### 3.1 Migration en mode DRY-RUN (simulation)
```bash
python3 /home/user/02_ETL_MIGRATION.py --dry-run
```

**Output attendu:**
```
🚀 DÉBUT DE LA MIGRATION MONGODB → POSTGRESQL
⚠️  MODE DRY-RUN (Aucune donnée ne sera modifiée)
🔍 Vérification des données MongoDB...
📊 Total: XXXX documents
📝 Migration: UTILISATEURS
  Trouvé: XX utilisateurs
  ✅ XX utilisateurs migrés
...
```

- [ ] Vérifier qu'aucune donnée n'a été modifiée
- [ ] Vérifier les logs pour erreurs
- [ ] Valider le nombre de documents

### 3.2 Migration réelle
```bash
python3 /home/user/02_ETL_MIGRATION.py
```

**Monitorage:**
- Vérifier le fichier log: `tail -f /home/user/migration.log`
- Monitorez PostgreSQL: `watch 'SELECT count(*) FROM users; SELECT count(*) FROM clients;'`
- Vérifiez les erreurs: `grep "❌" /home/user/migration.log | wc -l`

### 3.3 Vérifications post-migration
```bash
python3 << 'EOF'
import json
import pymongo
import psycopg2

# Charger stats pre-migration
with open('/home/user/mongodb_stats_pre_migration.json') as f:
    pre_stats = json.load(f)

# Vérifier MongoDB
mongo_client = pymongo.MongoClient('mongodb://localhost:27017')
mongo_db = mongo_client['fabs_ci_erp']

# Vérifier PostgreSQL
pg_conn = psycopg2.connect("dbname=erp_fabs_ci user=user password=password")
pg_cursor = pg_conn.cursor()

comparisons = {
    'users': ('utilisateurs', 'users'),
    'clients': ('clients', 'clients'),
    'produits': ('produits', 'produits'),
    'commandes': ('commandes', 'commandes'),
    'factures': ('factures', 'factures'),
    'paiements': ('paiements', 'paiements'),
    'stock': ('stock', 'stock')
}

print("VÉRIFICATION POST-MIGRATION:")
print("=" * 60)

errors = []
for mongo_name, (mongo_table, pg_table) in comparisons.items():
    mongo_count = mongo_db[mongo_table].count_documents({})
    
    pg_cursor.execute(f"SELECT COUNT(*) FROM {pg_table}")
    pg_count = pg_cursor.fetchone()[0]
    
    match = "✅" if mongo_count == pg_count else "❌"
    print(f"{match} {mongo_name}: MongoDB={mongo_count}, PostgreSQL={pg_count}")
    
    if mongo_count != pg_count:
        errors.append({
            'collection': mongo_name,
            'mongo_count': mongo_count,
            'pg_count': pg_count,
            'difference': mongo_count - pg_count
        })

if errors:
    print("\n❌ DIFFÉRENCES DÉTECTÉES:")
    for error in errors:
        print(f"  {error['collection']}: {error['difference']} documents manquants")
else:
    print("\n✅ TOUS LES DOCUMENTS MIGRÉS AVEC SUCCÈS")

pg_cursor.close()
pg_conn.close()
mongo_client.close()
EOF
```

---

## PHASE 4: TESTS FONCTIONNELS (1 heure)

### 4.1 Tests de données basiques

**Clients:**
```sql
SELECT COUNT(*) as total,
       COUNT(CASE WHEN status = 'actif' THEN 1 END) as actifs,
       COUNT(CASE WHEN status = 'inactif' THEN 1 END) as inactifs
FROM clients;
```

**Commandes & Factures:**
```sql
SELECT c.name, COUNT(co.id) as orders, COUNT(f.id) as invoices
FROM clients c
LEFT JOIN commandes co ON c.id = co.client_id
LEFT JOIN factures f ON c.id = f.client_id
GROUP BY c.id, c.name
ORDER BY orders DESC
LIMIT 10;
```

**Stock:**
```sql
SELECT p.name, SUM(s.quantity) as total_qty, COUNT(DISTINCT d.id) as depots
FROM produits p
LEFT JOIN stock s ON p.id = s.product_id
LEFT JOIN depots d ON s.depot_id = d.id
GROUP BY p.id, p.name
ORDER BY total_qty DESC
LIMIT 10;
```

### 4.2 Tests des relations (FK)

```sql
-- Vérifier orphelins
SELECT COUNT(*) FROM commande_lignes WHERE order_id NOT IN (SELECT id FROM commandes);
SELECT COUNT(*) FROM facture_lignes WHERE facture_id NOT IN (SELECT id FROM factures);
SELECT COUNT(*) FROM bl_lignes WHERE bl_id NOT IN (SELECT id FROM bons_livraison);

-- Doit retourner 0 pour tous
```

### 4.3 Tests de performances

```sql
-- Simple query
EXPLAIN ANALYZE
SELECT * FROM clients WHERE status = 'actif' LIMIT 10;

-- Join query
EXPLAIN ANALYZE
SELECT c.name, f.invoice_number, f.total_amount
FROM clients c
JOIN factures f ON c.id = f.client_id
WHERE c.status = 'actif'
LIMIT 50;

-- Aggregation
EXPLAIN ANALYZE
SELECT DATE_TRUNC('month', f.created_at) as month,
       COUNT(*) as invoice_count,
       SUM(f.total_amount) as total_amount
FROM factures
WHERE created_at >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY DATE_TRUNC('month', f.created_at)
ORDER BY month DESC;
```

**Critères d'acceptation:**
- ✅ Queries simples < 100ms
- ✅ Joins < 500ms
- ✅ Aggregations < 2s

---

## PHASE 5: REFACTORISATION BACKEND (2-3 heures)

### 5.1 Créer models SQLAlchemy

**Fichier:** `/home/user/ERP-FABS-V10/backend/models_postgresql.py`

Exemple:
```python
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    nom_complet = Column(String(255), nullable=False)
    role = Column(String(50), default='viewer')
    actif = Column(Boolean, default=True)
    # ... autres colonnes

class Client(Base):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    # ... autres colonnes
    
    # Relations
    commandes = relationship("Commande", back_populates="client")
    factures = relationship("Facture", back_populates="client")
```

### 5.2 Créer repositories PostgreSQL

**Pattern:** Repository Pattern pour l'abstraction données

```python
class ClientRepository:
    def __init__(self, session):
        self.session = session
    
    async def find_by_id(self, client_id):
        return self.session.query(Client).filter_by(client_id=client_id).first()
    
    async def find_all(self, skip=0, limit=100):
        return self.session.query(Client).offset(skip).limit(limit).all()
    
    async def create(self, data):
        client = Client(**data)
        self.session.add(client)
        self.session.commit()
        return client
    
    async def update(self, client_id, data):
        client = self.find_by_id(client_id)
        for key, value in data.items():
            setattr(client, key, value)
        self.session.commit()
        return client
```

### 5.3 Mettre à jour les API endpoints

**Avant (MongoDB):**
```python
@router.get("/clients")
async def list_clients():
    cursor = db.clients.find({}).skip(offset).limit(limit).sort("created_at", -1)
    return [doc for doc in cursor]
```

**Après (PostgreSQL):**
```python
@router.get("/clients")
async def list_clients(skip: int = 0, limit: int = 100):
    clients = client_repo.find_all(skip=skip, limit=limit)
    return clients
```

### 5.4 Mettre à jour services

**Patterns:**
- ✅ Utiliser SQLAlchemy ORM
- ✅ Transactions ACID
- ✅ Gestion des exceptions PostgreSQL
- ✅ Utiliser les vues pour rapports
- ✅ Batch operations pour performance

---

## PHASE 6: CONFIGURATION REDIS (30 min)

Redis reste inchangé:
- [ ] Cache (sessions, queries)
- [ ] Files d'attente (background jobs)
- [ ] Notifications temps réel
- [ ] Locks distribués

Pas de modification, juste vérifier qu'il est actif:
```bash
redis-cli ping
# PONG
```

---

## PHASE 7: TESTS COMPLETS (1-2 heures)

### 7.1 Tests unitaires
```bash
cd /home/user/ERP-FABS-V10/backend
python -m pytest tests/ -v --cov=. --cov-report=html
```

- [ ] Couverture: 80%+
- [ ] Tests critiques: 100% de réussite
- [ ] Pas de warnings

### 7.2 Tests d'intégration

**Workflow Ventes complet:**
- [ ] Créer client ✅
- [ ] Créer commande ✅
- [ ] Générer facture ✅
- [ ] Enregistrer paiement ✅
- [ ] Créer bon livraison ✅
- [ ] Mettre à jour stock ✅
- [ ] Générer rapport ✅

**Tests du lot:**
```bash
python3 << 'EOF'
import asyncio
from backend.clients_module import create_client
from backend.commandes_module import create_order
from backend.factures_module import create_invoice

async def test_sales_workflow():
    # 1. Créer client
    client = await create_client({
        'name': 'TEST CLIENT',
        'email': 'test@test.com'
    })
    assert client.client_id
    
    # 2. Créer commande
    order = await create_order({
        'client_id': client.client_id,
        'items': [
            {'product_id': 'P001', 'quantity': 10, 'unit_price': 100}
        ]
    })
    assert order.order_id
    
    # 3. Créer facture
    invoice = await create_invoice({
        'order_id': order.order_id,
        'client_id': client.client_id
    })
    assert invoice.facture_id
    
    print("✅ Workflow ventes complète OK")

asyncio.run(test_sales_workflow())
EOF
```

### 7.3 Tests de charge

```bash
# Simuler 10 requêtes concurrentes
ab -n 100 -c 10 http://localhost:8001/api/clients

# Résultats attendus:
# - Requests per second: 50+
# - Failed requests: 0
# - Mean time: < 200ms
```

---

## PHASE 8: DÉPLOIEMENT PROGRESSIF (1-2 heures)

### 8.1 Phase ALPHA (Parallèle: MongoDB + PostgreSQL)

**Objectif:** Valider que les deux bases sont synchronized

1. Modifier backend pour lire/écrire dans les deux:
```python
async def create_client(data):
    # Écrire dans MongoDB (ancien)
    mongo_result = await db.clients.insert_one(data)
    
    # Écrire dans PostgreSQL (nouveau)
    pg_result = client_repo.create(data)
    
    # Comparer les résultats
    assert mongo_result.inserted_id
    assert pg_result.id
    
    return pg_result  # Retourner PostgreSQL
```

2. Lancer en production pour 24h avec:
   - [ ] Monitoring des deux bases
   - [ ] Validation des écritures
   - [ ] Tests utilisateurs réels
   - [ ] Pas de différences détectées

### 8.2 Phase BETA (Basculer vers PostgreSQL)

1. Modifier backend pour utiliser PostgreSQL uniquement:
   - [ ] Remplacer tous les appels MongoDB
   - [ ] Rediriger les lectures vers PostgreSQL
   - [ ] Garder MongoDB en read-only pour rollback

2. Déployer:
```bash
cd /home/user/ERP-FABS-V10
git add backend/models_postgresql.py backend/repositories/
git commit -m "Migrate to PostgreSQL - Phase Beta"
git push origin main
```

3. Monitorer 48h:
   - [ ] Aucune erreur critique
   - [ ] Performances stables/meilleures
   - [ ] Utilisateurs signalent "normal"
   - [ ] Backups PostgreSQL validés

### 8.3 Décommissioner MongoDB

Après 1 semaine sans problèmes:
- [ ] Arrêter MongoDB
- [ ] Archiver les backups MongoDB
- [ ] Documenter la désactivation
- [ ] Supprimer les connexions MongoDB du code

```bash
# Arrêter MongoDB
systemctl stop mongod

# Archiver
tar czf /backups/mongodb_final_archive_$(date +%Y%m%d).tar.gz /var/lib/mongodb/

# Supprimer les imports MongoDB du code
grep -r "from pymongo" /home/user/ERP-FABS-V10/backend/ | wc -l
# Doit être 0
```

---

## PHASE 9: DOCUMENTER & CLÔTURER (30 min)

### 9.1 Générer rapport de migration

```markdown
# RAPPORT MIGRATION MONGODB → POSTGRESQL

**Date:** 2026-06-25
**Status:** COMPLÈTE ✅

## Statistiques
- Documents MongoDB: XXXX
- Lignes PostgreSQL: XXXX
- Taux de succès: 100%

## Tables créées
- 100+ tables
- 50+ indexes
- 10 types ENUM
- 3 vues utilitaires

## Tests
- ✅ Tests unitaires: 100% passage
- ✅ Tests intégration: Tous les workflows OK
- ✅ Tests performance: < 200ms avg
- ✅ Tests charge: 50+ req/s

## Rollback
- Backup MongoDB complet: /backups/mongodb_final/
- Scripts rollback: 02_ROLLBACK_PROCEDURES.sql

## Recommandations post-migration
1. Monitorer PostgreSQL 24/7
2. Backups quotidiens PostgreSQL
3. Optimizer les index par usage réel
4. Mettre en place alertes slow queries
```

### 9.2 Archiver les fichiers de migration

```bash
tar czf /home/user/migration_artefacts_$(date +%Y%m%d).tar.gz \
  /home/user/01_SCHEMA_POSTGRESQL_COMPLET.sql \
  /home/user/02_ETL_MIGRATION.py \
  /home/user/migration.log \
  /home/user/mongodb_stats_pre_migration.json
```

### 9.3 Communicatuer aux stakeholders

- [ ] Email: Migration complète et validée ✅
- [ ] Documentation: Mise à jour wiki/docs
- [ ] Training: Formation équipe support à PostgreSQL
- [ ] SLA: Mettre à jour les garanties de service

---

## PHASE 10: ROLLBACK (SI NÉCESSAIRE)

### 10.1 Rollback MongoDB (24h après bascule)

Si problèmes critiques:
```bash
# 1. Arrêter l'application
systemctl stop erp-fabs-api

# 2. Restaurer MongoDB
mongorestore /backups/mongodb_backup_20260625/

# 3. Réactiver code MongoDB
git checkout backend/models_sqlalchemy.py
git checkout backend/server.py

# 4. Redémarrer
systemctl start erp-fabs-api
systemctl start mongod
```

### 10.2 Rollback PostgreSQL

Si problèmes critiques après 1+ semaine:

```bash
# Conserver les données PostgreSQL
pg_dump erp_fabs_ci > /backups/pg_dump_$(date +%Y%m%d).sql

# Restaurer MongoDb
systemctl start mongod

# Basculer code
git revert HEAD~N

# Redémarrer
systemctl restart erp-fabs-api
```

---

## CHECKLIST FINALE VALIDATION

### Avant déploiement
- [ ] Backup MongoDB complet
- [ ] PostgreSQL opérationnel
- [ ] Schéma créé et validé
- [ ] ETL script testé (dry-run)
- [ ] Fenêtre de maintenance planifiée
- [ ] Équipe support en standby
- [ ] Plan rollback documenté

### Pendant migration
- [ ] Monitoring MongoDB (progression)
- [ ] Monitoring PostgreSQL (insertion)
- [ ] Monitoring disque/mémoire
- [ ] Monitoring réseau/connexions
- [ ] Logs d'erreurs: < 0.1%

### Après migration
- [ ] Vérifier counts: 100% match
- [ ] Tester workflows clés: Ventes, Achats, RH
- [ ] Performances: acceptable
- [ ] Audit logs: préservés
- [ ] Utilisateurs: fonctionnalité OK

### Avant clôture
- [ ] Tous les tests: PASSING
- [ ] Documentation: MISE À JOUR
- [ ] Rapports: GÉNÉRÉS
- [ ] Stakeholders: INFORMÉS
- [ ] Artefacts: ARCHIVÉS

---

## CONTACT & ESCALADE

**Si problèmes pendant migration:**

1. **❌ Erreur lors de schéma SQL**
   - Vérifier PostgreSQL version
   - Vérifier permissions utilisateur
   - Consulter logs: `tail -f /var/log/postgresql/`

2. **❌ Erreur lors de migration données**
   - Arrêter le script
   - Vérifier MongoDB connectivité
   - Vérifier PostgreSQL espace disque
   - Consulter: `/home/user/migration.log`

3. **❌ Problèmes performance post-migration**
   - Analyser avec `EXPLAIN ANALYZE`
   - Vérifier les index manquants
   - Vérifier statistics: `ANALYZE;`
   - Considérer partitioning si nécessaire

4. **❌ Données manquantes/corruptées**
   - IMMÉDIAT ROLLBACK
   - Contacter responsable données
   - Analyser différences
   - Redémarrer migration depuis backup

---

**✅ MIGRATION MONGODB → POSTGRESQL PRÊTE À EXÉCUTER**

Temps total estimé: **5-6 heures**  
Status: **À COMMENCER MAINTENANT**  
Risque: **BAS** (avec checklist complète)


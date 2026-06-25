# 📋 COMPLETE ERP MIGRATION PLAN
## MongoDB → PostgreSQL (Zero-Loss, Behavior-Preserving)

**Version:** 2.0  
**Scope:** 100% data preservation, zero behavior changes  
**Timeline:** ~8-12 hours  
**Target Go-Live:** 1 Juillet 2026

---

## 🎯 MISSION CRITICAL REQUIREMENTS

### Must-Have Criteria
- ✅ **Zero records lost** — Every document migrated
- ✅ **No ID changes** — All `_id` preserved
- ✅ **No field modifications** — Exact data types
- ✅ **Relationships intact** — All foreign keys valid
- ✅ **Dates preserved** — Timestamps unchanged
- ✅ **Behavior identical** — UI/API/Modules unchanged
- ✅ **Performance equivalent** — Response times OK
- ✅ **Audit trail complete** — All history intact

---

## 📊 PRE-MIGRATION ANALYSIS

### Phase 1: MongoDB Discovery (2h)

**Objective:** Understand complete current state

```bash
# Step 1: Analyze MongoDB Structure
python3 /home/user/MONGODB_COMPLETE_ANALYSIS.py

# Output:
#   - All 25+ collections identified
#   - Document count per collection
#   - Field types and relationships
#   - Data issues detected
#   - Report: /tmp/mongodb_analysis_complete.json
```

**Collections Expected:**
```
users
clients
produits
commandes (orders)
factures
paiements (payments)
fournisseurs (suppliers)
categorie_produit (product categories)
mouvements_stock (stock movements)
devis (quotes)
ventes (sales)
achats (purchases)
ressources_humaines (HR)
documents
notifications
audit_logs
sessions
api_keys
refresh_tokens
compliance_logs
security_audit_reports
performance_metrics
alert_rules
incidents
vulnerabilities
```

**Before-Migration Count Template:**
```
users:                   ~XX
clients:               ~1014
produits:                ~56
fournisseurs:          ~XXX
commandes:             ~XXX
factures:              ~XXX
paiements:             ~XXX
mouvements_stock:      ~XXX
devis:                 ~XXX
ventes:                ~XXX
achats:                ~XXX
...
────────────────────────────
TOTAL:              ~XXXXX
```

---

## 🔧 MIGRATION EXECUTION

### Phase 2: PostgreSQL Schema Design (3h)

**Objective:** Mirror MongoDB structure exactly

```sql
-- For each MongoDB collection, create corresponding table:

-- Example 1: Direct mapping (users)
CREATE TABLE users (
    id TEXT PRIMARY KEY,           -- Original _id
    email VARCHAR(255) UNIQUE,
    nom_complet TEXT,
    role VARCHAR(50),
    actif BOOLEAN,
    password_hash TEXT,
    picture TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _raw_mongodb JSONB            -- Full original document
);

-- Example 2: Complex objects (commandes)
CREATE TABLE commandes (
    id TEXT PRIMARY KEY,           -- Original _id
    numero_commande VARCHAR(50),
    client_id TEXT REFERENCES clients(id),
    date_commande TIMESTAMP,
    montant_total NUMERIC(15, 2),
    status VARCHAR(50),
    items JSONB,                   -- Array stored as JSON
    metadata JSONB,                -- Extra fields
    created_at TIMESTAMP,
    _raw_mongodb JSONB
);

-- Example 3: Audit trail (audit_logs)
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    action VARCHAR(100),
    collection TEXT,
    document_id TEXT,
    changes JSONB,
    timestamp TIMESTAMP,
    _raw_mongodb JSONB
);
```

**Rules:**
- ✅ Keep original `_id` as primary key (TEXT)
- ✅ Store full original document in `_raw_mongodb` (JSONB) for safety
- ✅ Create indices on frequently queried fields
- ✅ Use JSONB for nested objects/arrays
- ✅ Preserve all audit fields

### Phase 3: Complete ETL Migration (2-3h)

**Objective:** Migrate 100% of data

```bash
# Run complete migration engine
python3 /home/user/ETL_COMPLETE_MIGRATION_ENGINE.py

# Process:
# 1. Extract all documents from every collection
# 2. Transform preserving original IDs
# 3. Load into PostgreSQL with atomic transactions
# 4. Verify referential integrity
# 5. Compare before/after counts
# 6. Generate validation report
```

**ETL Phases:**
1. **Extract** — Fetch all MongoDB documents
2. **Transform** — Convert ObjectId → TEXT, DateTime → ISO8601
3. **Load** — Insert with transactions (all-or-nothing)
4. **Validate** — Check referential integrity
5. **Compare** — Before/after count matching

### Phase 4: Data Validation & Verification (2-3h)

**Objective:** Prove zero data loss

```sql
-- Validation Queries

-- 1. Count verification (MUST MATCH)
SELECT 'users' as collection, COUNT(*) as count FROM users
UNION ALL
SELECT 'clients', COUNT(*) FROM clients
UNION ALL
SELECT 'produits', COUNT(*) FROM produits
UNION ALL
SELECT 'fournisseurs', COUNT(*) FROM fournisseurs
UNION ALL
... (all collections)

-- 2. Duplicate ID check (MUST BE 0)
SELECT collection, id, COUNT(*) 
FROM (
    SELECT 'users' as collection, id FROM users
    UNION ALL
    SELECT 'clients', id FROM clients
    ...
) t
GROUP BY collection, id
HAVING COUNT(*) > 1;

-- 3. Referential integrity (MUST BE 0)
SELECT COUNT(*) FROM commandes 
WHERE client_id NOT IN (SELECT id FROM clients);

-- 4. Date preservation (SAMPLE CHECK)
SELECT 
    COUNT(*) as total,
    COUNT(created_at) as with_created_at,
    COUNT(updated_at) as with_updated_at,
    MIN(created_at) as oldest,
    MAX(created_at) as newest
FROM users;

-- 5. Field completeness (MUST HAVE NO NULLS in required fields)
SELECT COUNT(*) FROM users WHERE email IS NULL;
SELECT COUNT(*) FROM clients WHERE nom_client IS NULL;
SELECT COUNT(*) FROM produits WHERE code_produit IS NULL;

-- 6. Data type checks
SELECT 
    SUM(CASE WHEN montant_total < 0 THEN 1 ELSE 0 END) as negative_amounts,
    SUM(CASE WHEN montant_total > 999999999 THEN 1 ELSE 0 END) as impossible_amounts
FROM commandes;
```

---

## 🔐 BACKEND CONFIGURATION

### Phase 5: Update Backend to Use PostgreSQL (1h)

**Objective:** Point backend to PostgreSQL instead of MongoDB

**Files to update:**
```
/home/user/ERP-MIGRATION-V2/v2-target/backend/app_postgres.py
  - DATABASE_URL → PostgreSQL connection
  - Remove MongoDB initialization
  - Remove mongomock fallback

/home/user/ERP-MIGRATION-V2/v2-target/backend/db/dependencies.py
  - Create PostgreSQL session factory
  - Create repository classes
  - Replace MongoDB collection access

/home/user/ERP-MIGRATION-V2/v2-target/backend/db/models/
  - SQLAlchemy ORM models (if needed)
  - Or use sqlalchemy-json for JSONB fields
```

**Environment:**
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/erp_fabs_ci_postgres
MONGO_URL=  # Remove or set to dummy
USE_MONGODB=false
USE_POSTGRESQL=true
```

---

## 🧪 TESTING & VALIDATION

### Phase 6: Complete Testing (2-3h)

**Step 1: Unit Tests**
```bash
# Test all endpoints with real migrated data
pytest /home/user/ERP-MIGRATION-V2/v2-target/tests/

# Expected:
#   - GET /api/users → 200, returns migrated users
#   - GET /api/clients → 200, returns 1014 clients
#   - GET /api/produits → 200, returns 56 products
#   - GET /api/commandes → 200, returns all orders
#   - POST /api/commandes → works with migrated data
#   - All filters, sorts, searches work
```

**Step 2: End-to-End Tests**
```bash
# Test complete workflows
1. Login as migrated user
2. View client details
3. Create new order (references migrated product & client)
4. Generate invoice (references migrated order)
5. Export report (reads migrated data)
6. Check audit logs (migrated history)
```

**Step 3: Performance Tests**
```bash
# Load test with 20-50 concurrent users
# Expected response times < 200ms

python3 /home/user/ERP-MIGRATION-V2/v2-target/scripts/load_test.py \
    --users 50 \
    --duration 300 \
    --base_url http://localhost:8005
```

---

## 📈 ROLLBACK PLAN

**If migration fails:**

```sql
-- Option 1: Restore from backup
pg_restore --dbname=erp_fabs_ci_postgres /backup/pre_migration.dump

-- Option 2: Keep MongoDB running temporarily
# Keep MongoDB Atlas running during cutover
# If PostgreSQL fails, revert backend to MongoDB
# Then retry migration after fixing issues
```

---

## ✅ GO-LIVE CHECKLIST

- [ ] MongoDB analysis complete (all collections identified)
- [ ] Before-migration counts documented
- [ ] PostgreSQL schema created
- [ ] All 100% data migrated
- [ ] After-migration counts match before-migration
- [ ] Referential integrity validated
- [ ] No duplicate IDs
- [ ] All dates preserved
- [ ] All required fields present
- [ ] Backend configured for PostgreSQL
- [ ] All API endpoints tested
- [ ] All module workflows tested
- [ ] Performance acceptable
- [ ] Audit trails verified
- [ ] Sign-off from business owner
- [ ] Backup taken
- [ ] Rollback plan rehearsed
- [ ] Go-live scheduled
- [ ] Monitoring setup
- [ ] Support team briefed

---

## 📊 COMPARISON REPORT TEMPLATE

```markdown
# Migration Validation Report

## Before Migration (MongoDB)
| Collection | Count |
|------------|-------|
| users | XX |
| clients | 1014 |
| produits | 56 |
| ... | ... |
| **TOTAL** | **XXXXX** |

## After Migration (PostgreSQL)
| Collection | Count | Status |
|------------|-------|--------|
| users | XX | ✅ |
| clients | 1014 | ✅ |
| produits | 56 | ✅ |
| ... | ... | ✅ |
| **TOTAL** | **XXXXX** | ✅ |

## Validation Summary
- ✅ Zero record loss
- ✅ All IDs preserved
- ✅ All relationships valid
- ✅ All dates intact
- ✅ All modules functional
- ✅ Performance acceptable

## Sign-Off
**Migrated by:** Odelia Ode  
**Date:** 2026-06-25  
**Status:** 🟢 PRODUCTION-READY  
**MongoDB:** Decommissioned  
**PostgreSQL:** Live
```

---

## 🚀 EXECUTION TIMELINE

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | MongoDB Discovery & Analysis | 2h | ⏳ |
| 2 | PostgreSQL Schema Design | 3h | ⏳ |
| 3 | ETL Migration Execution | 2-3h | ⏳ |
| 4 | Data Validation & Verification | 2-3h | ⏳ |
| 5 | Backend Configuration | 1h | ⏳ |
| 6 | Testing & QA | 2-3h | ⏳ |
| **TOTAL** | | **12-15h** | ⏳ |

**Start:** Once MongoDB location confirmed  
**Target:** 1 Juillet 2026

---

## 📞 SUPPORT

**Questions during migration?**
- Check `/tmp/etl_migration_complete.json` for error details
- Review `/tmp/mongodb_analysis_complete.json` for structure
- All scripts have detailed logging

**After migration?**
- MongoDB can be archived/decommissioned
- PostgreSQL backups automated
- Monitoring setup for performance

---

**Prepared by:** Odelia Ode  
**Date:** 25 Juin 2026  
**Status:** Ready to execute once MongoDB location confirmed

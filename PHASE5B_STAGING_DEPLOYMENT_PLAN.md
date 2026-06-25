# PHASE 5B STAGING DEPLOYMENT PLAN
## Railway Deployment (Recommended)

**Date:** 25 JUN 2026  
**Target:** Staging environment (pre-production)  
**Timeline:** 1-3 JUL 2026 (5 days before go-live)

---

## ARCHITECTURE

```
GitHub (Main Branch)
    ↓
Railway (Auto-deploy)
    ├── Backend Service (FastAPI + PostgreSQL)
    │   ├── Runtime: Python 3.11+
    │   ├── Database: PostgreSQL (managed by Railway)
    │   ├── Env: DATABASE_URL, JWT_SECRET, ALLOWED_ORIGINS
    │   └── Port: 8000 (Railway auto-manages)
    │
    └── Frontend Service (Static React)
        ├── Build: npm run build
        ├── Serve: Static files (build/)
        ├── Env: REACT_APP_API_BASE_URL=https://backend.railway.app/api
        └── Port: 3000 (Railway auto-manages)
```

---

## STEP 1: RAILWAY ACCOUNT & PROJECT SETUP

### 1.1 Create Railway Account
- Go to https://railway.app
- Sign up with GitHub (recommended for auto-deploy)
- Create organization: `FABS-CI`

### 1.2 Create Railway Project
- New Project → Import from GitHub
- Repository: `https://github.com/FABS-CI/ERP-FABS-CI-GEST-V1-.0.0-PostgreSQL`
- Branch: `main` (auto-deploy on push)

### 1.3 Project Structure (Railway recognizes)
```
ERP-FABS-CI-GEST-V1-.0.0-PostgreSQL/
├── backend/                    ← FastAPI service (auto-detected)
│   ├── Procfile (optional)
│   ├── requirements.txt
│   ├── app_postgres.py
│   └── ...
├── frontend/                   ← React service (auto-detected)
│   ├── package.json
│   ├── public/
│   ├── src/
│   └── build/ (after npm run build)
└── .github/workflows/          ← CI/CD (optional but recommended)
```

---

## STEP 2: BACKEND SERVICE SETUP

### 2.1 Create Procfile (Backend)
**File:** `/backend/Procfile`

```
web: python -m uvicorn app_postgres:app --host 0.0.0.0 --port $PORT
```

### 2.2 Environment Variables (Railway Dashboard)
```
DATABASE_URL=postgresql+asyncpg://user:password@db.railway.app/erp_fabs_ci
JWT_SECRET=your-secret-key-min-32-chars
ALLOWED_ORIGINS=https://frontend.railway.app,https://yourdomain.com
ENVIRONMENT=staging
LOG_LEVEL=info
```

### 2.3 Database (Managed PostgreSQL on Railway)
- Railway → Add Service → PostgreSQL
- Auto-creates `DATABASE_URL` env variable
- Connection: Staging database (separate from production)
- Backups: Daily (configurable)

### 2.4 Build Command (if needed)
```bash
pip install -r requirements.txt
alembic upgrade head  # Run migrations (if using)
```

---

## STEP 3: FRONTEND SERVICE SETUP

### 3.1 Create Procfile (Frontend)
**File:** `/frontend/Procfile`

```
web: npm run build && npx serve -s build -l $PORT
```

### 3.2 Environment Variables (Frontend)
```
REACT_APP_API_BASE_URL=https://backend-staging.railway.app/api
REACT_APP_ENVIRONMENT=staging
```

**Note:** Railway sets `PORT` automatically. Frontend build must include env vars.

### 3.3 Build Process
1. `npm install` (Railway auto-runs on push)
2. `npm run build` (Procfile command)
3. Serve static files from `build/` folder

---

## STEP 4: GITHUB ACTIONS CI/CD (OPTIONAL)

**File:** `.github/workflows/deploy.yml`

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: railway-app/deploy-action@v1
        with:
          token: ${{ secrets.RAILWAY_TOKEN }}
          service: both  # Deploy both backend and frontend
```

**Setup:**
1. Railway Dashboard → Account → Tokens
2. Generate API Token
3. GitHub Repo → Settings → Secrets → Add `RAILWAY_TOKEN`

---

## STEP 5: TESTING CHECKLIST

### 5.1 Backend Health Check
```bash
curl -X GET https://backend-staging.railway.app/health

# Expected response:
{
  "status": "ok",
  "service": "ERP FABS-CI API",
  "version": "1.0.0",
  "timestamp": "2026-06-25T15:00:00"
}
```

### 5.2 API Endpoints (Sample)
```bash
# Get clients
curl -X GET https://backend-staging.railway.app/api/clients \
  -H "Authorization: Bearer <token>"

# Get products
curl -X GET https://backend-staging.railway.app/api/products

# Get orders
curl -X GET https://backend-staging.railway.app/api/orders
```

### 5.3 Frontend Smoke Tests
- ✅ Login page loads (`https://frontend-staging.railway.app/login`)
- ✅ API requests work (check browser console for CORS errors)
- ✅ Dashboard renders
- ✅ Navigation sidebar works
- ✅ Create/Read/Update/Delete flows work for:
  - Clients
  - Products
  - Orders
  - Invoices
  - Employees

---

## STEP 6: LOAD TESTING (20-50 USERS)

### 6.1 Locust (Python load testing)

**File:** `locustfile.py`

```python
from locust import HttpUser, task, between
import random

class ERP_User(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_clients(self):
        self.client.get("/api/clients", headers={"Authorization": f"Bearer {token}"})
    
    @task
    def get_products(self):
        self.client.get("/api/products")
    
    @task
    def get_orders(self):
        self.client.get("/api/orders")
    
    @task
    def create_order(self):
        payload = {
            "client_id": random.randint(1, 100),
            "lignes": [{"produit_id": 1, "quantite": 5}]
        }
        self.client.post("/api/orders", json=payload)
```

**Run:**
```bash
locust -f locustfile.py -u 50 -r 5 --run-time 5m \
  --host https://backend-staging.railway.app/api
```

**Monitor:**
- Response times (target: < 500ms @ 50 users)
- Error rate (target: 0%)
- Database connections (max: 20)

---

## STEP 7: E2E TESTS (CYPRESS OR PLAYWRIGHT)

**File:** `frontend/cypress/e2e/staging.spec.js`

```javascript
describe('ERP Staging E2E Tests', () => {
  const baseUrl = 'https://frontend-staging.railway.app'
  
  it('Login flow', () => {
    cy.visit(`${baseUrl}/login`)
    cy.get('input[name="email"]').type('pissken@editionsfabsci.com')
    cy.get('input[name="password"]').type('Admin@2025')
    cy.get('button[type="submit"]').click()
    cy.url().should('include', '/dashboard')
  })
  
  it('Create client', () => {
    cy.visit(`${baseUrl}/clients`)
    cy.get('button[data-testid="btn-add-client"]').click()
    cy.get('input[name="nom_client"]').type('Test Client')
    cy.get('input[name="email"]').type('test@example.com')
    cy.get('button[type="submit"]').click()
    cy.get('[role="alert"]').should('contain', 'Client created')
  })
  
  it('Create order', () => {
    cy.visit(`${baseUrl}/commandes`)
    cy.get('button[data-testid="btn-new-order"]').click()
    cy.get('select[name="client_id"]').select(1)
    // ... add line items
    cy.get('button[type="submit"]').click()
  })
})
```

**Run:**
```bash
npx cypress run --config baseUrl=https://frontend-staging.railway.app
```

---

## STEP 8: MONITORING & LOGGING

### 8.1 Railway Logs
- Dashboard → Services → Backend → Logs
- Monitor for:
  - Errors (500s)
  - Database connection issues
  - Authentication failures

### 8.2 Sentry (Error Tracking) — Optional
```bash
pip install sentry-sdk

# In app_postgres.py
import sentry_sdk
sentry_sdk.init(
    dsn="https://your-sentry-url",
    environment="staging",
    traces_sample_rate=0.1
)
```

### 8.3 Uptime Monitoring
- https://uptime-robot.com
- Monitor: `https://backend-staging.railway.app/health`
- Alert on downtime

---

## TIMELINE

| Date | Task | Owner |
|------|------|-------|
| 1 JUL | Railway setup + backend deploy | DevOps |
| 2 JUL | Frontend deploy + smoke tests | QA |
| 3 JUL | E2E testing (Cypress) | QA |
| 4 JUL | Load testing (20-50 users) | DevOps |
| 5 JUL | Fix issues + optimization | Dev |
| 10-15 JUL | Production go-live | All |

---

## ROLLBACK PLAN

If staging fails:
1. **Revert Git:** `git revert <commit>` → push to main
2. **Railway auto-deploys** revert
3. **MongoDB fallback:** Keep MongoDB running 14 days post-launch
4. **Restore backup:** Use PostgreSQL automated daily backups

---

## CHECKLIST

### Pre-Deployment
- ✅ Backend builds locally
- ✅ Frontend builds locally
- ✅ All env variables documented
- ✅ Database migrations prepared
- ✅ API documentation updated

### Deployment
- ⏳ Railway project created
- ⏳ GitHub auto-deploy enabled
- ⏳ Environment variables set
- ⏳ Backend service deployed
- ⏳ Frontend service deployed

### Post-Deployment
- ⏳ Health check passed
- ⏳ API endpoints tested
- ⏳ Frontend smoke tests passed
- ⏳ Load testing completed
- ⏳ E2E tests all green
- ⏳ Monitoring alerts configured

---

## CONTACTS & ESCALATION

| Role | Responsibility | Contact |
|------|-----------------|---------|
| DevOps | Railway setup, DB, monitoring | TBD |
| Backend Dev | API fixes, migrations | TBD |
| Frontend Dev | React build, UI fixes | TBD |
| QA | Testing, load tests | TBD |
| PM | Timeline, blockers | Odelia Ode |

---

**Next Step:** Execute Phase 5B deployment (1 JUL 2026)

# Phase 3: Launch Preparation Checklist

**Start Date:** 25 JUN 2026  
**Launch Date:** 10 JUL 2026  
**Time Available:** 15 days  

---

## 🎯 CRITICAL PATH (Blocking Launch)

### Week 1 (25-28 JUN) — Testing & Validation

- [ ] **Docker Smoke Test** (30 min)
  - [ ] PostgreSQL container starts
  - [ ] Backend container connects to DB
  - [ ] Redis container initializes
  - [ ] All services reach healthy state within 60s
  
- [ ] **Integration Test: Clients → Orders → Invoices** (2 hours)
  - [ ] Create client via clients_module
  - [ ] Create order via commandes_module
  - [ ] Verify order stored in PostgreSQL
  - [ ] Check order retrieval works
  - [ ] Verify client lookup from order works
  
- [ ] **Load Test (20 Concurrent Users)** (1.5 hours)
  - [ ] Target: response time < 500ms average
  - [ ] Test: list clients, create order, get order
  - [ ] Monitor: CPU, memory, PostgreSQL connections
  - [ ] Pass criteria: zero crashes, all requests succeed
  
- [ ] **Rollback Procedure Documented** (1 hour)
  - [ ] MongoDB backup procedure documented
  - [ ] Fallback instructions if PostgreSQL fails
  - [ ] Data sync procedure (PostgreSQL ↔ MongoDB)
  - [ ] Recovery time objective: < 30 minutes

### Week 2 (29 JUN - 5 JUL) — Pre-Launch

- [ ] **All 19 Test Suites Pass** (3 hours)
  - [ ] Run full test suite locally
  - [ ] Fix any broken tests
  - [ ] Achieve 100% pass rate (or document exceptions)
  
- [ ] **Performance Baseline Established** (2 hours)
  - [ ] Measure: average response time per endpoint
  - [ ] Measure: 95th percentile latency
  - [ ] Measure: throughput (req/sec)
  - [ ] Document baseline for post-launch comparison
  
- [ ] **Monitoring & Alerting Configured** (2 hours)
  - [ ] Grafana dashboard for PostgreSQL metrics
  - [ ] Alert: High error rate (> 1%)
  - [ ] Alert: Slow queries (> 1 second)
  - [ ] Alert: Connection pool exhaustion
  - [ ] Alert: Disk space low
  
- [ ] **Deployment Runbook Finalized** (1.5 hours)
  - [ ] Step-by-step launch procedure
  - [ ] Health check validation commands
  - [ ] Rollback procedures documented
  - [ ] Communication template for downtime notification
  
- [ ] **MongoDB Backup Created & Validated** (1 hour)
  - [ ] Full backup of all MongoDB data
  - [ ] Test restore procedure
  - [ ] Store backup with 2-week retention policy
  - [ ] Document backup location & access

- [ ] **Final Security Review** (1 hour)
  - [ ] PostgreSQL password not in code (use env vars)
  - [ ] Connection strings use parameterized queries
  - [ ] No SQL injection vulnerabilities (scan code)
  - [ ] Secrets management verified (.env files excluded from git)

---

## 🚀 LAUNCH DAY (10 JUL)

- [ ] **Pre-Launch Checklist (30 min before)**
  - [ ] All team members briefed
  - [ ] Rollback procedure reviewed
  - [ ] Monitoring dashboard open
  - [ ] Slack channel for communication ready
  
- [ ] **Deployment Execution** (1-2 hours expected)
  - [ ] Announce planned maintenance window to users
  - [ ] Deploy refactored clients_module.py
  - [ ] Deploy refactored commandes_module.py
  - [ ] Deploy compatibility shim (db/motor_compat.py)
  - [ ] Configure other modules to use compat DB
  - [ ] Start all services with PostgreSQL
  - [ ] Validate health checks pass
  
- [ ] **Validation (1 hour)**
  - [ ] List clients endpoint responds (API test)
  - [ ] Create order endpoint works (end-to-end test)
  - [ ] Check PostgreSQL logs for errors
  - [ ] Verify no 500 errors in API responses
  - [ ] Monitor response times (< 500ms acceptable)
  
- [ ] **Post-Launch Monitoring (24 hours)**
  - [ ] Check error rates every 15 minutes for first hour
  - [ ] Monitor every hour for first 8 hours
  - [ ] Monitor every 4 hours for day 2
  - [ ] Be prepared to rollback if issues detected

---

## 📋 OPTIONAL (Post-Launch, Non-Blocking)

### Week 3-4 (11-30 JUL) — Gradual Refactoring

- [ ] **Refactor factures_module.py** (2-3 hours)
  - [ ] Study original module
  - [ ] Create PostgreSQL version
  - [ ] Test with invoice generation
  - [ ] Deploy (or keep on compat shim)
  
- [ ] **Refactor comptabilite_module.py** (2-3 hours)
  - [ ] Study original module
  - [ ] Create PostgreSQL version
  - [ ] Test accounting calculations
  - [ ] Deploy
  
- [ ] **Refactor administration_module.py** (1.5 hours)
  - [ ] Study original module
  - [ ] Create PostgreSQL version
  - [ ] Test user/role operations
  - [ ] Deploy
  
- [ ] **Refactor analytics_module.py** (1.5 hours)
  - [ ] Study original module
  - [ ] Create PostgreSQL version with SQLAlchemy aggregations
  - [ ] Test report generation
  - [ ] Deploy
  
- [ ] **Refactor bi_analytics_module.py** (1 hour)
  - [ ] Study original module
  - [ ] Create PostgreSQL version
  - [ ] Test BI queries
  - [ ] Deploy

- [ ] **Remove Compatibility Shim** (30 min)
  - [ ] Verify all modules using native repos
  - [ ] Delete motor_compat.py
  - [ ] Update imports in router builders
  - [ ] Final test of all modules

- [ ] **Performance Optimization** (2-3 hours)
  - [ ] Add missing indexes (identified from slow query log)
  - [ ] Optimize N+1 queries (identified from profiling)
  - [ ] Enable query caching where appropriate
  - [ ] Measure improvement vs. baseline

---

## 📞 ESCALATION CONTACTS

| Issue | Contact | Response Time |
|-------|---------|---|
| PostgreSQL down | DevOps Lead | 15 min |
| API not responding | Backend Lead | 10 min |
| Data migration issue | DB Admin | 20 min |
| Business impact | Project Manager | 30 min |

---

## ✅ GO/NO-GO DECISION CRITERIA

### MUST HAVE (Blocking Launch)
- [ ] Docker smoke test: PASS
- [ ] Integration test: PASS  
- [ ] Load test 20 users: PASS (< 500ms)
- [ ] Rollback procedure: DOCUMENTED
- [ ] All critical tests: PASS

### SHOULD HAVE (Nice to Have)
- [ ] All 19 test suites: PASS
- [ ] Performance baseline: ESTABLISHED
- [ ] Monitoring configured: YES
- [ ] Runbook: WRITTEN

### SIGN-OFF
- [ ] DevOps Lead: Approved deployment process
- [ ] Tech Lead: Approved code quality
- [ ] Project Manager: Confirmed timeline
- [ ] Product Owner: Confirmed feature completeness

---

## 📊 SUCCESS METRICS (First 24 Hours)

| Metric | Target | Acceptable | Failure |
|--------|--------|-----------|---------|
| Error Rate | < 0.1% | < 0.5% | > 1% (rollback) |
| Avg Response Time | < 200ms | < 500ms | > 1s (investigate) |
| 95th Latency | < 400ms | < 800ms | > 2s (investigate) |
| Availability | 99.9% | 99% | < 99% (rollback) |
| Data Loss | 0 records | 0 records | Any loss (rollback) |

---

## 📝 SIGN-OFF

**Prepared By:** Odelia Ode  
**For:** ERP FABS-CI PostgreSQL Migration  
**Status:** Ready for execution  
**Last Updated:** 25 JUN 2026 15:00 UTC  

---

**APPROVAL REQUIRED:**

- [ ] Tech Lead _________________ Date: _______
- [ ] DevOps Lead _______________ Date: _______
- [ ] Project Manager __________ Date: _______


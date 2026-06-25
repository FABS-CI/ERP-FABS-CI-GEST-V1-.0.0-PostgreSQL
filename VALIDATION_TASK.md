# V2.0 VALIDATION TASK — PROGRESS TRACKER

## Current Task
**Fix Dependency Injection in all 6 routes + services**

## Status
- ✅ Created db/dependencies.py (all repo providers)
- ✅ Fixed routes/clients.py
- ✅ Fixed routes/products.py
- ✅ Fixed routes/orders.py
- 🔄 NEXT: Fix routes/invoices.py (3 repos: invoice, order, client)
- ⏳ TODO: Fix routes/employees.py (1 repo: employee)
- ⏳ TODO: Fix routes/users.py (1 repo: user)
- ⏳ TODO: Test all 30 endpoints
- ⏳ TODO: Load test (20-50 users)
- ⏳ TODO: Generate final sign-off report

## Modules to Validate (6 Critical)
1. **CRM + Clients** → routes/clients.py ✅
2. **Ventes + Facturation** → routes/orders.py ✅ + routes/invoices.py 🔄
3. **Achats + Stocks** → routes/products.py ✅
4. **Comptabilité + Rapports** → routes/invoices.py 🔄
5. **RH + Paie** → routes/employees.py ⏳
6. **Admin + Logs** → routes/users.py ⏳

## Go-Live Date
**1er juillet 2026** ✓

## Notes
- Bug: Services expect repos in __init__(), routes didn't pass them
- Solution: Create Depends() providers in db/dependencies.py, inject into routes
- Strategy: Fix routes 1-by-1, test each module after fix

"""
ERP FABS-CI — FastAPI App (PostgreSQL)
PHASE 3: FastAPI Integration with SQLAlchemy ORM
"""

import os
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import get_session, init_db, close_db
from routes import users, clients, products, orders, invoices, employees

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# LIFESPAN EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # STARTUP
    logger.info("🚀 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Closing database connections...")
    await close_db()
    logger.info("✅ Database closed")

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="ERP FABS-CI API",
    description="Enterprise Resource Planning for ÉDITIONS FABS-CI",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "ERP FABS-CI API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# API ROUTES
# ============================================================================

app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(invoices.router, prefix="/api/invoices", tags=["Invoices"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Generic exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    reload = os.getenv("API_RELOAD", "false").lower() == "true"
    
    uvicorn.run(
        "app_postgres:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

"""
Database base configuration - SQLAlchemy 2.0 + AsyncIO
PostgreSQL only (MongoDB removed)
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import event
from sqlalchemy.pool import NullPool

# ============================================================================
# DATABASE URL
# ============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost/erp_fabs_ci"
)

# ============================================================================
# ENGINE CONFIGURATION
# ============================================================================

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
    future=True,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,   # Recycle connections every hour
)

# ============================================================================
# SESSION FACTORY
# ============================================================================

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# ============================================================================
# DECLARATIVE BASE FOR MODELS
# ============================================================================

Base = declarative_base()

# ============================================================================
# SESSION DEPENDENCY FOR FASTAPI
# ============================================================================

async def get_session() -> AsyncSession:
    """Get async database session for FastAPI dependency injection"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database (create tables if they don't exist)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()

"""
Database configuration and initialization.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)


class Base(DeclarativeBase):
    """
    Base class for all database models.
    """
    pass


# Global variables for database connection
engine = None
SessionLocal = None


async def init_db():
    """
    Initialize database connection and create tables.
    """
    global engine, SessionLocal
    
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        echo=settings.DEBUG,
    )
    
    # Create session factory
    SessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Test connection
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error("Failed to connect to database", error=str(e))
        raise


async def get_db() -> AsyncSession:
    """
    Dependency to get database session.
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_db():
    """
    Close database connections.
    """
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")

"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
import structlog

from app.core.database import get_db
from app.core.config import get_settings

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "AI Technical Article Generation System"}


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check including database and Redis connectivity."""
    settings = get_settings()
    health_status = {
        "status": "healthy",
        "services": {
            "database": "unknown",
            "redis": "unknown",
            "api": "healthy"
        }
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status

import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, timezone

# ensure project root is on sys.path so 'app' package imports work when running main.py directly
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.routes.courses import router as courses_router
from app.routes.admin import router as admin_router
from app.jobs.scheduler import start_scheduler
from app.config import settings
from app.logging_config import setup_logging
from app.db.base import async_session
from sqlalchemy import text
import asyncpg

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Start background scheduler
    start_scheduler()
    logger.info("Background scheduler started")

    yield

    logger.info("Shutting down application")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Include routers
app.include_router(courses_router, prefix="/api/v1/courses", tags=["courses"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with database connection test."""
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except asyncpg.InterfaceError as e:
        # Connection exists but is busy with another operation
        logger.warning(f"Database connection busy: {e}")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
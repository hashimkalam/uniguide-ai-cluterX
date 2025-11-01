import asyncio
import logging
from app.db.base import engine, Base
from app.db.models import University, Course, EntryRequirement  # Import models to register them
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Models imported successfully")

async def create_tables():
    """Create all database tables."""
    print("Starting create_tables function")
    try:
        logger.info("Creating database tables...")
        print(f"Base metadata tables: {list(Base.metadata.tables.keys())}")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        raise

async def drop_tables():
    """Drop all database tables."""
    try:
        logger.info("Dropping database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop tables: {str(e)}")
        raise

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        asyncio.run(drop_tables())
    else:
        asyncio.run(create_tables())
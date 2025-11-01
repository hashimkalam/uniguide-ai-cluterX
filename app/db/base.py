from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Ensure the database URL uses asyncpg driver
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Log the database URL (mask password)
masked_url = database_url.replace(database_url.split('@')[0].split(':')[-1], '***')
logger.info(f"Connecting to database: {masked_url}")

try:
    engine = create_async_engine(database_url, future=True, echo=settings.debug)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    Base = declarative_base()
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

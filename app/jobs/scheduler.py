import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.ingest import run_data_ingestion
import asyncio

logger = logging.getLogger(__name__)

async def refresh_job():
    """Background job to refresh data from Discover Uni sources."""
    try:
        logger.info("Starting data refresh job...")
        
        # Ingest the data (data is already downloaded)
        results = await run_data_ingestion()
        logger.info(f"Data refresh completed: {results}")
    except Exception as e:
        logger.error(f"Data refresh failed: {str(e)}")

def sync_refresh_job():
    """Synchronous wrapper for the async refresh job."""
    asyncio.run(refresh_job())

def start_scheduler():
    """Start the background scheduler with data refresh job."""
    scheduler = BackgroundScheduler()

    # Add the data refresh job to run daily
    scheduler.add_job(
        sync_refresh_job,
        'interval',
        hours=24,  # Run daily
        id='refresh_discover_uni',
        name='Refresh Discover Uni Data',
        max_instances=1,  # Only one instance at a time
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started with daily data refresh job")

def trigger_manual_refresh():
    """Manually trigger a data refresh (for API endpoints)."""
    sync_refresh_job()

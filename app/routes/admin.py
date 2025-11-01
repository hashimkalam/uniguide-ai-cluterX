from fastapi import APIRouter, BackgroundTasks
from app.jobs.scheduler import trigger_manual_refresh
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/refresh-data", summary="Trigger manual data refresh")
async def refresh_data(background_tasks: BackgroundTasks):
    """
    Manually trigger a data refresh from Discover Uni sources.

    This runs the same process as the daily background job.
    """
    try:
        # Run in background to avoid blocking the API response
        background_tasks.add_task(trigger_manual_refresh)
        return {"message": "Data refresh started in background"}
    except Exception as e:
        logger.error(f"Failed to start data refresh: {str(e)}")
        return {"error": f"Failed to start data refresh: {str(e)}"}
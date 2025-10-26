import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from ..schemas import ScrapeTriggerRequest, StatusUpdate, DataIngest # New import

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/trigger/{site_name}", response_model=Dict[str, Any])
async def trigger_scraping_webhook(site_name: str, request: ScrapeTriggerRequest):
    """
    Webhook endpoint to trigger a scraping task for a specific site.

    This endpoint would typically be called by n8n to initiate a scrape.
    The request body contains additional parameters for the scraping job.
    """
    logger.info(f"Webhook received: Trigger scraping for site '{site_name}' with payload: {request.dict()}")
    # Here, you would typically enqueue a scraping job
    # For now, we'll just return a success message.
    return {"message": f"Scraping for site '{site_name}' triggered successfully.", "status": "received", "details": request.dict()}

@router.post("/status_update", response_model=Dict[str, Any])
async def receive_status_update_webhook(status_update: StatusUpdate):
    """
    Webhook endpoint to receive status updates from n8n or other services.

    This could be used to update the status of a scrape job, data validation, etc.
    """
    logger.info(f"Webhook received: Status update with payload: {status_update.dict()}")
    # Process the status update, e.g., update database records
    return {"message": "Status update received.", "status": "processed", "details": status_update.dict()}

@router.post("/data_injest", response_model=Dict[str, Any])
async def data_injest_webhook(data_ingest: DataIngest):
    """
    Webhook endpoint to receive data from n8n for direct injestion.

    This could be used if n8n performs some processing and then sends data back
    to the platform for storage.
    """
    logger.info(f"Webhook received: Data injestion with payload: {data_ingest.dict()}")
    # Here, you would typically process and store the incoming data
    return {"message": "Data injestion received.", "status": "processed", "details": data_ingest.dict()}

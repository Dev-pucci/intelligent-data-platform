"""
Scraper execution endpoints for n8n integration
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import subprocess
import os
from pathlib import Path
from typing import Optional
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ScraperRequest(BaseModel):
    config_name: str  # e.g., "jumia_spa", "amazon_products"

class ScraperResponse(BaseModel):
    status: str
    message: str
    config: str
    job_id: Optional[str] = None

@router.post("/run", response_model=ScraperResponse)
async def run_scraper(request: ScraperRequest, background_tasks: BackgroundTasks):
    """
    Execute a scraper with the specified config file.
    This endpoint is designed for n8n workflow integration.
    """
    # Validate config file exists
    config_path = Path(f"configs/sites/{request.config_name}.yml")
    if not config_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Configuration file not found: {request.config_name}.yml"
        )

    try:
        logger.info(f"Starting scraper for config: {request.config_name}")
        logger.info(f"Config path: {config_path}")

        # Run scraper synchronously (for n8n to wait for results)
        result = subprocess.run(
            ["python", "-m", "scrapers.scraper_runner", "--config", str(config_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        logger.info(f"Scraper return code: {result.returncode}")
        logger.info(f"Scraper stdout: {result.stdout}")
        logger.info(f"Scraper stderr: {result.stderr}")

        if result.returncode == 0:
            return ScraperResponse(
                status="success",
                message=f"Scraper executed successfully for {request.config_name}",
                config=request.config_name,
                job_id=None
            )
        else:
            logger.error(f"Scraper failed with stderr: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Scraper failed: {result.stderr}"
            )

    except subprocess.TimeoutExpired:
        logger.error(f"Scraper timeout for {request.config_name}")
        raise HTTPException(
            status_code=408,
            detail=f"Scraper timeout after 5 minutes for {request.config_name}"
        )
    except Exception as e:
        logger.error(f"Exception in scraper execution: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error executing scraper: {str(e)}"
        )

@router.get("/configs")
async def list_configs():
    """
    List all available scraper configurations.
    Useful for n8n dropdown selections.
    """
    configs_dir = Path("configs/sites")
    if not configs_dir.exists():
        return {"configs": []}

    configs = [
        f.stem for f in configs_dir.glob("*.yml")
    ]

    return {
        "configs": sorted(configs),
        "total": len(configs)
    }

@router.get("/health")
async def scraper_health():
    """
    Check if scraper service is healthy.
    """
    return {
        "status": "healthy",
        "service": "scraper-api",
        "python_available": True
    }

@router.post("/test", response_model=ScraperResponse)
async def test_scraper_endpoint(request: ScraperRequest):
    """
    Test endpoint - just validates config exists without running scraper
    """
    config_path = Path(f"configs/sites/{request.config_name}.yml")
    if not config_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Configuration file not found: {request.config_name}.yml"
        )

    return ScraperResponse(
        status="success",
        message=f"Config found for {request.config_name} (not executed - test mode)",
        config=request.config_name,
        job_id=None
    )

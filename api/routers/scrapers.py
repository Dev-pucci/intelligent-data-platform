"""
Scraper execution endpoints for n8n integration
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import subprocess
import os
from pathlib import Path
from typing import Optional

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
        # Run scraper synchronously (for n8n to wait for results)
        result = subprocess.run(
            ["python", "-m", "scrapers.scraper_runner", "--config", str(config_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            return ScraperResponse(
                status="success",
                message=f"Scraper executed successfully for {request.config_name}",
                config=request.config_name,
                job_id=None
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Scraper failed: {result.stderr}"
            )

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail=f"Scraper timeout after 5 minutes for {request.config_name}"
        )
    except Exception as e:
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

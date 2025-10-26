import uuid
from typing import List
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .routers import data, webhooks, scrapers
from .schemas import SiteConfig, SiteConfigCreate
from ..database.connection import get_db, Site
from .metrics import API_REQUESTS_TOTAL

openapi_tags = [
    {
        "name": "Data",
        "description": "Operations with scraped data.",
    },
    {
        "name": "Webhooks",
        "description": "Endpoints for n8n integration and external triggers.",
    },
    {
        "name": "Sites",
        "description": "Manage website configurations for scraping.",
    },
    {
        "name": "Scrapers",
        "description": "Execute and manage scraping jobs.",
    },
    {
        "name": "Monitoring",
        "description": "Health checks and system statistics.",
    },
]

app = FastAPI(
    title="Intelligent Data Acquisition Platform API",
    description="API for accessing scraped data and managing the platform.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

import os

# CORS Middleware
cors_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost,http://localhost:8080,http://localhost:3000")
origins = [origin.strip() for origin in cors_origins_str.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(data.router, tags=["Data"])
api_v1_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_v1_router.include_router(scrapers.router, prefix="/scrapers", tags=["Scrapers"])

# --- Site Management Endpoints ---
@api_v1_router.post("/sites", response_model=SiteConfig, status_code=status.HTTP_201_CREATED, tags=["Sites"])
async def create_site(site: SiteConfigCreate, db: Session = Depends(get_db)):
    """Create a new site configuration."""
    db_site = Site(name=site.name, config_file_path=site.config_file_path, is_active=site.is_active)
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return SiteConfig.from_orm(db_site)

@api_v1_router.get("/sites", response_model=List[SiteConfig], tags=["Sites"])
async def list_sites(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """List all site configurations."""
    sites = db.query(Site).offset(skip).limit(limit).all()
    return [SiteConfig.from_orm(site) for site in sites]

@api_v1_router.get("/sites/{site_id}", response_model=SiteConfig, tags=["Sites"])
async def get_site(site_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a single site configuration by ID."""
    site = db.query(Site).filter(Site.site_id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return SiteConfig.from_orm(site)

@api_v1_router.put("/sites/{site_id}", response_model=SiteConfig, tags=["Sites"])
async def update_site(site_id: uuid.UUID, site: SiteConfigCreate, db: Session = Depends(get_db)):
    """Update an existing site configuration."""
    db_site = db.query(Site).filter(Site.site_id == site_id).first()
    if not db_site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    db_site.name = site.name
    db_site.config_file_path = site.config_file_path
    db_site.is_active = site.is_active
    db.commit()
    db.refresh(db_site)
    return SiteConfig.from_orm(db_site)

@api_v1_router.delete("/sites/{site_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Sites"])
async def delete_site(site_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a site configuration."""
    db_site = db.query(Site).filter(Site.site_id == site_id).first()
    if not db_site:
        raise HTTPException(status_code=404, detail="Site not found")
    db.delete(db_site)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@api_v1_router.get("/health")
async def health_check():
    """Returns a health check status."""
    API_REQUESTS_TOTAL.labels(endpoint='/api/v1/health', status_code='200').inc()
    return {"status": "ok"}

from fastapi.responses import Response # New import
from .metrics import get_metrics_response, SCRAPER_REQUESTS_TOTAL, API_REQUESTS_TOTAL # New import

# ... (existing imports) ...

@api_v1_router.get("/stats")
async def get_system_stats():
    """Returns system statistics (placeholder)."""
    return {
        "total_sites_configured": 100,
        "sites_scraped_today": 15,
        "total_records": 10234,
        "crawler_status": "idle",
    }

@api_v1_router.post("/trigger/{site_name}") # Changed from {site} to {site_name} for consistency
async def trigger_scraping(site_name: str):
    """Triggers a scraping task for a specific site (placeholder)."""
    # In a real implementation, this would add a job to a queue (e.g., Redis).
    SCRAPER_REQUESTS_TOTAL.labels(site=site_name, type='unknown', status='triggered').inc() # Increment metric
    API_REQUESTS_TOTAL.labels(endpoint='/api/v1/trigger/{site_name}', status_code='200').inc() # Increment API metric
    return {"message": f"Scraping task for site '{site_name}' has been triggered."}


# --- Prometheus Metrics Endpoint ---
@app.get("/metrics")
async def metrics():
    """Exposes Prometheus metrics."""
    return Response(content=get_metrics_response(), media_type="text/plain")


app.include_router(api_v1_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Intelligent Data Acquisition Platform API"}

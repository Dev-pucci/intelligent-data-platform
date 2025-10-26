from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid

# --- Data Models ---

class ScrapedDataItem(BaseModel):
    id: int
    source_url: str
    product_name: Optional[str] = None
    price: Optional[float] = None
    scraped_at: Optional[datetime] = None
    data_hash: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True # Enable ORM mode for Pydantic

# --- Request Models ---

class SiteConfigBase(BaseModel):
    name: str = Field(..., example="Example Site")
    config_file_path: str = Field(..., example="/path/to/config.yml")
    is_active: bool = True

class SiteConfigCreate(SiteConfigBase):
    pass

class SiteConfig(SiteConfigBase):
    site_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ScrapeTriggerRequest(BaseModel):
    site_name: str = Field(..., example="TechCrunch Blog")
    url: Optional[str] = Field(None, example="https://techcrunch.com/category/artificial-intelligence/")
    # Additional parameters for the scraping job can be added here
    job_parameters: Optional[Dict[str, Any]] = None

class StatusUpdate(BaseModel):
    job_id: uuid.UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    status: str = Field(..., example="completed", pattern="^(started|completed|failed)$")
    message: Optional[str] = None
    items_processed: Optional[int] = None
    error_details: Optional[Dict[str, Any]] = None

class DataIngest(BaseModel):
    site_id: uuid.UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    job_id: uuid.UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    data: List[Dict[str, Any]] = Field(..., example=[{"product_name": "Test", "price": 10.0}])
    # Potentially add validation rules or a specific Pydantic model for items in 'data'

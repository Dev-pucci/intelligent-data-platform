from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel # Keep BaseModel for other potential local models if needed
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...database.connection import get_db, ScrapedData # Import get_db and ScrapedData model
from ..schemas import ScrapedDataItem # New import for ScrapedDataItem

router = APIRouter()
@router.get("/data", response_model=List[ScrapedDataItem])
async def list_scraped_data(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    product_name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    source_url_filter: Optional[str] = Query(None, alias="source_url"), # Renamed to avoid conflict with model field
    q: Optional[str] = None # Search query
):
    """
    Lists all scraped data records with filtering, searching, and pagination.
    """
    query = db.query(ScrapedData)

    if product_name:
        query = query.filter(ScrapedData.product_name.ilike(f"%{product_name}%"))
    if min_price:
        query = query.filter(ScrapedData.price >= min_price)
    if max_price:
        query = query.filter(ScrapedData.price <= max_price)
    if source_url_filter:
        query = query.filter(ScrapedData.source_url.ilike(f"%{source_url_filter}%"))
    if q:
        # Simple full-text search across relevant text fields
        query = query.filter(
            (ScrapedData.product_name.ilike(f"%{q}%")) |
            (ScrapedData.source_url.ilike(f"%{q}%"))
        )

    data_items = query.offset(skip).limit(limit).all()
    return [ScrapedDataItem.from_orm(item) for item in data_items]

@router.get("/data/{id}", response_model=ScrapedDataItem)
async def get_scraped_data_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single scraped data record by its ID.
    """
    item = db.query(ScrapedData).filter(ScrapedData.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ScrapedDataItem.from_orm(item)


import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func

# Database connection URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

# SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# SQLAlchemy Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# --- ORM Models ---

class Site(Base):
    __tablename__ = "sites"

    site_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    config_file_path = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    crawl_states = relationship("CrawlState", back_populates="site")
    scrape_jobs = relationship("ScrapeJob", back_populates="site")
    scraped_data = relationship("ScrapedData", back_populates="site")

    def __repr__(self):
        return f"<Site(name='{self.name}', site_id='{self.site_id}')>"

class CrawlState(Base):
    __tablename__ = "crawl_state"

    url = Column(Text, primary_key=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.site_id", ondelete="SET NULL"))
    status = Column(String(20), nullable=False) # pending, completed, failed, in_progress
    last_crawled = Column(DateTime(timezone=True))
    retry_count = Column(Integer, default=0)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())

    site = relationship("Site", back_populates="crawl_states")

    def __repr__(self):
        return f"<CrawlState(url='{self.url}', status='{self.status}')>"

class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.site_id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False) # started, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    items_scraped = Column(Integer, default=0)
    log_summary = Column(Text)

    site = relationship("Site", back_populates="scrape_jobs")
    scraped_data = relationship("ScrapedData", back_populates="job")

    def __repr__(self):
        return f"<ScrapeJob(job_id='{self.job_id}', status='{self.status}')>"

class ScrapedData(Base):
    __tablename__ = "scraped_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("scrape_jobs.job_id", ondelete="SET NULL"))
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.site_id", ondelete="SET NULL"))
    source_url = Column(Text, nullable=False)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    # Dynamic data fields (examples from schema.sql)
    product_name = Column(Text)
    price = Column(DECIMAL(10, 2))
    
    data_hash = Column(String(64), nullable=False)
    raw_data = Column(JSONB)

    job = relationship("ScrapeJob", back_populates="scraped_data")
    site = relationship("Site", back_populates="scraped_data")
    data_quality_issues = relationship("DataQualityIssue", back_populates="scraped_data")

    def __repr__(self):
        return f"<ScrapedData(id={self.id}, source_url='{self.source_url}')>"

class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    issue_id = Column(Integer, primary_key=True, autoincrement=True)
    scraped_data_id = Column(Integer, ForeignKey("scraped_data.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    issue_type = Column(String(100), nullable=False)
    details = Column(Text)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    scraped_data = relationship("ScrapedData", back_populates="data_quality_issues")

    def __repr__(self):
        return f"<DataQualityIssue(issue_id={self.issue_id}, issue_type='{self.issue_type}')>"

from sqlalchemy.dialects.postgresql import insert # New import
from sqlalchemy.orm import Session # New import

# ... (existing imports and models) ...

# Function to create all tables (for initial setup or migrations)
def create_all_tables():
    Base.metadata.create_all(engine)

def batch_insert_scraped_data(db: Session, data: List[Dict[str, Any]]):
    """
    Performs a batch insert of scraped data with conflict resolution.

    If a record with the same source_url already exists, it updates
    the existing record if the data_hash is different. Otherwise, it ignores.

    Args:
        db: The SQLAlchemy session.
        data: A list of dictionaries, where each dictionary represents a scraped item.
              Each dictionary should contain keys matching ScrapedData model attributes.
    """
    if not data:
        logger.info("No data provided for batch insert.")
        return

    # Filter out items that don't have a data_hash or source_url, as they are crucial for conflict resolution
    valid_data = [item for item in data if item.get('data_hash') and item.get('source_url')]
    if not valid_data:
        logger.warning("No valid data (missing data_hash or source_url) to insert.")
        return

    # Prepare data for insertion, ensuring all fields are present or defaulted
    insert_data = []
    for item in valid_data:
        item_to_insert = {
            "job_id": item.get("job_id"),
            "site_id": item.get("site_id"),
            "source_url": item["source_url"],
            "scraped_at": item.get("scraped_at", datetime.now()),
            "product_name": item.get("product_name"),
            "price": item.get("price"),
            "data_hash": item["data_hash"],
            "raw_data": item.get("raw_data"),
        }
        insert_data.append(item_to_insert)

    stmt = insert(ScrapedData).values(insert_data)

    # Define the ON CONFLICT clause
    on_conflict_stmt = stmt.on_conflict_do_update(
        index_elements=[ScrapedData.source_url], # Unique constraint on source_url
        set_=dict(
            product_name=stmt.excluded.product_name,
            price=stmt.excluded.price,
            scraped_at=stmt.excluded.scraped_at,
            data_hash=stmt.excluded.data_hash,
            raw_data=stmt.excluded.raw_data,
        ),
        where=ScrapedData.data_hash != stmt.excluded.data_hash # Only update if data_hash is different
    )

    try:
        db.execute(on_conflict_stmt)
        db.commit()
        logger.info(f"Successfully batch inserted/updated {len(insert_data)} scraped data items.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during batch insert of scraped data: {e}", exc_info=True)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

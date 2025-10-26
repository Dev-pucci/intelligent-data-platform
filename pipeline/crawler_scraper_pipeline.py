import logging
import yaml
from typing import Any, Dict, List
from urllib.parse import urlparse

from sqlalchemy.orm import Session # New import

from ..crawler.crawler_engine import CrawlerEngine
from ..scrapers.core.universal_scraper import UniversalScraper
from ..database.connection import batch_insert_scraped_data # New import
from .utils import generate_data_hash # New import

logger = logging.getLogger(__name__)

class CrawlerScraperPipeline:
    """
    Orchestrates the complete data acquisition pipeline:
    Crawler -> Scraper -> Parser -> Validator -> Storage.
    """

    def __init__(self, crawler_config: Dict[str, Any], scraper_configs: Dict[str, Any], db_session: Session):
        """
        Initializes the pipeline components.

        Args:
            crawler_config: Configuration for the CrawlerEngine.
            scraper_configs: A dictionary where keys are site names and values are
                             their respective scraper configurations.
            db_session: The SQLAlchemy database session.
        """
        self.crawler_config = crawler_config
        self.scraper_configs = scraper_configs
        self.db_session = db_session
        self.crawler = CrawlerEngine(seed_urls=crawler_config.get('seed_urls', []), config=crawler_config)
        self.universal_scraper = UniversalScraper()
        logger.info("CrawlerScraperPipeline initialized.")

    def run_pipeline(self):
        """
        Executes the full crawling, scraping, parsing, and storage pipeline.
        """
        logger.info("Starting the data acquisition pipeline.")
        for url in self.crawler.crawl():
            logger.info(f"Processing URL from crawler: {url}")
            
            # Find the appropriate scraper config based on the URL's domain or a pattern
            matched_config = None
            for site_name, site_config in self.scraper_configs.items():
                # Simple domain matching for now. Can be improved with more sophisticated rules.
                if urlparse(url).netloc == urlparse(site_config.get('seed_url', '')).netloc:
                    matched_config = site_config
                    break
            
            if not matched_config:
                logger.warning(f"No matching scraper config found for URL: {url}. Skipping.")
                continue

            try:
                scraped_data = self.universal_scraper.scrape_site(matched_config, url)
                if scraped_data:
                    logger.info(f"Scraped {len(scraped_data)} items from {url}.")
                    # Add data_hash and other metadata before storing
                    processed_data = []
                    for item in scraped_data:
                        item['data_hash'] = generate_data_hash(item)
                        item['source_url'] = url # Ensure source_url is in the item
                        # Add job_id and site_id if available from context
                        # item['job_id'] = current_job_id
                        # item['site_id'] = matched_config.get('site_id')
                        processed_data.append(item)
                    self._store_data(processed_data)
                else:
                    logger.info(f"No data scraped from {url}.")
            except Exception as e:
                logger.error(f"Error during scraping or parsing for {url}: {e}", exc_info=True)
        
        logger.info("Data acquisition pipeline finished.")

    def _store_data(self, data: List[Dict[str, Any]]):
        """
        Stores data into the database using batch insert with conflict resolution.
        """
        logger.info(f"Storing {len(data)} items to database.")
        batch_insert_scraped_data(self.db_session, data)

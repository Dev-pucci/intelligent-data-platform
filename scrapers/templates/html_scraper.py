import logging
import time
from typing import Any, Dict, List, Optional

import requests
# from bs4 import BeautifulSoup # No longer needed directly here

from scrapers.core.base_scraper import BaseScraper
from parsers.parser_manager import ParserManager # Import ParserManager

logger = logging.getLogger(__name__)

# Instantiate ParserManager once
parser_manager = ParserManager()


class HTMLScraper(BaseScraper):
    """
    Scraper for static HTML websites.

    This scraper fetches HTML content from a URL, delegates parsing
    to the ParserManager, and includes basic validation.
    """

    def __init__(self, config: Dict[str, Any], session: Optional[requests.Session] = None):
        """
        Initializes the HTMLScraper.

        Args:
            config: A dictionary containing scraper configuration.
            session: An optional requests.Session object for making HTTP requests.
        """
        super().__init__(config)
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def extract(self, url: str) -> str:
        """
        Extracts raw HTML content from a given URL.

        Args:
            url: The URL of the static HTML page to fetch.

        Returns:
            The raw HTML content as a string. Returns an empty string if fetching fails.
        """
        logger.info(f"[{self.name}] Extracting HTML from URL: {url}")
        response = self._fetch_page(url)
        if response:
            return response.text
        return ""

    def validate(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Performs basic validation on the extracted data.

        For now, this simply returns the data as is. More complex validation
        rules can be added here or delegated to a separate validator module.

        Args:
            data: A list of dictionaries, where each dictionary is a scraped item.

        Returns:
            The validated list of dictionaries.
        """
        logger.info(f"[{self.name}] Validating {len(data)} items.")
        # Example: filter out items that don't have a 'title'
        # return [item for item in data if item.get('title')]
        return data

    def run(self, url: str) -> List[Dict[str, Any]]:
        """
        Executes the complete scraping process for a given URL.

        Orchestrates extraction, parsing via ParserManager, and validation.

        Args:
            url: The URL of the static HTML page to scrape.

        Returns:
            A list of dictionaries, where each dictionary is a validated and
            processed scraped item. Returns an empty list if the process fails.
        """
        logger.info(f"[{self.name}] Running scrape process for URL: {url}")
        raw_content = self.extract(url)
        if not raw_content:
            return []

        try:
            parsed_data = parser_manager.parse(raw_content, self.config)
            validated_data = self.validate(parsed_data)
            return validated_data
        except Exception as e:
            logger.error(f"[{self.name}] Failed to parse or validate data from {url}: {e}")
            return []

    def _fetch_page(self, url: str, retries: int = 3, backoff_factor: float = 0.5) -> Optional[requests.Response]:
        """
        Fetches the HTML content of a page with retry logic.

        Args:
            url: The URL to fetch.
            retries: Number of retry attempts.
            backoff_factor: Factor for exponential backoff between retries.

        Returns:
            A requests.Response object if successful, otherwise None.
        """
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                logger.info(f"[{self.name}] Successfully fetched {url}")
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"[{self.name}] Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    sleep_time = backoff_factor * (2 ** attempt)
                    logger.info(f"[{self.name}] Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"[{self.name}] All {retries} retries failed for {url}.")
        return None

import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, Page, Browser, Playwright

from scrapers.core.base_scraper import BaseScraper
from parsers.parser_manager import ParserManager

logger = logging.getLogger(__name__)

# Instantiate ParserManager once
parser_manager = ParserManager()


class SPAScraper(BaseScraper):
    """
    Scraper for JavaScript-rendered websites (SPAs) using Playwright.

    This scraper uses Playwright to control a headless browser, allowing it to
    render JavaScript and interact with the page before extracting the HTML.
    It then delegates parsing to the ParserManager.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the SPAScraper.

        Args:
            config: A dictionary containing scraper configuration.
        """
        super().__init__(config)

    def extract(self, page: Page, url: str, parser_config: Dict[str, Any]) -> str:
        """
        Extracts raw HTML content from a given SPA URL using Playwright.

        Args:
            page: The Playwright page object.
            url: The URL of the JavaScript-rendered page to fetch.
            parser_config: The parser configuration for the page.

        Returns:
            The raw HTML content as a string. Returns an empty string if fetching fails.
        """
        logger.info(f"[{self.name}] Extracting HTML from URL: {url}")
        html_content = self._navigate_and_get_html(page, url, parser_config)
        return html_content if html_content else ""

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
            url: The URL of the JavaScript-rendered page to scrape.

        Returns:
            A list of dictionaries, where each dictionary is a validated and
            processed scraped item. Returns an empty list if the process fails.
        """
        logger.info(f"[{self.name}] Running scrape process for URL: {url}")
        all_items = []
        try:
            with sync_playwright() as p:
                browser = self._launch_browser(p)
                page = browser.new_page()
                
                # Scrape the first page
                raw_content = self.extract(page, url, self.config)
                if raw_content:
                    parsed_data = parser_manager.parse(raw_content, self.config)
                    all_items.extend(parsed_data)

                # Handle pagination
                all_items.extend(self._handle_pagination(page, url))

                # Handle detail page scraping
                if self.config.get('detail_parser'):
                    all_items = self._scrape_detail_pages(page, all_items)

                browser.close()
        except Exception as e:
            logger.error(f"[{self.name}] A critical error occurred during Playwright operation: {e}", exc_info=True)

        validated_data = self.validate(all_items)
        return validated_data

    def _scrape_detail_pages(self, page: Page, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scrapes detail pages for each item in the listing.

        This method is flexible and can handle any URL field name specified in the config.
        It supports rate limiting, error handling, and progress tracking.

        Args:
            page: The Playwright page object
            items: List of items from the listing page

        Returns:
            List of items with enriched detail page data
        """
        detail_parser_config = self.config.get('detail_parser')
        if not detail_parser_config:
            return items

        # Get the URL field name from config (defaults to common field names)
        url_field = detail_parser_config.get('url_field', self._detect_url_field(items))
        if not url_field:
            logger.warning(f"[{self.name}] Could not determine URL field for detail pages. Skipping detail scraping.")
            return items

        logger.info(f"[{self.name}] Starting detail page scraping for {len(items)} items using URL field: '{url_field}'")

        # Get rate limiting config
        detail_rate_limit = detail_parser_config.get('rate_limit', {})
        delay_between_requests = detail_rate_limit.get('delay', 2)
        max_detail_pages = detail_parser_config.get('max_pages', len(items))

        updated_items = []
        success_count = 0
        error_count = 0

        for idx, item in enumerate(items[:max_detail_pages], 1):
            detail_url = item.get(url_field)

            if not detail_url:
                logger.debug(f"[{self.name}] Item {idx}/{len(items)} has no URL in field '{url_field}', skipping")
                updated_items.append(item)
                continue

            # Ensure absolute URL
            if not detail_url.startswith('http'):
                base_url = detail_parser_config.get('base_url', '')
                if base_url:
                    detail_url = urljoin(base_url, detail_url)
                else:
                    logger.warning(f"[{self.name}] Relative URL found but no base_url configured: {detail_url}")
                    updated_items.append(item)
                    continue

            try:
                logger.info(f"[{self.name}] Scraping detail page {idx}/{min(max_detail_pages, len(items))}: {detail_url}")

                # Scrape detail page with error handling
                detail_data = self._scrape_detail_page(page, detail_url, detail_parser_config)

                if detail_data:
                    # Merge detail data with item data
                    # Use prefix for detail fields if configured to avoid conflicts
                    prefix = detail_parser_config.get('field_prefix', '')
                    if prefix:
                        detail_data = {f"{prefix}{k}": v for k, v in detail_data.items()}

                    item.update(detail_data)
                    success_count += 1
                    logger.debug(f"[{self.name}] Successfully scraped {len(detail_data)} fields from detail page")
                else:
                    logger.warning(f"[{self.name}] No data extracted from detail page: {detail_url}")
                    error_count += 1

                updated_items.append(item)

                # Rate limiting between detail page requests
                if idx < min(max_detail_pages, len(items)):
                    time.sleep(delay_between_requests)

            except Exception as e:
                logger.error(f"[{self.name}] Error scraping detail page {detail_url}: {e}", exc_info=True)
                error_count += 1
                updated_items.append(item)  # Keep original item even if detail scraping fails

        logger.info(f"[{self.name}] Detail page scraping completed: {success_count} successful, {error_count} errors")
        return updated_items

    def _detect_url_field(self, items: List[Dict[str, Any]]) -> Optional[str]:
        """
        Automatically detect the URL field name from items.

        Tries common field names for URLs in order of priority.

        Args:
            items: List of items to analyze

        Returns:
            The detected URL field name, or None if not found
        """
        if not items:
            return None

        # Common URL field names in priority order
        common_url_fields = [
            'url', 'listing_url', 'product_url', 'video_url', 'article_url',
            'link', 'href', 'detail_url', 'page_url', 'item_url'
        ]

        # Check each common field name
        sample_item = items[0]
        for field_name in common_url_fields:
            if field_name in sample_item:
                value = sample_item[field_name]
                # Verify it looks like a URL
                if value and (isinstance(value, str) and ('http' in value or '/' in value)):
                    logger.info(f"[{self.name}] Auto-detected URL field: '{field_name}'")
                    return field_name

        # If not found in common names, look for any field containing 'url' or 'link'
        for key in sample_item.keys():
            if 'url' in key.lower() or 'link' in key.lower():
                logger.info(f"[{self.name}] Auto-detected URL field: '{key}'")
                return key

        return None

    def _scrape_detail_page(self, page: Page, url: str, detail_parser_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scrapes a single detail page and returns extracted data.

        This method handles:
        - Navigation to detail page
        - Waiting for dynamic content
        - Content extraction
        - Error handling

        Args:
            page: The Playwright page object
            url: The detail page URL to scrape
            detail_parser_config: Configuration for the detail parser

        Returns:
            Dictionary of extracted data from the detail page, or empty dict on failure
        """
        try:
            raw_content = self.extract(page, url, detail_parser_config)
            if not raw_content:
                logger.warning(f"[{self.name}] No HTML content extracted from detail page: {url}")
                return {}

            # Parse the content using the detail parser configuration
            parsed_data = parser_manager.parse(raw_content, detail_parser_config)

            if not parsed_data:
                logger.warning(f"[{self.name}] Parser returned no data from detail page: {url}")
                return {}

            # Return first item if multiple items parsed (detail pages usually have one main item)
            result = parsed_data[0] if isinstance(parsed_data, list) and parsed_data else parsed_data

            return result if isinstance(result, dict) else {}

        except Exception as e:
            logger.error(f"[{self.name}] Error parsing detail page {url}: {e}", exc_info=True)
            return {}

    def _handle_pagination(self, page: Page, initial_url: str) -> List[Dict[str, Any]]:
        """Handles pagination based on the configuration."""
        pagination_config = self.config.get('pagination')
        if not pagination_config:
            return []

        pagination_type = pagination_config.get('type')
        if not pagination_type:
            logger.warning(f"[{self.name}] Pagination is configured but 'type' is missing.")
            return []

        paginated_items = []
        if pagination_type == 'click':
            paginated_items.extend(self._handle_click_pagination(page))
        elif pagination_type == 'scroll':
            paginated_items.extend(self._handle_scroll_pagination(page))
        elif pagination_type == 'url_pattern':
            paginated_items.extend(self._handle_url_pattern_pagination(page, initial_url))
        else:
            logger.warning(f"[{self.name}] Unknown pagination type: {pagination_type}")

        return paginated_items

    def _handle_click_pagination(self, page: Page) -> List[Dict[str, Any]]:
        """Handles click-based pagination."""
        pagination_config = self.config.get('pagination', {})
        next_button_selector = pagination_config.get('next_button_selector')
        if not next_button_selector:
            logger.warning(f"[{self.name}] Pagination type is 'click' but 'next_button_selector' is missing.")
            return []

        max_pages = pagination_config.get('max_pages', 5)
        delay = pagination_config.get('delay', 2)
        paginated_items = []

        for page_num in range(1, max_pages):
            try:
                logger.info(f"[{self.name}] Checking for next page (Page {page_num + 1}/{max_pages})")
                next_button = page.query_selector(next_button_selector)
                if not next_button or not next_button.is_enabled():
                    logger.info(f"[{self.name}] No more pages to scrape.")
                    break

                logger.info(f"[{self.name}] Clicking next page button.")
                next_button.click()
                page.wait_for_timeout(delay * 1000)

                raw_content = page.content()
                if raw_content:
                    parsed_data = parser_manager.parse(raw_content, self.config)
                    paginated_items.extend(parsed_data)

            except Exception as e:
                logger.error(f"[{self.name}] Error during click pagination: {e}", exc_info=True)
                break

        return paginated_items

    def _handle_scroll_pagination(self, page: Page) -> List[Dict[str, Any]]:
        """Handles scroll-based pagination (infinite scroll)."""
        pagination_config = self.config.get('pagination', {})
        max_scrolls = pagination_config.get('max_pages', 5) # Re-using max_pages as max_scrolls
        delay = pagination_config.get('delay', 2)
        paginated_items = []

        for i in range(max_scrolls):
            logger.info(f"[{self.name}] Scrolling to load more content (Scroll {i + 1}/{max_scrolls})")
            self._scroll_page(page)
            page.wait_for_timeout(delay * 1000)
            raw_content = page.content()
            if raw_content:
                # We are re-parsing the whole page content, which might be inefficient.
                # A more advanced implementation could parse only the new content.
                parsed_data = parser_manager.parse(raw_content, self.config)
                paginated_items.extend(parsed_data)
        
        return paginated_items

    def _handle_url_pattern_pagination(self, page: Page, initial_url: str) -> List[Dict[str, Any]]:
        """Handles URL pattern-based pagination."""
        pagination_config = self.config.get('pagination', {})
        url_pattern = pagination_config.get('url_pattern')
        if not url_pattern:
            logger.warning(f"[{self.name}] Pagination type is 'url_pattern' but 'url_pattern' is missing.")
            return []

        max_pages = pagination_config.get('max_pages', 5)
        paginated_items = []

        for page_num in range(2, max_pages + 1): # Start from page 2
            next_url = url_pattern.format(page_num=page_num)
            logger.info(f"[{self.name}] Scraping next page from URL pattern: {next_url}")
            raw_content = self.extract(page, next_url, self.config)
            if not raw_content:
                logger.warning(f"[{self.name}] No content found for URL: {next_url}")
                break
            
            parsed_data = parser_manager.parse(raw_content, self.config)
            paginated_items.extend(parsed_data)

        return paginated_items

    def _launch_browser(self, p: Playwright) -> Browser:
        """Launches a Playwright browser instance."""
        logger.info(f"[{self.name}] Launching headless browser.")
        return p.chromium.launch(headless=True)

    def _navigate_and_get_html(self, page: Page, url: str, parser_config: Dict[str, Any], retries: int = 3, backoff_factor: float = 0.5) -> str:
        """
        Navigates to the URL and returns the page's HTML content with retry logic.
        """
        for attempt in range(retries):
            try:
                logger.info(f"[{self.name}] Navigating to {url} (Attempt {attempt + 1}/{retries})")
                page.goto(url, wait_until='domcontentloaded', timeout=60000)

                wait_selector = parser_config.get('wait_for')
                if wait_selector:
                    logger.info(f"[{self.name}] Waiting for selector: '{wait_selector}'")
                    page.wait_for_selector(wait_selector, timeout=30000)

                if parser_config.get('scroll', False) and not parser_config.get('pagination', {}).get('type') == 'scroll':
                    logger.info(f"[{self.name}] Scrolling page to load dynamic content.")
                    self._scroll_page(page)

                logger.info(f"[{self.name}] Retrieving HTML content.")
                return page.content()
            except Exception as e:
                logger.warning(f"[{self.name}] Navigation or content retrieval failed for {url}: {e}")
                if attempt < retries - 1:
                    import time
                    sleep_time = backoff_factor * (2 ** attempt)
                    logger.info(f"[{self.name}] Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"[{self.name}] All {retries} retry attempts failed for {url}.")
        return ""

    def _scroll_page(self, page: Page):
        """Scrolls the page to the bottom to trigger lazy-loading."""
        logger.info(f"[{self.name}] Scrolling to bottom of the page.")
        last_height = page.evaluate("document.body.scrollHeight")
        for _ in range(5): # Limit scrolls to prevent infinite loops
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        logger.info(f"[{self.name}] Finished scrolling.")

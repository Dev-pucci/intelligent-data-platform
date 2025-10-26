import logging
import yaml
from typing import Any, Dict, List, Type

from scrapers.templates.html_scraper import HTMLScraper
from scrapers.templates.spa_scraper import SPAScraper
from scrapers.core.base_scraper import BaseScraper # For type hinting

logger = logging.getLogger(__name__)

class UniversalScraper:
    """
    A universal scraper engine that routes scraping tasks to the correct
    scraper template based on the site's configuration type.
    """

    def __init__(self):
        """
        Initializes the UniversalScraper and registers available scraper templates.
        """
        self._scraper_registry: Dict[str, Type[BaseScraper]] = {}
        self.register_scraper('html', HTMLScraper)
        self.register_scraper('spa', SPAScraper)
        # Register other scrapers as they are implemented
        # self.register_scraper('api', APIScraper)
        # self.register_scraper('pdf', PDFScraper)
        # self.register_scraper('excel', ExcelScraper)

    def register_scraper(self, scraper_type: str, scraper_class: Type[BaseScraper]):
        """
        Registers a scraper class for a given type string.

        Args:
            scraper_type: The string identifier for the scraper (e.g., 'html', 'spa').
            scraper_class: The class implementation of the scraper.
        """
        if not issubclass(scraper_class, BaseScraper):
            raise TypeError("scraper_class must be a subclass of BaseScraper")
        logger.info(f"Registering scraper type '{scraper_type}'.")
        self._scraper_registry[scraper_type] = scraper_class

    def scrape_site(self, config: Dict[str, Any], url: str) -> List[Dict[str, Any]]:
        """
        Scrapes a site based on its configuration and a target URL.

        Args:
            config: The loaded site configuration dictionary.
            url: The specific URL to scrape.

        Returns:
            A list of dictionaries containing the extracted and validated data.
        """
        scraper_type = config.get('type')
        if not scraper_type:
            raise ValueError("Site configuration must specify a 'type'.")

        ScraperClass = self._scraper_registry.get(scraper_type)
        if not ScraperClass:
            raise ValueError(f"No scraper registered for type: {scraper_type}")

        logger.info(f"Instantiating {scraper_type} scraper for URL: {url}")
        scraper_instance = ScraperClass(config)
        
        try:
            return scraper_instance.run(url)
        except Exception as e:
            logger.error(f"Error running {scraper_type} scraper for {url}: {e}", exc_info=True)
            return []

    def load_config_and_scrape(self, config_path: str, url: str) -> List[Dict[str, Any]]:
        """
        Loads a site configuration from a YAML file and then scrapes the site.

        Args:
            config_path: The path to the YAML configuration file.
            url: The specific URL to scrape.

        Returns:
            A list of dictionaries containing the extracted and validated data.
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            return []
        except yaml.YAMLError as e:
            logger.error(f"Error loading YAML config from {config_path}: {e}")
            return []
        
        return self.scrape_site(config, url)

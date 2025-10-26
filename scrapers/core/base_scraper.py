import abc
from typing import Any, Dict, List

class BaseScraper(abc.ABC):
    """
    Abstract base class for all scrapers.

    Defines the common interface that all scraper templates must implement.
    This ensures that the universal scraper engine can interact with any
    scraper template in a consistent way.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the scraper with its site-specific configuration.

        Args:
            config: A dictionary containing configuration details for a
                    specific site, such as URL patterns, parser settings, etc.
        """
        self.config = config
        self.name = config.get("name", "UnknownScraper")

    @abc.abstractmethod
    def extract(self, url: str) -> str:
        """
        Abstract method to extract raw content from a given URL.

        This method is responsible for fetching the raw content (e.g., HTML, JSON,
        PDF text) from the target URL.

        Args:
            url: The target URL to extract content from.

        Returns:
            The raw content as a string. Returns an empty string if extraction fails.
        """
        pass

    @abc.abstractmethod
    def validate(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Abstract method to validate extracted data.

        This method applies validation rules to the extracted data.

        Args:
            data: A list of dictionaries, where each dictionary represents an extracted item.

        Returns:
            A list of dictionaries with validated data. Invalid items might be
            filtered out or marked.
        """
        pass

    @abc.abstractmethod
    def run(self, url: str) -> List[Dict[str, Any]]:
        """
        Abstract method to run the complete scraping process for a given URL.

        This method orchestrates the extraction, parsing, and validation steps.

        Args:
            url: The target URL to scrape.

        Returns:
            A list of dictionaries, where each dictionary represents a validated
            and processed scraped item. Returns an empty list if the process fails.
        """
        pass

    def __repr__(self) -> str:
        """
        Returns a string representation of the scraper instance.
        """
        return f"<{self.__class__.__name__} for '{self.name}'>"

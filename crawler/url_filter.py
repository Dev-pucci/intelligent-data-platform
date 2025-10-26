import re
from typing import List, Set, Dict, Any
from urllib.parse import urlparse

class URLFilter:
    """
    Manages URL filtering based on include/exclude patterns and deduplication.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the URLFilter with configuration.

        Args:
            config: A dictionary with crawler configuration, specifically:
                - url_patterns: List of regex patterns to include.
                - exclude_patterns: List of regex patterns to exclude.
        """
        self.include_patterns = [re.compile(p) for p in config.get('url_patterns', [])]
        self.exclude_patterns = [re.compile(p) for p in config.get('exclude_patterns', [])]
        self.visited_urls: Set[str] = set()

    def is_valid_and_new(self, url: str) -> bool:
        """
        Checks if a URL is valid according to patterns and has not been visited yet.

        Args:
            url: The URL to check.

        Returns:
            True if the URL is valid and new, False otherwise.
        """
        # Must be http or https
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Check against exclusion patterns
        if any(pattern.search(url) for pattern in self.exclude_patterns):
            return False
            
        # If include patterns are defined, the URL must match at least one
        if self.include_patterns:
            if not any(pattern.search(url) for pattern in self.include_patterns):
                return False
        
        # Check for deduplication
        if url in self.visited_urls:
            return False
        
        return True

    def mark_as_visited(self, url: str):
        """Marks a URL as visited."""
        self.visited_urls.add(url)

    def get_visited_count(self) -> int:
        """Returns the number of unique URLs visited."""
        return len(self.visited_urls)

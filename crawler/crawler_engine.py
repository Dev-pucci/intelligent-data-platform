import logging
import time
import re
from collections import deque
from typing import List, Set, Deque, Dict, Any, Iterator
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from crawler.url_filter import URLFilter # Import URLFilter

logger = logging.getLogger(__name__)

class CrawlerEngine:
    """
    A web crawler engine that discovers URLs based on different strategies.

    The engine starts with a set of seed URLs and systematically browses
    websites to find new URLs. It supports breadth-first and depth-first
    crawling strategies, respects robots.txt, and filters URLs based on
    configurable patterns.
    """

    def __init__(self, seed_urls: List[str], config: Dict[str, Any]):
        """
        Initializes the CrawlerEngine.

        Args:
            seed_urls: A list of starting URLs for the crawl.
            config: A dictionary with crawler configuration:
                - strategy: 'bfs' (breadth-first) or 'dfs' (depth-first).
                - url_patterns: List of regex patterns to include.
                - exclude_patterns: List of regex patterns to exclude.
                - rate_limit: Seconds to wait between requests to the same domain.
                - max_depth: Maximum depth to crawl from the seed URLs.
                - user_agent: The User-Agent string to use for requests.
        """
        self.config = config
        self.strategy = config.get('strategy', 'bfs')
        self.rate_limit = config.get('rate_limit', 1.0)
        self.max_depth = config.get('max_depth', 5)
        self.user_agent = config.get('user_agent', 'GeminiCrawler/1.0')

        # The frontier stores tuples of (url, depth)
        if self.strategy == 'bfs':
            self.frontier: Deque[(str, int)] = deque((url, 0) for url in seed_urls)
        elif self.strategy == 'dfs':
            self.frontier: List[(str, int)] = [(url, 0) for url in seed_urls]
        else:
            raise ValueError(f"Unsupported crawling strategy: {self.strategy}")

        self.url_filter = URLFilter(config) # Instantiate URLFilter
        # self.visited_urls: Set[str] = set() # Moved to URLFilter
        self.robot_parsers: Dict[str, RobotFileParser] = {}
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        self.domain_last_crawled: Dict[str, float] = {}

    def crawl(self) -> Iterator[str]:
        """
        Starts the crawling process and yields discovered URLs.

        Returns:
            An iterator that yields valid, discovered URLs.
        """
        while self.frontier:
            if self.strategy == 'bfs':
                current_url, depth = self.frontier.popleft()
            else: # dfs
                current_url, depth = self.frontier.pop()

            # Use URLFilter for deduplication
            if not self.url_filter.is_valid_and_new(current_url):
                continue

            if depth > self.max_depth:
                logger.info(f"Skipping {current_url}, max depth {self.max_depth} exceeded.")
                continue

            domain = urlparse(current_url).netloc
            if not self._can_fetch(domain, current_url):
                logger.info(f"Skipping {current_url} due to robots.txt restrictions.")
                continue

            # Apply rate limiting
            last_crawled_time = self.domain_last_crawled.get(domain, 0)
            elapsed_time = time.time() - last_crawled_time
            if elapsed_time < self.rate_limit:
                sleep_time = self.rate_limit - elapsed_time
                logger.info(f"Rate limiting {domain}. Sleeping for {sleep_time:.2f}s.")
                time.sleep(sleep_time)

            self.domain_last_crawled[domain] = time.time()
            self.url_filter.mark_as_visited(current_url) # Mark as visited
            logger.info(f"Crawling [Depth: {depth}]: {current_url}")

            yield current_url

            try:
                response = self.session.get(current_url, timeout=15)
                response.raise_for_status()
                
                new_links = self._extract_links(response.text, current_url)
                for link in new_links:
                    # Check validity and newness using URLFilter
                    if self.url_filter.is_valid_and_new(link):
                        self.frontier.append((link, depth + 1))

            except requests.RequestException as e:
                logger.error(f"Failed to fetch {current_url}: {e}")

    def _get_robot_parser(self, domain: str) -> RobotFileParser:
        """
        Retrieves, caches, and returns a RobotFileParser for a given domain.
        """
        if domain not in self.robot_parsers:
            robots_url = urljoin(f"https://{domain}", "robots.txt")
            parser = RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
                logger.info(f"Successfully read robots.txt for {domain}")
            except Exception as e:
                logger.warning(f"Could not read robots.txt for {domain}: {e}")
            self.robot_parsers[domain] = parser
        return self.robot_parsers[domain]

    def _can_fetch(self, domain: str, url: str) -> bool:
        """
        Checks if the crawler is allowed to fetch a URL by robots.txt.
        """
        parser = self._get_robot_parser(domain)
        return parser.can_fetch(self.user_agent, url)

    def _extract_links(self, html_content: str, base_url: str) -> Set[str]:
        """
        Parses HTML to extract and filter links.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links: Set[str] = set()
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            absolute_link = urljoin(base_url, link)
            absolute_link = urlparse(absolute_link)._replace(fragment="").geturl()

            # No longer need to call _is_valid_link here, URLFilter handles it
            links.add(absolute_link)
        return links

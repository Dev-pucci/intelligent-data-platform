from prometheus_client import Counter, Histogram, generate_latest

# --- Scraper Metrics ---

# Counter for total scrape requests, labeled by site, type (html, spa, etc.), and status (success, failed)
SCRAPER_REQUESTS_TOTAL = Counter(
    'scraper_requests_total',
    'Total number of scrape requests',
    ['site', 'type', 'status']
)

# Histogram for scrape duration, labeled by site and type
SCRAPER_DURATION_SECONDS = Histogram(
    'scraper_duration_seconds',
    'Histogram of scrape duration in seconds',
    ['site', 'type']
)

# Counter for total items scraped, labeled by site and type
SCRAPER_ITEMS_SCRAPED_TOTAL = Counter(
    'scraper_items_scraped_total',
    'Total number of items scraped',
    ['site', 'type']
)

# --- Crawler Metrics ---

# Counter for total URLs discovered, labeled by site
CRAWLER_URLS_DISCOVERED_TOTAL = Counter(
    'crawler_urls_discovered_total',
    'Total number of URLs discovered by the crawler',
    ['site']
)

# Counter for total URLs visited, labeled by site
CRAWLER_URLS_VISITED_TOTAL = Counter(
    'crawler_urls_visited_total',
    'Total number of URLs visited by the crawler',
    ['site']
)

# --- API Metrics (example) ---

# Counter for total API requests, labeled by endpoint and status code
API_REQUESTS_TOTAL = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['endpoint', 'status_code']
)

# Histogram for API request duration
API_REQUEST_DURATION_SECONDS = Histogram(
    'api_request_duration_seconds',
    'Histogram of API request duration in seconds',
    ['endpoint']
)

# --- Functions to expose metrics ---

def get_metrics_response() -> bytes:
    """
    Generates the latest Prometheus metrics in a byte string format.
    """
    return generate_latest()

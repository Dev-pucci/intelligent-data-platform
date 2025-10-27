"""
Scraper runner module - executes scraping jobs based on config files
"""
import argparse
import yaml
from pathlib import Path
import sys

from scrapers.core.universal_scraper import UniversalScraper


def run_scraper(config_path: str):
    """
    Run a scraper based on the provided config file path.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        list: Results of the scraping operation
    """
    # Validate config file exists
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Load config to get URL
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Support both 'start_url' and 'seed_url'
    url = config.get('start_url') or config.get('seed_url')
    if not url:
        raise ValueError(f"Config file must contain 'start_url' or 'seed_url': {config_path}")

    # Initialize scraper (no arguments needed)
    scraper = UniversalScraper()

    # Run scraper with config path and URL
    print(f"Starting scraper for: {config.get('name', 'Unknown')}")
    print(f"Target URL: {url}")

    results = scraper.load_config_and_scrape(str(config_file), url)

    print(f"Scraping completed. Found {len(results)} items.")
    return results


def main():
    """
    CLI entry point for running scrapers
    """
    parser = argparse.ArgumentParser(description='Run a web scraper')
    parser.add_argument('--config', required=True, help='Path to config YAML file')

    args = parser.parse_args()

    try:
        results = run_scraper(args.config)
        print(f"Success! Scraped {len(results)} items.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

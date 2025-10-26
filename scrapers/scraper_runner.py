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
        dict: Results of the scraping operation
    """
    # Load config
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Initialize scraper
    scraper = UniversalScraper(config)

    # Run scraper
    print(f"Starting scraper for: {config.get('name', 'Unknown')}")
    results = scraper.scrape()

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

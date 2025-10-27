"""
Scraper runner module - executes scraping jobs based on config files
"""
import argparse
import yaml
from pathlib import Path
import sys
import json
import hashlib
from datetime import datetime

from scrapers.core.universal_scraper import UniversalScraper
from database.connection import get_db_session, ScrapedData


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

    # Save results to database
    if results:
        save_to_database(results, url, config.get('name', 'Unknown'))

    return results


def save_to_database(results: list, source_url: str, site_name: str):
    """
    Save scraped results to the database.

    Args:
        results: List of scraped data dictionaries
        source_url: The URL that was scraped
        site_name: Name of the site
    """
    db = next(get_db_session())
    saved_count = 0

    try:
        for item in results:
            # Create hash of the data for deduplication
            data_str = json.dumps(item, sort_keys=True)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()

            # Check if item already exists
            existing = db.query(ScrapedData).filter_by(data_hash=data_hash).first()
            if existing:
                continue  # Skip duplicates

            # Create new record
            scraped_item = ScrapedData(
                source_url=item.get('product_url', source_url),
                product_name=item.get('product_name'),
                price=item.get('price'),
                data_hash=data_hash,
                raw_data=item
                # scraped_at is auto-set by database default
            )

            db.add(scraped_item)
            saved_count += 1

        db.commit()
        print(f"Saved {saved_count} new items to database (skipped {len(results) - saved_count} duplicates)")

    except Exception as e:
        db.rollback()
        print(f"Error saving to database: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


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

import os
import yaml
import requests
import logging
from typing import Dict, Any, List, Optional

# Assuming the project structure allows direct import or it's run from project root
from intelligent_data_platform.parsers.ai_parser import AIParser
from intelligent_data_platform.scrapers.templates.html_scraper import HTMLScraper # For fetching HTML
from intelligent_data_platform.scrapers.templates.spa_scraper import SPAScraper # For fetching SPA HTML
from intelligent_data_platform.configs.config_validator import ConfigValidator # To validate generated config

logger = logging.getLogger(__name__)

# Initialize AIParser (assuming Ollama is running)
ai_parser = AIParser()
config_validator = ConfigValidator()

def generate_config_from_url(url: str, output_dir: str = os.getenv("CONFIG_OUTPUT_DIR", "configs/sites"), site_name: Optional[str] = None) -> Optional[str]:
    """
    Generates a YAML configuration file for a given URL using AI to suggest parsing rules.

    Args:
        url: The URL of the website to generate a config for.
        output_dir: The directory to save the generated YAML file.
        site_name: Optional. A name for the site. If not provided, derived from the URL.

    Returns:
        The path to the generated config file, or None if generation fails.
    """
    logger.info(f"Attempting to generate config for URL: {url}")

    # 1. Fetch raw content (simplified - could use UniversalScraper later)
    # Determine if it's likely HTML or SPA based on URL or initial response
    # For now, let's try HTMLScraper first, then suggest SPA if needed.
    
    # Dummy config for scraper to fetch content
    scraper_config = {
        "name": site_name or url.split('//')[-1].split('/')[0].replace('.', '_'),
        "type": "html", # Assume html for initial fetch
        "seed_url": url
    }
    
    # Use HTMLScraper to get initial content
    html_scraper = HTMLScraper(scraper_config)
    raw_content = html_scraper.extract(url)

    if not raw_content:
        logger.warning(f"Could not fetch content from {url} using HTMLScraper. Trying SPAScraper.")
        # Try SPAScraper if HTMLScraper fails
        spa_scraper = SPAScraper(scraper_config) # Type is still html, but it uses Playwright
        raw_content = spa_scraper.extract(url)
        if not raw_content:
            logger.error(f"Could not fetch content from {url} using either HTMLScraper or SPAScraper.")
            return None
        scraper_config["type"] = "spa" # Update type if SPA scraper was used

    # 2. Use AI to suggest parsing rules
    logger.info("Using AI to suggest parsing rules...")
    ai_config = {
        "model": os.getenv("AI_PARSER_MODEL", "gemini-pro"), # Load from env var
        "prompt_template": os.getenv("AI_PARSER_PROMPT_TEMPLATE", "Analyze the following HTML content from a webpage. Identify common data items like product names, prices, article titles, descriptions, URLs, etc. Suggest a 'parser_config' (CSS selectors) for extracting these fields. Provide the output as a JSON object with 'container' and 'fields' keys. HTML: {text}"), # Load from env var
        "fields": ["container", "fields"] # Instruct AI to return these keys
    }
    
    # Pass a snippet of HTML to avoid exceeding LLM context window
    html_snippet = raw_content[:4000] # Limit to first 4000 characters
    
    suggested_parser_config_list = ai_parser.parse(html_snippet, ai_config)
    
    if not suggested_parser_config_list:
        logger.error("AI failed to suggest parser configuration.")
        return None
    
    suggested_parser_config = suggested_parser_config_list[0] # Take the first suggestion

    # 3. Construct the YAML config
    generated_config = {
        "name": site_name or url.split('//')[-1].split('/')[0].replace('.', '_'),
        "type": scraper_config["type"],
        "seed_url": url,
        "crawler_settings": {
            "url_patterns": [],
            "exclude_patterns": [],
            "max_depth": 2
        },
        "scraper_settings": {
            "wait_for": suggested_parser_config.get("container", ""), # Use AI suggested container
            "scroll": False
        },
        "parser_type": "css", # Default to CSS based on AI prompt
        "parser_config": suggested_parser_config,
        "transformations": {},
        "validation_rules": {}
    }

    # 4. Validate the generated config
    is_valid, errors = config_validator.validate_config(generated_config)
    if not is_valid:
        logger.error(f"Generated config is invalid: {errors}")
        return None

    # 5. Save the YAML file
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_name = f"{generated_config['name'].lower().replace(' ', '_')}.yml"
    output_path = os.path.join(output_dir, file_name)

    try:
        with open(output_path, 'w') as f:
            yaml.dump(generated_config, f, sort_keys=False, indent=2)
        logger.info(f"Successfully generated config: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to write config file {output_path}: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    test_url = "https://www.amazon.com/s?k=laptop" # Example e-commerce site
    # test_url = "https://techcrunch.com/category/artificial-intelligence/" # Example news site
    
    # Ensure GEMINI_API_KEY is set in your environment
    # export GEMINI_API_KEY="YOUR_API_KEY"
    
    generated_file = generate_config_from_url(test_url)
    if generated_file:
        print(f"Config generated at: {generated_file}")
    else:
        print("Config generation failed.")

import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)

class CSSParser(BaseParser):
    """
    A parser that extracts data from HTML content using CSS selectors.
    """

    def parse(self, content: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parses HTML content using CSS selectors defined in the configuration.

        Args:
            content: The raw HTML content as a string.
            config: Configuration for the CSS parser, must include:
                - 'container': A CSS selector to select the main item containers.
                - 'fields': A dictionary where keys are field names and values are
                            CSS selectors relative to the container to extract data.

        Returns:
            A list of dictionaries, where each dictionary represents an extracted item.
            Returns an empty list if parsing fails or no items are found.
        """
        try:
            soup = BeautifulSoup(content, 'html.parser')
        except Exception as e:
            logger.error(f"Failed to parse HTML content with BeautifulSoup: {e}")
            return []

        parser_config = config.get('parser_config', {}) # Get the parser_config sub-dictionary
        container_selector = parser_config.get('container')
        if not container_selector:
            logger.error("CSSParser config must include a 'container' selector within 'parser_config'.")
            return []

        item_elements = soup.select(container_selector)
        if not item_elements:
            logger.warning(f"No elements found with container selector: '{container_selector}'")
            return []

        logger.info(f"Found {len(item_elements)} items with container selector.")

        fields = parser_config.get('fields', {}) # Get fields from parser_config
        if not fields:
            logger.error("CSSParser config must include a 'fields' dictionary within 'parser_config'.")
            return []

        results = []
        for item_element in item_elements:
            item_data = {}
            for field_name, selector_info in fields.items():
                try:
                    parts = selector_info.split('::', 1)
                    selector = parts[0]
                    extractor = parts[1] if len(parts) > 1 else 'text'

                    element = item_element.select_one(selector)
                    if element:
                        if extractor == 'text':
                            item_data[field_name] = element.get_text(strip=True)
                        elif extractor.startswith('attr'):
                            attr_name = extractor[5:-1]
                            item_data[field_name] = element.get(attr_name)
                        else:
                            item_data[field_name] = None
                    else:
                        item_data[field_name] = None
                except Exception as e:
                    logger.error(f"Error parsing field '{field_name}' with selector '{selector_info}': {e}")
                    item_data[field_name] = None
            results.append(item_data)

        logger.info(f"Successfully parsed {len(results)} items using CSS.")
        return results

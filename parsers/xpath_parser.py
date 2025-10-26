import logging
from typing import Any, Dict, List

from lxml import html

from parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)

class XPathParser(BaseParser):
    """
    A parser that extracts data from HTML content using XPath expressions.
    """

    def parse(self, content: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parses HTML content using XPath expressions defined in the configuration.

        Args:
            content: The raw HTML content as a string.
            config: Configuration for the XPath parser, must include:
                - 'container': An XPath expression to select the main item containers.
                - 'fields': A dictionary where keys are field names and values are
                            XPath expressions relative to the container to extract data.

        Returns:
            A list of dictionaries, where each dictionary represents an extracted item.
            Returns an empty list if parsing fails or no items are found.
        """
        try:
            tree = html.fromstring(content)
        except Exception as e:
            logger.error(f"Failed to parse HTML content with lxml: {e}")
            return []

        parser_config = config.get('parser_config', {})
        container_xpath = parser_config.get('container')
        if not container_xpath:
            logger.error("XPathParser config must include a 'container' XPath expression.")
            return []

        item_containers = tree.xpath(container_xpath)
        if not item_containers:
            logger.warning(f"No items found with container XPath: '{container_xpath}'")
            return []

        logger.info(f"Found {len(item_containers)} items with container XPath.")

        fields = parser_config.get('fields', {})
        if not fields:
            logger.error("XPathParser config must include a 'fields' dictionary.")
            return []

        extracted_data = []
        for item_container in item_containers:
            item_data = {}
            for field_name, xpath_expression in fields.items():
                try:
                    result = item_container.xpath(xpath_expression)
                    
                    if result:
                        if isinstance(result, list):
                            if len(result) > 0:
                                if isinstance(result[0], html.HtmlElement):
                                    item_data[field_name] = result[0].text_content().strip()
                                else:
                                    item_data[field_name] = " ".join(result).strip()
                            else:
                                item_data[field_name] = None
                        else:
                            if isinstance(result, html.HtmlElement):
                                item_data[field_name] = result.text_content().strip()
                            else:
                                item_data[field_name] = str(result).strip()
                    else:
                        item_data[field_name] = None
                except Exception as e:
                    logger.error(f"Error extracting field '{field_name}' with XPath '{xpath_expression}': {e}")
                    item_data[field_name] = None
            extracted_data.append(item_data)

        logger.info(f"Successfully parsed {len(extracted_data)} items using XPath.")
        return extracted_data

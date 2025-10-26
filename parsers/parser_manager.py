import logging
from typing import Any, Dict, List, Type

# Concrete parser imports
from parsers.base_parser import BaseParser
from parsers.css_parser import CSSParser
from parsers.xpath_parser import XPathParser
# from parsers.json_parser import JSONParser # Not yet implemented
from parsers.ai_parser import AIParser

logger = logging.getLogger(__name__)


class ParserManager:
    """
    Manages and delegates parsing tasks to the appropriate registered parser.

    This class holds a registry of available parsers and selects the correct one
    based on the configuration provided. It's designed to be extensible,
    allowing new parsers to be registered dynamically.
    """

    def __init__(self):
        """Initializes the ParserManager and registers available parsers."""
        self._parser_registry: Dict[str, Type[BaseParser]] = {}
        self.register_parser('css', CSSParser)
        self.register_parser('xpath', XPathParser)
        self.register_parser('ai', AIParser)
        # self.register_parser('json', JSONParser) # Register when implemented

    def register_parser(self, parser_type: str, parser_class: Type[BaseParser]):
        """
        Registers a parser class for a given type string.

        Args:
            parser_type: The string identifier for the parser (e.g., 'css', 'json').
            parser_class: The class implementation of the parser.
        """
        if not issubclass(parser_class, BaseParser):
            raise TypeError("parser_class must be a subclass of BaseParser")
        logger.info(f"Registering parser type '{parser_type}'.")
        self._parser_registry[parser_type] = parser_class

    def get_parser(self, parser_type: str) -> BaseParser:
        """
        Retrieves an instance of a registered parser.

        Args:
            parser_type: The string identifier for the parser.

        Returns:
            An instance of the requested parser.
        
        Raises:
            ValueError: If no parser is registered for the given type.
        """
        ParserClass = self._parser_registry.get(parser_type)
        if not ParserClass:
            logger.error(f"No parser registered for type '{parser_type}'.")
            raise ValueError(f"Unsupported parser type: {parser_type}")
        return ParserClass()

    def parse(self, content: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Selects a parser based on config and parses the content.

        This is the main entry point for the parsing process. It uses the
        'parser_type' from the config to select the strategy and delegates
        the work to the appropriate parser instance.

        Args:
            content: The raw content (HTML, JSON, etc.) to be parsed.
            config: The configuration dictionary, which must contain 'parser_type'
                    and the specific settings for that parser.

        Returns:
            A list of dictionaries containing the extracted data.
        """
        parser_type = config.get('parser_type')
        if not parser_type:
            raise ValueError("'parser_type' must be specified in the configuration.")

        logger.info(f"Attempting to parse content using '{parser_type}' parser.")
        try:
            parser = self.get_parser(parser_type)
            # The full config is passed to the parser
            return parser.parse(content, config)
        except ValueError as e:
            # Re-raising the error from get_parser
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"An error occurred during parsing with '{parser_type}': {e}", exc_info=True)
            # In a future implementation, fallback logic would be triggered here.
            return []

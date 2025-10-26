import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

class ConfigValidator:
    """
    Validates site configuration dictionaries to ensure all required fields
    and structural integrity are met.
    """

    REQUIRED_FIELDS: Dict[str, Any] = {
        "name": str,
        "type": lambda x: x in ["html", "spa", "api", "pdf", "excel"],
        "seed_url": str,
        "parser_type": lambda x: x in ["css", "xpath", "json", "ai"],
        "parser_config": dict,
    }

    # Define required fields for specific parser types
    PARSER_CONFIG_REQUIRED_FIELDS: Dict[str, Dict[str, Any]] = {
        "css": {
            "container": str,
            "fields": dict,
        },
        "xpath": {
            "container": str,
            "fields": dict,
        },
        "json": {
            "container": str,
            "fields": dict,
        },
        "ai": {
            "model": str,
            "prompt_template": str,
            "fields": list,
        },
    }

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates a given site configuration dictionary.

        Args:
            config: The site configuration dictionary to validate.

        Returns:
            A tuple containing:
                - bool: True if the config is valid, False otherwise.
                - List[str]: A list of error messages if validation fails.
        """
        errors: List[str] = []

        # Validate top-level required fields
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in config:
                errors.append(f"Missing required field: '{field}'")
                continue
            
            if callable(expected_type): # For type checks with specific values (e.g., 'type')
                if not expected_type(config[field]):
                    errors.append(f"Invalid value for field '{field}': '{config[field]}'")
            elif not isinstance(config[field], expected_type):
                errors.append(f"Field '{field}' expected type '{expected_type.__name__}', got '{type(config[field]).__name__}'")

        # Validate parser-specific required fields
        parser_type = config.get("parser_type")
        parser_config = config.get("parser_config")

        if parser_type and parser_config:
            required_parser_fields = self.PARSER_CONFIG_REQUIRED_FIELDS.get(parser_type)
            if required_parser_fields:
                for field, expected_type in required_parser_fields.items():
                    if field not in parser_config:
                        errors.append(f"Missing required field for '{parser_type}' parser_config: '{field}'")
                        continue
                    if not isinstance(parser_config[field], expected_type):
                        errors.append(f"Field '{field}' in parser_config expected type '{expected_type.__name__}', got '{type(parser_config[field]).__name__}'")
            else:
                errors.append(f"Unknown parser_type '{parser_type}' specified in config.")

        if errors:
            logger.error(f"Configuration validation failed with errors: {errors}")
            return False, errors
        
        logger.info("Configuration validated successfully.")
        return True, []

import logging
import re
from typing import Any, Dict, List, Callable, Optional

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Validates a list of data dictionaries against a set of predefined rules.

    Identifies missing fields, incorrect types, or values that do not meet
    specified criteria.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the DataValidator with validation rules.

        Args:
            config: A dictionary containing validation rules. Expected keys:
                - 'validation_rules': A dictionary where keys are field names
                                      and values are dictionaries defining validation
                                      rules for that field.
                                      Example:
                                      {
                                          'product_name': {'required': True, 'min_length': 5},
                                          'price': {'required': True, 'type': 'float', 'min_value': 0},
                                          'url': {'required': True, 'regex': '^https?://'}
                                      }
        """
        self.config = config
        self.validation_rules = config.get('validation_rules', {})

    def validate(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Applies validation rules to a list of data dictionaries.

        Args:
            data: A list of dictionaries (transformed items).

        Returns:
            A list of dictionaries, where each dictionary is a validated item.
            Invalid items are logged and can optionally be filtered out.
        """
        validated_data = []
        for item_index, item in enumerate(data):
            is_valid = True
            issues = []
            for field_name, rules in self.validation_rules.items():
                value = item.get(field_name)

                # Required check
                if rules.get('required') and (value is None or value == ''):
                    is_valid = False
                    issues.append(f"Field '{field_name}' is required but missing or empty.")

                # Type check (basic)
                if 'type' in rules and value is not None:
                    expected_type = rules['type']
                    if expected_type == 'str' and not isinstance(value, str):
                        is_valid = False
                        issues.append(f"Field '{field_name}' expected type '{expected_type}', got '{type(value).__name__}'.")
                    elif expected_type == 'int' and not isinstance(value, int):
                        is_valid = False
                        issues.append(f"Field '{field_name}' expected type '{expected_type}', got '{type(value).__name__}'.")
                    elif expected_type == 'float' and not isinstance(value, (float, int)): # int can be float
                        is_valid = False
                        issues.append(f"Field '{field_name}' expected type '{expected_type}', got '{type(value).__name__}'.")
                    elif expected_type == 'bool' and not isinstance(value, bool):
                        is_valid = False
                        issues.append(f"Field '{field_name}' expected type '{expected_type}', got '{type(value).__name__}'.")

                # Min/Max length for strings
                if isinstance(value, str):
                    if 'min_length' in rules and len(value) < rules['min_length']:
                        is_valid = False
                        issues.append(f"Field '{field_name}' min_length {rules['min_length']} not met.")
                    if 'max_length' in rules and len(value) > rules['max_length']:
                        is_valid = False
                        issues.append(f"Field '{field_name}' max_length {rules['max_length']} exceeded.")

                # Min/Max value for numbers
                if isinstance(value, (int, float)):
                    if 'min_value' in rules and value < rules['min_value']:
                        is_valid = False
                        issues.append(f"Field '{field_name}' min_value {rules['min_value']} not met.")
                    if 'max_value' in rules and value > rules['max_value']:
                        is_valid = False
                        issues.append(f"Field '{field_name}' max_value {rules['max_value']} exceeded.")

                # Regex pattern matching
                if 'regex' in rules and isinstance(value, str):
                    if not re.match(rules['regex'], value):
                        is_valid = False
                        issues.append(f"Field '{field_name}' does not match regex pattern '{rules['regex']}'.")
            
            if is_valid:
                validated_data.append(item)
            else:
                logger.warning(f"Validation failed for item {item_index}: {issues}. Item: {item}")
                # In a real system, we might store these issues in the data_quality_issues table.
        
        logger.info(f"Validated {len(data)} items. {len(validated_data)} items passed validation.")
        return validated_data

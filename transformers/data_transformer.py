import logging
from typing import Any, Dict, List, Callable, Optional

logger = logging.getLogger(__name__)

class DataTransformer:
    """
    Transforms a list of parsed data dictionaries based on a defined configuration.

    This includes field mapping, type conversion, and basic data cleaning.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the DataTransformer with transformation configuration.

        Args:
            config: A dictionary containing transformation rules. Expected keys:
                - 'transformations': A dictionary where keys are target field names
                                     and values are dictionaries defining transformation
                                     steps for that field.
                                     Example:
                                     {
                                         'price': {
                                             'source_field': 'raw_price',
                                             'steps': [
                                                 {'strip': '$'},
                                                 {'convert': 'float'}
                                             ]
                                         },
                                         'product_name': {
                                             'source_field': 'title',
                                             'steps': [
                                                 {'clean_whitespace': True}
                                             ]
                                         }
                                     }
        """
        self.config = config
        self.transform_rules = config.get('transformations', {})
        self._type_converters: Dict[str, Callable[[Any], Any]] = {
            'str': str,
            'int': int,
            'float': float,
            'bool': self._to_bool,
            # Add more complex converters as needed
        }

    def _to_bool(self, value: Any) -> bool:
        """Converts a value to boolean."""
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return bool(value)

    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Applies transformations to a list of data dictionaries.

        Args:
            data: A list of dictionaries (parsed items).

        Returns:
            A list of transformed dictionaries.
        """
        transformed_data = []
        for item in data:
            transformed_item = {}
            for target_field, rules in self.transform_rules.items():
                source_field = rules.get('source_field', target_field) # Default to target_field if not specified
                value = item.get(source_field)
                
                steps = rules.get('steps', [])
                for step in steps:
                    if 'strip' in step:
                        if isinstance(value, str):
                            value = value.replace(step['strip'], '').strip()
                    elif 'replace' in step:
                        if isinstance(value, str):
                            value = value.replace(step['replace']['old'], step['replace']['new'])
                    elif 'convert' in step:
                        converter_type = step['convert']
                        converter = self._type_converters.get(converter_type)
                        if converter and value is not None:
                            try:
                                value = converter(value)
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Failed to convert value '{value}' to '{converter_type}' for field '{target_field}': {e}")
                                value = None # Set to None on conversion failure
                    elif 'clean_whitespace' in step and step['clean_whitespace'] is True:
                        if isinstance(value, str):
                            value = ' '.join(value.split()).strip()
                    # Add more transformation steps as needed
                transformed_item[target_field] = value
            transformed_data.append(transformed_item)
        return transformed_data

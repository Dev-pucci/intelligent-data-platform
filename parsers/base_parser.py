import abc
from typing import Any, Dict, List


class BaseParser(abc.ABC):
    """Abstract base class for all content parsers."""

    @abc.abstractmethod
    def parse(self, content: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parses the given content to extract structured data.

        Args:
            content: The raw content (e.g., HTML, JSON string) to parse.
            config: The parser-specific configuration details.

        Returns:
            A list of dictionaries, where each dictionary is an extracted item.
        """
        pass

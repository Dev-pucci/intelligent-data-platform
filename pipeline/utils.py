import hashlib
import json
from typing import Dict, Any

def generate_data_hash(data_item: Dict[str, Any]) -> str:
    """
    Generates a SHA256 hash for a given data item (dictionary).

    The dictionary is first converted to a canonical JSON string to ensure
    consistent hashing regardless of dictionary key order.

    Args:
        data_item: A dictionary representing a single scraped item.

    Returns:
        A SHA256 hash string of the data item.
    """
    # Sort keys to ensure consistent JSON string representation
    canonical_string = json.dumps(data_item, sort_keys=True, ensure_ascii=False)
    
    return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()

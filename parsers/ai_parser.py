import logging
import json
import os # New import
from typing import Any, Dict, List

import requests

from parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)

class AIParser(BaseParser):
    """
    A parser that uses an AI model (via Gemini API) to extract structured data.

    This parser constructs a prompt and sends it to the Gemini API to get
    the data back in a structured format.
    """

    def __init__(self):
        """
        Initializes the AIParser.
        """
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") # Get API key from environment variable
        if not self.gemini_api_key:
            logger.error("GEMINI_API_KEY environment variable not set.")
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    def parse(self, content: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parses content using an AI model.

        Args:
            content: The raw text content to parse.
            config: Configuration for the AI parser, must include:
                - 'model': The Gemini model to use (e.g., 'gemini-pro').
                - 'prompt_template': A template for the prompt, e.g.,
                  "Extract {fields} from the following text. Return as JSON. Text: {text}"
                - 'fields': A list of field names to extract.

        Returns:
            A list containing a single dictionary of the extracted data,
            or an empty list if parsing fails.
        """
        parser_config = config.get('parser_config', {})
        model = parser_config.get('model', 'gemini-pro') # Default to gemini-pro
        prompt_template = parser_config.get('prompt_template')
        fields_to_extract = parser_config.get('fields')

        if not all([prompt_template, fields_to_extract]):
            logger.error("AIParser config must include 'prompt_template' and 'fields' within 'parser_config'.")
            return []

        fields_str = ", ".join(fields_to_extract)
        prompt_text = prompt_template.format(fields=fields_str, text=content)

        logger.info(f"Sending prompt to Gemini AI model '{model}'.")

        headers = {
            "Content-Type": "application/json",
        }
        params = {
            "key": self.gemini_api_key
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_text}
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json" # Request JSON output
            }
        }

        try:
            response = requests.post(f"{self.gemini_api_url}?key={self.gemini_api_key}", headers=headers, json=payload, timeout=120)
            response.raise_for_status()

            response_data = response.json()
            
            # Gemini API response structure is different
            # It's usually response_data['candidates'][0]['content']['parts'][0]['text']
            # And that text itself is a JSON string.
            
            # Extract the text content from the Gemini response
            extracted_text = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
            
            if not extracted_text:
                logger.error("Gemini API response did not contain expected text content.")
                logger.debug(f"Raw Gemini response: {response_data}")
                return []

            # The extracted text should be a JSON string, so parse it
            extracted_data = json.loads(extracted_text)
            
            # If the AI returns a single object, wrap it in a list
            if isinstance(extracted_data, dict):
                return [extracted_data]
            elif isinstance(extracted_data, list):
                return extracted_data
            else:
                logger.error(f"Gemini API returned unexpected data type: {type(extracted_data)}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request failed: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from Gemini API response: {e}")
            logger.debug(f"Raw Gemini API response text: {extracted_text}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred in AIParser: {e}", exc_info=True)
            return []

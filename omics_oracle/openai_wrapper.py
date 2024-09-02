import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from ..prompts import base_prompt

class OpenAIWrapper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_environment()
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4"  # Changed to gpt-4 as gpt-4o is not a standard model name

    def _load_environment(self):
        """Load environment variables from .env file."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dotenv_path = os.path.join(current_dir, '..', '.env')
        self.logger.info(f"Looking for .env file at: {dotenv_path}")
        
        if load_dotenv(dotenv_path):
            self.logger.info("Successfully loaded .env file")
        else:
            self.logger.error("Failed to load .env file")
            raise ValueError("Failed to load .env file")

        self.api_key = os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set in the .env file")

    def send_query(self, query: str) -> str:
        """Send a query to the OpenAI API and return the response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": base_prompt},
                    {"role": "user", "content": query}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error in OpenAI API call: {str(e)}")
            return None

    def generate_aql(self, query: str) -> str:
        """Generate an AQL query based on the natural language query."""
        return self.send_query(query)
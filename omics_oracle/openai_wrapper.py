import os
import logging
import traceback
from dotenv import load_dotenv
from openai import OpenAI
from omics_oracle.prompts import base_prompt as default_base_prompt

class OpenAIWrapper:
    def __init__(self, base_prompt=default_base_prompt):
        self.logger = logging.getLogger(__name__)
        self._load_environment()
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"
        self.base_prompt = base_prompt
        self.logger.info("OpenAIWrapper initialized successfully")

    def _load_environment(self):
        """Load environment variables from .env file."""
        try:
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
                self.logger.error("OPENAI_API_KEY not found in .env file")
                raise ValueError("OPENAI_API_KEY must be set in the .env file")
            else:
                self.logger.info("OPENAI_API_KEY loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading environment: {e}\n\n{traceback.format_exc()}")
            raise

    def send_query(self, query: str) -> str:
        """Send a query to the OpenAI API and return the response."""
        self.logger.debug(f"Sending query to OpenAI: {query}")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.base_prompt},
                    {"role": "user", "content": query}
                ]
            )
            self.logger.debug(f"OpenAI response received: {response.choices[0].message.content}")
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error in OpenAI API call: {e}\n\n{traceback.format_exc()}")
            return None

    def generate_aql(self, query: str) -> str:
        """Generate an AQL query based on the natural language query."""
        self.logger.debug(f"Generating AQL for query: {query}")
        try:
            aql = self.send_query(query)
            self.logger.debug(f"Generated AQL: {aql}")
            return aql
        except Exception as e:
            self.logger.error(f"Error generating AQL: {e}\n\n{traceback.format_exc()}")
            return None
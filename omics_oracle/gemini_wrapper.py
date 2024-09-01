# omics_oracle/gemini_wrapper.py

import os
import requests
import json
import httpx
from typing import Dict, Any, List
from .logger import setup_logger
from dotenv import load_dotenv

class GeminiWrapper:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self._load_environment()
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

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

        self.api_key = os.getenv('GEMINI_AUTH')
        self.base_url = os.getenv('GEMINI_URL')

        if not self.api_key or not self.base_url:
            raise ValueError("GEMINI_AUTH and GEMINI_URL must be set in the .env file")

    def send_query(self, query: str, context: str = "general") -> Dict[str, Any]:
        """
        Send a query to the Gemini API and return the response.

        Args:
            query (str): The natural language query to send to the API.
            context (str): The context of the query (e.g., "general", "biomedical", "aql_generation").

        Returns:
            Dict[str, Any]: The API response as a dictionary.

        Raises:
            requests.RequestException: If there's an error with the API request.
        """
        prompt = self._generate_prompt(query, context)
        payload = {
            "model": "gemini-pro",
            "messages": [{"role": "user", "content": prompt}]
        }

        self.logger.info(f"Sending request to: {self.base_url}")
        self.logger.debug(f"Headers: {json.dumps(self.headers, indent=2)}")
        self.logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            self.logger.info(f"Response status code: {response.status_code}")
            self.logger.debug(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
            self.logger.debug(f"Response content: {response.text}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error sending query to Gemini API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Error response content: {e.response.text}")
            raise

    def interpret_response(self, response: Dict[str, Any]) -> str:
        """
        Interpret the Gemini API response and extract the relevant content.

        Args:
            response (Dict[str, Any]): The API response dictionary.

        Returns:
            str: The extracted content from the response.
        """
        try:
            content = response['choices'][0]['message']['content']
            self.logger.info("Successfully interpreted Gemini API response")
            return content
        except KeyError as e:
            self.logger.error(f"Error interpreting Gemini API response: {e}")
            return "Error: Unable to interpret the response"
        except Exception as e:
            self.logger.error(f"Unexpected error interpreting Gemini API response: {e}")
            return "Error: An unexpected error occurred"

    def _generate_prompt(self, query: str, context: str) -> str:
        """
        Generate a specialized prompt based on the query context.

        Args:
            query (str): The original user query.
            context (str): The context of the query.

        Returns:
            str: The generated prompt.
        """
        base_prompt = "You are an AI assistant specializing in biomedical knowledge. "
        
        if context == "biomedical":
            prompt = base_prompt + f"Interpret the following biomedical query and provide a detailed explanation: '{query}'"
        elif context == "aql_generation":
            prompt = base_prompt + f"Generate an AQL (ArangoDB Query Language) query to answer the following biomedical question using the SPOKE knowledge graph: '{query}'. The query should start with 'AQL:' followed by the actual AQL query."
        else:  # general context
            prompt = base_prompt + f"Please answer the following question: '{query}'"

        return prompt

    def generate_aql_query(self, biomedical_query: str) -> str:
        """
        Generate an AQL query based on a biomedical question.

        Args:
            biomedical_query (str): The biomedical question.

        Returns:
            str: The generated AQL query.
        """
        response = self.send_query(biomedical_query, context="aql_generation")
        interpreted_response = self.interpret_response(response)
        aql_query = self._extract_aql_query(interpreted_response)
        return aql_query

    def _extract_aql_query(self, response: str) -> str:
        """
        Extract the AQL query from the Gemini response.

        Args:
            response (str): The Gemini response containing the AQL query.

        Returns:
            str: The extracted AQL query.
        """
        try:
            aql_start = response.index("AQL:") + 4
            aql_query = response[aql_start:].strip()
            return aql_query
        except ValueError:
            self.logger.error("No AQL query found in the response")
            return ""

    def interpret_spoke_results(self, spoke_results: List[Dict[str, Any]], original_query: str) -> str:
        """
        Interpret the SPOKE results in the context of the original query.

        Args:
            spoke_results (List[Dict[str, Any]]): The results from the SPOKE knowledge graph.
            original_query (str): The original biomedical query.

        Returns:
            str: An interpretation of the SPOKE results.
        """
        interpretation_prompt = f"Based on the original biomedical query '{original_query}' and the following results from the SPOKE knowledge graph: {spoke_results}, provide a concise interpretation of the findings, highlighting key biomedical insights."
        response = self.send_query(interpretation_prompt, context="biomedical")
        return self.interpret_response(response)
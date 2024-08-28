# omics_oracle/gemini_wrapper.py

import requests
from typing import Dict, Any, List
from .logger import setup_logger

class GeminiWrapper:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.logger = setup_logger(__name__)

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

        try:
            self.logger.info(f"Sending query to Gemini API: {prompt}")
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            self.logger.info("Successfully received response from Gemini API")
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error sending query to Gemini API: {e}")
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
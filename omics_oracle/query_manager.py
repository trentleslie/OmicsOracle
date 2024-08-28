# omics_oracle/query_manager.py

from .gemini_wrapper import GeminiWrapper
from .spoke_wrapper import SpokeWrapper
from typing import Dict, Any
from .logger import setup_logger

class QueryManager:
    def __init__(self, gemini_wrapper: GeminiWrapper, spoke_wrapper: SpokeWrapper):
        self.gemini = gemini_wrapper
        self.spoke = spoke_wrapper
        self.logger = setup_logger(__name__)

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query through the Gemini and Spoke APIs.

        Args:
            user_query (str): The natural language query from the user.

        Returns:
            Dict[str, Any]: A dictionary containing the processed results.
        """
        self.logger.info(f"Processing user query: {user_query}")
        try:
            # Step 1: Send the user query to Gemini for interpretation
            gemini_response = self.gemini.send_query(user_query)
            interpreted_query = self.gemini.interpret_response(gemini_response)
            self.logger.info(f"Gemini interpretation: {interpreted_query}")

            # Step 2: Extract AQL query from Gemini's response
            aql_query = self.extract_aql_from_response(interpreted_query)
            self.logger.info(f"Extracted AQL query: {aql_query}")

            # Step 3: Execute the AQL query on the Spoke knowledge graph
            if aql_query:
                spoke_results = self.spoke.execute_aql(aql_query)
                self.logger.info(f"Spoke query executed. Results count: {len(spoke_results)}")
            else:
                spoke_results = []
                self.logger.warning("No AQL query extracted. Skipping Spoke query execution.")

            # Step 4: Send the Spoke results back to Gemini for final interpretation
            final_interpretation = self.get_final_interpretation(spoke_results, user_query)
            self.logger.info("Final interpretation generated")

            return {
                "original_query": user_query,
                "gemini_interpretation": interpreted_query,
                "aql_query": aql_query,
                "spoke_results": spoke_results,
                "final_interpretation": final_interpretation
            }
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            raise

    def extract_aql_from_response(self, gemini_response: str) -> str:
        """
        Extract the AQL query from Gemini's response.
        This is a placeholder and should be implemented based on the actual format of Gemini's response.
        """
        try:
            if "AQL:" in gemini_response:
                aql_query = gemini_response.split("AQL:")[1].strip()
                self.logger.info(f"AQL query extracted: {aql_query}")
                return aql_query
            else:
                self.logger.warning("No AQL query found in Gemini's response")
                return ""
        except Exception as e:
            self.logger.error(f"Error extracting AQL query: {e}")
            return ""

    def get_final_interpretation(self, spoke_results: list, original_query: str) -> str:
        """
        Get the final interpretation of the Spoke results from Gemini.
        """
        try:
            interpretation_prompt = f"Based on the original query '{original_query}' and the following results from the knowledge graph: {spoke_results}, provide a concise interpretation of the findings."
            self.logger.info("Sending final interpretation request to Gemini")
            gemini_response = self.gemini.send_query(interpretation_prompt)
            final_interpretation = self.gemini.interpret_response(gemini_response)
            self.logger.info("Received final interpretation from Gemini")
            return final_interpretation
        except Exception as e:
            self.logger.error(f"Error getting final interpretation: {e}")
            raise
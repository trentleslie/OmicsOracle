import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from omics_oracle.gemini_wrapper import GeminiWrapper
from omics_oracle.spoke_wrapper import SpokeWrapper
from omics_oracle.query_manager import QueryManager
from omics_oracle.gradio_interface import create_interface

def main():
    # Initialize wrappers with placeholder values
    # In a real-world scenario, these would be replaced with actual API keys and connection details
    gemini_wrapper = GeminiWrapper(api_key="PLACEHOLDER_API_KEY", base_url="https://api.gemini.com/v1")
    spoke_wrapper = SpokeWrapper(host="http://localhost:8529", db_name="spoke", username="root", password="password")

    # Initialize the query manager
    query_manager = QueryManager(gemini_wrapper, spoke_wrapper)

    # Create and launch the Gradio interface
    interface = create_interface(query_manager)
    interface.launch()

if __name__ == "__main__":
    main()
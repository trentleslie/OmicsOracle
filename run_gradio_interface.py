import os
from dotenv import load_dotenv
from omics_oracle.gemini_wrapper import GeminiWrapper
from omics_oracle.spoke_wrapper import SpokeWrapper
from omics_oracle.query_manager import QueryManager
from omics_oracle.gradio_interface import create_styled_interface

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Initialize and launch the OmicsOracle biomedical query system.

    This function sets up the Gemini API and SPOKE database connections,
    initializes the query manager, and launches the Gradio interface.
    """
    # Gemini API configuration
    gemini_auth = os.getenv('GEMINI_AUTH')
    gemini_url = os.getenv('GEMINI_URL')

    if not gemini_auth or not gemini_url:
        raise ValueError("GEMINI_AUTH and GEMINI_URL must be set in the .env file")

    # SPOKE configuration
    spoke_host = os.getenv('SPOKE_HOST')
    spoke_db = os.getenv('SPOKE_DB')
    spoke_username = os.getenv('SPOKE_USERNAME')
    spoke_password = os.getenv('SPOKE_PASSWORD')

    if not spoke_host or not spoke_db or not spoke_username or not spoke_password:
        raise ValueError("SPOKE_HOST, SPOKE_DB, SPOKE_USERNAME, and SPOKE_PASSWORD must be set in the .env file")

    # Initialize wrappers
    gemini_wrapper = GeminiWrapper(api_key=gemini_auth, base_url=gemini_url)
    spoke_wrapper = SpokeWrapper(
        host=spoke_host,
        db_name=spoke_db,
        username=spoke_username,
        password=spoke_password
    )

    # Initialize the query manager
    query_manager = QueryManager(gemini_wrapper, spoke_wrapper)

    # Create and launch the Gradio interface
    interface = create_styled_interface(query_manager)
    interface.launch(share=True)

if __name__ == '__main__':
    main()
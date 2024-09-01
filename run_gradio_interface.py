import logging
from dotenv import load_dotenv
from omics_oracle.gemini_wrapper import GeminiWrapper
from omics_oracle.spoke_wrapper import SpokeWrapper
from omics_oracle.query_manager import QueryManager
from omics_oracle.gradio_interface import create_styled_interface
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Reduce logging level for some noisy libraries
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

# Set logging level for omics_oracle modules
logging.getLogger('omics_oracle').setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Initialize and launch the OmicsOracle biomedical query system.

    This function sets up the Gemini API and SPOKE database connections,
    initializes the query manager, and launches the Gradio interface.
    """
    logger.info("Initializing OmicsOracle biomedical query system...")

    # Initialize wrappers
    gemini_wrapper = GeminiWrapper()
    spoke_wrapper = SpokeWrapper()

    # Initialize the query manager
    query_manager = QueryManager(gemini_wrapper, spoke_wrapper)

    # Create and launch the Gradio interface
    logger.info("Creating Gradio interface...")
    interface = create_styled_interface(query_manager)
    
    logger.info("Launching Gradio interface...")
    try:
        interface.launch(share=True)
    except KeyboardInterrupt:
        logger.info("Gracefully shutting down the server...")
        interface.close()
        sys.exit(0)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
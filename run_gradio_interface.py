import logging
import sys
from dotenv import load_dotenv
from omics_oracle.spoke_wrapper import SpokeWrapper
from omics_oracle.query_manager import QueryManager
from omics_oracle.gradio_interface import create_styled_interface
from omics_oracle.openai_wrapper import OpenAIWrapper

# Configure logging to file and console
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("omics_oracle.log"),
                        logging.StreamHandler(sys.stdout)
                    ])

logger = logging.getLogger(__name__)

# Reduce logging level for some noisy libraries
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

def main():
    """
    Initialize and launch the OmicsOracle biomedical query system.
    """
    logger.info("Initializing OmicsOracle biomedical query system...")

    # Load environment variables
    load_dotenv()

    # Initialize wrappers
    spoke_wrapper = SpokeWrapper()
    openai_wrapper = OpenAIWrapper()

    # Initialize the query manager
    query_manager = QueryManager(spoke_wrapper, openai_wrapper)

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
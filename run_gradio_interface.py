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

    try:
        load_dotenv()
        logger.info("Environment variables loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load environment variables: {e}")
        sys.exit(1)

    try:
        spoke_wrapper = SpokeWrapper()
        logger.info("SpokeWrapper initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize SpokeWrapper: {e}")
        sys.exit(1)

    try:
        openai_wrapper = OpenAIWrapper()
        logger.info("OpenAIWrapper initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAIWrapper: {e}")
        sys.exit(1)

    try:
        query_manager = QueryManager(spoke_wrapper, openai_wrapper)
        logger.info("QueryManager initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize QueryManager: {e}")
        sys.exit(1)

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
        logger.error(f"An error occurred while launching the Gradio interface: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
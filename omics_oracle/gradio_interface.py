import gradio as gr
from omics_oracle.query_manager import QueryManager
from omics_oracle.openai_wrapper import OpenAIWrapper
from omics_oracle.spoke_wrapper import SpokeWrapper
import logging
import traceback
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='error.log')
logger = logging.getLogger(__name__)

def process_query(query: str, query_manager: QueryManager) -> str:
    logger.debug(f"Submit button clicked with query: {query}")
    logger.debug(f"Received query: {query}")
    if not query.strip():
        logger.error("Empty query received")
        return "Error: Query cannot be empty. Please enter a valid query."
    
    try:
        logger.debug("Starting to process the query with QueryManager...")
        response = query_manager.process_query(query)
        logger.debug(f"QueryManager returned response: {response}")

        formatted_response = format_response(response)
        logger.debug(f"Formatted response: {formatted_response}")
        return formatted_response
    except ValueError as ve:
        logger.error(f"ValueError while processing query: {ve}\n\n{traceback.format_exc()}")
        return f"An error occurred: {str(ve)}"
    except Exception as e:
        logger.error(f"Exception while processing query: {e}\n\n{traceback.format_exc()}")
        return f"An unexpected error occurred. Please try again later. If the problem persists, contact support. Details: {str(e)}"

def format_response(response: dict) -> str:
    logger.debug(f"Formatting response: {response}")
    formatted = f"Original Query: {response['original_query']}\n\n"
    formatted += f"AQL Query: {response.get('aql_query', 'No AQL query generated')}\n\n"
    formatted += f"SPOKE Results: {json.dumps(response.get('spoke_results', []), indent=2)}\n\n"
    formatted += f"Interpretation: {response['interpretation']}\n\n"
    if 'attempt_count' in response:
        formatted += f"Attempt Count: {response['attempt_count']}"
    logger.debug(f"Formatted response: {formatted}")
    return formatted

custom_css = """
body {
    font-family: Arial, sans-serif;
    background-color: #1a1a2e;
    color: #e0e0e0;
}
#centered-content {
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
    text-align: center;
}
.container {
    max-width: 800px;
    margin: auto;
    padding: 20px;
    background-color: #16213e;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
}
textarea, button {
    width: 100% !important;
    box-sizing: border-box !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
}

/* Apply a max-width based on the actual pixel width */
textarea {
    font-size: 16px !important;
    background-color: #0f3460 !important;
    color: #e0e0e0 !important;
    border: 1px solid #1f4287 !important;
    max-width: 800px !important; /* Adjust this value to match the actual container width */
}

button {
    background-color: #1f4287 !important;
    color: white !important;
    padding: 10px 20px !important;
    border: none !important;
    border-radius: 5px !important;
    cursor: pointer !important;
    margin-top: 10px !important;
    margin-bottom: 10px !important;
    font-size: 16px !important;
    max-width: 800px !important; /* Set the same max-width as the textarea or container */
    width: 100% !important; /* Ensure it scales down proportionally */
    display: block;
    margin-left: auto;
    margin-right: auto;
}

button:hover {
    background-color: #2a5298 !important;
}
h1 {
    font-size: 2.5em !important;
    margin-bottom: 20px !important;
    text-align: center;
}
footer {
    display: none !important;
}
.block {
    padding: 0 !important;
}
"""

def create_styled_interface(query_manager: QueryManager):
    """
    Create and configure a styled Gradio interface for the OmicsOracle system.

    Args:
        query_manager (QueryManager): The QueryManager instance to process queries.

    Returns:
        gr.Blocks: The configured Gradio interface with custom styling.
    """
    logger.debug("Creating styled Gradio interface")

    with gr.Blocks(css=custom_css) as interface:
        with gr.Column(elem_id="centered-content"):
            gr.Markdown("# OmicsOracle Biomedical Query System")
            
            query_input = gr.Textbox(
                lines=5,
                label="Enter your biomedical query here...",
                elem_id="query_input"
            )
            
            submit_button = gr.Button("Submit Query", elem_id="submit_button")

            response_output = gr.Textbox(label="Response", lines=15, elem_id="response_output")
            
            gr.Markdown("Enter a biomedical query, and the system will provide an answer based on the available data.")
            
            submit_button.click(
                lambda q: process_query(q, query_manager),
                inputs=query_input,
                outputs=response_output
            )

    logger.debug("Styled Gradio interface created successfully")
    return interface

if __name__ == "__main__":
    # This is just for testing purposes. In production, use run_gradio_interface.py
    try:
        openai_wrapper = OpenAIWrapper()
        spoke_wrapper = SpokeWrapper()
        test_query_manager = QueryManager(spoke_wrapper, openai_wrapper)
        demo = create_styled_interface(test_query_manager)
        demo.launch(debug=True)
    except Exception as e:
        logger.error(f"Error in main execution: {e}\n\n{traceback.format_exc()}")
        raise

import gradio as gr
from omics_oracle.query_manager import QueryManager

import logging

logger = logging.getLogger(__name__)

def process_query(query: str, query_manager: QueryManager) -> str:
    try:
        logger.debug(f"Processing query: {query}")
        results = query_manager.process_query(query)
        return f"""
Original Query:
{results['original_query']}

Gemini Interpretation:
{results['gemini_interpretation']}

AQL Query:
{results['aql_query']}

Spoke Results:
{results['spoke_results']}

Final Interpretation:
{results['final_interpretation']}
        """
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return f'An error occurred: {str(e)}'

def create_interface(query_manager: QueryManager) -> gr.Blocks:
    logger.debug("Creating Gradio interface")
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="gray", neutral_hue="slate")) as demo:
        gr.Markdown("# OmicsOracle")
        
        # Center the content
        with gr.Column(scale=1, elem_id="centered-content"):
            # Input text box
            input_text = gr.Textbox(
                label="Enter your biomedical query",
                placeholder="e.g. What genes are associated with Alzheimer's disease?",
                lines=5
            )
            
            # Submit button
            submit_btn = gr.Button("Submit Query")
            
            # Output text box
            output_text = gr.Textbox(label="Query Results", lines=20)
            
            logger.debug("Setting up click event")
            submit_btn.click(
                lambda query: process_query(query, query_manager),
                inputs=input_text,
                outputs=output_text,
                api_name="query"
            )
            logger.debug("Click event set up successfully")

    logger.debug("Gradio interface created successfully")
    return demo

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

def create_styled_interface(query_manager: QueryManager) -> gr.Blocks:
    logger.debug("Creating styled interface")
    interface = create_interface(query_manager)
    interface.css = custom_css
    return interface

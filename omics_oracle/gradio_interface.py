import gradio as gr
from omics_oracle.query_manager import QueryManager
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_query(query: str, query_manager: QueryManager) -> str:
    logger.debug(f"Processing query: {query}")
    try:
        results = query_manager.process_query(query)
        return f'''Original Query:
{results['original_query']}

Gemini Interpretation:
{results['gemini_interpretation']}

AQL Query:
{results['aql_query']}

Spoke Results:
{results['spoke_results']}

Final Interpretation:
{results['final_interpretation']}'''
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return f'An error occurred: {str(e)}'

def create_interface(query_manager: QueryManager) -> gr.Blocks:
    logger.debug("Creating Gradio interface")
    with gr.Blocks(theme=gr.themes.Soft(primary_hue='blue', secondary_hue='gray', neutral_hue='slate')) as demo:
        gr.Markdown('# OmicsOracle')
        with gr.Column(scale=1, min_width=800):
            input_text = gr.Textbox(
                label='Enter your biomedical query',
                placeholder='e.g. What genes are associated with Alzheimer\'s disease?',
                lines=5
            )
            submit_btn = gr.Button('Submit Query', size='sm')
            output_text = gr.Textbox(label='Query Results', lines=20)

        logger.debug("Setting up click event")
        submit_btn.click(
            fn=lambda query: process_query(query, query_manager),
            inputs=input_text,
            outputs=output_text,
            api_name='query'
        )
        logger.debug("Click event set up successfully")

    logger.debug("Gradio interface created successfully")
    return demo

custom_css = """
/* Your custom CSS here */
"""

def create_styled_interface(query_manager: QueryManager) -> gr.Blocks:
    logger.debug("Creating styled interface")
    interface = create_interface(query_manager)
    interface.css = custom_css
    return interface
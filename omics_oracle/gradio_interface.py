# omics_oracle/gradio_interface.py

import gradio as gr
from .query_manager import QueryManager
from .gemini_wrapper import GeminiWrapper
from .spoke_wrapper import SpokeWrapper

def create_interface(query_manager: QueryManager):
    def process_query(query: str) -> str:
        try:
            results = query_manager.process_query(query)
            return f"""
            Original Query: {results['original_query']}

            Gemini Interpretation: {results['gemini_interpretation']}

            AQL Query: {results['aql_query']}

            Spoke Results: {results['spoke_results']}

            Final Interpretation: {results['final_interpretation']}
            """
        except Exception as e:
            return f"An error occurred: {str(e)}"

    iface = gr.Interface(
        fn=process_query,
        inputs=gr.Textbox(lines=2, placeholder="Enter your biomedical query here..."),
        outputs="text",
        title="OmicsOracle: Biomedical Query System",
        description="Enter a natural language query about biomedical data, and get insights from our knowledge graph!"
    )
    return iface

def launch_interface():
    # Initialize your wrappers and query manager here
    gemini_wrapper = GeminiWrapper(api_key="YOUR_API_KEY", base_url="YOUR_BASE_URL")
    spoke_wrapper = SpokeWrapper(host="YOUR_HOST", db_name="YOUR_DB_NAME", username="YOUR_USERNAME", password="YOUR_PASSWORD")
    query_manager = QueryManager(gemini_wrapper, spoke_wrapper)

    # Create and launch the interface
    iface = create_interface(query_manager)
    iface.launch()

if __name__ == "__main__":
    launch_interface()
import gradio as gr
import logging
import traceback

# Set up basic logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def button_click_action():
    """
    Function to be called when the button is clicked.
    It will log a message and print to the console.
    """
    logger.debug("Button was clicked!")
    print("Button was clicked!")
    return "Button Clicked!"  # Display this message in the Gradio output

def create_test_interface():
    """
    Create a simple Gradio interface with a button.
    """
    logger.debug("Creating test Gradio interface with a single button.")
    
    with gr.Blocks() as interface:
        gr.Markdown("# Test Gradio Interface")
        test_button = gr.Button("Click Me!", elem_id="test_button")
        test_output = gr.Textbox(label="Output")

        test_button.click(fn=button_click_action, inputs=None, outputs=test_output)
    
    logger.debug("Test Gradio interface created successfully.")
    return interface

if __name__ == "__main__":
    try:
        demo = create_test_interface()
        demo.launch(server_name="0.0.0.0", server_port=7862)  # Change port here if needed
    except Exception as e:
        logger.error(f"Failed to launch Gradio interface: {e}\n\n{traceback.format_exc()}")

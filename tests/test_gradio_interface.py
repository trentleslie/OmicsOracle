import unittest
from unittest.mock import patch, MagicMock, call
from omics_oracle.gradio_interface import create_styled_interface, process_query, custom_css, format_response
from omics_oracle.query_manager import QueryManager
import logging

class TestGradioInterface(unittest.TestCase):
    @patch('omics_oracle.gradio_interface.gr')
    def test_create_styled_interface(self, mock_gr):
        # Ensure the logger is set to debug level
        logger = logging.getLogger('omics_oracle.gradio_interface')
        logger.setLevel(logging.DEBUG)

        # Set up log capture
        with self.assertLogs(logger, level='DEBUG') as log_capture:
            # Mock QueryManager
            mock_query_manager = MagicMock(spec=QueryManager)

            # Mock Gradio components
            mock_blocks = MagicMock()
            mock_column = MagicMock()
            mock_markdown = MagicMock()
            mock_textbox = MagicMock()
            mock_button = MagicMock()

            mock_gr.Blocks.return_value.__enter__.return_value = mock_blocks
            mock_gr.Column.return_value.__enter__.return_value = mock_column
            mock_gr.Markdown.return_value = mock_markdown
            mock_gr.Textbox.side_effect = [mock_textbox, MagicMock()]  # Input and output textboxes
            mock_gr.Button.return_value = mock_button

            # Call the create_styled_interface function
            interface = create_styled_interface(mock_query_manager)

            # Verify that the interface is not None
            self.assertIsNotNone(interface, "The created interface should not be None")

            # Check if the Blocks context manager was used with custom CSS
            mock_gr.Blocks.assert_called_once_with(css=custom_css)

            # Check if the components were created
            mock_gr.Column.assert_called_once()
            self.assertEqual(mock_gr.Markdown.call_count, 2)
            self.assertEqual(mock_gr.Textbox.call_count, 2)
            mock_gr.Button.assert_called_once()

            # Check if the button click event is set up correctly
            self.assertTrue(mock_button.click.called, "The click event was not set up.")

            # Verify the arguments passed to the click method
            click_args = mock_button.click.call_args
            self.assertIsNotNone(click_args, "Click arguments are None")
            args, kwargs = click_args
            self.assertEqual(len(args), 1, "Expected one positional argument")
            self.assertTrue(callable(args[0]), "First argument should be a callable (lambda function)")
            self.assertIn('inputs', kwargs, "Missing 'inputs' keyword argument")
            self.assertIn('outputs', kwargs, "Missing 'outputs' keyword argument")
            self.assertEqual(kwargs['inputs'], mock_textbox)
            self.assertIsInstance(kwargs['outputs'], MagicMock)

            # Check if the debug logs were captured
            self.assertIn('DEBUG:omics_oracle.gradio_interface:Creating styled Gradio interface', log_capture.output)
            self.assertIn('DEBUG:omics_oracle.gradio_interface:Styled Gradio interface created successfully', log_capture.output)

    @patch('omics_oracle.gradio_interface.logger')
    def test_process_query(self, mock_logger):
        mock_query_manager = MagicMock(spec=QueryManager)
        mock_query_manager.process_query.return_value = {
            "original_query": "Test query",
            "aql_query": "FOR doc IN collection RETURN doc",
            "spoke_results": [{"result": "data"}],
            "interpretation": "Test interpretation"
        }

        result = process_query("Test query", mock_query_manager)
        
        expected_result = format_response(mock_query_manager.process_query.return_value)
        self.assertEqual(result, expected_result)

        # Check if both debug log messages were called in the correct order
        expected_calls = [
            call("Processing query: Test query"),
            call(f"Query processed successfully. Response: {mock_query_manager.process_query.return_value}")
        ]
        mock_logger.debug.assert_has_calls(expected_calls, any_order=False)

        # Check if the query_manager's process_query method was called
        mock_query_manager.process_query.assert_called_once_with("Test query")

    def test_format_response(self):
        test_response = {
            "original_query": "Test query",
            "aql_query": "FOR doc IN collection RETURN doc",
            "spoke_results": [{"result": "data"}],
            "interpretation": "Test interpretation"
        }
        formatted = format_response(test_response)
        self.assertIn("Original Query: Test query", formatted)
        self.assertIn("AQL Query: FOR doc IN collection RETURN doc", formatted)
        self.assertIn("SPOKE Results: [\n  {\n    \"result\": \"data\"\n  }\n]", formatted)
        self.assertIn("Interpretation: Test interpretation", formatted)

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from omics_oracle.gradio_interface import create_interface, process_query
import logging

class TestGradioInterface(unittest.TestCase):
    @patch('omics_oracle.gradio_interface.gr')
    def test_create_interface_click_event(self, mock_gr):
        # Ensure the logger is set to debug level
        logger = logging.getLogger('omics_oracle.gradio_interface')
        logger.setLevel(logging.DEBUG)

        # Set up log capture
        with self.assertLogs(logger, level='DEBUG') as log_capture:
            mock_query_manager = MagicMock()

            # Mock Gradio components
            mock_textbox = MagicMock()
            mock_button = MagicMock()
            mock_column = MagicMock()
            mock_gr.Textbox.side_effect = [mock_textbox, MagicMock()]  # Input and output textboxes
            mock_gr.Button.return_value = mock_button
            mock_gr.Column.return_value = mock_column

            # Call the create_interface function
            create_interface(mock_query_manager)

            # Check if the button click event is set up correctly
            self.assertTrue(mock_button.click.called, "The click event was not set up.")

            # Verify the arguments passed to the click method
            click_args = mock_button.click.call_args
            self.assertIsNotNone(click_args, "Click arguments are None")
            args, kwargs = click_args
            self.assertEqual(len(args), 1, "Expected one positional argument")
            self.assertEqual(len(kwargs), 3, "Expected three keyword arguments")
            self.assertIn('inputs', kwargs, "Missing 'inputs' keyword argument")
            self.assertIn('outputs', kwargs, "Missing 'outputs' keyword argument")
            self.assertEqual(kwargs['inputs'], mock_textbox)
            self.assertEqual(kwargs['api_name'], 'query')

            # Test the lambda function
            click_fn = args[0]  # The lambda function
            mock_query_manager.process_query.return_value = {
                'original_query': 'Test query',
                'gemini_interpretation': 'Interpreted query',
                'aql_query': 'TEST AQL',
                'spoke_results': [{"id": "123", "name": "Result1"}],
                'final_interpretation': 'Final result'
            }
            result = click_fn("Test query")

            mock_query_manager.process_query.assert_called_once_with("Test query")
            self.assertIn("Original Query:", result)
            self.assertIn("Final Interpretation:", result)

            # Print log messages for debugging
            log_messages = [record.getMessage() for record in log_capture.records]
            print(f"Captured Log Messages: {log_messages}")

            # Check log messages
            self.assertIn("Creating Gradio interface", log_messages)
            self.assertIn("Setting up click event", log_messages)
            self.assertIn("Click event set up successfully", log_messages)
            self.assertIn("Gradio interface created successfully", log_messages)
            self.assertIn("Processing query: Test query", log_messages)

    def test_process_query(self):
        logger = logging.getLogger('omics_oracle.gradio_interface')
        logger.setLevel(logging.DEBUG)

        with self.assertLogs(logger, level='DEBUG') as log_capture:
            mock_query_manager = MagicMock()
            mock_query_manager.process_query.return_value = {
                'original_query': 'Test query',
                'gemini_interpretation': 'Interpreted query',
                'aql_query': 'TEST AQL',
                'spoke_results': [{"id": "123", "name": "Result1"}],
                'final_interpretation': 'Final result'
            }

            result = process_query("Test query", mock_query_manager)
            self.assertIn("Original Query:\nTest query", result)
            self.assertIn("Gemini Interpretation:\nInterpreted query", result)
            self.assertIn("AQL Query:\nTEST AQL", result)
            self.assertIn("Spoke Results:\n[{'id': '123', 'name': 'Result1'}]", result)
            self.assertIn("Final Interpretation:\nFinal result", result)

            # Check log messages
            log_messages = [record.getMessage() for record in log_capture.records]
            self.assertIn("Processing query: Test query", log_messages)

if __name__ == '__main__':
    unittest.main()

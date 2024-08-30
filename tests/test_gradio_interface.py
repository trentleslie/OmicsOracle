import unittest
from unittest.mock import patch, MagicMock, call
from omics_oracle.gradio_interface import create_interface, process_query
import logging

class TestGradioInterface(unittest.TestCase):
    @patch('omics_oracle.gradio_interface.gr')
    def test_create_interface_click_event(self, mock_gr):
        # Set up log capture
        with self.assertLogs('omics_oracle.gradio_interface', level='DEBUG') as log_capture:
            mock_query_manager = MagicMock()
            
            # Mock Gradio components
            mock_textbox = MagicMock()
            mock_button = MagicMock()
            mock_gr.Textbox.side_effect = [mock_textbox, MagicMock()]  # Input and output textboxes
            mock_gr.Button.return_value = mock_button
            
            # Call the create_interface function
            create_interface(mock_query_manager)
            
            # Debug information
            print(f"mock_button.click.called: {mock_button.click.called}")
            print(f"mock_button.click.call_args: {mock_button.click.call_args}")
            print(f"mock_button methods: {dir(mock_button)}")
            
            # Check if the button click event is set up correctly
            self.assertTrue(mock_button.click.called, "The click event was not set up.")
            
            # Verify the arguments passed to the click method
            click_args = mock_button.click.call_args
            self.assertIsNotNone(click_args, "Click arguments are None")
            args, kwargs = click_args
            self.assertEqual(len(args), 0, "Unexpected positional arguments")
            self.assertIn('fn', kwargs, "Missing 'fn' keyword argument")
            self.assertIn('inputs', kwargs, "Missing 'inputs' keyword argument")
            self.assertIn('outputs', kwargs, "Missing 'outputs' keyword argument")
            self.assertEqual(kwargs['inputs'], mock_textbox)
            self.assertEqual(kwargs['api_name'], 'query')

            # Test the lambda function
            click_fn = kwargs['fn']
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
            
            # Check log messages
            log_messages = [record.getMessage() for record in log_capture.records]
            print(f"Log messages: {log_messages}")
            self.assertIn("Creating Gradio interface", log_messages)
            self.assertIn("Setting up click event", log_messages)
            self.assertIn("Click event set up successfully", log_messages)
            self.assertIn("Gradio interface created successfully", log_messages)

    def test_process_query(self):
        with self.assertLogs('omics_oracle.gradio_interface', level='DEBUG') as log_capture:
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
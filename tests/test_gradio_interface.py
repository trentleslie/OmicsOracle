import unittest
from unittest.mock import patch, MagicMock, call
from omics_oracle.gradio_interface import create_styled_interface, process_query, format_response
from omics_oracle.query_manager import QueryManager

class TestGradioInterface(unittest.TestCase):
    @patch('omics_oracle.gradio_interface.logger')
    def test_create_styled_interface(self, mock_logger):
        mock_query_manager = MagicMock(spec=QueryManager)

        interface = create_styled_interface(mock_query_manager)

        self.assertIsNotNone(interface, "The created interface should not be None")

        # Check if the logs contain the appropriate messages
        mock_logger.debug.assert_has_calls([
            call("Creating styled Gradio interface"),
            call("Styled Gradio interface created successfully")
        ], any_order=False)

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

        # Updated expected log messages to match the new logging calls
        expected_calls = [
            call("Received query: Test query"),
            call("Starting to process the query with QueryManager..."),
            call(f"QueryManager returned response: {mock_query_manager.process_query.return_value}"),
            call(f"Formatting response: {mock_query_manager.process_query.return_value}"),
            call(f"Formatted response: {expected_result}")
        ]
        mock_logger.debug.assert_has_calls(expected_calls, any_order=False)

    @patch('omics_oracle.gradio_interface.logger')
    def test_process_query_unexpected_error(self, mock_logger):
        mock_query_manager = MagicMock(spec=QueryManager)
        mock_query_manager.process_query.side_effect = Exception("Unexpected error")

        result = process_query("Query causing unexpected error", mock_query_manager)

        self.assertTrue(result.startswith("An unexpected error occurred. Please try again later. If the problem persists, contact support. Details: Unexpected error"))

        # Updated expected log message to match the new error log format
        mock_logger.error.assert_called_once()
        error_log = mock_logger.error.call_args[0][0]
        self.assertIn("Exception while processing query: Unexpected error", error_log)
        self.assertIn("Traceback", error_log)

    @patch('omics_oracle.gradio_interface.logger')
    def test_process_query_value_error(self, mock_logger):
        mock_query_manager = MagicMock(spec=QueryManager)
        mock_query_manager.process_query.side_effect = ValueError("Invalid query format")

        result = process_query("Invalid query", mock_query_manager)

        expected_result = "An error occurred: Invalid query format"
        self.assertEqual(result, expected_result)

        # Updated the expected log message to match the new log format
        mock_logger.error.assert_called_once()
        error_log = mock_logger.error.call_args[0][0]
        self.assertIn("ValueError while processing query: Invalid query format", error_log)
        self.assertIn("Traceback", error_log)

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

    @unittest.skip("Skipping submit button test as it is better suited for integration testing.")
    @patch('omics_oracle.gradio_interface.logger')
    @patch('omics_oracle.gradio_interface.process_query')
    def test_submit_button_debugging(self, mock_process_query, mock_logger):
        pass

if __name__ == '__main__':
    unittest.main()

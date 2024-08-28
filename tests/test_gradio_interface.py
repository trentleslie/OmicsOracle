import unittest
from unittest.mock import patch, MagicMock
from omics_oracle.gradio_interface import create_interface

class TestGradioInterface(unittest.TestCase):
    @patch('omics_oracle.gradio_interface.gr')
    def test_create_interface(self, mock_gr):
        mock_query_manager = MagicMock()
        mock_query_manager.process_query.return_value = {
            'original_query': 'Test query',
            'gemini_interpretation': 'Interpreted query',
            'aql_query': 'TEST AQL',
            'spoke_results': [{"id": "123", "name": "Result1"}],
            'final_interpretation': 'Final result'
        }

        create_interface(mock_query_manager)

        mock_gr.Interface.assert_called_once()
        interface_call = mock_gr.Interface.call_args
        self.assertIn('fn', interface_call[1])
        self.assertIn('inputs', interface_call[1])
        self.assertIn('outputs', interface_call[1])

        # Test the process_query function
        process_query_fn = interface_call[1]['fn']
        result = process_query_fn("Test query")
        self.assertIn('Original Query: Test query', result)
        self.assertIn('Gemini Interpretation: Interpreted query', result)
        self.assertIn('AQL Query: TEST AQL', result)
        self.assertIn("Spoke Results: [{'id': '123', 'name': 'Result1'}]", result)
        self.assertIn('Final Interpretation: Final result', result)

if __name__ == '__main__':
    unittest.main()
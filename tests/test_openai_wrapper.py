import unittest
from unittest.mock import patch, MagicMock
from omics_oracle.openai_wrapper import OpenAIWrapper
from prompts import base_prompt

class TestOpenAIWrapper(unittest.TestCase):

    @patch('omics_oracle.openai_wrapper.OpenAI')
    @patch('omics_oracle.openai_wrapper.load_dotenv')
    @patch('omics_oracle.openai_wrapper.os.getenv')
    def setUp(self, mock_getenv, mock_load_dotenv, mock_openai):
        mock_getenv.return_value = "test_api_key"
        self.mock_openai = mock_openai
        self.wrapper = OpenAIWrapper()
        self.mock_openai.assert_called_once_with(api_key="test_api_key")

    def test_initialization(self):
        self.assertEqual(self.wrapper.model, "gpt-4")

    def test_send_query(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        self.wrapper.client.chat.completions.create.return_value = mock_response

        query = "Test query"
        response = self.wrapper.send_query(query)

        self.wrapper.client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[
                {"role": "system", "content": base_prompt},
                {"role": "user", "content": query}
            ]
        )
        self.assertEqual(response, "Test response")

    def test_send_query_error(self):
        self.wrapper.client.chat.completions.create.side_effect = Exception("API Error")

        query = "Test query"
        response = self.wrapper.send_query(query)

        self.assertIsNone(response)

    def test_generate_aql(self):
        self.wrapper.send_query = MagicMock(return_value="Generated AQL")

        query = "Generate AQL for test"
        response = self.wrapper.generate_aql(query)

        self.wrapper.send_query.assert_called_once_with(query)
        self.assertEqual(response, "Generated AQL")

if __name__ == '__main__':
    unittest.main()
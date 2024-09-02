import pytest
from unittest.mock import patch, MagicMock
from omics_oracle.openai_wrapper import OpenAIWrapper

# Mock base prompt
mock_base_prompt = "Mocked base prompt for testing"

class TestOpenAIWrapper:

    @patch('omics_oracle.openai_wrapper.OpenAI')
    @patch('omics_oracle.openai_wrapper.load_dotenv')
    @patch('omics_oracle.openai_wrapper.os.getenv')
    def setup_method(self, method, mock_getenv, mock_load_dotenv, mock_openai):
        mock_getenv.return_value = "test_api_key"
        self.mock_openai = mock_openai
        self.wrapper = OpenAIWrapper(base_prompt=mock_base_prompt)
        self.mock_openai.assert_called_once_with(api_key="test_api_key")

    def test_initialization(self):
        assert isinstance(self.wrapper, OpenAIWrapper)
        assert self.wrapper.model == "gpt-4o"
        assert self.wrapper.base_prompt == mock_base_prompt

    def test_send_query(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        self.wrapper.client.chat.completions.create.return_value = mock_response

        query = "Test query"
        response = self.wrapper.send_query(query)

        self.wrapper.client.chat.completions.create.assert_called_once_with(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": mock_base_prompt},
                {"role": "user", "content": query}
            ]
        )
        assert response == "Test response"

    def test_send_query_error(self):
        self.wrapper.client.chat.completions.create.side_effect = Exception("API Error")

        query = "Test query"
        response = self.wrapper.send_query(query)

        assert response is None

    def test_generate_aql(self):
        self.wrapper.send_query = MagicMock(return_value="Generated AQL")

        query = "Generate AQL for test"
        response = self.wrapper.generate_aql(query)

        self.wrapper.send_query.assert_called_once_with(query)
        assert response == "Generated AQL"

if __name__ == '__main__':
    pytest.main()
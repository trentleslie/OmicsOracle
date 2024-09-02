import pytest
from unittest.mock import patch, MagicMock, call
from omics_oracle.openai_wrapper import OpenAIWrapper

# Mock base prompt
mock_base_prompt = "Mocked base prompt for testing"

class TestOpenAIWrapper:

    @patch('omics_oracle.openai_wrapper.OpenAI')
    @patch('omics_oracle.openai_wrapper.load_dotenv')
    @patch('omics_oracle.openai_wrapper.os.getenv')
    @patch('omics_oracle.openai_wrapper.logging.getLogger')
    def setup_method(self, method, mock_get_logger, mock_getenv, mock_load_dotenv, mock_openai):
        mock_getenv.return_value = "test_api_key"
        self.mock_openai = mock_openai
        self.mock_logger = MagicMock()
        mock_get_logger.return_value = self.mock_logger
        self.wrapper = OpenAIWrapper(base_prompt=mock_base_prompt)
        self.mock_openai.assert_called_once_with(api_key="test_api_key")

    def test_initialization(self):
        assert isinstance(self.wrapper, OpenAIWrapper)
        assert self.wrapper.model == "gpt-4o"
        assert self.wrapper.base_prompt == mock_base_prompt
        self.mock_logger.info.assert_called_with("OpenAIWrapper initialized successfully")

    def test_load_environment(self):
        with patch('omics_oracle.openai_wrapper.os.path.dirname') as mock_dirname:
            mock_dirname.return_value = '/mock/path'
            with patch('omics_oracle.openai_wrapper.load_dotenv', return_value=True) as mock_load_dotenv:
                with patch('omics_oracle.openai_wrapper.os.getenv', return_value='fake_api_key') as mock_getenv:
                    self.wrapper._load_environment()
        
        mock_load_dotenv.assert_called_once_with('/mock/path/../.env')
        mock_getenv.assert_called_once_with('OPENAI_API_KEY')
        self.mock_logger.info.assert_has_calls([
            call("Looking for .env file at: /mock/path/../.env"),
            call("Successfully loaded .env file")
        ])
        assert self.wrapper.api_key == 'fake_api_key'

    def test_load_environment_error(self):
        with patch('omics_oracle.openai_wrapper.os.path.dirname') as mock_dirname:
            mock_dirname.return_value = '/mock/path'
            with patch('omics_oracle.openai_wrapper.load_dotenv', return_value=False) as mock_load_dotenv:
                with pytest.raises(ValueError, match="Failed to load .env file"):
                    self.wrapper._load_environment()
        
        mock_load_dotenv.assert_called_once_with('/mock/path/../.env')
        assert self.mock_logger.error.call_count == 2
        error_logs = [call.args[0] for call in self.mock_logger.error.call_args_list]
        assert "Failed to load .env file" in error_logs[0]
        assert "Error loading environment: Failed to load .env file" in error_logs[1]
        assert "Traceback" in error_logs[1]

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
        self.mock_logger.debug.assert_has_calls([
            call("Sending query to OpenAI: Test query"),
            call("OpenAI response received: Test response")
        ])

    def test_send_query_error(self):
        self.wrapper.client.chat.completions.create.side_effect = Exception("API Error")

        query = "Test query"
        response = self.wrapper.send_query(query)

        assert response is None
        self.mock_logger.error.assert_called_once()
        error_log = self.mock_logger.error.call_args[0][0]
        assert "Error in OpenAI API call: API Error" in error_log
        assert "Traceback" in error_log

    def test_generate_aql(self):
        self.wrapper.send_query = MagicMock(return_value="Generated AQL")

        query = "Generate AQL for test"
        response = self.wrapper.generate_aql(query)

        self.wrapper.send_query.assert_called_once_with(query)
        assert response == "Generated AQL"
        self.mock_logger.debug.assert_has_calls([
            call("Generating AQL for query: Generate AQL for test"),
            call("Generated AQL: Generated AQL")
        ])

    def test_generate_aql_error(self):
        self.wrapper.send_query = MagicMock(side_effect=Exception("AQL Generation Error"))

        query = "Generate AQL for test"
        response = self.wrapper.generate_aql(query)

        assert response is None
        self.mock_logger.error.assert_called_once()
        error_log = self.mock_logger.error.call_args[0][0]
        assert "Error generating AQL: AQL Generation Error" in error_log
        assert "Traceback" in error_log

if __name__ == '__main__':
    pytest.main()
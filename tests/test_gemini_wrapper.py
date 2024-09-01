import pytest
from unittest.mock import Mock, patch
from omics_oracle.gemini_wrapper import GeminiWrapper

@pytest.fixture
def gemini_wrapper():
    with patch('omics_oracle.gemini_wrapper.load_dotenv', return_value=True):
        with patch.dict('os.environ', {
            'GEMINI_AUTH': 'test_key',
            'GEMINI_URL': 'https://test.api.com'
        }):
            return GeminiWrapper()

def test_send_query(gemini_wrapper):
    with patch('omics_oracle.gemini_wrapper.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_post.return_value = mock_response

        response = gemini_wrapper.send_query("Test query", context="general")
        
        assert response == {"choices": [{"message": {"content": "Test response"}}]}
        mock_post.assert_called_once()

def test_interpret_response(gemini_wrapper):
    response = {"choices": [{"message": {"content": "Test content"}}]}
    result = gemini_wrapper.interpret_response(response)
    assert result == "Test content"

def test_generate_aql_query(gemini_wrapper):
    with patch.object(gemini_wrapper, 'send_query') as mock_send_query:
        mock_send_query.return_value = {"choices": [{"message": {"content": "AQL: FOR doc IN collection RETURN doc"}}]}
        
        aql_query = gemini_wrapper.generate_aql_query("Find all documents")
        
        assert aql_query == "FOR doc IN collection RETURN doc"
        mock_send_query.assert_called_once_with("Find all documents", context="aql_generation")

def test_interpret_spoke_results(gemini_wrapper):
    with patch.object(gemini_wrapper, 'send_query') as mock_send_query:
        mock_send_query.return_value = {"choices": [{"message": {"content": "Interpretation of results"}}]}
        
        interpretation = gemini_wrapper.interpret_spoke_results([{"result": "data"}], "Original query")
        
        assert interpretation == "Interpretation of results"
        mock_send_query.assert_called_once()

def test_error_handling(gemini_wrapper):
    with patch('omics_oracle.gemini_wrapper.requests.post') as mock_post:
        mock_post.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            gemini_wrapper.send_query("Test query")

def test_load_environment_failure():
    with patch('omics_oracle.gemini_wrapper.load_dotenv', return_value=False):
        with pytest.raises(ValueError, match="Failed to load .env file"):
            GeminiWrapper()

def test_missing_environment_variables():
    with patch('omics_oracle.gemini_wrapper.load_dotenv', return_value=True):
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_AUTH and GEMINI_URL must be set in the .env file"):
                GeminiWrapper()

# Add more tests as needed to cover edge cases and error scenarios
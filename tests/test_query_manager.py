import pytest
from unittest.mock import Mock, patch
from omics_oracle.query_manager import QueryManager

@pytest.fixture
def query_manager():
    mock_gemini_wrapper = Mock()
    mock_spoke_wrapper = Mock()
    return QueryManager(gemini_wrapper=mock_gemini_wrapper, spoke_wrapper=mock_spoke_wrapper)

def test_process_query(query_manager):
    # Mock the GeminiWrapper and SpokeWrapper responses
    query_manager.gemini.send_query.return_value = {"choices": [{"message": {"content": "Interpreted query"}}]}
    query_manager.gemini.interpret_response.side_effect = ["AQL: FOR doc IN collection RETURN doc", "Final interpretation"]
    query_manager.spoke.execute_aql.return_value = [{"result": "data"}]

    result = query_manager.process_query("Test biomedical query")

    assert result["original_query"] == "Test biomedical query"
    assert result["gemini_interpretation"] == "AQL: FOR doc IN collection RETURN doc"
    assert result["aql_query"] == "FOR doc IN collection RETURN doc"
    assert result["spoke_results"] == [{"result": "data"}]
    assert result["final_interpretation"] == "Final interpretation"

def test_process_query_no_aql(query_manager):
    # Test the scenario where no AQL query is generated
    query_manager.gemini.send_query.return_value = {"choices": [{"message": {"content": "No AQL generated"}}]}
    query_manager.gemini.interpret_response.return_value = "No AQL found"

    result = query_manager.process_query("Invalid biomedical query")

    assert result["aql_query"] == ""
    assert result["spoke_results"] == []

def test_error_handling(query_manager):
    # Test error handling in the process_query method
    query_manager.gemini.send_query.side_effect = Exception("API Error")

    with pytest.raises(Exception):
        query_manager.process_query("Test query")

def test_extract_aql_from_response(query_manager):
    aql_query = query_manager.extract_aql_from_response("Some text AQL: FOR doc IN collection RETURN doc")
    assert aql_query == "FOR doc IN collection RETURN doc"

    no_aql = query_manager.extract_aql_from_response("No AQL in this response")
    assert no_aql == ""

# Add more tests as needed to cover edge cases and error scenarios
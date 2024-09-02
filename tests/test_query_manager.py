import pytest
from unittest.mock import Mock, patch
from omics_oracle.query_manager import QueryManager

@pytest.fixture
def query_manager():
    mock_spoke_wrapper = Mock()
    return QueryManager(spoke_wrapper=mock_spoke_wrapper)

def test_process_query(query_manager):
    # Mock the SpokeWrapper response
    query_manager.spoke.execute_aql.return_value = [{"result": "data"}]

    result = query_manager.process_query("Test biomedical query")

    assert result["original_query"] == "Test biomedical query"
    assert "aql_query" in result
    assert result["spoke_results"] == [{"result": "data"}]
    assert "interpretation" in result

def test_process_query_no_aql(query_manager):
    # Test the scenario where no AQL query is generated
    with patch.object(QueryManager, 'convert_to_aql', return_value=""):
        result = query_manager.process_query("Invalid biomedical query")

        assert result["aql_query"] == ""
        assert result["spoke_results"] == []

def test_error_handling(query_manager):
    # Test error handling in the process_query method
    with patch.object(QueryManager, 'convert_to_aql', side_effect=Exception("Conversion Error")):
        with pytest.raises(Exception):
            query_manager.process_query("Test query")

def test_convert_to_aql(query_manager):
    aql_query = query_manager.convert_to_aql("Test biomedical query")
    assert isinstance(aql_query, str)
    assert len(aql_query) > 0

def test_interpret_results(query_manager):
    interpretation = query_manager.interpret_results([{"result": "data"}], "Test query")
    assert isinstance(interpretation, str)
    assert "Found 1 results" in interpretation

# Add more tests as needed to cover edge cases and error scenarios
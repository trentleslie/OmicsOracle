import pytest
from unittest.mock import Mock, patch, MagicMock
from omics_oracle.query_manager import QueryManager
from omics_oracle.openai_wrapper import OpenAIWrapper

class RunnableMock(MagicMock):
    def __instancecheck__(self, instance):
        return True

@pytest.fixture
def mock_openai():
    with patch('omics_oracle.query_manager.ChatOpenAI', new_callable=RunnableMock) as mock_chat_openai:
        mock_chat_openai.return_value.invoke.return_value.content = "Mocked response"
        yield mock_chat_openai

@pytest.fixture
def query_manager(mock_openai):
    mock_spoke_wrapper = Mock()
    mock_openai_wrapper = Mock(spec=OpenAIWrapper)
    mock_openai_wrapper.api_key = "test_api_key"
    with patch('omics_oracle.query_manager.ArangoClient'), \
         patch('omics_oracle.query_manager.ArangoGraph'), \
         patch('omics_oracle.query_manager.ArangoGraphQAChain'):
        return QueryManager(spoke_wrapper=mock_spoke_wrapper, openai_wrapper=mock_openai_wrapper)

def test_process_query(query_manager):
    # Mock the SpokeWrapper response
    query_manager.spoke.execute_aql.return_value = [{"result": "data"}]
    
    # Mock the ArangoGraphQAChain response
    query_manager.qa_chain.invoke.return_value = {"result": "mocked AQL result"}

    result = query_manager.process_query("Test biomedical query")

    assert result["original_query"] == "Test biomedical query"
    assert "aql_result" in result
    assert "interpretation" in result
    assert "attempt_count" in result

def test_process_query_no_result(query_manager):
    # Test the scenario where no AQL result is generated
    query_manager.qa_chain.invoke.return_value = {"result": ""}

    result = query_manager.process_query("Invalid biomedical query")

    assert result["aql_result"] == []
    assert result["interpretation"] == "No interpretation available."
    assert result["attempt_count"] == 3  # Max attempts

def test_error_handling(query_manager):
    # Test error handling in the process_query method
    query_manager.qa_chain.invoke.side_effect = Exception("Test error")

    result = query_manager.process_query("Test query")

    assert "error" in result
    assert "An error occurred: Test error" in result["error"]

def test_execute_aql(query_manager):
    query_manager.qa_chain.invoke.return_value = {"result": "mocked AQL result"}
    
    result = query_manager.execute_aql("Test AQL query")
    
    assert "captured_output" in result

def test_interpret_aql_result(query_manager):
    aql_result = [{"gene": "GENE1", "pathway": "PATHWAY1"}]
    interpretation = query_manager.interpret_aql_result(aql_result)
    
    assert isinstance(interpretation, str)
    assert len(interpretation) > 0

# Add more tests as needed to cover edge cases and error scenarios
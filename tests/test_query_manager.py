import pytest
from unittest.mock import Mock, patch, MagicMock, call
from omics_oracle.query_manager import QueryManager
from omics_oracle.openai_wrapper import OpenAIWrapper
from omics_oracle.prompts import base_prompt

def truncate(text: str, max_length: int = 100) -> str:
    return text[:max_length] + "..." if len(text) > max_length else text

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
         patch('omics_oracle.query_manager.ArangoGraphQAChain'), \
         patch('omics_oracle.query_manager.setup_logger') as mock_setup_logger:
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        return QueryManager(spoke_wrapper=mock_spoke_wrapper, openai_wrapper=mock_openai_wrapper)

def test_process_query(query_manager):
    query_manager.spoke.execute_aql.return_value = [{"result": "data"}]
    query_manager.qa_chain.invoke.return_value = {"result": "mocked AQL result"}

    result = query_manager.process_query("Test biomedical query")

    assert result["original_query"] == "Test biomedical query"
    assert "aql_result" in result
    assert "interpretation" in result
    assert "attempt_count" in result

    full_query = f"Test biomedical query{base_prompt}"
    expected_calls = [
        call(f"Full query: {truncate(full_query)}"),
        call("Attempt 1: Executing query..."),
        call(f"Starting sequential chain for query: {truncate(full_query)}"),
        call(f"Attempting to execute AQL query: {truncate(full_query)}"),
        call("AQL query execution output: {'result': 'mocked AQL result'}"),
        call("Extracting AQL result from captured output"),
        call("No AQL result found in captured output"),
        call("Attempt - No AQL result found."),
        call("Sequential chain completed. Final response: {'aql_result': []}"),
        call("Attempt 1 - AQL Result: []"),
        call("Attempt 1 - No AQL result found."),
    ]
    query_manager.logger.debug.assert_has_calls(expected_calls, any_order=True)

def test_process_query_no_result(query_manager):
    query_manager.qa_chain.invoke.return_value = {"result": ""}

    result = query_manager.process_query("Invalid biomedical query")

    assert result["aql_result"] == []
    assert result["interpretation"] == "No interpretation available."
    assert result["attempt_count"] == 3  # Max attempts

    full_query = f"Invalid biomedical query{base_prompt}"
    failure_message = "The prior AQL query failed to return results. Please think this through step by step and refine your AQL statement. The original question is as follows:"

    expected_calls = [
        call(f"Full query: {truncate(full_query)}"),
        call("Attempt 1: Executing query..."),
        call(f"Starting sequential chain for query: {truncate(full_query)}"),
        call(f"Attempting to execute AQL query: {truncate(full_query)}"),
        call("Attempt - No AQL result found."),
        call("Sequential chain completed. Final response: {'aql_result': []}"),
        call("Attempt 1 - AQL Result: []"),
        call("Attempt 1 - No AQL result found."),
        call(f"Refined query for next attempt: {truncate(failure_message + ' ' + full_query)}"),
        call("Attempt 2: Executing query..."),
        call(f"Starting sequential chain for query: {truncate(failure_message + ' ' + full_query)}"),
        call(f"Attempting to execute AQL query: {truncate(failure_message + ' ' + full_query)}"),
        call("Attempt - No AQL result found."),
        call("Sequential chain completed. Final response: {'aql_result': []}"),
        call("Attempt 2 - AQL Result: []"),
        call("Attempt 2 - No AQL result found."),
        call(f"Refined query for next attempt: {truncate(failure_message + ' ' + failure_message + ' ' + full_query)}"),
        call("Attempt 3: Executing query..."),
        call(f"Starting sequential chain for query: {truncate(failure_message + ' ' + failure_message + ' ' + full_query)}"),
        call(f"Attempting to execute AQL query: {truncate(failure_message + ' ' + failure_message + ' ' + full_query)}"),
        call("Attempt - No AQL result found."),
        call("Sequential chain completed. Final response: {'aql_result': []}"),
        call("Attempt 3 - AQL Result: []"),
        call("Attempt 3 - No AQL result found."),
    ]
    query_manager.logger.debug.assert_has_calls(expected_calls, any_order=True)

def test_error_handling(query_manager):
    query_manager.qa_chain.invoke.side_effect = Exception("Test error")

    result = query_manager.process_query("Test query")

    assert "error" in result
    assert "An error occurred: Error in attempt 1: Error executing AQL query: Test error" in result["error"]

    query_manager.logger.error.assert_called_with("Error in attempt 1: Error executing AQL query: Test error")

def test_execute_aql(query_manager):
    mock_result = {"result": "mocked AQL result"}
    query_manager.qa_chain.invoke.return_value = mock_result

    result = query_manager.execute_aql("Test AQL query")

    assert "captured_output" in result
    assert str(mock_result) in result["captured_output"]

    query_manager.logger.debug.assert_has_calls([
        call(f"Attempting to execute AQL query: {truncate('Test AQL query')}"),
        call(f"AQL query execution output: {str(mock_result)}")
    ], any_order=True)

def test_interpret_aql_result(query_manager):
    aql_result = [{"gene": "GENE1", "pathway": "PATHWAY1"}]
    interpretation = query_manager.interpret_aql_result(aql_result)
    
    assert isinstance(interpretation, str)
    assert len(interpretation) > 0

    query_manager.logger.debug.assert_has_calls([
        call("Interpreting AQL result"),
        call(f"LLM interpretation: {truncate(interpretation)}")
    ], any_order=True)

# Add more tests as needed to cover edge cases and error scenarios
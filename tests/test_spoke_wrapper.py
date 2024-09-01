import pytest
from unittest.mock import Mock, patch, MagicMock
from omics_oracle.spoke_wrapper import SpokeWrapper

@pytest.fixture
def mock_pyarango_connection():
    with patch('omics_oracle.spoke_wrapper.Connection') as mock_connection:
        mock_db = MagicMock()
        mock_connection.return_value.__getitem__.return_value = mock_db
        yield mock_connection

@pytest.fixture
def spoke_wrapper(mock_pyarango_connection):
    with patch('omics_oracle.spoke_wrapper.load_dotenv', return_value=True):
        with patch.dict('os.environ', {
            'ARANGO_HOST': 'test_host',
            'ARANGO_DB': 'test_db',
            'ARANGO_USERNAME': 'test_user',
            'ARANGO_PASSWORD': 'test_pass'
        }):
            return SpokeWrapper()

def test_list_collections(spoke_wrapper):
    spoke_wrapper.db.collections = {"collection1": Mock(), "collection2": Mock()}
    
    result = spoke_wrapper.list_collections()
    
    assert result == ["collection1", "collection2"]

def test_execute_aql(spoke_wrapper):
    mock_aql_query = MagicMock()
    mock_aql_query.return_value = [{"result": "data"}]
    spoke_wrapper.db.AQLQuery = mock_aql_query

    result = spoke_wrapper.execute_aql("FOR doc IN collection RETURN doc")

    assert result == [{"result": "data"}]
    mock_aql_query.assert_called_once_with("FOR doc IN collection RETURN doc", bindVars=None, rawResults=True)

def test_get_entity(spoke_wrapper):
    mock_collection = MagicMock()
    mock_collection.__getitem__.return_value = {"_key": "test_key", "name": "Test Entity"}
    spoke_wrapper.db.__getitem__ = MagicMock(return_value=mock_collection)

    entity = spoke_wrapper.get_entity("test_collection", "test_key")

    assert entity == {"_key": "test_key", "name": "Test Entity"}
    spoke_wrapper.db.__getitem__.assert_called_once_with("test_collection")
    mock_collection.__getitem__.assert_called_once_with("test_key")

def test_get_connected_entities(spoke_wrapper):
    mock_aql_query = MagicMock()
    mock_aql_query.return_value = [
        {"entity": {"id": "connected_id", "name": "Connected Entity"}, "edge": {"label": "TEST_EDGE"}}
    ]
    spoke_wrapper.db.AQLQuery = mock_aql_query

    connected_entities = spoke_wrapper.get_connected_entities("test_id", edge_label="TEST_EDGE")

    assert len(connected_entities) == 1
    assert connected_entities[0]["entity"]["name"] == "Connected Entity"
    mock_aql_query.assert_called_once()
    call_args = mock_aql_query.call_args
    assert "FOR v, e IN 1..1 OUTBOUND @start_id @@edge_collection" in call_args[0][0]
    assert call_args[1]['bindVars']['start_id'] == "test_id"
    assert call_args[1]['bindVars']['edge_label'] == "TEST_EDGE"

def test_traverse_graph(spoke_wrapper):
    mock_aql_query = MagicMock()
    mock_aql_query.return_value = [
        {"vertices": ["v1", "v2"], "edges": ["e1"]}
    ]
    spoke_wrapper.db.AQLQuery = mock_aql_query

    traversal_result = spoke_wrapper.traverse_graph("start_id", max_depth=2, edge_label="TEST_EDGE")

    assert len(traversal_result) == 1
    assert traversal_result[0]["vertices"] == ["v1", "v2"]
    assert traversal_result[0]["edges"] == ["e1"]
    mock_aql_query.assert_called_once()
    call_args = mock_aql_query.call_args
    assert "FOR v, e, p IN 1..@max_depth OUTBOUND @start_id @@edge_collection" in call_args[0][0]
    assert call_args[1]['bindVars']['start_id'] == "start_id"
    assert call_args[1]['bindVars']['max_depth'] == 2
    assert call_args[1]['bindVars']['edge_label'] == "TEST_EDGE"

def test_error_handling_execute_aql(spoke_wrapper):
    spoke_wrapper.db.AQLQuery.side_effect = Exception("Database Error")

    result = spoke_wrapper.execute_aql("Invalid query")

    assert result == []
    spoke_wrapper.db.AQLQuery.assert_called_once_with("Invalid query", bindVars=None, rawResults=True)

def test_error_handling_get_entity(spoke_wrapper):
    spoke_wrapper.db.__getitem__ = MagicMock(side_effect=Exception("Collection not found"))

    result = spoke_wrapper.get_entity("non_existent_collection", "test_key")

    assert result is None
    spoke_wrapper.db.__getitem__.assert_called_once_with("non_existent_collection")

def test_load_environment_failure():
    with patch('omics_oracle.spoke_wrapper.load_dotenv', return_value=False):
        with pytest.raises(ValueError, match="Failed to load .env file"):
            SpokeWrapper()

def test_missing_environment_variables():
    with patch('omics_oracle.spoke_wrapper.load_dotenv', return_value=True):
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="ARANGO_HOST, ARANGO_DB, ARANGO_USERNAME, and ARANGO_PASSWORD must be set in the .env file"):
                SpokeWrapper()

# Add more tests as needed to cover edge cases and error scenarios
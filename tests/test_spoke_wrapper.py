import pytest
from unittest.mock import Mock, patch, MagicMock
from omics_oracle.spoke_wrapper import SpokeWrapper

@pytest.fixture
def mock_arango_client():
    with patch('omics_oracle.spoke_wrapper.ArangoClient') as mock_client:
        mock_db = Mock()
        mock_client.return_value.db.return_value = mock_db
        yield mock_client

@pytest.fixture
def spoke_wrapper(mock_arango_client):
    return SpokeWrapper(host="test_host", db_name="test_db", username="test_user", password="test_pass")

def test_list_collections(spoke_wrapper):
    spoke_wrapper.db.collections.return_value = ["collection1", "collection2"]
    
    result = spoke_wrapper.list_collections()
    
    assert result == ["collection1", "collection2"]
    spoke_wrapper.db.collections.assert_called_once()

def test_execute_aql(spoke_wrapper):
    mock_cursor = MagicMock()
    mock_cursor.__iter__.return_value = [{"result": "data"}]
    spoke_wrapper.db.aql.execute.return_value = mock_cursor

    result = spoke_wrapper.execute_aql("FOR doc IN collection RETURN doc")

    assert result == [{"result": "data"}]
    spoke_wrapper.db.aql.execute.assert_called_once_with("FOR doc IN collection RETURN doc", bind_vars=None, count=True)

def test_get_entity(spoke_wrapper):
    mock_collection = MagicMock()
    mock_collection.get.return_value = {"_key": "test_key", "name": "Test Entity"}
    spoke_wrapper.db.collection.return_value = mock_collection

    entity = spoke_wrapper.get_entity("test_collection", "test_key")

    assert entity == {"_key": "test_key", "name": "Test Entity"}
    spoke_wrapper.db.collection.assert_called_once_with("test_collection")
    mock_collection.get.assert_called_once_with("test_key")

def test_get_connected_entities(spoke_wrapper):
    mock_cursor = MagicMock()
    mock_cursor.__iter__.return_value = [
        {"entity": {"id": "connected_id", "name": "Connected Entity"}, "edge": {"label": "TEST_EDGE"}}
    ]
    spoke_wrapper.db.aql.execute.return_value = mock_cursor

    connected_entities = spoke_wrapper.get_connected_entities("test_id", edge_label="TEST_EDGE")

    assert len(connected_entities) == 1
    assert connected_entities[0]["entity"]["name"] == "Connected Entity"
    spoke_wrapper.db.aql.execute.assert_called_once()
    call_args = spoke_wrapper.db.aql.execute.call_args
    assert "FOR v, e IN 1..1 OUTBOUND @start_id @@edge_collection" in call_args[0][0]
    assert call_args[1]['bind_vars']['start_id'] == "test_id"
    assert call_args[1]['bind_vars']['edge_label'] == "TEST_EDGE"

def test_traverse_graph(spoke_wrapper):
    mock_cursor = MagicMock()
    mock_cursor.__iter__.return_value = [
        {"vertices": ["v1", "v2"], "edges": ["e1"]}
    ]
    spoke_wrapper.db.aql.execute.return_value = mock_cursor

    traversal_result = spoke_wrapper.traverse_graph("start_id", max_depth=2, edge_label="TEST_EDGE")

    assert len(traversal_result) == 1
    assert traversal_result[0]["vertices"] == ["v1", "v2"]
    assert traversal_result[0]["edges"] == ["e1"]
    spoke_wrapper.db.aql.execute.assert_called_once()
    call_args = spoke_wrapper.db.aql.execute.call_args
    assert "FOR v, e, p IN 1..@max_depth OUTBOUND @start_id @@edge_collection" in call_args[0][0]
    assert call_args[1]['bind_vars']['start_id'] == "start_id"
    assert call_args[1]['bind_vars']['max_depth'] == 2
    assert call_args[1]['bind_vars']['edge_label'] == "TEST_EDGE"

def test_error_handling_execute_aql(spoke_wrapper):
    spoke_wrapper.db.aql.execute.side_effect = Exception("Database Error")

    result = spoke_wrapper.execute_aql("Invalid query")

    assert result == []
    spoke_wrapper.db.aql.execute.assert_called_once_with("Invalid query", bind_vars=None, count=True)

def test_error_handling_get_entity(spoke_wrapper):
    spoke_wrapper.db.collection.side_effect = Exception("Collection not found")

    result = spoke_wrapper.get_entity("non_existent_collection", "test_key")

    assert result is None
    spoke_wrapper.db.collection.assert_called_once_with("non_existent_collection")

# Add more tests as needed to cover edge cases and error scenarios
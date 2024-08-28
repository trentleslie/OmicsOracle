import pytest
from unittest.mock import Mock, patch, MagicMock
from omics_oracle.spoke_wrapper import SpokeWrapper, ArangoClient

@pytest.fixture
def mock_arango_client():
    with patch('omics_oracle.spoke_wrapper.ArangoClient') as mock_client:
        mock_db = Mock()
        mock_client.return_value.db.return_value = mock_db
        yield mock_client

@pytest.fixture
def spoke_wrapper(mock_arango_client):
    return SpokeWrapper(host="test_host", db_name="test_db", username="test_user", password="test_pass")

def test_execute_aql(spoke_wrapper):
    mock_cursor = MagicMock()
    mock_cursor.__iter__.return_value = [{"result": "data"}]
    spoke_wrapper.db.aql.execute.return_value = mock_cursor

    result = spoke_wrapper.execute_aql("FOR doc IN collection RETURN doc")

    assert result == [{"result": "data"}]
    spoke_wrapper.db.aql.execute.assert_called_once_with("FOR doc IN collection RETURN doc", bind_vars=None)

def test_get_entity_by_id(spoke_wrapper):
    mock_cursor = MagicMock()
    mock_cursor.__iter__.return_value = [{"id": "test_id", "name": "Test Entity"}]
    spoke_wrapper.db.aql.execute.return_value = mock_cursor

    entity = spoke_wrapper.get_entity_by_id("test_id")

    assert entity == {"id": "test_id", "name": "Test Entity"}
    spoke_wrapper.db.aql.execute.assert_called_once()

def test_get_connected_entities(spoke_wrapper):
    mock_cursor = MagicMock()
    mock_cursor.__iter__.return_value = [
        {"entity": {"id": "connected_id", "name": "Connected Entity"}, "edge": {"type": "TEST_EDGE"}}
    ]
    spoke_wrapper.db.aql.execute.return_value = mock_cursor

    connected_entities = spoke_wrapper.get_connected_entities("test_id", edge_label="TEST_EDGE")

    assert len(connected_entities) == 1
    assert connected_entities[0]["entity"]["name"] == "Connected Entity"
    spoke_wrapper.db.aql.execute.assert_called_once()

def test_error_handling(spoke_wrapper):
    spoke_wrapper.db.aql.execute.side_effect = Exception("Database Error")

    with pytest.raises(Exception):
        spoke_wrapper.execute_aql("Invalid query")

# Add more tests as needed to cover edge cases and error scenarios
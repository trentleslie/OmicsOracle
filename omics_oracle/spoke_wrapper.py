# omics_oracle/spoke_wrapper.py

from arango import ArangoClient
from arango.exceptions import ArangoError
from typing import Dict, Any, List
from .logger import setup_logger

class SpokeWrapper:
    def __init__(self, host: str, db_name: str, username: str, password: str):
        self.logger = setup_logger(__name__)
        try:
            self.client = ArangoClient(hosts=host)
            self.db = self.client.db(db_name, username=username, password=password)
            self.logger.info(f"Successfully connected to database: {db_name}")
        except ArangoError as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise

    def list_collections(self) -> List[str]:
        """
        List all collections in the database.

        Returns:
            List[str]: A list of collection names.
        """
        return list(self.db.collections())

    def execute_aql(self, aql_query: str, bind_vars: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute an AQL query against the Spoke knowledge graph.

        Args:
            aql_query (str): The AQL query to execute.
            bind_vars (Dict[str, Any], optional): Bind variables for the query. Defaults to None.

        Returns:
            List[Dict[str, Any]]: The query results as a list of dictionaries.
        """
        try:
            self.logger.info(f"Executing AQL query: {aql_query}")
            cursor = self.db.aql.execute(aql_query, bind_vars=bind_vars, count=True)
            results = list(cursor)
            self.logger.info(f"AQL query executed successfully. Retrieved {len(results)} results.")
            return results
        except Exception as e:
            self.logger.error(f"Error executing AQL query: {e}")
            return []

    def get_entity(self, collection: str, key: str) -> Dict[str, Any]:
        """
        Retrieve an entity from a specific collection by its key.

        Args:
            collection (str): The name of the collection.
            key (str): The key of the entity to retrieve.

        Returns:
            Dict[str, Any]: The entity data as a dictionary, or None if not found.
        """
        try:
            entity = self.db.collection(collection).get(key)
            if entity:
                self.logger.info(f"Successfully retrieved entity with key: {key} from collection: {collection}")
                return entity
            else:
                self.logger.warning(f"No entity found with key: {key} in collection: {collection}")
                return None
        except Exception as e:
            self.logger.error(f"Error retrieving entity with key {key} from collection {collection}: {e}")
            return None

    def get_connected_entities(self, start_id: str, edge_label: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve entities connected to a given entity, optionally filtered by edge label.

        Args:
            start_id (str): The ID of the entity to start from.
            edge_label (str, optional): The label of the edges to traverse. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of connected entities.
        """
        query = """
        FOR v, e IN 1..1 OUTBOUND @start_id @@edge_collection
        FILTER e.label == @edge_label
        RETURN {entity: v, edge: e}
        """
        bind_vars = {
            'start_id': start_id,
            '@edge_collection': 'Edges',
            'edge_label': edge_label
        }
        return self.execute_aql(query, bind_vars=bind_vars)

    def traverse_graph(self, start_id: str, max_depth: int = 2, edge_label: str = None) -> List[Dict[str, Any]]:
        """
        Traverse the graph starting from a given entity, up to a specified depth.

        Args:
            start_id (str): The ID of the entity to start from.
            max_depth (int, optional): The maximum depth to traverse. Defaults to 2.
            edge_label (str, optional): The label of the edges to traverse. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of traversed paths.
        """
        query = """
        FOR v, e, p IN 1..@max_depth OUTBOUND @start_id @@edge_collection
        FILTER @edge_label == null OR e.label == @edge_label
        RETURN {
            vertices: p.vertices[*]._key,
            edges: p.edges[*].label
        }
        """
        bind_vars = {
            'start_id': start_id,
            '@edge_collection': 'Edges',
            'max_depth': max_depth,
            'edge_label': edge_label
        }
        return self.execute_aql(query, bind_vars=bind_vars)
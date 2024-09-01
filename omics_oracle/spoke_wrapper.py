# omics_oracle/spoke_wrapper.py

import os
from dotenv import load_dotenv
from pyArango.connection import Connection
from typing import Dict, Any, List
import logging

class SpokeWrapper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_environment()
        self._connect_to_database()

    def _load_environment(self):
        """Load environment variables from .env file."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dotenv_path = os.path.join(current_dir, '..', '.env')
        self.logger.info(f"Looking for .env file at: {dotenv_path}")
        
        if load_dotenv(dotenv_path):
            self.logger.info("Successfully loaded .env file")
        else:
            self.logger.error("Failed to load .env file")
            raise ValueError("Failed to load .env file")

        self.host = os.getenv('ARANGO_HOST')
        self.db_name = os.getenv('ARANGO_DB')
        self.username = os.getenv('ARANGO_USERNAME')
        self.password = os.getenv('ARANGO_PASSWORD')

        if not all([self.host, self.db_name, self.username, self.password]):
            raise ValueError("ARANGO_HOST, ARANGO_DB, ARANGO_USERNAME, and ARANGO_PASSWORD must be set in the .env file")

    def _connect_to_database(self):
        """Connect to the ArangoDB database."""
        try:
            self.conn = Connection(arangoURL=self.host, username=self.username, password=self.password)
            self.db = self.conn[self.db_name]
            self.logger.info(f"Connected to database: {self.db_name}")
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise

    def list_collections(self) -> List[str]:
        """
        List all collections in the database.

        Returns:
            List[str]: A list of collection names.
        """
        return list(self.db.collections.keys())

    def execute_aql(self, query: str, bind_vars: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute an AQL query against the Spoke knowledge graph.

        Args:
            query (str): The AQL query to execute.
            bind_vars (Dict[str, Any], optional): Bind variables for the query. Defaults to None.

        Returns:
            List[Dict[str, Any]]: The query results as a list of dictionaries.
        """
        try:
            self.logger.info("Executing AQL query")
            self.logger.debug(f"AQL query: {query}")
            results = list(self.db.AQLQuery(query, bindVars=bind_vars, rawResults=True))
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
            entity = self.db[collection][key]
            self.logger.info(f"Successfully retrieved entity from collection: {collection}")
            return entity
        except Exception as e:
            self.logger.error(f"Failed to retrieve entity: {e}")
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
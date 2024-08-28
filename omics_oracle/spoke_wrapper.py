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

    def execute_aql(self, aql_query: str, bind_vars: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute an AQL query against the Spoke knowledge graph.

        Args:
            aql_query (str): The AQL query to execute.
            bind_vars (Dict[str, Any], optional): Bind variables for the query. Defaults to None.

        Returns:
            List[Dict[str, Any]]: The query results as a list of dictionaries.

        Raises:
            ArangoError: If there's an error executing the AQL query.
        """
        try:
            self.logger.info(f"Executing AQL query: {aql_query}")
            cursor = self.db.aql.execute(aql_query, bind_vars=bind_vars)
            results = [doc for doc in cursor]
            self.logger.info(f"AQL query executed successfully. Retrieved {len(results)} results.")
            return results
        except ArangoError as e:
            self.logger.error(f"Error executing AQL query: {e}")
            raise

    def get_entity_by_id(self, entity_id: str) -> Dict[str, Any]:
        """
        Retrieve an entity from the knowledge graph by its ID.

        Args:
            entity_id (str): The ID of the entity to retrieve.

        Returns:
            Dict[str, Any]: The entity data as a dictionary.
        """
        try:
            aql_query = f"RETURN DOCUMENT('{entity_id}')"
            results = self.execute_aql(aql_query)
            if results:
                self.logger.info(f"Successfully retrieved entity with ID: {entity_id}")
                return results[0]
            else:
                self.logger.warning(f"No entity found with ID: {entity_id}")
                return None
        except ArangoError as e:
            self.logger.error(f"Error retrieving entity with ID {entity_id}: {e}")
            raise

    def get_connected_entities(self, entity_id: str, edge_label: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve entities connected to a given entity, optionally filtered by edge label.

        Args:
            entity_id (str): The ID of the entity to start from.
            edge_label (str, optional): The label of the edges to traverse. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of connected entities.
        """
        try:
            aql_query = f"""
            FOR v, e, p IN 1..1 OUTBOUND '{entity_id}' GRAPH 'spoke'
            {f"FILTER e.label == '{edge_label}'" if edge_label else ""}
            RETURN {{entity: v, edge: e}}
            """
            results = self.execute_aql(aql_query)
            self.logger.info(f"Retrieved {len(results)} connected entities for entity ID: {entity_id}")
            return results
        except ArangoError as e:
            self.logger.error(f"Error retrieving connected entities for entity ID {entity_id}: {e}")
            raise
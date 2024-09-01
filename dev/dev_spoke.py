# %%
import logging
import os

from dotenv import load_dotenv
from pyArango.connection import Connection


# %%
class SpokeWrapper:
    def __init__(self):
        load_dotenv(os.path.join(os.getcwd(), '..', '.env'))
        
        self.host = os.getenv('ARANGO_HOST')
        self.db_name = os.getenv('ARANGO_DB')
        self.username = os.getenv('ARANGO_USERNAME')
        self.password = os.getenv('ARANGO_PASSWORD')
        
        try:
            self.conn = Connection(arangoURL=self.host, username=self.username, password=self.password)
            self.db = self.conn[self.db_name]
            logging.info(f"Connected to database: {self.db_name}")
        except Exception as e:
            logging.error(f"Failed to connect to database: {e}")
            raise

    def list_collections(self):
        return list(self.db.collections.keys())

    def execute_aql(self, query, bind_vars=None):
        try:
            return list(self.db.AQLQuery(query, bindVars=bind_vars, rawResults=True))
        except Exception as e:
            logging.error(f"AQL Query Error: {e}")
            return []

    def get_entity(self, collection, key):
        try:
            return self.db[collection][key]
        except Exception as e:
            logging.error(f"Failed to retrieve entity: {e}")
            return None

    def get_connected_entities(self, start_id, edge_label=None):
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

def test_spoke_wrapper():
    spoke = SpokeWrapper()
    
    logging.info("Listing all collections:")
    logging.info(spoke.list_collections())
    
    logging.info("\nFetching a single entity:")
    entity = spoke.get_entity('Nodes', '100005')  # Adjust the key if needed
    logging.info(entity)
    
    if entity:
        logging.info("\nFetching connected entities:")
        connected = spoke.get_connected_entities(entity._id, "PARTICIPATES_GpPW")
        logging.info(f"Number of connected entities: {len(connected)}")
        for item in connected[:5]:  # Print the first 5 connected entities
            logging.info(f"Entity: {item['entity']}")
            logging.info(f"Edge: {item['edge']}")
            logging.info("---")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_spoke_wrapper()


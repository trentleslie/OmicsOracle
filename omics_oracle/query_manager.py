# omics_oracle/query_manager.py

import json
import io
import re
from contextlib import redirect_stdout
from typing import Dict, List, Any
from arango import ArangoClient
from langchain_community.graphs import ArangoGraph
from langchain_openai import ChatOpenAI
from langchain.chains import ArangoGraphQAChain
from .logger import setup_logger
from .spoke_wrapper import SpokeWrapper
from .prompts import base_prompt
from .openai_wrapper import OpenAIWrapper

class QueryManager:
    def __init__(self, spoke_wrapper: SpokeWrapper, openai_wrapper: OpenAIWrapper):
        self.spoke = spoke_wrapper
        self.openai_wrapper = openai_wrapper
        self.logger = setup_logger(__name__)
        
        # Initialize ChatOpenAI
        try:
            self.llm = ChatOpenAI(temperature=0, model='gpt-4o', openai_api_key=self.openai_wrapper.api_key)
            self.logger.info("ChatOpenAI initialization successful!")
        except Exception as e:
            self.logger.error(f"ChatOpenAI initialization failed: {e}")
            raise

        # Initialize the ArangoDB client and connect to the database
        try:
            self.client = ArangoClient(hosts='http://127.0.0.1:8529')
            self.db = self.client.db('spoke23_human', username='root', password='ph')
            self.logger.info("ArangoDB connection successful!")
        except Exception as e:
            self.logger.error(f"ArangoDB connection failed: {e}")
            raise

        # Fetch the existing graph from the database
        try:
            self.graph = ArangoGraph(self.db)
            self.logger.info("ArangoGraph initialization successful!")
        except Exception as e:
            self.logger.error(f"ArangoGraph initialization failed: {e}")
            raise

        # Instantiate ArangoGraphQAChain
        try:
            self.qa_chain = ArangoGraphQAChain.from_llm(
                self.llm, 
                graph=self.graph, 
                verbose=True, 
                return_aql_query=True, 
                return_aql_result=True
            )
            self.logger.info("ArangoGraphQAChain initialization successful!")
        except Exception as e:
            self.logger.error(f"ArangoGraphQAChain initialization failed: {e}")
            raise

    def capture_stdout(self, func, *args, **kwargs) -> str:
        f = io.StringIO()
        with redirect_stdout(f):
            func(*args, **kwargs)
        captured_output = f.getvalue()
        return captured_output

    def execute_aql(self, query: str) -> Dict[str, str]:
        try:
            self.logger.debug(f"Executing AQL query: {query}")
            captured_output = self.capture_stdout(self.qa_chain.invoke, {self.qa_chain.input_key: query})
            self.logger.debug(f"AQL query execution completed. Captured output: {captured_output}")
            return {'captured_output': captured_output}
        except Exception as e:
            self.logger.error(f"Error executing AQL query: {e}")
            return {'error': str(e)}

    def clean_output(self, output: str) -> str:
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        cleaned_output = ansi_escape.sub('', output)
        return cleaned_output

    def fix_json_format(self, aql_result_line: str) -> str:
        fixed_json = aql_result_line.replace("'", '"').replace('\\', '\\\\').replace('\n', '\\n')
        return fixed_json

    def extract_aql_result(self, captured_output: str) -> Dict[str, list]:
        self.logger.debug("Extracting AQL result from captured output")
        cleaned_output = self.clean_output(captured_output)
        lines = cleaned_output.splitlines()
        aql_result_line = None
        for i, line in enumerate(lines):
            if "AQL Result:" in line:
                if i + 1 < len(lines):
                    aql_result_line = lines[i + 1].strip()
                break

        if aql_result_line:
            try:
                fixed_json = self.fix_json_format(aql_result_line)
                aql_result = json.loads(fixed_json)
                self.logger.debug(f"Extracted AQL result: {aql_result}")
                return {'aql_result': aql_result}
            except json.JSONDecodeError:
                self.logger.error("Failed to parse AQL result JSON")
        else:
            self.logger.warning("No AQL result found in captured output")
        return {'aql_result': []}

    def interpret_aql_result(self, aql_result: List[Dict[str, Any]]) -> str:
        self.logger.debug("Interpreting AQL result")
        prompt = (
            "Based on the following AQL results, provide a detailed and comprehensive scientific story "
            "that explains the associations between the genes and pathways:\n\n"
            f"AQL Results: {aql_result}\n\n"
        )
        try:
            response = self.llm.invoke(prompt)
            self.logger.debug(f"LLM interpretation: {response.content}")
            return response.content
        except Exception as e:
            self.logger.error(f"Error interpreting AQL result: {e}")
            return "Error interpreting results."

    def sequential_chain(self, query: str) -> Dict[str, Any]:
        self.logger.debug(f"Starting sequential chain for query: {query}")
        response = self.execute_aql(query)
        if 'error' in response:
            self.logger.error(f"Error in sequential chain: {response['error']}")
            return {'error': response['error']}
        
        captured_output = response['captured_output']
        final_response = self.extract_aql_result(captured_output)
        
        aql_result = final_response.get('aql_result', [])
        if aql_result:
            self.logger.debug("AQL result found, interpreting...")
            scientific_story = self.interpret_aql_result(aql_result)
            final_response['scientific_story'] = scientific_story
        else:
            self.logger.warning("No AQL result found in sequential chain")

        self.logger.debug(f"Sequential chain completed. Final response: {final_response}")
        return final_response

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query through the ArangoGraphQAChain.

        Args:
            user_query (str): The natural language query from the user.

        Returns:
            Dict[str, Any]: A dictionary containing the processed results.
        """
        self.logger.info(f"Processing user query: {user_query}")
        full_query = user_query + base_prompt
        self.logger.debug(f"Full query with base prompt: {full_query}")

        max_attempts = 3
        attempt = 1
        success = False
        failure_message = ("The prior AQL query failed to return results. "
                           "Please think this through step by step and refine your AQL statement. "
                           "The original question is as follows:")

        while attempt <= max_attempts and not success:
            self.logger.debug(f"Attempt {attempt}: Executing query...")
            response = self.sequential_chain(full_query)
            
            if 'error' in response:
                self.logger.error(f"Error in attempt {attempt}: {response['error']}")
                return {"error": f"An error occurred: {response['error']}"}
            
            aql_result = response.get('aql_result', [])

            if aql_result:
                success = True
                self.logger.debug(f"Attempt {attempt} - AQL Result: {aql_result}")
                self.logger.debug(f"LLM Interpretation: {response.get('scientific_story')}")
            else:
                self.logger.debug(f"Attempt {attempt} - AQL Result: No result found.")
                if attempt < max_attempts:
                    full_query = f"{failure_message} {full_query}"
                    self.logger.debug(f"Refined query for next attempt: {full_query}")
                else:
                    self.logger.warning(f"No result found after {max_attempts} tries.")

            attempt += 1

        final_response = {
            "original_query": user_query,
            "aql_result": aql_result,
            "interpretation": response.get('scientific_story', "No interpretation available."),
            "attempt_count": attempt - 1
        }
        self.logger.info(f"Query processing completed. Final response: {final_response}")
        return final_response

# Example usage (for testing purposes)
if __name__ == "__main__":
    # This is just for testing. In production, use the appropriate initialization.
    openai_wrapper = OpenAIWrapper()
    query_manager = QueryManager(SpokeWrapper(), openai_wrapper)
    question = "Which genes are most strongly associated with the development of Type 2 Diabetes, and what pathways do they influence?"
    result = query_manager.process_query(question)
    print(json.dumps(result, indent=2))
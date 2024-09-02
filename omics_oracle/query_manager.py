# omics_oracle/query_manager.py

import json
import io
import re
import traceback
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

def truncate(text: str, max_length: int = 100) -> str:
    return text[:max_length] + "..." if len(text) > max_length else text

class QueryManager:
    def __init__(self, spoke_wrapper: SpokeWrapper, openai_wrapper: OpenAIWrapper):
        self.spoke = spoke_wrapper
        self.openai_wrapper = openai_wrapper
        
        # Initialize the logger
        self.logger = setup_logger(__name__)

        # Example log message on initialization
        self.logger.info("QueryManager initialized successfully")
        
        # Initialize ChatOpenAI
        try:
            self.llm = ChatOpenAI(temperature=0, model='gpt-4o', openai_api_key=self.openai_wrapper.api_key)
            self.logger.info("ChatOpenAI initialization successful!")
        except Exception as e:
            self.logger.error(f"ChatOpenAI initialization failed: {e}\n\n{truncate(traceback.format_exc())}")
            raise

        # Initialize the ArangoDB client and connect to the database
        try:
            self.client = ArangoClient(hosts='http://127.0.0.1:8529')
            self.db = self.client.db('spoke23_human', username='root', password='ph')
            self.logger.info("ArangoDB connection successful!")
        except Exception as e:
            self.logger.error(f"ArangoDB connection failed: {e}\n\n{truncate(traceback.format_exc())}")
            raise

        # Fetch the existing graph from the database
        try:
            self.graph = ArangoGraph(self.db)
            self.logger.info("ArangoGraph initialization successful!")
        except Exception as e:
            self.logger.error(f"ArangoGraph initialization failed: {e}\n\n{truncate(traceback.format_exc())}")
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
            self.logger.error(f"ArangoGraphQAChain initialization failed: {e}\n\n{truncate(traceback.format_exc())}")
            raise

    def capture_stdout(self, func, *args, **kwargs) -> str:
        f = io.StringIO()
        with redirect_stdout(f):
            func(*args, **kwargs)
        captured_output = f.getvalue()
        return captured_output

    def execute_aql(self, query: str) -> Dict[str, str]:
        self.logger.debug(f"Attempting to execute AQL query: {truncate(query)}")
        try:
            result = self.qa_chain.invoke({self.qa_chain.input_key: query})
            captured_output = str(result)
            self.logger.debug(f"AQL query execution output: {truncate(captured_output)}")
            return {'captured_output': captured_output}
        except Exception as e:
            error_message = f"Error executing AQL query: {e}"
            self.logger.error(truncate(error_message))
            return {'error': error_message}

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
                self.logger.debug(f"Extracted AQL result: {truncate(str(aql_result))}")
                return {'aql_result': aql_result}
            except json.JSONDecodeError:
                self.logger.error(f"Failed to parse AQL result JSON: {truncate(aql_result_line)}")
        else:
            self.logger.debug("No AQL result found in captured output")
        return {'aql_result': []}

    def interpret_aql_result(self, aql_result: List[Dict[str, Any]]) -> str:
        self.logger.debug("Interpreting AQL result")
        prompt = (
            "Based on the following AQL results, provide a detailed and comprehensive scientific story "
            "that explains the associations between the genes and pathways:\n\n"
            f"AQL Results: {truncate(str(aql_result))}\n\n"
        )
        try:
            response = self.llm.invoke(prompt)
            interpretation = response.content
            self.logger.debug(f"LLM interpretation: {truncate(interpretation)}")
            return interpretation
        except Exception as e:
            error_message = f"Error interpreting AQL result: {e}"
            self.logger.error(truncate(error_message))
            return "Error interpreting results."

    def sequential_chain(self, query: str) -> Dict[str, Any]:
        self.logger.debug(f"Starting sequential chain for query: {truncate(query)}")
        response = self.execute_aql(query)
        if 'error' in response:
            self.logger.error(f"Error in sequential chain: {truncate(response['error'])}")
            return {'error': response['error']}
        
        captured_output = response['captured_output']
        final_response = self.extract_aql_result(captured_output)
        
        aql_result = final_response.get('aql_result', [])
        if aql_result:
            self.logger.debug(f"Attempt - AQL Result: {truncate(str(aql_result))}")
            scientific_story = self.interpret_aql_result(aql_result)
            self.logger.debug(f"LLM Interpretation: {truncate(scientific_story)}")
            final_response['scientific_story'] = scientific_story
        else:
            self.logger.debug("Attempt - No AQL result found.")

        self.logger.debug(f"Sequential chain completed. Final response: {truncate(str(final_response))}")
        return final_response

    def process_query(self, user_query: str) -> Dict[str, Any]:
        self.logger.debug(f"Starting to process user query: {truncate(user_query)}")
        full_query = user_query + base_prompt
        self.logger.debug(f"Full query: {truncate(full_query)}")

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
                error_message = f"Error in attempt {attempt}: {response['error']}"
                self.logger.error(truncate(error_message))
                return {"error": f"An error occurred: {error_message}"}
            
            aql_result = response.get('aql_result', [])
            self.logger.debug(f"Attempt {attempt} - AQL Result: {truncate(str(aql_result))}")

            if aql_result:
                success = True
                self.logger.debug(f"LLM Interpretation: {truncate(response.get('scientific_story', ''))}")
            else:
                self.logger.debug(f"Attempt {attempt} - No AQL result found.")
                if attempt < max_attempts:
                    full_query = f"{failure_message} {full_query}"
                    self.logger.debug(f"Refined query for next attempt: {truncate(full_query)}")
                else:
                    self.logger.warning(f"No result found after {max_attempts} tries.")

            attempt += 1

        return {
            "original_query": user_query,
            "aql_result": aql_result,
            "interpretation": response.get('scientific_story', "No interpretation available."),
            "attempt_count": attempt - 1
        }

# Example usage (for testing purposes)
if __name__ == "__main__":
    # This is just for testing. In production, use the appropriate initialization.
    openai_wrapper = OpenAIWrapper()
    query_manager = QueryManager(SpokeWrapper(), openai_wrapper)
    question = "Which genes are most strongly associated with the development of Type 2 Diabetes, and what pathways do they influence?"
    result = query_manager.process_query(question)
    print(json.dumps(result, indent=2))
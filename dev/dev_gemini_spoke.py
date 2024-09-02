import dspy
import os
import requests
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
import logging
from collections import deque
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
current_dir = os.getcwd()
dotenv_path = os.path.join(current_dir, '..', '.env')
if load_dotenv(dotenv_path):
    logger.info("Successfully loaded .env file")
else:
    raise ValueError("Failed to load .env file")

# Gemini API configuration
gemini_auth = os.getenv('GEMINI_AUTH')
gemini_url = os.getenv('GEMINI_URL')

if not gemini_auth or not gemini_url:
    raise ValueError("GEMINI_AUTH and GEMINI_URL must be set in the .env file")

class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove calls older than the period
            while self.calls and now - self.calls[0] >= self.period:
                self.calls.popleft()
            
            # If we've reached the maximum number of calls, wait
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            # Make the call
            result = func(*args, **kwargs)
            self.calls.append(time.time())
            return result
        return wrapper

class GeminiWrapper(object):
    def __init__(self):
        self.kwargs = {
            "temperature": 0.7,
            "max_tokens": 1000
        }
        self.rate_limiter = RateLimiter(max_calls=10, period=1.0)  # 10 calls per second
    
    @RateLimiter(max_calls=10, period=1.0)
    def send_query(self, query: str, temperature: float = None, max_tokens: int = None, retries: int = 3) -> Optional[Dict[str, Any]]:
        headers = {
            "Authorization": gemini_auth,
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gemini-pro",
            "messages": [{"role": "user", "content": query}],
            "temperature": temperature or self.kwargs["temperature"],
            "max_tokens": max_tokens or self.kwargs["max_tokens"]
        }
        
        logger.debug(f"Sending query to Gemini API: {query}")
        for attempt in range(retries):
            try:
                response = requests.post(gemini_url, headers=headers, json=payload)
                response.raise_for_status()
                logger.debug(f"Received response from Gemini API: {response.json()}")
                return response.json()
            except requests.RequestException as e:
                logger.error(f"Error sending query to Gemini API (Attempt {attempt + 1}/{retries}): {e}")
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"Error response content: {e.response.text}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Max retries reached. Unable to get a valid response from Gemini API.")
                    return None

    def __call__(self, prompt: str, **kwargs) -> str:
        temperature = kwargs.get('temperature', self.kwargs["temperature"])
        max_tokens = kwargs.get('max_tokens', self.kwargs["max_tokens"])
        result = self.send_query(prompt, temperature, max_tokens)
        if result and 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        return ""

    def check_api(self):
        test_query = "What is 2 + 2?"
        try:
            response = self.send_query(test_query)
            if response and 'choices' in response and len(response['choices']) > 0:
                logger.info("Gemini API check successful.")
                return True
            else:
                logger.error("Gemini API check failed: Unexpected response format.")
                return False
        except Exception as e:
            logger.error(f"Gemini API check failed: {str(e)}")
            return False

class BiomedicalQueryGenerator(dspy.Signature):
    """Generate a biomedical query based on a given question."""

    question = dspy.InputField()
    query = dspy.OutputField(desc="The generated biomedical query")

class AQLQueryGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_query = dspy.ChainOfThought(BiomedicalQueryGenerator)
    
    def forward(self, question: str) -> str:
        logger.debug(f"Generating AQL query for question: {question}")
        response = self.generate_query(question=question)
        logger.debug(f"Generated AQL query: {response.query}")
        return response.query

class SPOKEQueryExecutor:
    def __init__(self):
        # Placeholder for SPOKE database connection
        pass
    
    def execute_query(self, aql_query: str) -> List[Dict[str, Any]]:
        # Placeholder for actual SPOKE query execution
        # For now, return a simulated result
        logger.debug(f"Executing SPOKE query: {aql_query}")
        result = [{"result": f"Simulated SPOKE result for query: {aql_query}"}]
        logger.debug(f"SPOKE query result: {result}")
        return result

class BiomedicalAnswerGenerator(dspy.Signature):
    """Generate an answer to a biomedical question based on given context."""

    question = dspy.InputField()
    context = dspy.InputField()
    answer = dspy.OutputField(desc="The generated answer to the biomedical question")

class BiomedicalRAG(dspy.Module):
    def __init__(self):
        super().__init__()
        self.query_generator = AQLQueryGenerator()
        self.spoke_executor = SPOKEQueryExecutor()
        self.answer_generator = dspy.ChainOfThought(BiomedicalAnswerGenerator)
    
    def forward(self, question: str) -> Dict[str, Any]:
        logger.info(f"Processing question: {question}")
        aql_query = self.query_generator(question)
        spoke_results = self.spoke_executor.execute_query(aql_query)
        context = str(spoke_results)  # Convert results to string for simplicity
        logger.debug(f"Context for answer generation: {context}")
        response = self.answer_generator(question=question, context=context)
        logger.info(f"Generated answer: {response.answer}")
        return {
            "question": question,
            "aql_query": aql_query,
            "spoke_results": spoke_results,
            "answer": response.answer
        }

def validate_aql_query(example, pred):
    query = pred.query if hasattr(pred, 'query') else pred
    if not isinstance(query, str):
        return False
    required_keywords = ["FOR", "IN", "RETURN"]
    return all(keyword in query.upper() for keyword in required_keywords)

def main():
    logger.info("Initializing OmicsOracle biomedical query system...")

    # Configure DSPy with the Gemini model
    gemini = GeminiWrapper()
    
    # Perform API check
    if not gemini.check_api():
        logger.error("Exiting due to Gemini API check failure.")
        return

    dspy.settings.configure(lm=gemini)

    # Create and use the BiomedicalRAG pipeline
    logger.info("Creating BiomedicalRAG pipeline...")
    rag = BiomedicalRAG()

    # Example usage
    try:
        logger.info("Running example queries...")
        example_questions = [
            "What genes are mutated in cystic fibrosis?",
            "What proteins are involved in the p53 signaling pathway?",
            "List common drug targets for treating type 2 diabetes."
        ]
        for question in example_questions:
            logger.info(f"Processing question: {question}")
            result = rag(question)
            print(json.dumps(result, indent=2))
            print("\n" + "="*50 + "\n")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error("Traceback:", exc_info=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred in the main execution: {e}")
        logger.error("Traceback:", exc_info=True)
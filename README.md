# OmicsOracle

OmicsOracle is a Python package that integrates the Gemini API, OpenAI's GPT-4o model, SPOKE knowledge graph (using ArangoDB), and a Gradio interface to create a user-friendly system for querying and analyzing biomedical data.

## System Requirements

OmicsOracle has been set up and tested with Python 3.9.18. Make sure you have this version or a compatible one installed on your system.

## Installation

To install OmicsOracle, follow these steps:

1. Clone this repository:
   ```bash
   git clone https://git.phenome.health/trent.leslie/omicsoracle.git
   cd omicsoracle
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install ArangoDB:
   ```bash
   # Add the repository key to apt
   curl -OL https://download.arangodb.com/arangodb312/DEBIAN/Release.key
   sudo apt-key add - < Release.key

   # Use apt-get to install arangodb
   echo 'deb https://download.arangodb.com/arangodb312/DEBIAN/ /' | sudo tee /etc/apt/sources.list.d/arangodb.list
   sudo apt-get install apt-transport-https
   sudo apt-get update
   sudo apt-get install arangodb3=3.12.2-1

   # To install the debug symbols package (not required by default)
   # sudo apt-get install arangodb3-dbg=3.12.2-1
   ```

4. Import SPOKE JSON to ArangoDB:
   ```bash
   wget https://git.phenome.health/-/snippets/4/raw/main/import_spoke_json_to_arangodb.py
   python import_spoke_json_to_arangodb.py
   ```

## Configuration

OmicsOracle uses environment variables for configuration. Create a `.env` file in the root directory of the project with the following content:

```
GEMINI_AUTH=your_gemini_auth_key
GEMINI_URL=your_gemini_api_url
ARANGO_HOST=your_arango_host
ARANGO_DB=your_arango_database_name
ARANGO_USERNAME=your_arango_username
ARANGO_PASSWORD=your_arango_password
OPENAI_API_KEY=your_openai_api_key
```

Make sure to replace the placeholder values with your actual API keys and connection details.

## Usage

To use OmicsOracle, follow these steps:

1. Ensure you have installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up the environment variables by creating a `.env` file as described in the Configuration section.

3. Run the Gradio interface using the following command from the project root directory:
   ```bash
   python run_gradio_interface.py
   ```

This will launch a web interface where you can enter your biomedical queries. The interface will be accessible in your web browser, typically at `http://localhost:7861` unless specified otherwise.

## Development

To contribute to OmicsOracle, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Implement your changes
4. Write tests for your new feature
5. Run the test suite to ensure all tests pass:
   ```bash
   python -m pytest tests/ -v
   ```
6. Submit a pull request

## Recent Changes

- Added OpenAIWrapper to integrate OpenAI's GPT-4o model
- Updated both GeminiWrapper and SpokeWrapper to load configuration from environment variables
- Improved error handling and logging in all wrappers
- SpokeWrapper continues to use pyArango for interacting with the ArangoDB-based SPOKE database
- Updated the initialization process for wrappers to use environment variables
- Integrated Gradio interface for a user-friendly query system
- Added run_gradio_interface.py for easy launching of the Gradio interface
- Improved test suite with mock implementations for better isolation
- Updated OpenAIWrapper to allow for dependency injection of base prompts, improving testability
- Fixed import statement for ArangoGraph to use the new path from langchain_community.graphs
- Updated QueryManager to handle cases where 'attempt_count' is not present in the response
- Improved test coverage for QueryManager and GradioInterface
- Resolved issues with mock objects in test suite, ensuring all tests pass successfully

## Testing

To run the test suite, use the following command from the project root directory:

```bash
python -m pytest tests/ -v
```

This will run all tests and display detailed output. Make sure all tests pass before submitting a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
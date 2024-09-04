# OmicsOracle

OmicsOracle is a Python package that integrates the Gemini API, OpenAI's GPT-4o model, SPOKE knowledge graph (using ArangoDB), and a Gradio interface to create a user-friendly system for querying and analyzing biomedical data.

## System Requirements

OmicsOracle requires Python 3.9.18. Make sure you have this version installed on your system before proceeding.

## Installation

To install OmicsOracle, follow these steps:

1. Install Python 3.9.18:
   First, check if Python 3.9 is already installed:
   ```bash
   python3.9 --version
   ```
   
   If you see an error or a different version, follow these steps to install Python 3.9.18:
   
   For Ubuntu/Debian:
   ```bash
   sudo apt update
   sudo apt install software-properties-common
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update
   sudo apt install python3.9 python3.9-venv
   ```
   
   For macOS (using Homebrew):
   ```bash
   brew install python@3.9
   ```
   
   For other operating systems, please refer to the official Python documentation for installation instructions.

   After installation, verify that Python 3.9 is installed correctly:
   ```bash
   python3.9 --version
   ```

2. Set up a virtual environment with Python 3.9.18:
   Create a directory for your virtual environments (if you don't already have one):
   ```bash
   mkdir ~/venvs
   cd ~/venvs
   ```

   Create a virtual environment for OmicsOracle:
   ```bash
   python3.9 -m venv omics_env
   ```

   Activate the virtual environment:
   ```bash
   source omics_env/bin/activate
   ```

   Your prompt should now indicate that you're in the virtual environment (e.g., `(omics_env) $`).

3. Clone the OmicsOracle repository:
   ```bash
   git clone https://git.phenome.health/trent.leslie/omicsoracle.git
   cd omicsoracle
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Install ArangoDB:
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

   During the installation process, you will be prompted to set a password for the root user. Use the password 'ph' as subsequent scripts assume this password:
   ```
   Please enter password for root user:
   ph
   ```

6. Start ArangoDB:
   After installation, you can start ArangoDB using the following command:
   ```bash
   sudo systemctl start arangodb3
   ```
   To ensure ArangoDB starts automatically on system boot, you can enable the service:
   ```bash
   sudo systemctl enable arangodb3
   ```
   You can check the status of the ArangoDB service using:
   ```bash
   sudo systemctl status arangodb3
   ```

7. Import SPOKE JSON to ArangoDB:
   First, download the import script:
   ```bash
   wget https://git.phenome.health/-/snippets/4/raw/main/import_spoke_json_to_arangodb.py
   ```

   You have two options to run the import script:

   a. Run the script normally (this will keep the process in the foreground):
   ```bash
   python import_spoke_json_to_arangodb.py
   ```

   b. Run the script using `nohup` to keep it running in the background, even if you're disconnected from the session:
   ```bash
   nohup python import_spoke_json_to_arangodb.py > import_log.out 2>&1 &
   ```
   This command will run the script in the background, redirect output to `import_log.out`, and continue running even if you close your terminal session. You can check the progress by viewing the `import_log.out` file:
   ```bash
   tail -f import_log.out
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

1. Ensure you're in the virtual environment. If not, activate it:
   ```bash
   source ~/venvs/omics_env/bin/activate
   ```

2. Navigate to the OmicsOracle directory:
   ```bash
   cd path/to/omicsoracle
   ```

3. Set up the environment variables by creating a `.env` file as described in the Configuration section.

4. Run the Gradio interface using the following command from the project root directory:
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
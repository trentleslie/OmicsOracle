# OmicsOracle

OmicsOracle is a Python package that integrates the Gemini API, SPOKE knowledge graph (using ArangoDB), and a Gradio interface to create a user-friendly system for querying and analyzing biomedical data.

## Installation

To install OmicsOracle, clone this repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/omics_oracle.git
cd omics_oracle
pip install -r requirements.txt
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
```

Make sure to replace the placeholder values with your actual API keys and connection details.

## Usage

To use OmicsOracle, you can run the Gradio interface using the following command from the project root directory:

```bash
python run_gradio_interface.py
```

This will launch a web interface where you can enter your biomedical queries. The interface will be accessible in your web browser, typically at `http://localhost:7860` unless specified otherwise.

## Development

To contribute to OmicsOracle, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Implement your changes
4. Write tests for your new feature
5. Run the test suite to ensure all tests pass
6. Submit a pull request

## Recent Changes

- Updated both GeminiWrapper and SpokeWrapper to load configuration from environment variables
- Improved error handling and logging in both wrappers
- SpokeWrapper continues to use pyArango for interacting with the ArangoDB-based SPOKE database
- Updated the initialization process for both wrappers to use environment variables
- Integrated Gradio interface for a user-friendly query system
- Added run_gradio_interface.py for easy launching of the Gradio interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.
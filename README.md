# OmicsOracle

OmicsOracle is a Python package that integrates the Gemini API, Spoke knowledge graph API, and a Gradio interface to create a user-friendly system for querying and analyzing biomedical data.

## Installation

To install OmicsOracle, clone this repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/omics_oracle.git
cd omics_oracle
pip install -r requirements.txt
```

## Usage

To use OmicsOracle, you need to set up your API keys and connection details for the Gemini API and Spoke knowledge graph. Update the `launch_interface` function in `omics_oracle/gradio_interface.py` with your credentials:

```python
gemini_wrapper = GeminiWrapper(api_key="YOUR_API_KEY", base_url="YOUR_BASE_URL")
spoke_wrapper = SpokeWrapper(host="YOUR_HOST", db_name="YOUR_DB_NAME", username="YOUR_USERNAME", password="YOUR_PASSWORD")
```

Then, you can run the Gradio interface:

```bash
python -m omics_oracle.gradio_interface
```

This will launch a web interface where you can enter your biomedical queries.

## Development

To contribute to OmicsOracle, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Implement your changes
4. Write tests for your new feature
5. Run the test suite to ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
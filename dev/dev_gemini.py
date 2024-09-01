import os
import requests
import json
import httpx
from dotenv import load_dotenv

# Get the current working directory
current_dir = os.getcwd()

# Construct the path to the .env file in the parent directory
dotenv_path = os.path.join(current_dir, '..', '.env')

print(f"Looking for .env file at: {dotenv_path}")

# Load the .env file
if load_dotenv(dotenv_path):
    print("Successfully loaded .env file")
else:
    print("Failed to load .env file")

# Gemini API configuration
gemini_auth = os.getenv('GEMINI_AUTH')
gemini_url = os.getenv('GEMINI_URL')

if not gemini_auth or not gemini_url:
    raise ValueError("GEMINI_AUTH and GEMINI_URL must be set in the .env file")

print(f"GEMINI_AUTH: {gemini_auth}")
print(f"GEMINI_URL: {gemini_url}")

def send_query_to_gemini(query: str) -> dict:
    """
    Send a query to the Gemini API and return the response.
    """
    headers = {
        "Authorization": gemini_auth,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gemini-pro",
        "messages": [{"role": "user", "content": query}]
    }
    
    print(f"Sending request to: {gemini_url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(gemini_url, headers=headers, json=payload)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
        print(f"Response content: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error sending query to Gemini API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error response content: {e.response.text}")
        return None

# Test with a simple GET request
print("Attempting a simple GET request:")
try:
    response = requests.get(gemini_url)
    print(f"GET request status code: {response.status_code}")
    print(f"GET request content: {response.text}")
except requests.RequestException as e:
    print(f"Error making GET request: {e}")

# Test with httpx
print("\nAttempting request with httpx:")
with httpx.Client() as client:
    try:
        headers = {
            "Authorization": gemini_auth,
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gemini-pro",
            "messages": [{"role": "user", "content": "Test query"}]
        }
        response = client.post(gemini_url, headers=headers, json=payload)
        print(f"HTTPX status code: {response.status_code}")
        print(f"HTTPX content: {response.text}")
    except httpx.RequestError as e:
        print(f"HTTPX error: {e}")

# Test the Gemini API
print("\nTesting Gemini API with main function:")
test_query = "What are the main symptoms of Alzheimer's disease?"
result = send_query_to_gemini(test_query)

if result:
    print("Gemini API Response:")
    print(json.dumps(result, indent=2))
    
    # Extract and print the content of the response
    if 'choices' in result and len(result['choices']) > 0:
        content = result['choices'][0].get('message', {}).get('content', 'No content found')
        print("\nExtracted Content:")
        print(content)
    else:
        print("Unexpected response structure")
else:
    print("Failed to get a response from Gemini API")
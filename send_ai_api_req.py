"""
LocalAI API Request Example

LocalAI is compatible with the OpenAI API format.
It can be run via Docker or standalone.

Run LocalAI via Docker:
  docker run -p 8080:8080 -e MODELS_PATH=/models -v ~/.cache/localai/models:/models localai/localai:latest
"""

import requests
import os

# Configuration
LOCALAI_URL = os.environ.get("LOCALAI_URL", "http://localhost:8080")
MODEL = os.environ.get("LOCALAI_MODEL", "versatillama-llama-3.2-3b-instruct-abliterated")  # Model name available in LocalAI


def send_chat_request(prompt: str) -> dict:
    """Send a chat completion request to LocalAI"""
    
    url = f"{LOCALAI_URL}/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.5,
        "max_tokens": 150,
    }
    
    try:
        print(f"Sending request to LocalAI at {LOCALAI_URL}...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            print(f"✓ Response: {message}")
            return result
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to LocalAI at {LOCALAI_URL}")
        print("Make sure LocalAI is running: docker run -p 8080:8080 localai/localai:latest")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def send_completion_request(prompt: str) -> dict:
    """Send a text completion request to LocalAI"""
    
    url = f"{LOCALAI_URL}/v1/completions"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "temperature": 0.5,
        "max_tokens": 150,
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            text = result["choices"][0]["text"]
            print(f"✓ Response: {text}")
            return result
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


if __name__ == "__main__":
    print("=== LocalAI API Test ===\n")
    
    # Test chat completion
    print("Testing Chat Completion API:")
    send_chat_request("What is the capital of France?")
    
    print("\n" + "=" * 50 + "\n")
    
    # Test text completion
    print("Testing Text Completion API:")
    send_completion_request("The capital of France is")
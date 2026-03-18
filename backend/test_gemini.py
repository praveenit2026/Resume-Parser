import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("GEMINI_API_KEY not found in .env")
    exit(1)

model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

payload = {
    "contents": [{
        "parts": [{"text": "Hello, this is a very short test. Please reply with 'API is working'."}]
    }]
}

try:
    print(f"Testing the API using model: {model}...")
    start_time = time.time()
    response = requests.post(url, json=payload, timeout=10)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No text found')
        print("\n✅ SUCCESS!")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print(f"Response: {text}")
    else:
        print(f"\n❌ ERROR: API returned status code {response.status_code}")
        print("Response Details:")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ ERROR: Failed to make the request: {e}")

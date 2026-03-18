import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def list_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    response = httpx.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        models = response.json()
        for model in models.get("models", []):
            print(f"Name: {model['name']}, Methods: {model['supportedGenerationMethods']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    list_models()

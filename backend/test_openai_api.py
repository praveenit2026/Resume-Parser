import requests
import json

url = "http://127.0.0.1:8001/api/analyze"

job_description = "We are looking for a Python backend developer with experience in FastAPI, Docker, and AWS."

try:
    with open("../frontend/dummy_resume.txt", "r") as f:
        resume_text = f.read()
except FileNotFoundError:
    resume_text = "I am a Python developer with 5 years of experience in Django and FastAPI. I know Docker and AWS."

data = {
    "job_description": job_description,
    "resume_text": resume_text
}

print("Sending request to backend...")
response = requests.post(url, data=data)

print(f"Status Code: {response.status_code}")
try:
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Response text:", response.text)

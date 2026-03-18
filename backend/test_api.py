import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test health
        r = await client.get("http://localhost:8000/health")
        print("Health:", r.json())
        
        # Test analyze
        r = await client.post(
            "http://localhost:8000/api/analyze",
            data={
                "job_description": "Senior Python Developer. Requirements: Python, FastAPI, SQL, Docker, 3+ years experience.",
                "resume_text": "Jane Doe is a Python developer with 4 years of experience in Python, FastAPI, PostgreSQL, Docker, and REST APIs. She has a BS in Computer Science from Stanford University."
            }
        )
        print("Status:", r.status_code)
        print("Response:", r.text[:1000])

asyncio.run(test())

import httpx
import asyncio

async def test():
    key = "5c23e138-29cf-435e-ba54-eafc6d507a1e"
    print(f"Testing API key: {key}")
    
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.sambanova.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "Meta-Llama-3.1-70B-Instruct",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
        )
        print("Status code:", r.status_code)
        print("Response text:", r.text)

asyncio.run(test())

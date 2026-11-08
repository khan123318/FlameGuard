
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import time

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

print("Testing Gemini Generate Content API...")

start = time.perf_counter()

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Reply with exactly one word: OK",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="low"
        )
    )
)

elapsed = time.perf_counter() - start

print("\nResponse:", response.text)
print(f"Response time: {elapsed:.2f} seconds")


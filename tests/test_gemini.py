from google import genai
from dotenv import load_dotenv
import os

# Load API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in .env")

# Connect to Gemini
client = genai.Client(api_key=api_key)

try:
    # Send a request using the Interactions API
    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=(
            "Explain briefly why studying combustion "
            "in microgravity is important for spacecraft safety."
        )
    )

    print("\nGemini Response:\n")
    print(response.output_text)

except Exception as error:
    print("\nGemini API Error:")
    print(error)


import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for m in client.models.list():
    name = m.name.lower()
    if 'imagen' in name or 'veo' in name:
        print(f"Model: {m.name}, Supported operations: {m.supported_generation_methods}")

import os

from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
print("Starting video generation...")
try:
    operation = client.models.generate_videos(
        model='veo-2.0-generate-001',
        prompt='A single red pixel blinking'
    )
    print(f"Operation type: {type(operation)}")
    print(f"Operation dir: {dir(operation)}")
    print(f"Operation vars: {vars(operation) if hasattr(operation, '__dict__') else 'No vars'}")
except Exception as e:
    print(f"Error: {e}")

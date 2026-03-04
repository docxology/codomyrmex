import os
from google import genai
try:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    models = list(client.models.list())
    for m in models:
        if "veo" in m.name.lower() or "video" in m.name.lower():
            print(f"Model: {m.name}, Actions: {m.supported_actions}")
except Exception as e:
    print(f"Error: {e}")

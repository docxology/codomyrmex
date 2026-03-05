import os

from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

models_to_test = ["veo-2.0-generate", "veo-3.1-generate", "veo-001-preview", "lumiere-generate", "veo-1.0-generate"]
for m in models_to_test:
    print(f"\n--- Testing {m} ---")
    try:
        op = client.models.generate_videos(model=m, prompt="A blue circle, 1 second")
        print(f"Success initializing operation for {m}")
    except Exception as e:
        print(f"Failed {m}: {str(e)[:150]}")

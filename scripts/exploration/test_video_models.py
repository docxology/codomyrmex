import os
from google import genai
import sys

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    sys.exit(1)

client = genai.Client(api_key=api_key)
models = client.models.list()
video_models = []
image_models = []
for m in models:
    name = m.name.lower()
    if "veo" in name or "video" in name:
        video_models.append(m.name)
    if "imagen" in name or "image" in name:
        image_models.append(m.name)
        
print("VIDEO MODELS:", video_models)
print("IMAGE MODELS:", image_models)

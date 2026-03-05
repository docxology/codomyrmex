import os

from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
print("Starting generation...")
operation = client.models.generate_videos(
    model="veo-2.0-generate-001",
    prompt="A minimalist animation of a loading circle, 2 seconds",
    config={"person_generation": "ALLOW_ADULT"},
)
print("Polling operation...")
import contextlib
import time

while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation=operation)

if operation.error:
    print(f"Error: {operation.error}")
else:
    result = operation.result
    print(f"Result type: {type(result)}")
    print(f"Result dir: {dir(result)}")
    if hasattr(result, "generated_videos"):
        print(f"Has generated_videos: {len(result.generated_videos)}")
    if hasattr(result, "videos"):
        print(f"Has videos: {len(result.videos)}")
    try:
        print(f"Dump: {result.model_dump()}")
    except Exception as e:
        print(f"Dump error: {e}")
        with contextlib.suppress(AttributeError):
            print(f"Dict: {result.__dict__}")

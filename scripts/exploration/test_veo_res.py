import os
import sys

from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("No GEMINI_API_KEY set.")
    sys.exit(1)

client = genai.Client(api_key=api_key)
print("Starting Veo 2 prediction...")
try:
    operation = client.models.generate_videos(
        model="veo-2.0-generate-001",
        prompt="A minimalist animation of a loading circle, 2 seconds",
    )
    import time
    while not operation.done:
        print(".", end="", flush=True)
        time.sleep(5)
        operation = client.operations.get(operation=operation)
    print("\nDone")
    if operation.error:
        print(f"Error from operation: {operation.error}")
    else:
        print("Success! Got result.")
        result = operation.result
        if hasattr(result, "generated_videos"):
            print(f"Generated {len(result.generated_videos)} videos.")
            if len(result.generated_videos) > 0:
                print(f"Video bytes length: {len(result.generated_videos[0].video.video_bytes)}")
except Exception as e:
    print(f"Exception: {e}")

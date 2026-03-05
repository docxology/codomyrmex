import os
import sys
import urllib.request

from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
print("Starting Veo 2 prediction for download test...")
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
        sys.exit(1)

    result = operation.result
    if hasattr(result, "generated_videos") and len(result.generated_videos) > 0:
        video_obj = result.generated_videos[0].video
        uri = getattr(video_obj, "uri", None)
        bytes_val = getattr(video_obj, "video_bytes", None)
        print(f"Bytes: {'yes' if bytes_val else 'no'}")
        print(f"URI: {uri}")
        if uri:
            print("Downloading from URI...")
            urllib.request.urlretrieve(uri, "output/test_veo_uri_download.mp4")
            print("Successfully downloaded to output/test_veo_uri_download.mp4")
except Exception as e:
    print(f"Exception: {e}")

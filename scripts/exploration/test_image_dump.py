import os

from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
print("Generating image...")
try:
    result = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt='A tiny cute ant programmer typing on a mechanical keyboard',
        config=dict(number_of_images=1, aspect_ratio="1:1")
    )
    for img in result.images:
        print(f"Bytes len: {len(img.image.image_bytes)}")
except Exception as e:
    print(f"Error: {e}")

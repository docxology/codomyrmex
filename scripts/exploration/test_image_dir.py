import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
try:
    result = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt='A tiny cute ant',
        config=dict(number_of_images=1)
    )
    for img in result.images:
        print("IMG:", dir(img))
        print("IMG dict properties?", vars(img) if hasattr(img, '__dict__') else "No vars")
        print("IMG.image:", dir(img.image))
except Exception as e:
    print(f"Error: {e}")

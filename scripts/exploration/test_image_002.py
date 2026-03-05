import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    result = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt='A tiny cute ant programmer typing on a mechanical keyboard',
        config=dict(
            number_of_images=1,
            aspect_ratio="1:1"
        )
    )
    print("Success. Image count:", len(result.images))
    if result.images:
        print("First image byte length:", len(result.images[0].image.image_bytes))
        with open("output/test_image_2.png", "wb") as f:
            f.write(result.images[0].image.image_bytes)
        print("Written to output/test_image_2.png")
except Exception as e:
    print(f"Error: {e}")

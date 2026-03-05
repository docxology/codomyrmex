import os

from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Generating image with imagen-4.0-generate-001")
try:
    result = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt='A tiny cute ant programmer typing on a mechanical keyboard',
        config=dict(
            number_of_images=1,
            aspect_ratio="1:1"
        )
    )
    if result.images:
        print("Success! Image generated.")
        with open("output/test_image_4.png", "wb") as f:
            f.write(result.images[0].image.image_bytes)
        print("Saved to output/test_image_4.png")
except Exception as e:
    print(f"Error: {e}")
